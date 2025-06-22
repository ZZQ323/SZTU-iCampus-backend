#!/usr/bin/env python3
"""
补全缺失的Mock数据生成
"""

import random
import json
from datetime import datetime, date, timedelta
from faker import Faker
from loguru import logger
import sqlite3
import os

def complete_missing_data():
    """补全缺失的数据"""
    logger.info("开始补全缺失的数据...")
    
    db_path = "sztu_campus.db"
    if not os.path.exists(db_path):
        logger.error("数据库文件不存在")
        return
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 1. 补全部门数据
        complete_departments(cursor)
        
        # 2. 补全教室占用数据
        complete_room_occupations(cursor)
        
        # 3. 补全其他系统数据
        complete_system_data(cursor)
        
        conn.commit()
        logger.info("✅ 缺失数据补全完成！")
        
    except Exception as e:
        logger.error(f"❌ 补全数据时出错: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

def complete_departments(cursor):
    """补全部门数据"""
    logger.info("正在补全部门数据...")
    
    # 检查是否已有部门数据
    cursor.execute("SELECT COUNT(*) FROM departments")
    if cursor.fetchone()[0] > 0:
        logger.info("部门数据已存在，跳过")
        return
    
    # 获取学院数据
    cursor.execute("SELECT college_id, college_name, college_code FROM colleges")
    colleges = cursor.fetchall()
    
    departments_data = []
    for college_id, college_name, college_code in colleges:
        # 为每个学院创建2个部门
        dept_names = [f"{college_name}办公室", f"{college_name}教学管理办公室"]
        
        for i, dept_name in enumerate(dept_names, 1):
            dept_id = f"D{college_id[1:]}{str(i).zfill(2)}"
            departments_data.append((
                dept_id, dept_name, 'administrative', college_id, None, 1,
                f"0755-{random.randint(20000000, 29999999)}",
                f"dept{dept_id.lower()}@sztu.edu.cn",
                f"{college_code}1-{random.randint(101, 205)}",
                None, None, random.randint(5, 15),
                f"{college_name}管理部门", '["部门管理", "日常事务"]',
                0, 'active', 1, None
            ))
    
    # 插入部门数据
    cursor.executemany("""
        INSERT OR IGNORE INTO departments 
        (department_id, department_name, department_type, college_id, parent_department_id, level,
         phone, email, office_location, head_id, deputy_head_id, total_staff, 
         description, responsibilities, is_deleted, status, is_active, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, departments_data)
    
    logger.info(f"✅ 补全 {len(departments_data)} 个部门")

def complete_room_occupations(cursor):
    """补全教室占用数据"""
    logger.info("正在补全教室占用数据...")
    
    # 检查是否已有数据
    cursor.execute("SELECT COUNT(*) FROM room_occupations")
    if cursor.fetchone()[0] > 0:
        logger.info("教室占用数据已存在，跳过")
        return
    
    # 获取教室和教师数据
    cursor.execute("""
        SELECT location_id, capacity FROM locations 
        WHERE location_type IN ('classroom', 'lab', 'multimedia') 
        LIMIT 50
    """)
    locations = cursor.fetchall()
    
    cursor.execute("""
        SELECT employee_id FROM persons 
        WHERE person_type IN ('teacher', 'assistant_teacher') 
        LIMIT 30
    """)
    teachers = cursor.fetchall()
    
    if not locations or not teachers:
        logger.warning("没有足够的地点或教师数据")
        return
    
    occupations_data = []
    faker = Faker()
    
    for location_id, capacity in locations:
        for _ in range(random.randint(3, 8)):  # 每个教室3-8个占用记录
            occupation_id = f"RO{datetime.now().year}{str(len(occupations_data) + 1).zfill(6)}"
            teacher_id = random.choice(teachers)[0]
            occupation_type = random.choice(['class', 'exam', 'meeting', 'event'])
            
            start_date = faker.date_between(start_date='-30d', end_date='+30d')
            start_time = random.choice(['08:30', '10:30', '14:00', '16:00'])
            end_times = {'08:30': '10:10', '10:30': '12:10', '14:00': '15:40', '16:00': '17:40'}
            
            occupations_data.append((
                occupation_id, location_id, occupation_type, start_date,
                start_time, end_times[start_time], teacher_id,
                get_occupation_reason(occupation_type),
                random.choice(['confirmed', 'pending']),
                random.randint(20, min(capacity or 50, 80)),
                '["projector", "microphone"]', f"{occupation_type}使用"
            ))
    
    # 插入教室占用数据
    cursor.executemany("""
        INSERT OR IGNORE INTO room_occupations 
        (occupation_id, location_id, occupation_type, date, start_time, end_time,
         applicant_id, application_reason, status, attendance_count, equipment_used, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, occupations_data)
    
    logger.info(f"✅ 补全 {len(occupations_data)} 条教室占用记录")

def complete_system_data(cursor):
    """补全系统相关数据"""
    logger.info("正在补全系统数据...")
    
    # 1. 平台配置数据
    complete_platform_configs(cursor)
    
    # 2. 工作流实例数据
    complete_workflow_instances(cursor)
    
    # 3. 设备注册数据
    complete_device_registrations(cursor)
    
    # 4. 审计日志数据
    complete_audit_logs(cursor)

def complete_platform_configs(cursor):
    """补全平台配置数据"""
    cursor.execute("SELECT COUNT(*) FROM platform_configs")
    if cursor.fetchone()[0] > 0:
        return
    
    configs = [
        ('PC2024001', '学生服务平台', 'STUDENT_PORTAL', '{"max_course_selection": 8}', 1, 'v1.0'),
        ('PC2024002', '教师工作平台', 'TEACHER_PORTAL', '{"max_classes_per_term": 6}', 1, 'v1.0'),
        ('PC2024003', '管理员系统', 'ADMIN_PORTAL', '{"user_management_enabled": true}', 1, 'v1.0'),
        ('PC2024004', '科研管理平台', 'RESEARCH_PLATFORM', '{"project_management": true}', 1, 'v1.0'),
    ]
    
    cursor.executemany("""
        INSERT OR IGNORE INTO platform_configs 
        (config_id, platform_name, platform_code, config_data, is_active, version)
        VALUES (?, ?, ?, ?, ?, ?)
    """, configs)
    
    logger.info(f"✅ 补全 {len(configs)} 条平台配置")

def complete_workflow_instances(cursor):
    """补全工作流实例数据"""
    cursor.execute("SELECT COUNT(*) FROM workflow_instances")
    if cursor.fetchone()[0] > 0:
        return
    
    # 获取一些学生用于生成工作流
    cursor.execute("SELECT person_id FROM persons WHERE person_type='student' LIMIT 20")
    students = cursor.fetchall()
    
    if not students:
        return
    
    workflows = []
    workflow_types = ['course_selection', 'grade_appeal', 'scholarship_application']
    
    for i, (person_id,) in enumerate(students[:10]):  # 生成10个工作流实例
        instance_id = f"WF{datetime.now().year}{str(i+1).zfill(6)}"
        workflow_type = random.choice(workflow_types)
        
        workflows.append((
            instance_id, workflow_type, get_workflow_name(workflow_type),
            person_id, random.randint(1, 3), random.randint(3, 5),
            random.choice(['pending', 'approved', 'in_progress']),
            random.choice(['low', 'medium', 'high']),
            datetime.now() - timedelta(days=random.randint(1, 30)),
            f'{{"type": "{workflow_type}", "person_id": "{person_id}"}}'
        ))
    
    cursor.executemany("""
        INSERT OR IGNORE INTO workflow_instances 
        (instance_id, workflow_type, workflow_name, initiator_id, current_step, 
         total_steps, status, priority, start_date, workflow_data)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, workflows)
    
    logger.info(f"✅ 补全 {len(workflows)} 条工作流实例")

def complete_device_registrations(cursor):
    """补全设备注册数据"""
    cursor.execute("SELECT COUNT(*) FROM device_registrations")
    if cursor.fetchone()[0] > 0:
        return
    
    cursor.execute("SELECT person_id FROM persons LIMIT 15")
    persons = cursor.fetchall()
    
    devices = []
    device_names = ['iPhone 15', 'MacBook Pro', 'iPad Air', 'Samsung Galaxy S24']
    
    for i, (person_id,) in enumerate(persons):
        registration_id = f"DR{datetime.now().year}{str(i+1).zfill(6)}"
        devices.append((
            registration_id, person_id, random.choice(device_names),
            random.choice(['mobile', 'laptop', 'tablet']),
            generate_mac_address(),
            datetime.now() - timedelta(days=random.randint(1, 100)),
            'active',
            datetime.now() - timedelta(days=random.randint(0, 7))
        ))
    
    cursor.executemany("""
        INSERT OR IGNORE INTO device_registrations 
        (registration_id, person_id, device_name, device_type, mac_address, 
         registration_date, status, last_online)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, devices)
    
    logger.info(f"✅ 补全 {len(devices)} 条设备注册")

def complete_audit_logs(cursor):
    """补全审计日志数据"""
    cursor.execute("SELECT COUNT(*) FROM audit_logs")
    if cursor.fetchone()[0] > 0:
        return
    
    cursor.execute("SELECT person_id FROM persons LIMIT 10")
    persons = cursor.fetchall()
    
    logs = []
    actions = ['login', 'logout', 'grade_query', 'course_selection']
    
    for i, (person_id,) in enumerate(persons):
        log_id = f"AL{datetime.now().year}{str(i+1).zfill(6)}"
        logs.append((
            log_id, person_id, random.choice(actions), 'EMS',
            f"10.{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}",
            'Mozilla/5.0',
            datetime.now() - timedelta(days=random.randint(0, 30)),
            'success',
            '{"action": "user_action"}'
        ))
    
    cursor.executemany("""
        INSERT OR IGNORE INTO audit_logs 
        (log_id, user_id, action, resource, ip_address, user_agent, 
         timestamp, status, details)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, logs)
    
    logger.info(f"✅ 补全 {len(logs)} 条审计日志")

# 辅助函数
def get_occupation_reason(occupation_type):
    reasons = {
        'class': '高等数学课程教学',
        'exam': '期末考试',
        'meeting': '学院会议',
        'event': '学术讲座'
    }
    return reasons.get(occupation_type, '常规使用')

def get_workflow_name(workflow_type):
    names = {
        'course_selection': '课程选择申请',
        'grade_appeal': '成绩申诉流程',
        'scholarship_application': '奖学金申请'
    }
    return names.get(workflow_type, '未知流程')

def generate_mac_address():
    return ':'.join([f"{random.randint(0, 255):02x}" for _ in range(6)])

if __name__ == "__main__":
    complete_missing_data() 