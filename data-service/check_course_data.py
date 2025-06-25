#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import json

def check_course_data():
    """检查学生的课程数据"""
    
    conn = sqlite3.connect('sztu_campus.db')
    cursor = conn.cursor()
    
    students = ['202100043218', '202100008036']
    names = ['李建国', '冯华']
    
    for student_id, name in zip(students, names):
        print(f"\n=== {name} ({student_id}) ===")
        
        # 检查选课记录
        cursor.execute('''
            SELECT COUNT(*) FROM enrollments 
            WHERE student_id = ? AND is_deleted = 0
        ''', (student_id,))
        enrollment_count = cursor.fetchone()[0]
        print(f"选课记录: {enrollment_count} 门")
        
        # 检查成绩记录
        cursor.execute('''
            SELECT COUNT(*) FROM grades 
            WHERE student_id = ? AND is_deleted = 0
        ''', (student_id,))
        grade_count = cursor.fetchone()[0]
        print(f"成绩记录: {grade_count} 门")
        
        # 查看具体的课程信息
        cursor.execute('''
            SELECT 
                c.course_name, c.course_code, c.credit_hours, c.course_type,
                g.total_score, g.grade_level, ci.semester
            FROM grades g
            JOIN course_instances ci ON g.course_instance_id = ci.instance_id
            JOIN courses c ON ci.course_id = c.course_id
            WHERE g.student_id = ? AND g.is_deleted = 0
            ORDER BY c.course_name
        ''', (student_id,))
        courses = cursor.fetchall()
        
        if courses:
            print("课程详情:")
            total_credits = 0
            total_points = 0
            for i, course in enumerate(courses, 1):
                course_name, course_code, credits, course_type, score, grade, semester = course
                total_credits += credits
                total_points += score if score else 0
                print(f"  {i}. {course_name} ({course_code})")
                print(f"     学分: {credits} | 类型: {course_type} | 成绩: {score} ({grade}) | 学期: {semester}")
            
            avg_score = total_points / len(courses) if courses else 0
            print(f"总学分: {total_credits} | 平均分: {avg_score:.1f}")
        else:
            print("❌ 没有找到课程记录")
    
    conn.close()

if __name__ == "__main__":
    check_course_data() 