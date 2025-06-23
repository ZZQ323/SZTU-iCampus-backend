#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3
import json
from datetime import datetime

def check_database_data():
    """检查数据库数据情况"""
    
    # 连接数据库
    conn = sqlite3.connect('sztu_campus.db')
    cursor = conn.cursor()

    print('=== 数据库表统计 ===')
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()
    print(f'总表数: {len(tables)}')

    print('\n=== 各表数据量统计 ===')
    table_counts = {}
    for table in tables:
        table_name = table[0]
        cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
        count = cursor.fetchone()[0]
        table_counts[table_name] = count
        print(f'{table_name}: {count:,} 条')

    print('\n=== 核心业务表详细检查 ===')

    # 检查announcements表
    print('\n--- announcements表 ---')
    cursor.execute('SELECT COUNT(*) FROM announcements')
    ann_count = cursor.fetchone()[0]
    print(f'公告总数: {ann_count}')

    if ann_count > 0:
        cursor.execute('SELECT title, department, category, publish_time FROM announcements ORDER BY publish_time DESC LIMIT 5')
        announcements = cursor.fetchall()
        for i, ann in enumerate(announcements, 1):
            print(f'{i}. 标题: {ann[0][:40]}...')
            print(f'   部门: {ann[1]}, 分类: {ann[2]}, 发布时间: {ann[3]}')

    # 检查events表
    print('\n--- events表 ---')
    cursor.execute('SELECT COUNT(*) FROM events')
    event_count = cursor.fetchone()[0]
    print(f'活动总数: {event_count}')

    # 检查event_registrations表
    print('\n--- event_registrations表 ---')
    cursor.execute('SELECT COUNT(*) FROM event_registrations')
    reg_count = cursor.fetchone()[0]
    print(f'活动报名总数: {reg_count}')

    # 检查user_reading_records表
    print('\n--- user_reading_records表 ---')
    cursor.execute('SELECT COUNT(*) FROM user_reading_records')
    reading_count = cursor.fetchone()[0]
    print(f'用户阅读记录总数: {reading_count}')

    print('\n=== 人员数据统计 ===')
    cursor.execute('SELECT person_type, COUNT(*) FROM persons GROUP BY person_type')
    person_stats = cursor.fetchall()
    total_persons = 0
    for person_type, count in person_stats:
        print(f'{person_type}: {count:,} 人')
        total_persons += count
    print(f'总人数: {total_persons:,} 人')

    print('\n=== 需要关注的空表 ===')
    empty_tables = []
    important_tables = ['persons','colleges','majors','departments','classes','locations','courses','assets','books','enrollments','course_instances','class_schedules','borrow_records','transactions','room_occupations','grades','grade_statistics','announcements','events','event_registrations','research_projects','research_applications','paper_library','campus_cards','network_permissions','system_access','platform_configs','user_reading_records','device_registrations','audit_logs','workflow_instances']

    for table in important_tables:
        if table in table_counts and table_counts[table] == 0:
            empty_tables.append(table)
            print(f'⚠️  {table}: 0 条记录')

    print('\n=== 数据完整性分析 ===')
    
    # 检查是否有足够的测试数据用于校园应用
    analysis = []
    
    if ann_count < 10:
        analysis.append(f"📢 公告数据不足: 当前{ann_count}条，建议至少10条")
    
    if event_count == 0:
        analysis.append("🎯 缺少校园活动数据，建议添加一些测试活动")
    
    if 'class_schedules' in table_counts and table_counts['class_schedules'] == 0:
        analysis.append("📅 缺少课程表数据，这是核心功能")
    
    if reading_count == 0:
        analysis.append("📖 缺少用户阅读记录，无法测试阅读统计功能")

    if analysis:
        print("需要补充的数据:")
        for item in analysis:
            print(f"  {item}")
    else:
        print("✅ 数据完整性良好")

    conn.close()
    return empty_tables, analysis

if __name__ == "__main__":
    empty_tables, analysis = check_database_data() 