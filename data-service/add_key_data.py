import sqlite3
from datetime import datetime, timedelta
import random

def add_key_data():
    conn = sqlite3.connect('sztu_campus.db')
    cursor = conn.cursor()
    
    print("=== 补充关键数据 ===")
    
    # 1. 先检查当前数据状态
    cursor.execute("SELECT COUNT(*) FROM departments")
    dept_count = cursor.fetchone()[0]
    print(f"departments当前: {dept_count} 条")
    
    cursor.execute("SELECT COUNT(*) FROM announcements")
    ann_count = cursor.fetchone()[0]
    print(f"announcements当前: {ann_count} 条")
    
    cursor.execute("SELECT COUNT(*) FROM events")
    event_count = cursor.fetchone()[0]
    print(f"events当前: {event_count} 条")
    
    # 2. 补充departments数据
    if dept_count == 0:
        print("\n补充departments数据...")
        departments = [
            ("DEPT001", "教务处", "administrative", "C001", "负责教学管理工作"),
            ("DEPT002", "学生处", "administrative", "C001", "负责学生管理工作"),
            ("DEPT003", "科研处", "administrative", "C001", "负责科研管理工作"),
        ]
        
        for dept_id, dept_name, dept_type, college_id, description in departments:
            cursor.execute("""
                INSERT OR IGNORE INTO departments 
                (department_id, department_name, department_type, college_id, level, description,
                 created_at, updated_at, is_deleted, status, is_active)
                VALUES (?, ?, ?, ?, 1, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0, 'active', 1)
            """, (dept_id, dept_name, dept_type, college_id, description))
        
        print(f"添加了 {len(departments)} 个部门")
    
    # 3. 补充公告数据
    if ann_count < 10:
        print("\n补充announcements数据...")
        new_announcements = [
            ("ANN2025004", "关于开展课程选课的通知", "春季学期课程选课工作即将开始。", "教务处", "education"),
            ("ANN2025005", "寒假值班安排通知", "寒假期间值班安排通知。", "学生处", "service"),
            ("ANN2025006", "创新创业大赛通知", "举办创新创业大赛。", "科研处", "academic"),
            ("ANN2025007", "图书馆资源使用指南", "新增电子资源使用说明。", "图书馆", "service"),
            ("ANN2025008", "网络安全管理通知", "加强校园网络安全管理。", "信息中心", "security"),
        ]
        
        # 获取一个发布者ID
        cursor.execute("SELECT person_id, name FROM persons WHERE person_type = 'admin' LIMIT 1")
        publisher_info = cursor.fetchone()
        if publisher_info:
            publisher_id, publisher_name = publisher_info
            
            for i, (ann_id, title, content, department, category) in enumerate(new_announcements):
                publish_time = datetime.now() - timedelta(days=i)
                cursor.execute("""
                    INSERT OR IGNORE INTO announcements
                    (announcement_id, title, content, publisher_id, publisher_name, department, 
                     category, priority, status, publish_time, target_audience, view_count,
                     created_at, updated_at, is_deleted)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 'normal', 'published', ?, 'all', ?,
                            CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0)
                """, (ann_id, title, content, publisher_id, publisher_name, department, 
                      category, publish_time, random.randint(50, 300)))
            
            print(f"添加了 {len(new_announcements)} 条公告")
    
    # 4. 补充events数据
    if event_count == 0:
        print("\n补充events数据...")
        # 获取组织者信息
        cursor.execute("SELECT person_id, name FROM persons WHERE person_type = 'admin' LIMIT 1")
        organizer_info = cursor.fetchone()
        if organizer_info:
            organizer_id, organizer_name = organizer_info
            
            future_time = datetime.now() + timedelta(days=7)
            events = [
                ("EVT2025001", "春季招聘会", "大型春季招聘会", "academic"),
                ("EVT2025002", "AI技术讲座", "人工智能技术分享", "academic"),
                ("EVT2025003", "校园文艺晚会", "新学期文艺晚会", "culture"),
            ]
            
            for i, (event_id, title, description, event_type) in enumerate(events):
                start_time = future_time + timedelta(days=i*3)
                end_time = start_time + timedelta(hours=3)
                
                cursor.execute("""
                    INSERT OR IGNORE INTO events
                    (event_id, title, description, event_type, organizer_id, organizer_name, 
                     start_time, end_time, status, is_public, target_audience,
                     created_at, updated_at, is_deleted)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'planned', 1, 'all',
                            CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0)
                """, (event_id, title, description, event_type, organizer_id, organizer_name,
                      start_time, end_time))
            
            print(f"添加了 {len(events)} 个活动")
    
    # 提交事务
    conn.commit()
    conn.close()
    
    print("\n=== 关键数据补充完成 ===")

if __name__ == "__main__":
    add_key_data() 