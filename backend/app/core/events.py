"""
事件推送系统
负责检测数据变化并推送事件给前端
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Set, Optional

# 🔄 使用HTTP客户端进行真正的HTTP请求，不导入Python模块
from app.core.http_client import http_client

logger = logging.getLogger(__name__)

class EventQueue:
    """事件队列系统 - 兼容旧API"""
    
    def __init__(self):
        self.subscribers: Dict[str, Any] = {}
        self.queues: Dict[str, List[Dict[str, Any]]] = {}
        self.global_queue: List[Dict[str, Any]] = []
        
    async def subscribe(self, user_id: str):
        """订阅用户事件"""
        if user_id not in self.queues:
            self.queues[user_id] = []
        if user_id not in self.subscribers:
            self.subscribers[user_id] = asyncio.Queue()
        return self.subscribers[user_id]
    
    async def unsubscribe(self, user_id: str, connection=None):
        """取消订阅"""
        if user_id in self.subscribers:
            del self.subscribers[user_id]
        if user_id in self.queues:
            del self.queues[user_id]
    
    def get_events_since(self, user_id: str, since: str) -> List[Dict[str, Any]]:
        """获取指定时间后的事件"""
        try:
            since_time = datetime.fromisoformat(since.replace('Z', '+00:00'))
            user_events = self.queues.get(user_id, [])
            return [
                event for event in user_events 
                if datetime.fromisoformat(event.get('timestamp', '')) > since_time
            ]
        except:
            return []
    
    async def publish(self, user_id: str, event_data: Dict[str, Any]):
        """发布事件到用户队列"""
        # 添加到用户队列
        if user_id not in self.queues:
            self.queues[user_id] = []
        
        event_data['timestamp'] = datetime.now().isoformat()
        self.queues[user_id].append(event_data)
        
        # 限制队列长度
        if len(self.queues[user_id]) > 100:
            self.queues[user_id] = self.queues[user_id][-100:]
        
        # 推送到订阅者
        if user_id in self.subscribers:
            try:
                await self.subscribers[user_id].put(event_data)
            except:
                pass

class EventManager:
    """事件管理器"""
    
    def __init__(self):
        self.subscribers: Dict[str, Set[Any]] = {}
        self.last_check: Dict[str, datetime] = {}
        self.running = False
        self.event_queue = EventQueue()  # 添加事件队列
        
    async def start(self):
        """启动事件系统"""
        if self.running:
            return
            
        self.running = True
        logger.info("🚀 事件推送系统启动")
        
        # 启动各种检查任务
        asyncio.create_task(self._monitor_announcements())
        asyncio.create_task(self._monitor_grades())
        asyncio.create_task(self._monitor_transactions())
        asyncio.create_task(self._monitor_library())
        
    async def stop(self):
        """停止事件系统"""
        self.running = False
        logger.info("🛑 事件推送系统停止")
    
    def subscribe(self, event_type: str, callback: Any):
        """订阅事件"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = set()
        self.subscribers[event_type].add(callback)
        
    def unsubscribe(self, event_type: str, callback: Any):
        """取消订阅"""
        if event_type in self.subscribers:
            self.subscribers[event_type].discard(callback)
    
    async def emit(self, event_type: str, data: Dict[str, Any]):
        """发射事件"""
        if event_type in self.subscribers:
            for callback in self.subscribers[event_type]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(event_type, data)
                    else:
                        callback(event_type, data)
                except Exception as e:
                    logger.error(f"事件回调失败: {e}")
                    
        # 同时推送到事件队列（用于流式推送）
        if "student_id" in data:
            await self.event_queue.publish(data["student_id"], {
                "event_type": event_type,
                **data
            })
        elif "person_id" in data:
            await self.event_queue.publish(data["person_id"], {
                "event_type": event_type,
                **data
            })
    
    async def _monitor_announcements(self):
        """监控公告更新"""
        while self.running:
            try:
                await self._check_announcements()
                await asyncio.sleep(30)  # 每30秒检查一次
            except Exception as e:
                logger.error(f"监控公告失败: {e}")
                await asyncio.sleep(60)
    
    async def _check_announcements(self):
        """检查公告更新"""
        try:
            # 🔄 HTTP请求data-service查询最近的公告（移除Django风格的时间过滤）
            recent_announcements = await http_client.query_table(
                "announcements",
                filters={
                    "is_deleted": False,
                    "status": "published"
                },
                order_by="publish_time DESC",
                limit=10
            )
            
            # 手动过滤时间（由于SQLite不支持Django风格的查询）
            last_check_time = self.last_check.get('announcements', 
                                                datetime.now() - timedelta(minutes=5))
            
            # 处理新公告
            for announcement in recent_announcements.get("records", []):
                try:
                    # 检查发布时间
                    publish_time_str = announcement.get("publish_time")
                    if publish_time_str:
                        publish_time = datetime.fromisoformat(publish_time_str.replace('Z', '+00:00'))
                        if publish_time > last_check_time:
                            await self.emit("announcement", {
                                "announcement_id": announcement.get("announcement_id"),
                                "title": announcement.get("title"),
                                "category": announcement.get("category"),
                                "priority": announcement.get("priority"),
                                "publish_time": announcement.get("publish_time"),
                                "is_urgent": announcement.get("is_urgent", False),
                                "is_pinned": announcement.get("is_pinned", False),
                                "is_public": True  # 公告是公开的
                            })
                except Exception as e:
                    logger.warning(f"处理公告记录失败: {e}")
                    continue
            
            # 更新检查时间
            self.last_check['announcements'] = datetime.now()
            
        except Exception as e:
            logger.error(f"检查公告更新失败: {e}")
    
    async def _monitor_grades(self):
        """监控成绩更新"""
        while self.running:
            try:
                await self._check_grades()
                await asyncio.sleep(60)  # 每1分钟检查一次
            except Exception as e:
                logger.error(f"监控成绩失败: {e}")
                await asyncio.sleep(120)
    
    async def _check_grades(self):
        """检查成绩更新"""
        try:
            # 🔄 HTTP请求data-service查询最近更新的成绩记录
            recent_grades = await http_client.query_table(
                "grades",
                filters={
                    "is_deleted": False,
                    "grade_status": "confirmed"
                },
                order_by="created_at DESC",
                limit=50
            )
            
            # 手动过滤时间
            last_check_time = self.last_check.get('grades', 
                                                datetime.now() - timedelta(minutes=5))
            
            # 检查是否有新成绩
            for grade in recent_grades.get("records", []):
                try:
                    # 检查成绩时间字段
                    grade_time_str = grade.get("created_at") or grade.get("updated_at") or grade.get("grade_time")
                    if grade_time_str:
                        grade_time = datetime.fromisoformat(grade_time_str.replace('Z', '+00:00'))
                        if grade_time > last_check_time:
                            # 🔄 HTTP请求获取课程信息
                            course_info = await http_client.query_table(
                                "courses",
                                filters={"course_id": grade.get("course_id")},
                                limit=1
                            )
                            
                            course_records = course_info.get("records", [])
                            course_name = course_records[0].get("course_name", "未知课程") if course_records else "未知课程"
                            
                            await self.emit("grade_update", {
                                "student_id": grade.get("student_id"),
                                "course_name": course_name,
                                "total_score": grade.get("total_score"),
                                "grade_level": grade.get("grade_level"),
                                "is_passed": grade.get("is_passed", False),
                                "grade_time": grade_time_str,
                                "is_public": False  # 成绩是私人的
                            })
                except Exception as e:
                    logger.warning(f"处理成绩记录失败: {e}")
                    continue
            
            # 更新检查时间
            self.last_check['grades'] = datetime.now()
            
        except Exception as e:
            logger.error(f"检查成绩更新失败: {e}")
    
    async def _monitor_transactions(self):
        """监控消费交易"""
        while self.running:
            try:
                await self._check_transactions()
                await asyncio.sleep(30)  # 每30秒检查一次
            except Exception as e:
                logger.error(f"监控交易失败: {e}")
                await asyncio.sleep(60)
    
    async def _check_transactions(self):
        """检查交易更新"""
        try:
            # 🔄 HTTP请求data-service查询最近的交易记录
            recent_transactions = await http_client.query_table(
                "transactions",
                filters={
                    "is_deleted": False,
                    "transaction_status": "success"
                },
                order_by="transaction_time DESC",
                limit=20
            )
            
            # 手动过滤时间
            last_check_time = self.last_check.get('transactions', 
                                                datetime.now() - timedelta(minutes=5))
            
            # 处理新交易
            for transaction in recent_transactions.get("records", []):
                try:
                    trans_time_str = transaction.get("transaction_time")
                    if trans_time_str:
                        trans_time = datetime.fromisoformat(trans_time_str.replace('Z', '+00:00'))
                        if trans_time > last_check_time:
                            await self.emit("transaction", {
                                "person_id": transaction.get("person_id"),
                                "amount": transaction.get("amount"),
                                "transaction_type": transaction.get("transaction_type"),
                                "merchant_name": transaction.get("merchant_name"),
                                "transaction_time": trans_time_str,
                                "balance_after": transaction.get("balance_after"),
                                "is_public": False  # 交易是私人的
                            })
                except Exception as e:
                    logger.warning(f"处理交易记录失败: {e}")
                    continue
            
            # 更新检查时间
            self.last_check['transactions'] = datetime.now()
            
        except Exception as e:
            logger.error(f"检查交易更新失败: {e}")
    
    async def _monitor_library(self):
        """监控图书馆操作"""
        while self.running:
            try:
                await self._check_library()
                await asyncio.sleep(120)  # 每2分钟检查一次
            except Exception as e:
                logger.error(f"监控图书馆失败: {e}")
                await asyncio.sleep(180)
    
    async def _check_library(self):
        """检查图书馆更新"""
        try:
            # 🔄 HTTP请求data-service查询最近的借阅记录
            borrow_records = await http_client.query_table(
                "borrow_records",
                filters={
                    "is_deleted": False
                },
                order_by="borrow_date DESC",
                limit=20
            )
            
            # 处理到期提醒
            for record in borrow_records.get("records", []):
                try:
                    due_date_str = record.get("due_date")
                    if due_date_str:
                        due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
                        days_left = (due_date - datetime.now()).days
                        
                        # 提前3天提醒
                        if days_left <= 3 and days_left >= 0:
                            # 🔄 HTTP请求获取图书信息
                            book_result = await http_client.query_table(
                                "books",
                                filters={"book_id": record.get("book_id")},
                                limit=1
                            )
                            
                            book_records = book_result.get("records", [])
                            book_title = book_records[0].get("title", "未知图书") if book_records else "未知图书"
                            
                            await self.emit("library_reminder", {
                                "borrower_id": record.get("borrower_id"),
                                "person_id": record.get("borrower_id"),  # 添加person_id用于推送
                                "book_title": book_title,
                                "due_date": due_date_str,
                                "days_left": days_left,
                                "record_id": record.get("record_id"),
                                "is_public": False  # 借阅提醒是私人的
                            })
                except Exception as e:
                    logger.warning(f"处理借阅记录失败: {e}")
                    continue
            
            # 更新检查时间
            self.last_check['library'] = datetime.now()
            
        except Exception as e:
            logger.error(f"检查图书馆更新失败: {e}")

# 全局事件管理器实例
event_manager = EventManager()

# 导出兼容的event_queue对象
event_queue = event_manager.event_queue

async def start_event_system():
    """启动事件系统"""
    await event_manager.start()

async def stop_event_system():
    """停止事件系统"""
    await event_manager.stop()

def subscribe_to_event(event_type: str, callback: Any):
    """订阅事件"""
    event_manager.subscribe(event_type, callback)

def unsubscribe_from_event(event_type: str, callback: Any):
    """取消订阅事件"""
    event_manager.unsubscribe(event_type, callback)

async def emit_event(event_type: str, data: Dict[str, Any]):
    """发射事件"""
    await event_manager.emit(event_type, data) 