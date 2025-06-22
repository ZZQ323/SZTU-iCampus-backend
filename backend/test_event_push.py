#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
事件推送测试脚本
模拟数据库写入 → 事件队列 → 推送通知的完整流程
"""

import asyncio
import sqlite3
import json
import time
from datetime import datetime, timedelta
from typing import List
import random

# 导入事件系统
import sys
sys.path.append('.')
from app.core.events import (
    event_queue, EventType, EventPriority,
    create_announcement_event, create_grade_event, create_transaction_event
)

class EventTestRunner:
    """事件推送测试运行器"""
    
    def __init__(self):
        self.db_path = "../data-service/sztu_campus.db"
        self.test_users = []
        self.load_test_users()
    
    def load_test_users(self):
        """加载测试用户"""
        try:
            db = sqlite3.connect(self.db_path)
            cursor = db.cursor()
            
            # 获取不同类型的测试用户
            cursor.execute("SELECT student_id, name FROM persons WHERE person_type='student' LIMIT 5")
            students = cursor.fetchall()
            
            cursor.execute("SELECT employee_id, name FROM persons WHERE person_type='teacher' LIMIT 3")
            teachers = cursor.fetchall()
            
            cursor.execute("SELECT employee_id, name FROM persons WHERE person_type='admin' LIMIT 2")
            admins = cursor.fetchall()
            
            self.test_users = {
                'students': students,
                'teachers': teachers,
                'admins': admins
            }
            
            db.close()
            print(f"✅ 加载测试用户: {len(students)}学生, {len(teachers)}教师, {len(admins)}管理员")
            
        except Exception as e:
            print(f"❌ 加载测试用户失败: {e}")
    
    async def test_scenario_1_announcement(self):
        """测试场景1: 系统公告推送"""
        print("\n🔔 测试场景1: 系统公告推送")
        
        # 1. 模拟数据库写入
        announcement_data = {
            "title": "关于期末考试安排的重要通知",
            "content": "各位同学，期末考试将于下周开始，请做好准备。考试时间安排请查看教务系统。",
            "department": "教务处",
            "publish_time": datetime.now().isoformat(),
            "category": "academic",
            "urgent": True
        }
        
        self._simulate_db_insert("announcements", announcement_data)
        
        # 2. 触发事件推送
        event = create_announcement_event(
            title=announcement_data["title"],
            content=announcement_data["content"],
            department=announcement_data["department"]
        )
        
        await event_queue.publish_event(event)
        print(f"📤 公告事件已推送: {event.event_id}")
        
        return event
    
    async def test_scenario_2_grade_update(self):
        """测试场景2: 成绩更新推送"""
        print("\n📊 测试场景2: 成绩更新推送")
        
        # 随机选择学生
        student_id, student_name = random.choice(self.test_users['students'])
        
        # 1. 模拟成绩录入
        grade_data = {
            "student_id": student_id,
            "course_name": "高等数学A",
            "teacher": "张教授",
            "scores": {
                "attendance": 95,
                "homework": 88,
                "midterm": 92,
                "final": 89,
                "total": 90
            },
            "grade_level": "A-",
            "semester": "2024-2025-1",
            "update_time": datetime.now().isoformat()
        }
        
        self._simulate_db_insert("grades", grade_data)
        
        # 2. 触发成绩推送事件
        event = create_grade_event(
            student_id=student_id,
            course_name=grade_data["course_name"],
            score=grade_data["scores"]["total"],
            grade_level=grade_data["grade_level"]
        )
        
        await event_queue.publish_event(event)
        print(f"📤 成绩事件已推送给学生 {student_name} ({student_id})")
        
        return event
    
    async def test_scenario_3_transaction(self):
        """测试场景3: 消费流水推送"""
        print("\n💳 测试场景3: 消费流水推送")
        
        # 随机选择学生
        student_id, student_name = random.choice(self.test_users['students'])
        
        # 1. 模拟消费记录
        transaction_data = {
            "person_id": student_id,
            "card_number": student_id,
            "transaction_type": "consumption",
            "amount": -15.50,
            "balance_before": 300.00,
            "balance_after": 284.50,
            "merchant": "第一食堂",
            "location": "F1-1F",
            "transaction_time": datetime.now().isoformat(),
            "items": [
                {"item_name": "宫保鸡丁", "quantity": 1, "unit_price": 8.00},
                {"item_name": "米饭", "quantity": 1, "unit_price": 2.00},
                {"item_name": "西红柿鸡蛋汤", "quantity": 1, "unit_price": 2.50},
                {"item_name": "餐具费", "quantity": 1, "unit_price": 1.00}
            ]
        }
        
        self._simulate_db_insert("transactions", transaction_data)
        
        # 2. 触发消费推送事件
        event = create_transaction_event(
            user_id=student_id,
            amount=transaction_data["amount"],
            location=transaction_data["merchant"],
            balance=transaction_data["balance_after"]
        )
        
        await event_queue.publish_event(event)
        print(f"📤 消费事件已推送给学生 {student_name} ({student_id}): {transaction_data['amount']}元")
        
        return event
    
    async def test_scenario_4_library_reminder(self):
        """测试场景4: 图书到期提醒"""
        print("\n📚 测试场景4: 图书到期提醒")
        
        # 随机选择学生
        student_id, student_name = random.choice(self.test_users['students'])
        
        # 1. 模拟图书借阅到期检查
        library_data = {
            "student_id": student_id,
            "book_title": "算法导论（第三版）",
            "book_id": "B001",
            "borrow_date": "2024-11-20",
            "due_date": "2024-12-25", 
            "days_left": 4,
            "fine_amount": 0.0,
            "check_time": datetime.now().isoformat()
        }
        
        self._simulate_db_insert("library_reminders", library_data)
        
        # 2. 触发图书到期提醒事件
        from app.core.events import Event
        event = Event(
            event_type=EventType.LIBRARY_REMINDER,
            data={
                "book_title": library_data["book_title"],
                "due_date": library_data["due_date"],
                "days_left": library_data["days_left"],
                "fine_amount": library_data["fine_amount"],
                "action_required": "请及时归还或续借"
            },
            target_users=[student_id],
            priority=EventPriority.NORMAL
        )
        
        await event_queue.publish_event(event)
        print(f"📤 图书到期提醒已推送给学生 {student_name} ({student_id})")
        
        return event
    
    async def test_scenario_5_course_change(self):
        """测试场景5: 课程变更通知"""
        print("\n📅 测试场景5: 课程变更通知")
        
        # 选择所有学生（模拟课程变更影响多个学生）
        affected_students = [user[0] for user in self.test_users['students']]
        
        # 1. 模拟课程变更
        course_change_data = {
            "course_name": "数据结构与算法",
            "teacher": "李教授",
            "change_type": "time_change",
            "original_time": "周一 08:30-10:10",
            "new_time": "周一 10:30-12:10",
            "original_location": "C2-301",
            "new_location": "C2-305",
            "reason": "教室设备维护",
            "effective_date": "2024-12-25",
            "affected_students": affected_students,
            "update_time": datetime.now().isoformat()
        }
        
        self._simulate_db_insert("course_changes", course_change_data)
        
        # 2. 触发课程变更事件
        from app.core.events import Event
        event = Event(
            event_type=EventType.COURSE_CHANGE,
            data={
                "course_name": course_change_data["course_name"],
                "teacher": course_change_data["teacher"],
                "change_type": "时间地点变更",
                "old_schedule": f"{course_change_data['original_time']} @ {course_change_data['original_location']}",
                "new_schedule": f"{course_change_data['new_time']} @ {course_change_data['new_location']}",
                "reason": course_change_data["reason"],
                "effective_date": course_change_data["effective_date"]
            },
            target_users=affected_students,
            priority=EventPriority.HIGH
        )
        
        await event_queue.publish_event(event)
        print(f"📤 课程变更通知已推送给 {len(affected_students)} 名学生")
        
        return event
    
    def _simulate_db_insert(self, table_name: str, data: dict):
        """模拟数据库插入操作"""
        print(f"💾 模拟数据库插入: {table_name} <- {json.dumps(data, ensure_ascii=False, indent=2)}")
        # 实际实现中这里应该真正插入数据库
        # 为了测试简化，这里只是打印
    
    async def run_all_tests(self):
        """运行所有测试场景"""
        print("🚀 开始事件推送测试...")
        print("=" * 60)
        
        events = []
        
        # 依次运行各个测试场景
        events.append(await self.test_scenario_1_announcement())
        await asyncio.sleep(2)  # 间隔2秒
        
        events.append(await self.test_scenario_2_grade_update()) 
        await asyncio.sleep(2)
        
        events.append(await self.test_scenario_3_transaction())
        await asyncio.sleep(2)
        
        events.append(await self.test_scenario_4_library_reminder())
        await asyncio.sleep(2)
        
        events.append(await self.test_scenario_5_course_change())
        
        # 等待事件处理
        await asyncio.sleep(3)
        
        print("\n" + "=" * 60)
        print("📊 测试总结:")
        print(f"✅ 共推送 {len(events)} 个事件")
        print(f"🔗 在线用户数: {len(event_queue.subscribers)}")
        print(f"📮 全局事件队列: {len(event_queue.global_queue)} 个事件")
        
        # 显示事件详情
        for i, event in enumerate(events, 1):
            print(f"  {i}. {event.event_type} - {event.event_id}")
        
        return events
    
    async def test_continuous_push(self, duration: int = 60):
        """持续推送测试"""
        print(f"\n🔄 开始持续推送测试 (持续 {duration} 秒)...")
        
        start_time = time.time()
        event_count = 0
        
        while time.time() - start_time < duration:
            # 随机选择测试场景
            scenario = random.choice([
                self.test_scenario_2_grade_update,
                self.test_scenario_3_transaction,
                self.test_scenario_4_library_reminder
            ])
            
            await scenario()
            event_count += 1
            
            # 随机间隔 1-5 秒
            await asyncio.sleep(random.uniform(1, 5))
        
        print(f"✅ 持续推送测试完成: {event_count} 个事件")

async def main():
    """主函数"""
    print("🎯 SZTU-iCampus 事件推送测试脚本")
    print("=" * 60)
    
    # 初始化测试运行器
    runner = EventTestRunner()
    
    if not runner.test_users['students']:
        print("❌ 无法加载测试用户，请确保数据库连接正常")
        return
    
    # 选择测试模式
    print("\n请选择测试模式:")
    print("1. 运行完整测试场景")
    print("2. 持续推送测试")
    print("3. 单个场景测试")
    
    choice = input("请输入选择 (1-3): ").strip()
    
    if choice == "1":
        await runner.run_all_tests()
    elif choice == "2":
        duration = int(input("持续时间(秒，默认60): ") or 60)
        await runner.test_continuous_push(duration)
    elif choice == "3":
        print("\n可选场景:")
        print("1. 系统公告")
        print("2. 成绩更新") 
        print("3. 消费流水")
        print("4. 图书提醒")
        print("5. 课程变更")
        
        scenario_choice = input("请选择场景 (1-5): ").strip()
        scenarios = {
            "1": runner.test_scenario_1_announcement,
            "2": runner.test_scenario_2_grade_update,
            "3": runner.test_scenario_3_transaction,
            "4": runner.test_scenario_4_library_reminder,
            "5": runner.test_scenario_5_course_change
        }
        
        if scenario_choice in scenarios:
            await scenarios[scenario_choice]()
        else:
            print("❌ 无效选择")
    else:
        print("❌ 无效选择")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试运行错误: {e}")
        import traceback
        traceback.print_exc() 