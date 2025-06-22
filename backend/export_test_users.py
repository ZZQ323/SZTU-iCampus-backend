#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
导出测试用户名单
用于前端验证和推送测试
"""

import sqlite3
import json
from datetime import datetime

def export_test_users():
    """导出固定的测试用户列表"""
    db_path = "../data-service/sztu_campus.db"
    
    try:
        # 先检查数据库文件是否存在
        import os
        if not os.path.exists(db_path):
            print(f"❌ 数据库文件不存在: {db_path}")
            return None
            
        db = sqlite3.connect(db_path)
        cursor = db.cursor()
        
        # 先检查表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='persons'")
        if not cursor.fetchone():
            print("❌ persons表不存在")
            return None
        
        # 获取测试用户数据
        test_users = {
            "export_time": datetime.now().isoformat(),
            "total_users": 0,
            "students": [],
            "teachers": [],
            "admins": [],
            "test_scenarios": []
        }
        
        # 1. 获取学生测试用户 (前10个用于测试)
        cursor.execute("""
            SELECT student_id, name, college_id, major_id, person_type
            FROM persons 
            WHERE person_type='student' AND student_id IS NOT NULL
            ORDER BY student_id 
            LIMIT 10
        """)
        students = cursor.fetchall()
        
        for student in students:
            test_users["students"].append({
                "user_id": student[0],
                "name": student[1],
                "college_id": student[2],
                "major_id": student[3], 
                "person_type": student[4],
                "login_id": student[0],  # 学号作为登录ID
                "events_subscribed": ["grade_update", "transaction", "library_reminder", "course_change"],
                "public_events": True
            })
        
        # 2. 获取教师测试用户 (前5个用于测试)
        cursor.execute("""
            SELECT employee_id, name, college_id, person_type
            FROM persons 
            WHERE person_type='teacher' AND employee_id IS NOT NULL
            ORDER BY employee_id 
            LIMIT 5
        """)
        teachers = cursor.fetchall()
        
        for teacher in teachers:
            test_users["teachers"].append({
                "user_id": teacher[0],
                "name": teacher[1],
                "college_id": teacher[2],
                "person_type": teacher[3],
                "login_id": teacher[0],  # 工号作为登录ID
                "events_subscribed": ["course_change", "system_message"],
                "public_events": True
            })
        
        # 3. 获取管理员测试用户 (前3个用于测试)
        cursor.execute("""
            SELECT employee_id, name, college_id, person_type
            FROM persons 
            WHERE person_type='admin' AND employee_id IS NOT NULL
            ORDER BY employee_id 
            LIMIT 3
        """)
        admins = cursor.fetchall()
        
        for admin in admins:
            test_users["admins"].append({
                "user_id": admin[0],
                "name": admin[1],
                "college_id": admin[2],
                "person_type": admin[3],
                "login_id": admin[0],  # 工号作为登录ID
                "events_subscribed": ["*"],  # 管理员订阅所有事件
                "public_events": True
            })
        
        # 4. 定义测试场景和对应的推送用户
        test_users["test_scenarios"] = [
            {
                "scenario_name": "系统公告推送",
                "event_type": "announcement",
                "is_public": True,
                "target_users": "all",  # 所有用户都会收到
                "description": "教务处发布的公告，所有用户都能收到"
            },
            {
                "scenario_name": "成绩更新推送", 
                "event_type": "grade_update",
                "is_public": False,
                "target_users": [user["user_id"] for user in test_users["students"]],
                "description": "成绩更新只推送给对应的学生"
            },
            {
                "scenario_name": "消费流水推送",
                "event_type": "transaction", 
                "is_public": False,
                "target_users": [user["user_id"] for user in test_users["students"]],
                "description": "校园卡消费只推送给消费的学生"
            },
            {
                "scenario_name": "图书到期提醒",
                "event_type": "library_reminder",
                "is_public": False, 
                "target_users": [user["user_id"] for user in test_users["students"]],
                "description": "图书到期提醒只推送给借书的学生"
            },
            {
                "scenario_name": "课程变更通知",
                "event_type": "course_change",
                "is_public": False,
                "target_users": [user["user_id"] for user in test_users["students"]],
                "description": "课程变更推送给选课的所有学生"
            }
        ]
        
        # 统计总数
        test_users["total_users"] = len(test_users["students"]) + len(test_users["teachers"]) + len(test_users["admins"])
        
        cursor.close()
        db.close()
        
        return test_users
        
    except Exception as e:
        print(f"❌ 导出测试用户失败: {e}")
        return None

def save_to_files(test_users):
    """保存到多种格式的文件"""
    
    # 1. 保存为JSON文件（完整数据）
    with open("test_users_full.json", "w", encoding="utf-8") as f:
        json.dump(test_users, f, ensure_ascii=False, indent=2)
    print("✅ 完整数据已保存到: test_users_full.json")
    
    # 2. 保存为前端友好的格式
    frontend_data = {
        "api_base_url": "http://localhost:8000/api/v1",
        "stream_endpoints": {
            "events": "/stream/events",
            "sync": "/stream/sync", 
            "status": "/stream/status"
        },
        "test_users": {
            "students": [
                {
                    "login_id": user["login_id"],
                    "name": user["name"],
                    "password": "123456",  # 固定测试密码
                    "events": user["events_subscribed"]
                } for user in test_users["students"][:5]  # 前5个学生
            ],
            "teachers": [
                {
                    "login_id": user["login_id"], 
                    "name": user["name"],
                    "password": "123456",
                    "events": user["events_subscribed"]
                } for user in test_users["teachers"][:2]  # 前2个教师
            ],
            "admins": [
                {
                    "login_id": user["login_id"],
                    "name": user["name"], 
                    "password": "123456",
                    "events": user["events_subscribed"]
                } for user in test_users["admins"][:1]  # 1个管理员
            ]
        },
        "push_test_data": {
            "announcement": {
                "title": "关于期末考试安排的重要通知",
                "content": "各位同学，期末考试将于下周开始，请做好准备。",
                "department": "教务处"
            },
            "grade_update": {
                "course_name": "高等数学A",
                "score": 90,
                "grade_level": "A-",
                "semester": "2024-2025-1"
            },
            "transaction": {
                "amount": -15.50,
                "location": "第一食堂",
                "balance": 284.50
            },
            "library_reminder": {
                "book_title": "算法导论（第三版）",
                "due_date": "2024-12-25",
                "days_left": 4
            }
        }
    }
    
    with open("frontend_test_config.json", "w", encoding="utf-8") as f:
        json.dump(frontend_data, f, ensure_ascii=False, indent=2)
    print("✅ 前端配置已保存到: frontend_test_config.json")
    
    # 3. 生成简单的用户列表
    user_list = []
    for user in test_users["students"][:5]:
        user_list.append(f"学生: {user['login_id']} ({user['name']}) - 密码: 123456")
    for user in test_users["teachers"][:2]:
        user_list.append(f"教师: {user['login_id']} ({user['name']}) - 密码: 123456")
    for user in test_users["admins"][:1]:
        user_list.append(f"管理员: {user['login_id']} ({user['name']}) - 密码: 123456")
    
    with open("test_users_simple.txt", "w", encoding="utf-8") as f:
        f.write("SZTU-iCampus 测试用户列表\n")
        f.write("=" * 50 + "\n\n")
        for user in user_list:
            f.write(user + "\n")
        f.write(f"\n总计: {len(user_list)} 个测试用户\n")
        f.write(f"导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    print("✅ 简单列表已保存到: test_users_simple.txt")

def main():
    """主函数"""
    print("🎯 SZTU-iCampus 测试用户导出工具")
    print("=" * 50)
    
    # 导出测试用户
    test_users = export_test_users()
    if not test_users:
        print("❌ 导出失败")
        return
    
    print(f"✅ 成功导出 {test_users['total_users']} 个测试用户:")
    print(f"   - 学生: {len(test_users['students'])} 人")
    print(f"   - 教师: {len(test_users['teachers'])} 人") 
    print(f"   - 管理员: {len(test_users['admins'])} 人")
    print(f"   - 测试场景: {len(test_users['test_scenarios'])} 个")
    
    # 保存到文件
    save_to_files(test_users)
    
    print("\n" + "=" * 50)
    print("📋 推荐的前端验证用户:")
    print("   学生: 202100000001 (唐勇) - 可接收成绩、消费、图书提醒")
    print("   教师: 2025001001 (高军) - 可接收课程变更通知")
    print("   管理员: 2025000001 (何平) - 可接收所有类型事件")
    print("\n   所有用户密码: 123456")
    print("   推送测试: 运行 python test_event_push.py")

if __name__ == "__main__":
    main() 