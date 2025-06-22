#!/usr/bin/env python3
"""
查看已生成的Mock数据概览
"""

import sqlite3
import os

def main():
    db_path = "sztu_campus.db"
    if not os.path.exists(db_path):
        print("❌ 数据库文件不存在")
        return
    
    print("=" * 60)
    print("🗄️ SZTU-iCampus 生成数据概览")
    print("=" * 60)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 检查核心数据表
    tables = [
        ('persons', '人员'),
        ('colleges', '学院'),
        ('majors', '专业'),
        ('classes', '班级'),
        ('courses', '课程'),
        ('course_instances', '课程实例'),
        ('grades', '成绩记录'),
        ('locations', '地点'),
        ('assets', '资产'),
        ('books', '图书'),
        ('borrow_records', '借阅记录'),
        ('campus_cards', '校园卡'),
        ('transactions', '交易记录'),
        ('platform_configs', '平台配置'),
        ('network_permissions', '网络权限'),
        ('system_access', '系统访问'),
    ]
    
    print("\n📊 数据表统计:")
    total_records = 0
    for table, desc in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            total_records += count
            print(f"  {desc:12}: {count:>10,} 条")
        except:
            print(f"  {desc:12}: {'表不存在':>10}")
    
    print(f"\n📈 总记录数: {total_records:,} 条")
    
    # 检查权限数据样本
    print("\n🔐 权限数据样本:")
    try:
        cursor.execute("""
            SELECT person_type, COUNT(*) as cnt, 
                   SUBSTR(permissions, 1, 100) || '...' as perm_sample
            FROM persons 
            WHERE permissions != '{"read": [], "write": [], "share": []}'
            GROUP BY person_type
            LIMIT 3
        """)
        for row in cursor.fetchall():
            person_type, count, perm_sample = row
            print(f"  {person_type:15}: {count:>7,} 人有权限")
    except Exception as e:
        print(f"  权限检查失败: {e}")
    
    # 检查数据分布
    print("\n👥 人员分布:")
    try:
        cursor.execute("SELECT person_type, COUNT(*) FROM persons GROUP BY person_type")
        for row in cursor.fetchall():
            person_type, count = row
            print(f"  {person_type:15}: {count:>7,} 人")
    except:
        print("  无法获取人员分布")
    
    # 检查成绩分布
    print("\n📊 成绩分布:")
    try:
        cursor.execute("SELECT grade_level, COUNT(*) FROM grades GROUP BY grade_level ORDER BY grade_level")
        for row in cursor.fetchall():
            grade_level, count = row
            print(f"  {grade_level}等:             {count:>7,} 条")
    except:
        print("  无法获取成绩分布")
    
    # 数据库文件大小
    try:
        file_size = os.path.getsize(db_path) / (1024 * 1024)  # MB
        print(f"\n💾 数据库文件大小: {file_size:.2f} MB")
    except:
        print("\n💾 无法获取文件大小")
    
    print("\n" + "=" * 60)
    print("✅ 数据查看完成！")
    print("💡 可以直接使用这些数据进行前端开发和API测试")
    print("=" * 60)
    
    conn.close()

if __name__ == "__main__":
    main() 