#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从数据库查询各种身份的测试账号
"""

import sqlite3
import sys

def generate_test_accounts():
    """从数据库生成各种身份的测试账号表格"""
    
    # 连接数据库
    try:
        db = sqlite3.connect('sztu_campus.db')
        cursor = db.cursor()
        print("✅ 数据库连接成功")
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return

    print("\n# SZTU-iCampus 各身份测试账号")
    print("\n| 身份类型 | 登录ID | 密码 | 姓名 | 备注 |")
    print("|---------|--------|------|------|------|")

    # 查询各种身份的用户
    queries = [
        ("学生", "SELECT student_id, password_plain, name FROM persons WHERE person_type='student' LIMIT 3"),
        ("普通教师", "SELECT employee_id, password_plain, name FROM persons WHERE person_type='teacher' LIMIT 3"),
        ("助教", "SELECT employee_id, password_plain, name FROM persons WHERE person_type='assistant_teacher' LIMIT 3"),
        ("管理员", "SELECT employee_id, password_plain, name FROM persons WHERE person_type='admin' LIMIT 3"),
    ]

    # 执行查询并输出结果
    for role_name, query in queries:
        try:
            cursor.execute(query)
            results = cursor.fetchall()
            
            if results:
                for i, (login_id, password, name) in enumerate(results):
                    if i == 0:
                        print(f"| {role_name} | {login_id} | {password} | {name} | 主要测试账号 |")
                    else:
                        print(f"|  | {login_id} | {password} | {name} | 备用账号 |")
            else:
                print(f"| {role_name} | - | - | - | 暂无数据 |")
                
        except Exception as e:
            print(f"| {role_name} | - | - | - | 查询错误: {e} |")

    # 由于数据生成时可能没有以下特殊角色，我们随机选择一些教师作为示例
    print("\n## 特殊角色示例（基于现有教师数据）")
    print("\n| 身份类型 | 登录ID | 密码 | 姓名 | 备注 |")
    print("|---------|--------|------|------|------|")

    special_roles = [
        "辅导员", "班主任", "院长", "专业主任", "图书管理员", "部门主管"
    ]

    try:
        # 随机选择一些教师作为特殊角色的示例
        cursor.execute("SELECT employee_id, password_plain, name FROM persons WHERE person_type='teacher' ORDER BY RANDOM() LIMIT 12")
        teachers = cursor.fetchall()
        
        role_index = 0
        for i, (login_id, password, name) in enumerate(teachers):
            if i % 2 == 0 and role_index < len(special_roles):
                role_name = special_roles[role_index]
                print(f"| {role_name} | {login_id} | {password} | {name} | 示例账号（教师身份） |")
                role_index += 1
            elif role_index > 0:
                print(f"|  | {login_id} | {password} | {name} | 备用账号 |")
    except Exception as e:
        print(f"| 特殊角色 | - | - | - | 查询错误: {e} |")

    # 统计信息
    print("\n## 数据库统计信息")
    try:
        cursor.execute("SELECT person_type, COUNT(*) FROM persons GROUP BY person_type")
        stats = cursor.fetchall()
        
        print("\n| 身份类型 | 人数 |")
        print("|---------|------|")
        
        type_names = {
            'student': '学生',
            'teacher': '教师', 
            'assistant_teacher': '助教',
            'admin': '管理员'
        }
        
        for person_type, count in stats:
            chinese_name = type_names.get(person_type, person_type)
            print(f"| {chinese_name} | {count:,} |")
    except Exception as e:
        print(f"统计信息查询失败: {e}")

    # 关闭数据库连接
    db.close()
    print(f"\n✅ 测试账号表格生成完成!")

if __name__ == "__main__":
    generate_test_accounts() 