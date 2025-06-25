#!/usr/bin/env python3
"""
增强版流式推送测试控制脚本 - 支持完整CRUD操作
专门用于测试实时更新功能
"""

import sqlite3
import sys
import time
from datetime import datetime
import random

print("🎯 增强版流式推送测试脚本已加载")

class EnhancedStreamTestController:
    def __init__(self):
        self.db_path = "data-service/sztu_campus.db"
        self.test_counter = 1
        
    def create_announcement(self):
        """创建测试公告"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 生成测试数据
            title = f"流式测试公告推送{self.test_counter}"
            content = self.generate_content()
            announcement_id = f"TEST_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}"
            current_time = datetime.now().isoformat()
            
            # 插入公告
            cursor.execute("""
                INSERT INTO announcements (
                    announcement_id, title, content, publisher_id, publisher_name,
                    department, category, priority, status, is_urgent, is_pinned,
                    publish_time, view_count, like_count, comment_count,
                    created_at, updated_at, is_deleted
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                announcement_id, title, content, "TEST_USER", "测试管理员",
                "信息技术部", "system", "normal", "published", False, False,
                current_time, 0, 0, 0,
                current_time, current_time, False
            ))
            
            conn.commit()
            conn.close()
            
            print(f"✅ 公告创建成功: {title}")
            print(f"   ID: {announcement_id}")
            print(f"   内容长度: {len(content)}字符")
            print(f"   发布时间: {current_time}")
            
            self.test_counter += 1
            return announcement_id
            
        except Exception as e:
            print(f"❌ 创建公告失败: {e}")
            import traceback
            traceback.print_exc()
            return None

    def update_announcement(self, announcement_id=None):
        """修改公告内容"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 如果没有指定ID，选择最新的测试公告
            if not announcement_id:
                cursor.execute("""
                    SELECT announcement_id, title FROM announcements 
                    WHERE title LIKE '流式测试公告推送%' AND is_deleted = 0
                    ORDER BY created_at DESC LIMIT 1
                """)
                result = cursor.fetchone()
                if not result:
                    print("❌ 没有找到可修改的测试公告")
                    conn.close()
                    return False
                announcement_id, old_title = result
            else:
                # 验证公告是否存在
                cursor.execute("""
                    SELECT title FROM announcements 
                    WHERE announcement_id = ? AND is_deleted = 0
                """, (announcement_id,))
                result = cursor.fetchone()
                if not result:
                    print(f"❌ 公告 {announcement_id} 不存在或已删除")
                    conn.close()
                    return False
                old_title = result[0]
            
            # 生成新内容
            timestamp = datetime.now().strftime('%H:%M:%S')
            updated_title = f"{old_title} [已修改 {timestamp}]"
            updated_content = f"【内容已更新】{self.generate_content()} 更新时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            current_time = datetime.now().isoformat()
            
            # 更新公告
            cursor.execute("""
                UPDATE announcements 
                SET title = ?, content = ?, updated_at = ?
                WHERE announcement_id = ?
            """, (updated_title, updated_content, current_time, announcement_id))
            
            if cursor.rowcount > 0:
                conn.commit()
                print(f"✅ 公告修改成功:")
                print(f"   ID: {announcement_id}")
                print(f"   新标题: {updated_title}")
                print(f"   内容长度: {len(updated_content)}字符")
                print(f"   更新时间: {current_time}")
            else:
                print(f"❌ 修改失败，没有找到公告 {announcement_id}")
                
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ 修改公告失败: {e}")
            import traceback
            traceback.print_exc()
            return False

    def delete_single_announcement(self, announcement_id=None):
        """删除单条公告"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 如果没有指定ID，选择最新的测试公告
            if not announcement_id:
                cursor.execute("""
                    SELECT announcement_id, title FROM announcements 
                    WHERE title LIKE '流式测试公告推送%' AND is_deleted = 0
                    ORDER BY created_at DESC LIMIT 1
                """)
                result = cursor.fetchone()
                if not result:
                    print("❌ 没有找到可删除的测试公告")
                    conn.close()
                    return False
                announcement_id, title = result
            else:
                # 验证公告是否存在
                cursor.execute("""
                    SELECT title FROM announcements 
                    WHERE announcement_id = ? AND is_deleted = 0
                """, (announcement_id,))
                result = cursor.fetchone()
                if not result:
                    print(f"❌ 公告 {announcement_id} 不存在或已删除")
                    conn.close()
                    return False
                title = result[0]
            
            # 软删除公告
            current_time = datetime.now().isoformat()
            cursor.execute("""
                UPDATE announcements 
                SET is_deleted = 1, deleted_at = ?, updated_at = ?
                WHERE announcement_id = ?
            """, (current_time, current_time, announcement_id))
            
            if cursor.rowcount > 0:
                conn.commit()
                print(f"✅ 公告删除成功:")
                print(f"   ID: {announcement_id}")
                print(f"   标题: {title}")
                print(f"   删除时间: {current_time}")
            else:
                print(f"❌ 删除失败，没有找到公告 {announcement_id}")
                
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ 删除公告失败: {e}")
            return False

    def list_test_announcements(self, limit=10):
        """列出测试公告"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT announcement_id, title, publisher_name, category, 
                       priority, publish_time, status, view_count, 
                       created_at, updated_at, is_deleted
                FROM announcements 
                WHERE title LIKE '流式测试公告推送%'
                ORDER BY created_at DESC 
                LIMIT ?
            """, (limit,))
            
            rows = cursor.fetchall()
            conn.close()
            
            if not rows:
                print("📋 暂无测试公告")
                return
            
            print(f"📋 最近 {len(rows)} 条测试公告:")
            print("-" * 100)
            for i, row in enumerate(rows, 1):
                status_text = "❌已删除" if row[10] else "✅正常"
                print(f"[{i:2d}] ID: {row[0]}")
                print(f"     标题: {row[1]}")
                print(f"     状态: {status_text} | 分类: {row[3]} | 优先级: {row[4]}")
                print(f"     创建: {row[8]} | 更新: {row[9]}")
                print("-" * 50)
            
        except Exception as e:
            print(f"❌ 查询公告失败: {e}")

    def simulate_real_time_changes(self):
        """模拟实时变更场景"""
        print("🔄 开始模拟实时变更场景...")
        
        # 1. 快速创建3条公告
        announcement_ids = []
        for i in range(3):
            print(f"创建第 {i+1} 条公告...")
            aid = self.create_announcement()
            if aid:
                announcement_ids.append(aid)
            time.sleep(2)
        
        time.sleep(3)
        
        # 2. 随机修改公告
        if announcement_ids:
            for aid in announcement_ids[:2]:  # 修改前两条
                print(f"修改公告 {aid}...")
                self.update_announcement(aid)
                time.sleep(2)
        
        time.sleep(3)
        
        # 3. 删除最后一条
        if announcement_ids:
            print(f"删除公告 {announcement_ids[-1]}...")
            self.delete_single_announcement(announcement_ids[-1])
        
        print("✅ 实时变更场景模拟完成")

    def generate_content(self):
        """生成300字测试内容"""
        content_templates = [
            "深圳技术大学智慧校园系统流式推送功能测试验证。本系统采用Server-Sent Events技术实现高效实时通信，确保校园信息及时准确传达给师生。测试内容包括公告发布、成绩更新、课表变更等多种场景，通过模拟真实使用环境检验系统性能表现。我们的目标是为师生提供更加便捷及时的校园信息服务体验。",
            
            "校园数字化转型进程中，实时信息推送技术发挥着至关重要的作用。本系统通过先进的流式数据处理技术，实现从数据产生到用户接收的全链路优化。当有新的校园公告发布时，系统会在30秒内自动检测并推送给相关用户，大大提升信息传递效率。同时具备智能去重、离线消息缓存、断网恢复等功能。",
            
            "深技大iCampus智慧校园平台致力于构建全方位数字化校园生态。通过集成公告系统、课表查询、成绩管理、图书馆服务等多个模块，为师生提供一站式校园服务体验。本次流式推送测试是系统优化升级的重要环节，我们将通过大量真实场景模拟来验证系统可靠性。",
        ]
        
        # 随机选择模板
        base_content = random.choice(content_templates)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        test_id = f"T{self.test_counter:03d}"
        
        content = f"【{test_id}】{base_content} 测试时间：{timestamp}，测试编号：{test_id}。"
        
        # 补充到300字符
        while len(content) < 290:
            content += f" 流式推送验证{random.randint(100, 999)}。"
        
        return content[:300]

if __name__ == "__main__":
    controller = EnhancedStreamTestController()
    
    print("🎯 增强版流式推送测试控制台")
    print("=" * 60)
    print("输入命令:")
    print("  1 - 创建单条公告")
    print("  2 - 查看测试公告列表")
    print("  3 - 修改最新测试公告")
    print("  4 - 删除最新测试公告")
    print("  5 - 指定ID修改公告")
    print("  6 - 指定ID删除公告")
    print("  7 - 模拟实时变更场景")
    print("  q - 退出")
    print("-" * 40)
    
    while True:
        try:
            choice = input("\n请选择操作: ").strip()
            
            if choice == 'q':
                print("👋 退出程序")
                break
            elif choice == '1':
                controller.create_announcement()
            elif choice == '2':
                controller.list_test_announcements()
            elif choice == '3':
                controller.update_announcement()
            elif choice == '4':
                confirm = input("确认删除最新测试公告? (y/N): ").strip().lower()
                if confirm == 'y':
                    controller.delete_single_announcement()
            elif choice == '5':
                announcement_id = input("输入公告ID: ").strip()
                if announcement_id:
                    controller.update_announcement(announcement_id)
                else:
                    print("❌ 请输入有效的公告ID")
            elif choice == '6':
                announcement_id = input("输入公告ID: ").strip()
                if announcement_id:
                    confirm = input(f"确认删除公告 {announcement_id}? (y/N): ").strip().lower()
                    if confirm == 'y':
                        controller.delete_single_announcement(announcement_id)
                else:
                    print("❌ 请输入有效的公告ID")
            elif choice == '7':
                controller.simulate_real_time_changes()
            else:
                print("❌ 无效选择，请重新输入")
                
        except KeyboardInterrupt:
            print("\n👋 程序被中断")
            break
        except Exception as e:
            print(f"❌ 操作失败: {e}")
            import traceback
            traceback.print_exc() 