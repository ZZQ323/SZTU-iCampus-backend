#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import json
import random
from datetime import datetime

def insert_course_data():
    """为指定学生插入2024-2025-1学期的课程数据"""
    
    print("=== 开始插入课程数据 ===")
    conn = sqlite3.connect('sztu_campus.db')
    cursor = conn.cursor()
    
    # 先检查数据库连接
    cursor.execute("SELECT COUNT(*) FROM persons WHERE person_type = 'student'")
    student_count = cursor.fetchone()[0]
    print(f"数据库中学生总数: {student_count}")
    
    # 查看一些样本学生ID
    cursor.execute("SELECT student_id, name FROM persons WHERE person_type = 'student' AND student_id LIKE '2021%' LIMIT 5")
    sample_students = cursor.fetchall()
    print("数据库中2021级学生样本:")
    for s in sample_students:
        print(f"  {s[0]} - {s[1]}")
    
    # 查询学生信息
    students = [
        {'student_id': '202100043218', 'name': '李建国'},
        {'student_id': '202100008036', 'name': '冯华'}
    ]
    
    print("=== 查询学生信息 ===")
    for student in students:
        cursor.execute('''
            SELECT person_id, student_id, name, college_id, major_id, class_id 
            FROM persons WHERE student_id = ?
        ''', (student['student_id'],))
        result = cursor.fetchone()
        if result:
            student.update({
                'person_id': result[0],
                'college_id': result[3],
                'major_id': result[4], 
                'class_id': result[5]
            })
            print(f"✅ {student['name']} ({student['student_id']}): {result}")
        else:
            print(f"❌ 未找到学生: {student['name']} ({student['student_id']})")
            return
    
    # 查询适合的课程实例 (2024-2025-1学期)
    print("\n=== 查询2024-2025-1学期的课程实例 ===")
    
    # 先查看所有学期
    cursor.execute("SELECT DISTINCT semester FROM course_instances ORDER BY semester")
    all_semesters = cursor.fetchall()
    print("数据库中所有学期:")
    for s in all_semesters:
        print(f"  {s[0]}")
    
    cursor.execute('''
        SELECT 
            ci.instance_id, ci.course_id, c.course_name, c.course_code, 
            c.credit_hours, c.course_type, ci.teacher_id
        FROM course_instances ci
        JOIN courses c ON ci.course_id = c.course_id
        WHERE ci.semester = '2024-2025-1' 
        ORDER BY c.course_type, c.course_name
        LIMIT 20
    ''')
    course_instances = cursor.fetchall()
    
    if not course_instances:
        print("❌ 没有找到2024-2025-1学期的课程实例")
        return
    
    print(f"找到 {len(course_instances)} 个课程实例")
    for i, ci in enumerate(course_instances[:10]):
        print(f"{i+1}. {ci[2]} ({ci[3]}) - {ci[5]} - {ci[1]}")
    
    # 为每个学生选择8门课程
    print("\n=== 为学生创建选课和成绩数据 ===")
    
    for student in students:
        print(f"\n--- 处理学生: {student['name']} ---")
        
        # 随机选择8门课程
        selected_courses = random.sample(course_instances, 8)
        
        for i, course in enumerate(selected_courses):
            instance_id, course_id, course_name, course_code, credit_hours, course_type, teacher_id = course
            
            # 生成选课记录ID
            enrollment_id = f"EN{datetime.now().strftime('%Y%m%d')}{student['student_id'][-4:]}{i+1:02d}"
            
            # 插入选课记录
            try:
                cursor.execute('''
                    INSERT INTO enrollments (
                        enrollment_id, student_id, course_instance_id, 
                        enrollment_type, enrollment_status, enrollment_date,
                        credit_hours, is_mandatory, attendance_requirement,
                        created_at, updated_at, is_deleted, status, is_active
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    enrollment_id, student['student_id'], instance_id,
                    'regular', 'enrolled', datetime.now(),
                    credit_hours, 1 if course_type == 'required' else 0, 80.0,
                    datetime.now(), datetime.now(), False, 'active', True
                ))
                
                # 生成成绩记录ID
                grade_id = f"GR{datetime.now().strftime('%Y%m%d')}{student['student_id'][-4:]}{i+1:02d}"
                
                # 生成随机成绩
                midterm_score = random.randint(75, 95)
                final_score = random.randint(75, 95)
                homework_score = random.randint(80, 95)
                total_score = round(midterm_score * 0.3 + final_score * 0.5 + homework_score * 0.2, 1)
                
                # 计算等级
                if total_score >= 90:
                    grade_level, grade_point = 'A', 4.0
                elif total_score >= 80:
                    grade_level, grade_point = 'B', 3.0
                elif total_score >= 70:
                    grade_level, grade_point = 'C', 2.0
                else:
                    grade_level, grade_point = 'D', 1.0
                
                # 插入成绩记录
                cursor.execute('''
                    INSERT INTO grades (
                        grade_id, student_id, course_instance_id,
                        midterm_score, final_score, homework_score, total_score,
                        grade_point, grade_level, 
                        score_weights, exam_type, grade_status, is_passed,
                        created_at, updated_at, is_deleted, status, is_active
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    grade_id, student['student_id'], instance_id,
                    midterm_score, final_score, homework_score, total_score,
                    grade_point, grade_level,
                    json.dumps({"midterm": 30, "final": 50, "homework": 20}),
                    'normal', 'confirmed', total_score >= 60,
                    datetime.now(), datetime.now(), False, 'active', True
                ))
                
                print(f"✅ {course_name} - 总分: {total_score} ({grade_level})")
                
            except Exception as e:
                print(f"❌ 插入失败 {course_name}: {e}")
    
    # 提交事务
    conn.commit()
    print(f"\n=== 数据插入完成 ===")
    
    # 验证插入结果
    print("\n=== 验证插入结果 ===")
    for student in students:
        cursor.execute('''
            SELECT COUNT(*) FROM enrollments 
            WHERE student_id = ? AND is_deleted = 0
        ''', (student['student_id'],))
        enrollment_count = cursor.fetchone()[0]
        
        cursor.execute('''
            SELECT COUNT(*) FROM grades 
            WHERE student_id = ? AND is_deleted = 0
        ''', (student['student_id'],))
        grade_count = cursor.fetchone()[0]
        
        print(f"{student['name']}: 选课 {enrollment_count} 门, 成绩 {grade_count} 门")
    
    conn.close()

if __name__ == "__main__":
    insert_course_data() 