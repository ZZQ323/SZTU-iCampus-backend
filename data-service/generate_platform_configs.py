#!/usr/bin/env python3
"""
生成平台配置数据 - 符合API文档要求
根据实际表结构为每个用户生成完整的平台配置
"""

import random
import json
import sqlite3
import os
from datetime import datetime, timedelta
from loguru import logger

def generate_platform_configs():
    """生成完整的平台配置数据"""
    logger.info("开始生成平台配置数据...")
    
    db_path = "sztu_campus.db"
    if not os.path.exists(db_path):
        logger.error("数据库文件不存在")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 检查是否已有数据
        cursor.execute("SELECT COUNT(*) FROM platform_configs")
        existing_count = cursor.fetchone()[0]
        
        if existing_count > 0:
            logger.info(f"已有 {existing_count} 条平台配置数据，清空重新生成...")
            cursor.execute("DELETE FROM platform_configs")
        
        # 获取所有人员数据
        cursor.execute("""
            SELECT person_id, person_type, name, student_id, employee_id 
            FROM persons 
            ORDER BY person_type, person_id
        """)
        persons = cursor.fetchall()
        
        if not persons:
            logger.error("没有人员数据，无法生成平台配置")
            return
        
        logger.info(f"获取到 {len(persons)} 个人员，开始生成平台配置...")
        
        platform_configs_data = []
        config_counter = 0
        
        # 定义平台类型和配置
        platforms = {
            'student_portal': {
                'name': '学生服务平台',
                'url': 'https://student.sztu.edu.cn',
                'applicable_types': ['student'],
                'auth_method': 'sso'
            },
            'teacher_portal': {
                'name': '教师工作平台', 
                'url': 'https://teacher.sztu.edu.cn',
                'applicable_types': ['teacher', 'assistant_teacher'],
                'auth_method': 'sso'
            },
            'admin_portal': {
                'name': '管理员系统',
                'url': 'https://admin.sztu.edu.cn',
                'applicable_types': ['admin'],
                'auth_method': 'password'
            },
            'research_platform': {
                'name': '科研管理平台',
                'url': 'https://research.sztu.edu.cn', 
                'applicable_types': ['teacher', 'assistant_teacher'],
                'auth_method': 'sso'
            },
            'library_system': {
                'name': '图书馆系统',
                'url': 'https://lib.sztu.edu.cn',
                'applicable_types': ['student', 'teacher', 'assistant_teacher', 'admin'],
                'auth_method': 'sso'
            },
            'financial_system': {
                'name': '财务管理系统',
                'url': 'https://finance.sztu.edu.cn',
                'applicable_types': ['student', 'teacher', 'assistant_teacher'],
                'auth_method': 'password'
            }
        }
        
        # 为每个人员生成相应的平台配置
        for person_id, person_type, name, student_id, employee_id in persons:
            for platform_type, platform_info in platforms.items():
                # 检查该人员类型是否适用于该平台
                if person_type not in platform_info['applicable_types']:
                    continue
                
                config_counter += 1
                config_id = f"PC{datetime.now().year}{str(config_counter).zfill(6)}"
                
                # 生成权限映射
                permission_mapping = generate_permission_mapping(person_type, platform_type)
                
                # 生成角色映射
                role_mapping = generate_role_mapping(person_type, platform_type)
                
                # 生成OAuth配置
                oauth_config = generate_oauth_config(platform_type)
                
                # 生成密码策略
                password_policy = generate_password_policy(person_type, platform_type)
                
                config = (
                    config_id,                              # config_id
                    person_id,                              # person_id
                    platform_info['name'],                  # platform_name
                    platform_type,                          # platform_type
                    platform_info['url'],                   # platform_url
                    platform_info['auth_method'],           # auth_method
                    1 if platform_info['auth_method'] == 'sso' else 0,  # sso_enabled
                    json.dumps(oauth_config, ensure_ascii=False),       # oauth_config
                    json.dumps(permission_mapping, ensure_ascii=False), # permission_mapping
                    json.dumps(role_mapping, ensure_ascii=False),       # role_mapping
                    random.randint(1800, 7200),             # session_timeout (30分钟-2小时)
                    random.randint(900, 3600),              # max_idle_time (15分钟-1小时)
                    random.randint(604800, 2592000),        # remember_me_duration (7-30天)
                    1 if person_type == 'admin' else 0,     # force_password_change
                    json.dumps(password_policy, ensure_ascii=False),    # password_policy
                    random.randint(3, 10),                  # login_retry_limit
                    'active',                               # config_status
                    datetime.now() - timedelta(days=random.randint(1, 30)),  # last_sync_time
                    0,                                      # is_deleted
                    'active',                               # status
                    1,                                      # is_active
                    f"{name}的{platform_info['name']}配置"  # notes
                )
                
                platform_configs_data.append(config)
                
                # 每1000条批量插入一次
                if len(platform_configs_data) >= 1000:
                    insert_batch(cursor, platform_configs_data)
                    logger.info(f"已插入 {len(platform_configs_data)} 条配置，总计: {config_counter}")
                    platform_configs_data.clear()
        
        # 插入剩余数据
        if platform_configs_data:
            insert_batch(cursor, platform_configs_data)
        
        conn.commit()
        logger.info(f"✅ 成功生成 {config_counter} 条平台配置数据")
        
        # 统计生成结果
        show_statistics(cursor)
        
    except Exception as e:
        logger.error(f"❌ 生成平台配置数据失败: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

def insert_batch(cursor, data):
    """批量插入数据"""
    cursor.executemany("""
        INSERT OR REPLACE INTO platform_configs 
        (config_id, person_id, platform_name, platform_type, platform_url, 
         auth_method, sso_enabled, oauth_config, permission_mapping, role_mapping,
         session_timeout, max_idle_time, remember_me_duration, force_password_change,
         password_policy, login_retry_limit, config_status, last_sync_time,
         is_deleted, status, is_active, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, data)

def generate_permission_mapping(person_type, platform_type):
    """根据人员类型和平台类型生成权限映射"""
    if person_type == 'student':
        if platform_type == 'student_portal':
            return {
                "read": ["own_schedule", "own_grades", "course_info", "announcements", "library_status"],
                "write": ["own_profile", "course_evaluation", "feedback"],
                "share": ["schedule", "contact_info"],
                "features": ["course_selection", "grade_query", "schedule_view", "library_service", "card_service"]
            }
        elif platform_type == 'library_system':
            return {
                "read": ["book_catalog", "own_borrow_records", "library_announcements"],
                "write": ["book_reservation", "renewal_request"],
                "share": ["reading_list"],
                "features": ["book_search", "borrow_renew", "reading_history"]
            }
        elif platform_type == 'financial_system':
            return {
                "read": ["own_transactions", "balance", "fee_status"],
                "write": ["payment_request"],
                "share": [],
                "features": ["balance_query", "transaction_history", "online_payment"]
            }
    
    elif person_type == 'teacher':
        if platform_type == 'teacher_portal':
            return {
                "read": ["own_courses", "student_grades", "teaching_schedule", "department_announcements"],
                "write": ["grade_input", "course_content", "teaching_plans", "announcements"],
                "share": ["course_materials", "teaching_resources"],
                "features": ["teaching_management", "grade_management", "course_planning", "student_info"]
            }
        elif platform_type == 'research_platform':
            return {
                "read": ["own_projects", "funding_info", "research_announcements", "collaboration_opportunities"],
                "write": ["project_application", "research_reports", "paper_submission"],
                "share": ["research_findings", "academic_achievements"],
                "features": ["project_management", "funding_application", "paper_management", "collaboration"]
            }
    
    elif person_type == 'admin':
        if platform_type == 'admin_portal':
            return {
                "read": ["*"],
                "write": ["user_management", "system_config", "policy_management", "all_announcements"],
                "share": ["system_reports", "statistical_data", "policy_documents"],
                "features": ["user_administration", "system_monitoring", "data_analytics", "policy_management"]
            }
    
    # 默认配置
    return {
        "read": ["public_info"],
        "write": ["own_profile"],
        "share": ["contact_info"],
        "features": ["basic_access"]
    }

def generate_role_mapping(person_type, platform_type):
    """生成角色映射配置"""
    if person_type == 'student':
        return {
            "primary_role": "undergraduate_student",
            "secondary_roles": ["library_user", "financial_user"],
            "role_hierarchy": ["student", "user"],
            "default_permissions": "student_basic"
        }
    elif person_type == 'teacher':
        return {
            "primary_role": "faculty_member",
            "secondary_roles": ["researcher", "course_instructor", "library_user"],
            "role_hierarchy": ["teacher", "staff", "user"],
            "default_permissions": "teacher_standard"
        }
    elif person_type == 'assistant_teacher':
        return {
            "primary_role": "teaching_assistant",
            "secondary_roles": ["course_assistant", "library_user"],
            "role_hierarchy": ["assistant", "staff", "user"],
            "default_permissions": "assistant_basic"
        }
    elif person_type == 'admin':
        return {
            "primary_role": "system_administrator",
            "secondary_roles": ["user_manager", "policy_maker"],
            "role_hierarchy": ["admin", "staff", "user"],
            "default_permissions": "admin_full"
        }
    
    return {
        "primary_role": "guest_user",
        "secondary_roles": [],
        "role_hierarchy": ["guest"],
        "default_permissions": "guest_readonly"
    }

def generate_oauth_config(platform_type):
    """生成OAuth配置"""
    if platform_type in ['student_portal', 'teacher_portal', 'library_system']:
        return {
            "client_id": f"sztu_{platform_type}_client",
            "scope": ["openid", "profile", "email"],
            "redirect_uri": f"https://{platform_type}.sztu.edu.cn/auth/callback",
            "provider": "sztu_sso",
            "auto_login": True,
            "token_expiry": 3600
        }
    else:
        return {
            "enabled": False,
            "reason": "Platform uses traditional authentication"
        }

def generate_password_policy(person_type, platform_type):
    """生成密码策略"""
    if person_type == 'admin':
        return {
            "min_length": 12,
            "require_uppercase": True,
            "require_lowercase": True,
            "require_numbers": True,
            "require_special_chars": True,
            "password_history": 12,
            "expiry_days": 60,
            "lockout_attempts": 3,
            "complexity_score": "high"
        }
    elif person_type in ['teacher', 'assistant_teacher']:
        return {
            "min_length": 8,
            "require_uppercase": True,
            "require_lowercase": True,
            "require_numbers": True,
            "require_special_chars": False,
            "password_history": 6,
            "expiry_days": 180,
            "lockout_attempts": 5,
            "complexity_score": "medium"
        }
    else:  # student
        return {
            "min_length": 6,
            "require_uppercase": False,
            "require_lowercase": True,
            "require_numbers": True,
            "require_special_chars": False,
            "password_history": 3,
            "expiry_days": 365,
            "lockout_attempts": 8,
            "complexity_score": "basic"
        }

def show_statistics(cursor):
    """显示生成统计信息"""
    logger.info("📊 平台配置数据统计:")
    
    # 按平台类型统计
    cursor.execute("""
        SELECT platform_type, COUNT(*) as count 
        FROM platform_configs 
        GROUP BY platform_type 
        ORDER BY count DESC
    """)
    
    for platform_type, count in cursor.fetchall():
        logger.info(f"  {platform_type}: {count:,} 条配置")
    
    # 按人员类型统计
    cursor.execute("""
        SELECT p.person_type, COUNT(pc.config_id) as config_count
        FROM persons p
        LEFT JOIN platform_configs pc ON p.person_id = pc.person_id
        GROUP BY p.person_type
        ORDER BY config_count DESC
    """)
    
    logger.info("\n👥 各人员类型的平台配置:")
    for person_type, config_count in cursor.fetchall():
        logger.info(f"  {person_type}: {config_count:,} 条配置")
    
    # 总计
    cursor.execute("SELECT COUNT(*) FROM platform_configs")
    total = cursor.fetchone()[0]
    logger.info(f"\n📈 平台配置总数: {total:,} 条")

if __name__ == "__main__":
    generate_platform_configs() 