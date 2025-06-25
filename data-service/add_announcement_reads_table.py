#!/usr/bin/env python3
"""
添加announcement_reads表到数据库
用于记录用户公告阅读状态
"""

import sqlite3
import os
from datetime import datetime

def create_announcement_reads_table():
    """创建announcement_reads表"""
    
    # 数据库路径
    db_path = "./sztu_campus.db"
    
    if not os.path.exists(db_path):
        print(f"❌ 数据库文件不存在: {db_path}")
        return False
    
    try:
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 创建announcement_reads表
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS announcement_reads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            announcement_id VARCHAR(20) NOT NULL,
            user_id VARCHAR(20) NOT NULL,
            read_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            is_confirmed BOOLEAN DEFAULT FALSE,
            confirm_time DATETIME NULL,
            reading_duration INTEGER DEFAULT 0,
            device_info VARCHAR(100) NULL,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
            deleted_at DATETIME NULL,
            status VARCHAR(20) NOT NULL DEFAULT 'active',
            is_active BOOLEAN NOT NULL DEFAULT TRUE,
            notes TEXT NULL,
            UNIQUE(announcement_id, user_id) ON CONFLICT REPLACE
        );
        """
        
        cursor.execute(create_table_sql)
        
        # 创建索引
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_announcement_reads_announcement_id ON announcement_reads(announcement_id);",
            "CREATE INDEX IF NOT EXISTS idx_announcement_reads_user_id ON announcement_reads(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_announcement_reads_read_time ON announcement_reads(read_time);",
            "CREATE INDEX IF NOT EXISTS idx_announcement_reads_status ON announcement_reads(status);",
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
        
        # 提交事务
        conn.commit()
        
        # 检查表是否创建成功
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='announcement_reads';")
        if cursor.fetchone():
            print("✅ announcement_reads表创建成功")
            
            # 查看表结构
            cursor.execute("PRAGMA table_info(announcement_reads);")
            columns = cursor.fetchall()
            print(f"📋 表结构 ({len(columns)} 列):")
            for col in columns:
                print(f"   - {col[1]} {col[2]} {'NOT NULL' if col[3] else 'NULL'}")
            
            return True
        else:
            print("❌ 表创建失败")
            return False
            
    except sqlite3.Error as e:
        print(f"❌ 数据库错误: {e}")
        return False
    finally:
        if conn:
            conn.close()

def add_sample_data():
    """添加一些示例数据"""
    
    db_path = "./sztu_campus.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查是否已有数据
        cursor.execute("SELECT COUNT(*) FROM announcement_reads;")
        count = cursor.fetchone()[0]
        
        if count > 0:
            print(f"📊 表中已有 {count} 条记录")
            return
        
        # 获取一些公告ID和用户ID作为示例
        cursor.execute("SELECT announcement_id FROM announcements LIMIT 3;")
        announcements = cursor.fetchall()
        
        cursor.execute("SELECT person_id FROM persons WHERE person_type='student' LIMIT 5;")
        users = cursor.fetchall()
        
        if announcements and users:
            # 添加示例阅读记录
            sample_reads = []
            for ann in announcements[:2]:  # 前2个公告
                for user in users[:3]:     # 前3个用户
                    sample_reads.append((
                        ann[0],  # announcement_id
                        user[0], # user_id
                        datetime.now().isoformat(),  # read_time
                        False,   # is_confirmed
                        None,    # confirm_time
                        30,      # reading_duration (seconds)
                        'miniprogram',  # device_info
                    ))
            
            insert_sql = """
            INSERT OR REPLACE INTO announcement_reads 
            (announcement_id, user_id, read_time, is_confirmed, confirm_time, reading_duration, device_info)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            
            cursor.executemany(insert_sql, sample_reads)
            conn.commit()
            
            print(f"✅ 添加了 {len(sample_reads)} 条示例阅读记录")
        else:
            print("⚠️  没有找到公告或用户数据，跳过示例数据添加")
            
    except sqlite3.Error as e:
        print(f"❌ 添加示例数据失败: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("🚀 开始创建announcement_reads表...")
    
    if create_announcement_reads_table():
        print("\n📝 添加示例数据...")
        add_sample_data()
        print("\n🎉 完成！数据库已更新")
        print("\n📖 接下来可以:")
        print("   1. 重启胶水层服务 (uvicorn main:app --reload)")
        print("   2. 测试公告已读功能")
    else:
        print("\n❌ 表创建失败，请检查错误信息") 