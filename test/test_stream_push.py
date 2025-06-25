#!/usr/bin/env python3
"""
流式推送功能测试脚本
测试公告实时推送的完整流程
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime, timedelta
import sys
import traceback

print("🚀 流式推送测试脚本加载完成")

class StreamPushTester:
    def __init__(self):
        self.backend_url = "http://localhost:8000"
        self.data_service_url = "http://localhost:8001"
        self.access_token = None
        self.session = None
        
    async def setup(self):
        """初始化测试环境"""
        self.session = aiohttp.ClientSession()
        print("🚀 流式推送测试初始化完成")
        
    async def cleanup(self):
        """清理测试环境"""
        if self.session:
            await self.session.close()
        print("🛑 测试环境清理完成")
    
    async def login_test_user(self):
        """登录测试用户"""
        try:
            login_data = {
                "login_id": "202100008036",
                "password": "008036Fh200StuKD",
                "login_type": "password"
            }
            
            async with self.session.post(
                f"{self.backend_url}/api/v1/auth/login",
                json=login_data
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get("code") == 0:
                        self.access_token = result["data"]["access_token"]
                        user_info = result["data"]["user_info"]
                        print(f"✅ 用户登录成功: {user_info['name']} ({user_info['student_id']})")
                        print(f"   学院: {user_info.get('college_name', '未知')}")
                        print(f"   专业: {user_info.get('major_name', '未知')}")
                        return True
                    else:
                        print(f"❌ 登录失败: {result.get('message', result.get('msg', '未知错误'))}")
                        return False
                else:
                    print(f"❌ 登录请求失败: HTTP {response.status}")
                    error_text = await response.text()
                    print(f"错误详情: {error_text}")
                    return False
                    
        except Exception as e:
            print(f"❌ 登录异常: {e}")
            traceback.print_exc()
            return False
    
    async def test_sse_connection(self):
        """测试SSE连接"""
        print("\n🔗 测试1: SSE连接稳定性")
        
        if not self.access_token:
            print("❌ 需要先登录")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            async with self.session.get(
                f"{self.backend_url}/api/v1/stream/events",
                headers=headers
            ) as response:
                print(f"📡 SSE连接状态: {response.status}")
                
                if response.status == 200:
                    print("✅ SSE连接建立成功")
                    
                    # 读取前几个事件来验证连接
                    event_count = 0
                    async for line in response.content:
                        line_str = line.decode('utf-8').strip()
                        if line_str.startswith('data:'):
                            try:
                                data = json.loads(line_str[5:])  # 去掉 'data:' 前缀
                                print(f"📥 收到事件: {data.get('status', 'unknown')}")
                                event_count += 1
                                
                                if event_count >= 2:  # 收到连接事件和心跳事件后退出
                                    break
                                    
                            except json.JSONDecodeError:
                                pass
                                
                    print(f"✅ SSE连接测试完成，收到 {event_count} 个事件")
                    return True
                else:
                    print(f"❌ SSE连接失败: {response.status}")
                    return False
                    
        except Exception as e:
            print(f"❌ SSE连接异常: {e}")
            return False
    
    async def add_test_announcement(self):
        """添加测试公告"""
        print("\n📢 测试2: 添加测试公告")
        
        try:
            test_announcement = {
                "title": f"[测试] 流式推送验证公告 - {datetime.now().strftime('%H:%M:%S')}",
                "content": "这是一条用于验证流式推送功能的测试公告。请忽略此消息。",
                "category": "system",
                "priority": "high", 
                "publish_time": datetime.now().isoformat(),
                "organization_id": 1,
                "author_id": 1,
                "is_urgent": True,
                "is_pinned": False,
                "is_deleted": False,
                "status": "published"
            }
            
            # 直接向data-service添加公告
            async with self.session.post(
                f"{self.data_service_url}/announcements",
                json=test_announcement
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    announcement_id = result.get("announcement_id")
                    print(f"✅ 测试公告创建成功: ID {announcement_id}")
                    return announcement_id
                else:
                    print(f"❌ 创建公告失败: HTTP {response.status}")
                    error_text = await response.text()
                    print(f"错误详情: {error_text}")
                    return None
                    
        except Exception as e:
            print(f"❌ 创建公告异常: {e}")
            traceback.print_exc()
            return None
    
    async def monitor_announcement_events(self, timeout=90):
        """监控公告事件推送"""
        print(f"\n🔍 测试3: 监控公告事件推送 (等待 {timeout} 秒)")
        
        if not self.access_token:
            print("❌ 需要先登录")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            async with self.session.get(
                f"{self.backend_url}/api/v1/stream/events",
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=timeout)
            ) as response:
                if response.status != 200:
                    print(f"❌ 事件流连接失败: {response.status}")
                    return False
                
                print("📡 开始监听事件流...")
                start_time = time.time()
                received_announcement = False
                
                async for line in response.content:
                    line_str = line.decode('utf-8').strip()
                    
                    if line_str.startswith('event:'):
                        event_type = line_str[6:].strip()
                        print(f"📥 事件类型: {event_type}")
                        
                        if event_type in ['announcement', 'notice', 'system_message']:
                            received_announcement = True
                            
                    elif line_str.startswith('data:'):
                        try:
                            data = json.loads(line_str[5:])
                            print(f"📄 事件数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
                            
                            if data.get('event_type') in ['announcement', 'notice', 'system_message']:
                                received_announcement = True
                                print("✅ 收到公告推送事件!")
                                
                        except json.JSONDecodeError:
                            pass
                    
                    # 检查超时
                    if time.time() - start_time > timeout:
                        break
                
                if received_announcement:
                    print("✅ 公告事件推送测试成功")
                    return True
                else:
                    print("⚠️ 未收到公告推送事件，检查事件监控系统")
                    return False
                    
        except asyncio.TimeoutError:
            print(f"⏰ 事件监控超时 ({timeout}秒)")
            return False
        except Exception as e:
            print(f"❌ 事件监控异常: {e}")
            traceback.print_exc()
            return False
    
    async def test_incremental_sync(self):
        """测试增量同步"""
        print("\n🔄 测试4: 增量同步功能")
        
        if not self.access_token:
            print("❌ 需要先登录")
            return False
            
        try:
            # 使用1小时前的时间戳进行同步
            since_time = (datetime.now() - timedelta(hours=1)).isoformat()
            
            headers = {"Authorization": f"Bearer {self.access_token}"}
            params = {"since": since_time}
            
            async with self.session.get(
                f"{self.backend_url}/api/v1/stream/sync",
                headers=headers,
                params=params
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get("status") == 0:
                        events = result["data"]["events"]
                        print(f"✅ 增量同步成功: 获取到 {len(events)} 个事件")
                        
                        # 显示事件详情
                        for event in events[:3]:  # 只显示前3个
                            print(f"   - {event.get('event_type', 'unknown')}: {event.get('timestamp', 'no time')}")
                        
                        return True
                    else:
                        print(f"❌ 增量同步失败: {result.get('msg')}")
                        return False
                else:
                    print(f"❌ 增量同步请求失败: HTTP {response.status}")
                    return False
                    
        except Exception as e:
            print(f"❌ 增量同步异常: {e}")
            return False
    
    async def test_network_recovery(self):
        """测试网络恢复场景（模拟）"""
        print("\n🌐 测试5: 网络恢复测试（模拟断线重连）")
        
        # 这里模拟网络恢复后的增量同步
        print("模拟场景：网络断开5分钟后恢复")
        
        # 获取5分钟前的时间戳
        disconnect_time = (datetime.now() - timedelta(minutes=5)).isoformat()
        
        if not self.access_token:
            print("❌ 需要先登录")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            params = {"since": disconnect_time}
            
            async with self.session.get(
                f"{self.backend_url}/api/v1/stream/sync",
                headers=headers,
                params=params
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    events = result["data"]["events"]
                    print(f"✅ 网络恢复同步: 获取到 {len(events)} 个错过的事件")
                    return True
                else:
                    print(f"❌ 网络恢复同步失败: HTTP {response.status}")
                    return False
                    
        except Exception as e:
            print(f"❌ 网络恢复测试异常: {e}")
            return False
    
    async def run_all_tests(self):
        """运行所有测试"""
        print("🎯 开始流式推送完整测试流程")
        print("=" * 50)
        
        results = []
        
        try:
            # 初始化
            await self.setup()
            
            # 测试1: 登录
            login_success = await self.login_test_user()
            results.append(("用户登录", login_success))
            
            if login_success:
                # 测试2: 用户SSE连接
                sse_success = await self.test_sse_connection()
                results.append(("用户SSE连接", sse_success))
                
                # 测试3: 增量同步
                sync_success = await self.test_incremental_sync()
                results.append(("增量同步", sync_success))
                
                # 测试4: 网络恢复模拟
                recovery_success = await self.test_network_recovery()
                results.append(("网络恢复", recovery_success))
                
                # 测试5: 实时推送（最重要的测试）
                print("\n🚀 开始实时推送测试...")
                
                # 启动事件监控任务
                monitor_task = asyncio.create_task(
                    self.monitor_announcement_events(timeout=60)
                )
                
                # 等待3秒确保监控开始
                await asyncio.sleep(3)
                
                # 添加测试公告
                announcement_id = await self.add_test_announcement()
                
                # 等待监控结果
                push_success = await monitor_task
                results.append(("实时推送", push_success))
            else:
                # 如果登录失败，尝试访客模式
                print("\n⚠️ 登录失败，切换到访客模式测试")
                guest_sse_success = await self.test_guest_sse_connection()
                results.append(("访客SSE连接", guest_sse_success))
                
                guest_sync_success = await self.test_guest_incremental_sync()
                results.append(("访客增量同步", guest_sync_success))
            
            # 输出测试结果
            print("\n" + "=" * 50)
            print("📊 测试结果汇总:")
            
            all_passed = True
            for test_name, success in results:
                if success == "跳过":
                    status = "⏭️ 跳过"
                elif success:
                    status = "✅ 通过"
                else:
                    status = "❌ 失败"
                    all_passed = False
                print(f"   {test_name}: {status}")
            
            print("\n" + "=" * 50)
            if all_passed:
                print("🎉 流式推送核心功能验证成功！")
                print("🎯 答辩亮点验证完成:")
                print("   ✅ SSE流式连接稳定性")
                print("   ✅ 增量同步机制")
                print("   ✅ 实时事件推送")
                print("   ✅ 网络恢复处理")
            else:
                print("⚠️ 部分测试失败，需要进一步排查")
                
            return all_passed
            
        except Exception as e:
            print(f"❌ 测试过程异常: {e}")
            traceback.print_exc()
            return False
        finally:
            await self.cleanup()

    async def test_guest_sse_connection(self):
        """测试访客SSE连接"""
        print("\n🔗 测试1: 访客SSE连接稳定性")
        
        try:
            async with self.session.get(
                f"{self.backend_url}/api/v1/stream/events/guest",
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                print(f"📡 访客SSE连接状态: {response.status}")
                
                if response.status == 200:
                    print("✅ 访客SSE连接建立成功")
                    
                    # 读取前几个事件来验证连接
                    event_count = 0
                    async for line in response.content:
                        line_str = line.decode('utf-8').strip()
                        if line_str.startswith('data:'):
                            try:
                                data = json.loads(line_str[5:])  # 去掉 'data:' 前缀
                                print(f"📥 收到访客事件: {data.get('status', 'unknown')}")
                                event_count += 1
                                
                                if event_count >= 2:  # 收到连接事件和心跳事件后退出
                                    break
                                    
                            except json.JSONDecodeError:
                                pass
                                
                    print(f"✅ 访客SSE连接测试完成，收到 {event_count} 个事件")
                    return True
                else:
                    print(f"❌ 访客SSE连接失败: {response.status}")
                    return False
                    
        except Exception as e:
            print(f"❌ 访客SSE连接异常: {e}")
            return False

    async def test_guest_incremental_sync(self):
        """测试访客增量同步"""
        print("\n🔄 测试2: 访客增量同步功能")
        
        try:
            # 使用1小时前的时间戳进行同步
            since_time = (datetime.now() - timedelta(hours=1)).isoformat()
            
            params = {"since": since_time}
            
            async with self.session.get(
                f"{self.backend_url}/api/v1/stream/sync/guest",
                params=params
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get("status") == 0:
                        events = result["data"]["events"]
                        print(f"✅ 访客增量同步成功: 获取到 {len(events)} 个事件")
                        
                        # 显示事件详情
                        for event in events[:3]:  # 只显示前3个
                            print(f"   - {event.get('event_type', 'unknown')}: {event.get('timestamp', 'no time')}")
                        
                        return True
                    else:
                        print(f"❌ 访客增量同步失败: {result.get('msg')}")
                        return False
                else:
                    print(f"❌ 访客增量同步请求失败: HTTP {response.status}")
                    return False
                    
        except Exception as e:
            print(f"❌ 访客增量同步异常: {e}")
            return False

    async def check_announcement_monitoring(self):
        """检查公告监控系统"""
        print("\n🔍 测试4: 检查公告监控系统")
        
        try:
            # 等待30秒，看事件监控系统是否检测到新公告
            print("等待30秒，检查事件监控系统...")
            await asyncio.sleep(30)
            
            # 检查流式推送状态
            async with self.session.get(
                f"{self.backend_url}/api/v1/stream/status"
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"📊 流式推送系统状态: {result}")
                    
                    total_events = result["data"]["total_events"]
                    if total_events > 0:
                        print(f"✅ 事件监控系统正常，共有 {total_events} 个事件")
                        return True
                    else:
                        print("⚠️ 暂无事件，但监控系统运行正常")
                        return True
                else:
                    print(f"❌ 无法获取流式推送状态: {response.status}")
                    return False
                    
        except Exception as e:
            print(f"❌ 检查公告监控异常: {e}")
            return False

async def main():
    print("开始流式推送测试")
    tester = StreamPushTester()
    success = await tester.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main()) 