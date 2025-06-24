#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import json

def get_diverse_test_accounts():
    """获取不同专业、不同学院的学生测试账号"""
    
    # 连接数据库
    conn = sqlite3.connect('sztu_campus.db')
    cursor = conn.cursor()

    # 首先查看所有专业
    majors_query = '''
    SELECT DISTINCT m.major_name, c.college_name, COUNT(p.student_id) as student_count
    FROM majors m 
    LEFT JOIN colleges c ON m.college_id = c.college_id
    LEFT JOIN persons p ON p.major_id = m.major_id AND p.person_type = 'student'
    WHERE p.student_id IS NOT NULL AND p.password_plain IS NOT NULL
    GROUP BY m.major_name, c.college_name
    HAVING student_count > 0
    ORDER BY c.college_name, m.major_name
    '''
    
    cursor.execute(majors_query)
    majors_data = cursor.fetchall()
    
    print('=== 数据库中的专业分布 ===')
    for major_name, college_name, count in majors_data[:15]:  # 显示前15个专业
        print(f'{college_name} - {major_name}: {count}名学生')
    print()

    # 查询不同学院、不同专业的学生
    query = '''
    SELECT DISTINCT
        p.student_id,
        p.name,
        p.password_plain,
        p.wechat_openid,
        p.phone,
        p.email,
        COALESCE(m.major_name, '未知专业') as major_name,
        COALESCE(c.college_name, '未知学院') as college_name,
        COALESCE(cl.class_name, '未知班级') as class_name,
        COUNT(DISTINCT e.course_instance_id) as course_count
    FROM persons p
    LEFT JOIN majors m ON p.major_id = m.major_id
    LEFT JOIN colleges c ON p.college_id = c.college_id
    LEFT JOIN classes cl ON p.class_id = cl.class_id
    LEFT JOIN enrollments e ON p.student_id = e.student_id
    WHERE p.person_type = 'student' 
        AND p.student_id IS NOT NULL
        AND p.password_plain IS NOT NULL
    GROUP BY p.student_id, p.major_id, p.college_id
    ORDER BY c.college_name, m.major_name, course_count DESC
    '''

    cursor.execute(query)
    results = cursor.fetchall()

    print('=== SZTU-iCampus 多样化测试账号 ===')
    print('从不同学院、不同专业中挑选的10个学生账号\n')

    selected_combinations = set()  # 用于记录学院-专业组合
    selected_students = []

    for row in results:
        student_id, name, password, wechat_openid, phone, email, major_name, college_name, class_name, course_count = row
        
        # 创建学院-专业组合标识
        combination = f"{college_name}-{major_name}"
        
        # 确保选择不同学院-专业组合的学生
        if combination not in selected_combinations or len(selected_students) < 10:
            if combination not in selected_combinations:
                selected_combinations.add(combination)
            
            selected_students.append({
                'student_id': student_id,
                'name': name,
                'password': password,
                'wechat_openid': wechat_openid,
                'phone': phone,
                'email': email,
                'major_name': major_name,
                'college_name': college_name,
                'class_name': class_name,
                'course_count': course_count,
                'combination': combination
            })
            
            if len(selected_students) >= 10:
                break

    # 显示选中的学生信息
    for i, student in enumerate(selected_students, 1):
        print(f'{i}. 【{student["college_name"]} - {student["major_name"]}】')
        print(f'   账号: {student["student_id"]}')
        print(f'   密码: {student["password"]}')
        print(f'   姓名: {student["name"]}')
        print(f'   班级: {student["class_name"]}')
        print(f'   选课数量: {student["course_count"]}门')
        print(f'   微信号: {"✅ 已绑定" if student["wechat_openid"] else "❌ 未绑定"}')
        if student["wechat_openid"]:
            print(f'   微信OpenID: {student["wechat_openid"][:15]}...')
        print(f'   手机: {student["phone"]}')
        print(f'   邮箱: {student["email"]}')
        print()

    # 生成特殊用户账号（管理员、教师等）
    print('=== 特殊角色测试账号 ===\n')
    
    # 查询教师账号
    teacher_query = '''
    SELECT employee_id, name, password_plain, person_type, wechat_openid, phone, email
    FROM persons
    WHERE person_type IN ('teacher', 'admin', 'assistant_teacher')
        AND employee_id IS NOT NULL
        AND password_plain IS NOT NULL
    ORDER BY person_type, employee_id
    LIMIT 5
    '''
    
    cursor.execute(teacher_query)
    teachers = cursor.fetchall()
    
    for i, teacher in enumerate(teachers, 1):
        employee_id, name, password, person_type, wechat_openid, phone, email = teacher
        role_name = {
            'teacher': '教师',
            'admin': '管理员', 
            'assistant_teacher': '助教'
        }.get(person_type, person_type)
        
        print(f'{i}. 【{role_name}】')
        print(f'   账号: {employee_id}')
        print(f'   密码: {password}')
        print(f'   姓名: {name}')
        print(f'   角色: {person_type}')
        print(f'   微信号: {"✅ 已绑定" if wechat_openid else "❌ 未绑定"}')
        print(f'   手机: {phone}')
        print(f'   邮箱: {email}')
        print()

    conn.close()
    
    print('=== 登录测试说明 ===')
    print('1. API登录地址: http://127.0.0.1:8000/api/v1/auth/login')
    print('2. 请求方法: POST')
    print('3. 请求体格式: {"login_id": "账号", "password": "密码"}')
    print('4. 成功后会返回JWT token，用于后续API调用')
    print('5. 前端登录页面会自动处理这些流程')
    print('\n=== 功能测试建议 ===')
    print('• 不同专业学生：测试个性化课表、成绩显示')
    print('• 有微信号学生：测试微信相关功能')
    print('• 教师账号：测试教师专用功能')
    print('• 管理员账号：测试系统管理功能')

if __name__ == '__main__':
    get_diverse_test_accounts() 