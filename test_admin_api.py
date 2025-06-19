#!/usr/bin/env python3
"""
管理员API测试脚本
用于测试新创建的管理员功能是否正常工作
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_admin_apis():
    """测试管理员相关API"""
    print("🔧 开始测试管理员API功能...")
    
    # 1. 测试未授权访问
    print("\n1. 测试未授权访问管理员API...")
    response = requests.get(f"{BASE_URL}/api/v1/admin/stats")
    print(f"未授权访问状态码: {response.status_code}")
    if response.status_code == 401:
        print("✅ 权限验证正常工作")
    
    # 2. 测试测试登录
    print("\n2. 测试用户登录...")
    login_data = {
        "student_id": "admin",
        "name": "管理员"
    }
    response = requests.post(f"{BASE_URL}/api/v1/auth/test-login", json=login_data)
    print(f"登录状态码: {response.status_code}")
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        print(f"✅ 登录成功，获取token: {token[:20]}...")
        
        # 3. 测试获取用户信息
        print("\n3. 测试获取用户信息...")
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/v1/auth/me", headers=headers)
        print(f"用户信息状态码: {response.status_code}")
        if response.status_code == 200:
            user_info = response.json()
            print(f"用户信息: {json.dumps(user_info, indent=2, ensure_ascii=False)}")
            is_admin = user_info.get("is_admin", False)
            print(f"是否为管理员: {is_admin}")
        
        # 4. 测试管理员API（可能会失败，因为默认用户不是管理员）
        print("\n4. 测试管理员统计API...")
        response = requests.get(f"{BASE_URL}/api/v1/admin/stats", headers=headers)
        print(f"管理员统计状态码: {response.status_code}")
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ 管理员API访问成功")
            print(f"系统统计: {json.dumps(stats, indent=2, ensure_ascii=False)}")
        elif response.status_code == 403:
            print("⚠️ 当前用户没有管理员权限（这是正常的）")
        
        # 5. 测试用户列表API
        print("\n5. 测试用户列表API...")
        response = requests.get(f"{BASE_URL}/api/v1/admin/users", headers=headers)
        print(f"用户列表状态码: {response.status_code}")
        if response.status_code == 403:
            print("⚠️ 权限验证正常工作")
        
    else:
        print("❌ 登录失败")

def test_api_docs():
    """测试API文档是否可访问"""
    print("\n📚 测试API文档访问...")
    response = requests.get(f"{BASE_URL}/docs")
    if response.status_code == 200:
        print("✅ API文档可正常访问: http://localhost:8000/docs")
    else:
        print("❌ API文档访问失败")

if __name__ == "__main__":
    print("🚀 SZTU-iCampus 管理员功能测试")
    print("=" * 50)
    
    try:
        test_api_docs()
        test_admin_apis()
        
        print("\n" + "=" * 50)
        print("🎉 测试完成！")
        print("\n💡 提示:")
        print("1. 访问 http://localhost:8000/docs 查看完整API文档")
        print("2. 要测试完整管理员功能，需要在数据库中设置用户的is_admin字段为true")
        print("3. 小程序端管理员入口只对管理员用户可见")
        
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端服务")
        print("请确保后端服务已启动：cd backend && python -m uvicorn main:app --reload")
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}") 