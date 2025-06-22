"""
事件驱动推送系统
实现数据库变化监听、事件队列管理和SSE推送
"""

import asyncio
import json
import time
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Set, Any
from collections import defaultdict, deque
import logging
from enum import Enum

logger = logging.getLogger(__name__)

class EventType(str, Enum):
    """事件类型枚举"""
    # 公开事件（所有用户可见）
    ANNOUNCEMENT = "announcement"           # 校园公告
    NOTICE = "notice"                      # 部门通知  
    SYSTEM_MESSAGE = "system_message"      # 系统消息
    EMERGENCY = "emergency"                # 紧急通知
    
    # 私人事件（仅相关用户可见）
    GRADE_UPDATE = "grade_update"          # 成绩更新
    COURSE_CHANGE = "course_change"        # 课程变更
    EXAM_REMINDER = "exam_reminder"        # 考试提醒
    LIBRARY_REMINDER = "library_reminder"  # 图书到期提醒
    TRANSACTION = "transaction"            # 消费流水
    ACTIVITY_RESULT = "activity_result"    # 活动结果
    SCHOLARSHIP = "scholarship"            # 奖学金通知

class EventPriority(str, Enum):
    """事件优先级"""
    LOW = "low"
    NORMAL = "normal" 
    HIGH = "high"
    URGENT = "urgent"

class Event:
    """事件数据模型"""
    
    def __init__(
        self,
        event_type: EventType,
        data: Dict[str, Any],
        target_users: Optional[List[str]] = None,
        priority: EventPriority = EventPriority.NORMAL,
        ttl: int = 86400  # 缓存时间（秒）
    ):
        self.event_id = f"evt_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        self.event_type = event_type
        self.data = data
        self.target_users = target_users or []
        self.priority = priority
        self.ttl = ttl
        self.timestamp = datetime.now().isoformat()
        self.is_public = event_type in [
            EventType.ANNOUNCEMENT, 
            EventType.NOTICE, 
            EventType.SYSTEM_MESSAGE, 
            EventType.EMERGENCY
        ]
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "timestamp": self.timestamp,
            "target_users": self.target_users,
            "is_public": self.is_public,
            "priority": self.priority,
            "data": self.data,
            "cache_policy": {
                "ttl": self.ttl,
                "persist": True
            }
        }

class EventQueue:
    """事件队列管理器"""
    
    def __init__(self):
        self.queues: Dict[str, deque] = defaultdict(deque)  # 用户ID -> 事件队列
        self.global_queue: deque = deque()  # 全局事件队列（公开事件）
        self.subscribers: Dict[str, Set[asyncio.Queue]] = defaultdict(set)  # 用户ID -> WebSocket连接
        self.event_history: Dict[str, List[Event]] = defaultdict(list)  # 事件历史
        self.max_queue_size = 1000
        self.max_history_size = 100
    
    async def publish_event(self, event: Event):
        """发布事件到队列"""
        logger.info(f"发布事件: {event.event_type} -> {event.target_users or 'all'}")
        
        if event.is_public:
            # 公开事件：添加到全局队列
            self.global_queue.append(event)
            if len(self.global_queue) > self.max_queue_size:
                self.global_queue.popleft()
            
            # 推送给所有在线用户
            await self._broadcast_to_all(event)
        else:
            # 私人事件：添加到特定用户队列
            for user_id in event.target_users:
                self.queues[user_id].append(event)
                if len(self.queues[user_id]) > self.max_queue_size:
                    self.queues[user_id].popleft()
                
                # 添加到历史记录
                self.event_history[user_id].append(event)
                if len(self.event_history[user_id]) > self.max_history_size:
                    self.event_history[user_id].pop(0)
                
                # 推送给在线用户
                await self._push_to_user(user_id, event)
    
    async def _broadcast_to_all(self, event: Event):
        """广播公开事件给所有在线用户"""
        for user_id, connections in self.subscribers.items():
            for connection in connections.copy():
                try:
                    await connection.put(event.to_dict())
                except Exception as e:
                    logger.error(f"推送失败 {user_id}: {e}")
                    connections.discard(connection)
    
    async def _push_to_user(self, user_id: str, event: Event):
        """推送事件给特定用户"""
        if user_id in self.subscribers:
            for connection in self.subscribers[user_id].copy():
                try:
                    await connection.put(event.to_dict())
                except Exception as e:
                    logger.error(f"推送失败 {user_id}: {e}")
                    self.subscribers[user_id].discard(connection)
    
    async def subscribe(self, user_id: str) -> asyncio.Queue:
        """用户订阅事件流"""
        connection = asyncio.Queue(maxsize=100)
        self.subscribers[user_id].add(connection)
        logger.info(f"用户 {user_id} 订阅事件流")
        
        # 立即推送未读的事件
        await self._push_unread_events(user_id, connection)
        
        return connection
    
    async def unsubscribe(self, user_id: str, connection: asyncio.Queue):
        """用户取消订阅"""
        if user_id in self.subscribers:
            self.subscribers[user_id].discard(connection)
            if not self.subscribers[user_id]:
                del self.subscribers[user_id]
        logger.info(f"用户 {user_id} 取消订阅")
    
    async def _push_unread_events(self, user_id: str, connection: asyncio.Queue):
        """推送未读事件"""
        # 推送公开事件（最近10条）
        recent_public = list(self.global_queue)[-10:]
        for event in recent_public:
            try:
                await connection.put(event.to_dict())
            except:
                break
        
        # 推送私人事件（最近20条）
        recent_private = list(self.queues[user_id])[-20:]
        for event in recent_private:
            try:
                await connection.put(event.to_dict())
            except:
                break
    
    def get_events_since(self, user_id: str, since_timestamp: str) -> List[Dict[str, Any]]:
        """获取指定时间之后的事件（增量同步）"""
        since_time = datetime.fromisoformat(since_timestamp.replace('Z', '+00:00'))
        events = []
        
        # 获取公开事件
        for event in self.global_queue:
            event_time = datetime.fromisoformat(event.timestamp)
            if event_time > since_time:
                events.append(event.to_dict())
        
        # 获取私人事件
        for event in self.queues[user_id]:
            event_time = datetime.fromisoformat(event.timestamp)
            if event_time > since_time:
                events.append(event.to_dict())
        
        # 按时间排序
        events.sort(key=lambda x: x['timestamp'])
        return events

class DatabaseChangeListener:
    """数据库变化监听器"""
    
    def __init__(self, event_queue: EventQueue):
        self.event_queue = event_queue
        self.last_check = {}  # 记录各表的最后检查时间
    
    async def start_monitoring(self):
        """开始监控数据库变化"""
        logger.info("开始监控数据库变化...")
        
        while True:
            try:
                await self._check_announcements()
                await self._check_grades()
                await self._check_transactions()
                await self._check_library_reminders()
                
                # 每30秒检查一次
                await asyncio.sleep(30)
            except Exception as e:
                logger.error(f"数据库监控错误: {e}")
                await asyncio.sleep(60)
    
    async def _check_announcements(self):
        """检查公告更新"""
        # TODO: 实际实现中需要连接数据库检查
        # 这里是模拟逻辑
        pass
    
    async def _check_grades(self):
        """检查成绩更新"""
        # TODO: 实际实现中需要连接数据库检查
        pass
    
    async def _check_transactions(self):
        """检查消费记录更新"""
        # TODO: 实际实现中需要连接数据库检查
        pass
    
    async def _check_library_reminders(self):
        """检查图书到期提醒"""
        # TODO: 实际实现中需要连接数据库检查
        pass

# 全局事件队列实例
event_queue = EventQueue()

# 数据库监听器实例
db_listener = DatabaseChangeListener(event_queue)

async def start_event_system():
    """启动事件系统"""
    logger.info("启动事件驱动推送系统...")
    
    # 启动数据库监听器
    asyncio.create_task(db_listener.start_monitoring())
    
    logger.info("事件系统启动完成")

def create_announcement_event(title: str, content: str, department: str) -> Event:
    """创建公告事件"""
    return Event(
        event_type=EventType.ANNOUNCEMENT,
        data={
            "title": title,
            "content": content,
            "department": department,
            "category": "system",
            "urgent": False
        },
        priority=EventPriority.NORMAL
    )

def create_grade_event(student_id: str, course_name: str, score: float, grade_level: str) -> Event:
    """创建成绩更新事件"""
    return Event(
        event_type=EventType.GRADE_UPDATE,
        data={
            "course_name": course_name,
            "score": score,
            "grade_level": grade_level,
            "semester": "2024-2025-1"
        },
        target_users=[student_id],
        priority=EventPriority.HIGH
    )

def create_transaction_event(user_id: str, amount: float, location: str, balance: float) -> Event:
    """创建消费流水事件"""
    return Event(
        event_type=EventType.TRANSACTION,
        data={
            "amount": amount,
            "location": location,
            "balance": balance,
            "time": datetime.now().strftime("%H:%M:%S")
        },
        target_users=[user_id],
        priority=EventPriority.LOW
    ) 