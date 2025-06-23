import sqlite3

try:
    conn = sqlite3.connect('sztu_campus.db')
    cursor = conn.cursor()
    
    # 检查表数量
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()
    print(f"总表数: {len(tables)}")
    
    # 列出所有表
    print("\n所有表名:")
    for table in tables:
        print(f"  {table[0]}")
    
    # 检查几个重要表的数据量
    important_tables = ['persons', 'announcements', 'events', 'courses', 'books']
    print("\n重要表数据量:")
    for table_name in important_tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"  {table_name}: {count:,} 条")
        except sqlite3.OperationalError as e:
            print(f"  {table_name}: 表不存在")
    
    conn.close()
    print("\n数据库检查完成！")
    
except Exception as e:
    print(f"错误: {e}") 