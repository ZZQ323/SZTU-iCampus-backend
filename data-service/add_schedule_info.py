#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import json
import random

def add_schedule_info():
    """为课程实例添加课表时间信息"""
    
    conn = sqlite3.connect('sztu_campus.db')
    cursor = conn.cursor()
    
    # 查询需要添加课表信息的课程实例
    students = ['202100043218', '202100008036']
    
    for student_id in students:
        print(f"\n=== 为学生 {student_id} 的课程添加课表信息 ===")
        
        # 查询该学生的所有课程实例
        cursor.execute('''
            SELECT DISTINCT ci.instance_id, c.course_name, ci.semester
            FROM course_instances ci
            JOIN enrollments e ON ci.instance_id = e.course_instance_id
            JOIN courses c ON ci.course_id = c.course_id
            WHERE e.student_id = ? AND e.is_deleted = 0
            ORDER BY ci.semester, c.course_name
        ''', (student_id,))
        course_instances = cursor.fetchall()
        
        print(f"找到 {len(course_instances)} 个课程实例")
        
        # 预定义时间段
        time_slots = [
            {"start_time": "08:30", "end_time": "10:10"},  # 第1-2节
            {"start_time": "10:30", "end_time": "12:10"},  # 第3-4节
            {"start_time": "14:30", "end_time": "16:10"},  # 第5-6节
            {"start_time": "16:30", "end_time": "18:10"},  # 第7-8节
            {"start_time": "19:30", "end_time": "21:10"},  # 第9-10节
        ]
        
        # 教学楼列表
        buildings = ["C1", "C2", "C3", "D1", "D2"]
        
        used_time_day_combos = set()  # 防止时间冲突
        
        for instance_id, course_name, semester in course_instances:
            # 生成不冲突的时间
            attempts = 0
            while attempts < 50:  # 最多尝试50次
                weekday = random.randint(1, 5)  # 周一到周五
                time_slot = random.choice(time_slots)
                combo = (weekday, time_slot["start_time"])
                
                if combo not in used_time_day_combos:
                    used_time_day_combos.add(combo)
                    break
                attempts += 1
            
            # 生成课表信息
            building = random.choice(buildings)
            room_num = f"{random.randint(1, 5)}{random.randint(1, 3):02d}"
            location = f"{building}-{room_num}"
            
            schedule_info = [{
                "day_of_week": weekday,
                "start_time": time_slot["start_time"], 
                "end_time": time_slot["end_time"],
                "location": location,
                "building_name": f"{'计算机学院' if building.startswith('C') else '教学楼'}{building[1]}号楼",
                "weeks": "1-16周",
                "class_type": "lecture"
            }]
            
            # 更新课程实例的schedule_info字段
            try:
                cursor.execute('''
                    UPDATE course_instances 
                    SET schedule_info = ?
                    WHERE instance_id = ?
                ''', (json.dumps(schedule_info), instance_id))
                
                weekday_names = ["", "周一", "周二", "周三", "周四", "周五"]
                print(f"✅ {course_name[:20]}... - {weekday_names[weekday]} {time_slot['start_time']}-{time_slot['end_time']} {location}")
                
            except Exception as e:
                print(f"❌ 更新失败 {course_name}: {e}")
    
    # 提交更改
    conn.commit()
    print(f"\n=== 课表信息添加完成 ===")
    
    # 验证结果
    print("\n=== 验证结果 ===")
    for student_id in students:
        cursor.execute('''
            SELECT COUNT(*) 
            FROM course_instances ci
            JOIN enrollments e ON ci.instance_id = e.course_instance_id
            WHERE e.student_id = ? AND e.is_deleted = 0 
            AND ci.schedule_info != '[]' AND ci.schedule_info IS NOT NULL
        ''', (student_id,))
        count = cursor.fetchone()[0]
        print(f"学生 {student_id}: {count} 门课程已有课表信息")
    
    conn.close()

if __name__ == "__main__":
    add_schedule_info() 