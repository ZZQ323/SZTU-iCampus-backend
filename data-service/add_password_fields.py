#!/usr/bin/env python3
"""
为数据库添加密码字段并为现有用户生成密码
密码生成规则：结合学号、专业、姓名拼音等信息，长度16-40字符
"""

import sqlite3
import os
import random
import hashlib
from loguru import logger
import pypinyin
import secrets
import string

def add_password_fields():
    """添加密码字段并生成密码"""
    logger.info("开始为数据库添加密码字段...")
    
    db_path = "sztu_campus.db"
    if not os.path.exists(db_path):
        logger.error("数据库文件不存在")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 1. 检查是否已有密码字段
        cursor.execute("PRAGMA table_info(persons)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'password_hash' not in columns:
            logger.info("添加密码相关字段...")
            cursor.execute("""
                ALTER TABLE persons ADD COLUMN password_hash VARCHAR(128);
            """)
            cursor.execute("""
                ALTER TABLE persons ADD COLUMN password_salt VARCHAR(32);
            """)
            cursor.execute("""
                ALTER TABLE persons ADD COLUMN password_plain VARCHAR(50);
            """)
            cursor.execute("""
                ALTER TABLE persons ADD COLUMN last_login DATETIME;
            """)
            cursor.execute("""
                ALTER TABLE persons ADD COLUMN login_attempts INTEGER DEFAULT 0;
            """)
            cursor.execute("""
                ALTER TABLE persons ADD COLUMN account_locked BOOLEAN DEFAULT 0;
            """)
            logger.info("✅ 密码字段添加完成")
        else:
            logger.info("密码字段已存在，继续生成密码...")
        
        # 2. 获取所有没有密码的用户
        cursor.execute("""
            SELECT person_id, person_type, name, student_id, employee_id, major_id, college_id
            FROM persons 
            WHERE password_hash IS NULL OR password_hash = ''
        """)
        persons = cursor.fetchall()
        
        if not persons:
            logger.info("所有用户已有密码，无需生成")
            return
        
        logger.info(f"需要为 {len(persons)} 个用户生成密码...")
        
        # 3. 为每个用户生成密码
        password_updates = []
        passwords_info = []  # 用于记录明文密码（仅用于测试）
        
        for person_id, person_type, name, student_id, employee_id, major_id, college_id in persons:
            # 生成密码
            password_plain = generate_password(name, student_id, employee_id, major_id, person_type)
            
            # 生成盐值和哈希
            salt = secrets.token_hex(16)
            password_hash = hashlib.sha256((password_plain + salt).encode()).hexdigest()
            
            password_updates.append((
                password_hash,
                salt, 
                password_plain,  # 临时存储明文用于测试
                0,  # login_attempts
                0,  # account_locked
                person_id
            ))
            
            # 记录密码信息用于输出
            passwords_info.append({
                'person_id': person_id,
                'person_type': person_type,
                'name': name,
                'login_id': student_id or employee_id,
                'password': password_plain
            })
        
        # 4. 批量更新密码
        cursor.executemany("""
            UPDATE persons 
            SET password_hash = ?, password_salt = ?, password_plain = ?,
                login_attempts = ?, account_locked = ?
            WHERE person_id = ?
        """, password_updates)
        
        conn.commit()
        logger.info(f"✅ 成功为 {len(password_updates)} 个用户生成密码")
        
        # 5. 输出密码统计信息
        show_password_statistics(cursor, passwords_info[:20])  # 只显示前20个作为示例
        
    except Exception as e:
        logger.error(f"❌ 添加密码字段失败: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

def generate_password(name, student_id, employee_id, major_id, person_type):
    """生成密码 - 结合多种信息，长度16-40字符"""
    
    # 获取姓名拼音
    name_pinyin = ''.join(pypinyin.lazy_pinyin(name, style=pypinyin.NORMAL))
    name_pinyin_abbr = ''.join([py[0] for py in pypinyin.lazy_pinyin(name, style=pypinyin.NORMAL)])
    
    # 获取登录ID
    login_id = student_id or employee_id or "unknown"
    
    # 基础组件
    components = []
    
    if person_type == 'student':
        # 学生密码：学号后6位 + 姓名拼音 + 专业编码后3位
        components = [
            login_id[-6:] if len(login_id) >= 6 else login_id,
            name_pinyin_abbr.capitalize(),
            (major_id or "000")[-3:],
            "Stu"
        ]
    elif person_type in ['teacher', 'assistant_teacher']:
        # 教师密码：工号后4位 + 姓名拼音 + 学院编码 + 年份
        components = [
            login_id[-4:] if len(login_id) >= 4 else login_id,
            name_pinyin[:4].capitalize(),
            "Sztu",
            "2024"
        ]
    elif person_type == 'admin':
        # 管理员密码：工号 + 姓名拼音缩写 + 随机字符
        components = [
            "Admin",
            login_id[-3:] if len(login_id) >= 3 else login_id,
            name_pinyin_abbr.upper(),
            secrets.token_hex(3)
        ]
    else:
        # 默认密码
        components = [
            "User",
            login_id[-4:] if len(login_id) >= 4 else login_id,
            name_pinyin[:3].capitalize(),
            "2024"
        ]
    
    # 组合基础密码
    base_password = ''.join(components)
    
    # 确保长度在16-40之间
    if len(base_password) < 16:
        # 不够长，添加随机字符
        needed = 16 - len(base_password)
        base_password += ''.join(random.choices(string.digits + string.ascii_letters, k=needed))
    elif len(base_password) > 40:
        # 太长，截取
        base_password = base_password[:40]
    
    # 确保包含数字和字母
    if not any(c.isdigit() for c in base_password):
        base_password = base_password[:-1] + str(random.randint(0, 9))
    
    if not any(c.isupper() for c in base_password):
        pos = random.randint(0, len(base_password) - 1)
        base_password = base_password[:pos] + base_password[pos].upper() + base_password[pos+1:]
    
    return base_password

def show_password_statistics(cursor, sample_passwords):
    """显示密码生成统计信息"""
    logger.info("📊 密码生成统计:")
    
    # 按用户类型统计
    cursor.execute("""
        SELECT person_type, COUNT(*) 
        FROM persons 
        WHERE password_hash IS NOT NULL 
        GROUP BY person_type
    """)
    
    for person_type, count in cursor.fetchall():
        logger.info(f"  {person_type}: {count:,} 个用户")
    
    # 显示密码示例
    logger.info("\n🔐 密码示例（仅测试用）:")
    for info in sample_passwords:
        logger.info(f"  {info['person_type']} | {info['login_id']} | {info['name']} | {info['password']}")
    
    # 密码长度分布
    cursor.execute("""
        SELECT 
            CASE 
                WHEN LENGTH(password_plain) < 20 THEN '16-19字符'
                WHEN LENGTH(password_plain) < 25 THEN '20-24字符'
                WHEN LENGTH(password_plain) < 30 THEN '25-29字符'
                WHEN LENGTH(password_plain) < 35 THEN '30-34字符'
                ELSE '35-40字符'
            END as length_range,
            COUNT(*) as count
        FROM persons 
        WHERE password_plain IS NOT NULL
        GROUP BY length_range
    """)
    
    logger.info("\n📏 密码长度分布:")
    for length_range, count in cursor.fetchall():
        logger.info(f"  {length_range}: {count:,} 个")
    
    # 总计
    cursor.execute("SELECT COUNT(*) FROM persons WHERE password_hash IS NOT NULL")
    total = cursor.fetchone()[0]
    logger.info(f"\n📈 总计: {total:,} 个用户已设置密码")

def create_test_login_data():
    """创建测试登录数据文件"""
    logger.info("生成测试登录数据...")
    
    db_path = "sztu_campus.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 获取各类型用户的登录信息
    cursor.execute("""
        SELECT person_type, student_id, employee_id, name, password_plain
        FROM persons 
        WHERE password_plain IS NOT NULL
        ORDER BY person_type, person_id
        LIMIT 50
    """)
    
    test_accounts = []
    for person_type, student_id, employee_id, name, password_plain in cursor.fetchall():
        login_id = student_id or employee_id
        test_accounts.append({
            'type': person_type,
            'login_id': login_id,
            'password': password_plain,
            'name': name
        })
    
    # 写入测试文件
    with open('test_login_accounts.txt', 'w', encoding='utf-8') as f:
        f.write("SZTU-iCampus 测试登录账号\n")
        f.write("="*50 + "\n\n")
        
        for account in test_accounts:
            f.write(f"类型: {account['type']}\n")
            f.write(f"登录ID: {account['login_id']}\n")
            f.write(f"密码: {account['password']}\n")
            f.write(f"姓名: {account['name']}\n")
            f.write("-" * 30 + "\n")
    
    logger.info("✅ 测试账号已写入 test_login_accounts.txt")
    
    conn.close()

if __name__ == "__main__":
    add_password_fields()
    create_test_login_data() 