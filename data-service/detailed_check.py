import sqlite3

def detailed_check():
    conn = sqlite3.connect('sztu_campus.db')
    cursor = conn.cursor()
    
    print("=== 详细数据库检查 ===\n")
    
    # 检查所有表的数据量
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()
    
    print("=== 所有表数据量统计 ===")
    table_counts = {}
    for table in tables:
        table_name = table[0]
        if table_name != 'sqlite_sequence':  # 跳过系统表
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            table_counts[table_name] = count
            status = "✅" if count > 0 else "⚠️"
            print(f"{status} {table_name}: {count:,} 条")
    
    # 检查核心业务数据
    print("\n=== 核心业务数据详情 ===")
    
    # 公告数据
    print("\n--- 公告数据 ---")
    cursor.execute("SELECT title, department, category, publish_time FROM announcements ORDER BY publish_time DESC")
    announcements = cursor.fetchall()
    for i, ann in enumerate(announcements, 1):
        print(f"{i}. 【{ann[2]}】{ann[0][:30]}...")
        print(f"   发布部门: {ann[1]}, 时间: {ann[3]}")
    
    # 人员统计
    print("\n--- 人员统计 ---")
    cursor.execute("SELECT person_type, COUNT(*) FROM persons WHERE is_deleted = 0 GROUP BY person_type")
    person_stats = cursor.fetchall()
    for person_type, count in person_stats:
        print(f"  {person_type}: {count:,} 人")
    
    # 课程统计
    print("\n--- 课程数据 ---")
    cursor.execute("SELECT college_id, COUNT(*) FROM courses GROUP BY college_id ORDER BY COUNT(*) DESC LIMIT 5")
    course_stats = cursor.fetchall()
    print("各学院课程数量 (前5名):")
    for college_id, count in course_stats:
        print(f"  {college_id}: {count} 门课程")
    
    # 图书统计
    print("\n--- 图书数据 ---")
    cursor.execute("SELECT category, COUNT(*) FROM books GROUP BY category ORDER BY COUNT(*) DESC LIMIT 5")
    book_stats = cursor.fetchall()
    print("图书分类统计 (前5名):")
    for category, count in book_stats:
        print(f"  {category}: {count} 本")
    
    # 交易统计
    print("\n--- 交易数据 ---")
    cursor.execute("SELECT COUNT(*) FROM transactions")
    transaction_count = cursor.fetchone()[0]
    cursor.execute("SELECT SUM(amount) FROM transactions WHERE transaction_type = 'consumption'")
    total_consumption = cursor.fetchone()[0] or 0
    print(f"  总交易记录: {transaction_count:,} 条")
    print(f"  总消费金额: {total_consumption:,.2f} 元")
    
    # 检查空表
    print("\n=== 需要关注的空表 ===")
    empty_tables = []
    important_empty_tables = []
    
    for table_name, count in table_counts.items():
        if count == 0:
            empty_tables.append(table_name)
            # 标记重要的空表
            if table_name in ['events', 'class_schedules', 'user_reading_records', 'departments']:
                important_empty_tables.append(table_name)
                print(f"🔴 {table_name}: 重要业务表为空")
            else:
                print(f"🟡 {table_name}: 空表")
    
    # 数据完整性建议
    print("\n=== 数据补充建议 ===")
    suggestions = []
    
    if table_counts.get('announcements', 0) < 10:
        suggestions.append("📢 建议补充更多公告数据 (当前仅3条)")
    
    if table_counts.get('events', 0) == 0:
        suggestions.append("🎯 建议添加校园活动数据")
    
    if table_counts.get('class_schedules', 0) == 0:
        suggestions.append("📅 建议添加课程表数据")
    
    if table_counts.get('user_reading_records', 0) == 0:
        suggestions.append("📖 建议生成用户阅读记录")
    
    if table_counts.get('departments', 0) == 0:
        suggestions.append("🏢 建议添加部门数据")
    
    if suggestions:
        for suggestion in suggestions:
            print(f"  {suggestion}")
    else:
        print("  ✅ 数据完整性良好")
    
    conn.close()
    return important_empty_tables, suggestions

if __name__ == "__main__":
    empty_tables, suggestions = detailed_check() 