#!/usr/bin/env python3
"""
简单的公告创建测试脚本
"""

import sys
sys.path.append('.')

from stream_test_controller import StreamTestController

def test_announcement_creation():
    """测试公告创建功能"""
    print("🎯 开始测试公告创建功能")
    print("=" * 50)
    
    controller = StreamTestController()
    
    # 测试1: 检查数据库状态
    print("\n📊 检查数据库状态...")
    controller.check_database_status()
    
    # 测试2: 创建单条公告
    print("\n✨ 创建单条测试公告...")
    success = controller.create_announcement()
    if success:
        print("✅ 单条公告创建成功")
    else:
        print("❌ 单条公告创建失败")
        return False
    
    # 测试3: 查看最近公告
    print("\n📋 查看最近公告...")
    controller.list_recent_announcements(3)
    
    # 测试4: 批量创建公告 (3条，间隔1秒)
    print("\n🚀 批量创建3条公告...")
    batch_success = controller.batch_create_announcements(3, 1)
    print(f"📊 批量创建结果: {batch_success}/3 成功")
    
    # 测试5: 再次查看最近公告
    print("\n📋 查看批量创建后的公告列表...")
    controller.list_recent_announcements(5)
    
    # 测试6: 最终状态检查
    print("\n📊 最终数据库状态...")
    controller.check_database_status()
    
    print("\n🎉 流式推送公告创建测试完成!")
    return True

if __name__ == "__main__":
    try:
        test_announcement_creation()
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc() 