#!/usr/bin/env python3
"""
测试登录功能的脚本
"""

import requests
import json

# 配置
API_BASE = "http://localhost:8000/api/v1"

def test_health():
    """测试健康检查"""
    print("🔍 测试健康检查...")
    try:
        response = requests.get("http://localhost:8000/health")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")
        return False

def test_login():
    """测试登录功能"""
    print("\n🔐 测试登录功能...")
    
    # 使用测试账号（从test_login_accounts.txt中选择）
    test_accounts = [
        {"login_id": "2025000001", "password": "Admin001HP1dbd10", "type": "管理员"},
        {"login_id": "2025001069", "password": "1069YangSztu2024", "type": "助教"},
        {"login_id": "202108090101", "password": "090101Ty901StuaB", "type": "学生"}  # 需要确认实际密码
    ]
    
    for account in test_accounts:
        print(f"\n测试{account['type']}登录: {account['login_id']}")
        
        try:
            response = requests.post(
                f"{API_BASE}/auth/login",
                json={
                    "login_id": account["login_id"],
                    "password": account["password"],
                    "remember_me": False
                },
                headers={"Content-Type": "application/json"}
            )
            
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ 登录成功!")
                print(f"用户: {data['user']['name']}")
                print(f"类型: {data['user']['person_type']}")
                print(f"学院: {data['user'].get('college_name', 'N/A')}")
                print(f"Token长度: {len(data['access_token'])}")
                
                # 测试获取用户信息
                test_get_user_info(data['access_token'])
                break
            else:
                print(f"❌ 登录失败: {response.text}")
                
        except Exception as e:
            print(f"❌ 请求异常: {e}")

def test_get_user_info(token):
    """测试获取用户信息"""
    print("\n👤 测试获取用户信息...")
    
    try:
        response = requests.get(
            f"{API_BASE}/auth/me",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
        )
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            user_info = response.json()
            print("✅ 获取用户信息成功!")
            print(f"姓名: {user_info['name']}")
            print(f"登录ID: {user_info['login_id']}")
            print(f"权限: {user_info['permissions']}")
        else:
            print(f"❌ 获取用户信息失败: {response.text}")
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")

def test_invalid_login():
    """测试错误登录"""
    print("\n❌ 测试错误登录...")
    
    try:
        response = requests.post(
            f"{API_BASE}/auth/login",
            json={
                "login_id": "wrong_id",
                "password": "wrong_password",
                "remember_me": False
            }
        )
        
        print(f"状态码: {response.status_code}")
        if response.status_code == 401:
            print("✅ 错误登录正确被拒绝")
        else:
            print(f"❌ 意外响应: {response.text}")
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")

if __name__ == "__main__":
    print("🚀 开始测试SZTU-iCampus认证系统")
    print("=" * 50)
    
    # 1. 健康检查
    if not test_health():
        print("服务未启动，请先启动服务")
        exit(1)
    
    # 2. 登录测试
    test_login()
    
    # 3. 错误登录测试
    test_invalid_login()
    
    print("\n🎉 测试完成!") 