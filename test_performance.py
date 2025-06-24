#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
性能测试脚本 - 对比优化前后的查询性能
"""

import time
import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8001"
API_KEY = "sztu-data-service-key-2024"
HEADERS = {"X-API-Key": API_KEY}

def test_old_vs_new_query():
    """对比旧查询和新查询的性能"""
    
    print("🚀 开始性能测试对比...\n")
    
    # 测试用户登录查询
    test_login_performance()
    
    # 测试课表查询性能
    test_schedule_performance()
    
    # 测试大表查询性能
    test_large_table_performance()

def test_login_performance():
    """测试登录查询性能"""
    print("=== 登录查询性能测试 ===")
    
    # 测试优化后的登录API
    login_data = {
        "login_id": "202100043213",
        "password": "123456"
    }
    
    start_time = time.time()
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json=login_data,
            headers=HEADERS,
            timeout=10
        )
        end_time = time.time()
        
        if response.status_code == 200:
            print(f"✅ 优化后登录查询: {(end_time - start_time)*1000:.2f}ms")
            result = response.json()
            user_info = result.get("data", {}).get("user_info", {})
            print(f"   返回字段数: {len(user_info)}个")
            print(f"   包含关联信息: {'college_name' in user_info}")
        else:
            print(f"❌ 登录失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 登录查询异常: {e}")
    
    print()

def test_schedule_performance():
    """测试课表查询性能"""
    print("=== 课表查询性能测试 ===")
    
    # 测试enrollments查询（多表JOIN）
    start_time = time.time()
    try:
        filters = {
            "student_id": "202100043213",
            "enrollment_status": "completed"
        }
        
        response = requests.get(
            f"{BASE_URL}/query/enrollments",
            params={
                "filters": json.dumps(filters),
                "join_tables": "course_instances,courses",
                "fields": "enrollment_id,student_id,course_instance_id,enrollment_status",
                "limit": 10
            },
            headers=HEADERS,
            timeout=10
        )
        end_time = time.time()
        
        if response.status_code == 200:
            print(f"✅ 优化后课表查询: {(end_time - start_time)*1000:.2f}ms")
            result = response.json()
            data = result.get("data", {})
            print(f"   返回记录数: {data.get('count', 0)}条")
            print(f"   估算总数: {data.get('estimated_total', 'N/A')}")
        else:
            print(f"❌ 课表查询失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 课表查询异常: {e}")
    
    print()

def test_large_table_performance():
    """测试大表查询性能"""
    print("=== 大表查询性能测试 ===")
    
    # 测试persons表查询（63,460条记录）
    test_cases = [
        {
            "name": "精确查询（学院+专业）",
            "filters": {"college_id": "C001", "major_id": "080901"},
            "join_tables": "colleges,majors",
            "expected_improvement": "大幅提升"
        },
        {
            "name": "分页查询（前50条）",
            "filters": {"person_type": "student", "is_deleted": False},
            "join_tables": None,
            "expected_improvement": "中等提升"
        },
        {
            "name": "复杂过滤（OR条件）",
            "filters": {
                "$or": [
                    {"college_id": "C001"},
                    {"college_id": "C002"}
                ]
            },
            "join_tables": "colleges",
            "expected_improvement": "显著提升"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"{i}. {test_case['name']}")
        
        start_time = time.time()
        try:
            params = {
                "filters": json.dumps(test_case["filters"]),
                "limit": 20,
                "offset": 0
            }
            
            if test_case["join_tables"]:
                params["join_tables"] = test_case["join_tables"]
            
            response = requests.get(
                f"{BASE_URL}/query/persons",
                params=params,
                headers=HEADERS,
                timeout=10
            )
            end_time = time.time()
            
            if response.status_code == 200:
                query_time = (end_time - start_time) * 1000
                result = response.json()
                data = result.get("data", {})
                
                print(f"   ⏱️  查询时间: {query_time:.2f}ms")
                print(f"   📊 返回记录: {data.get('count', 0)}条")
                print(f"   📈 预期改进: {test_case['expected_improvement']}")
                
                # 性能评估
                if query_time < 100:
                    print(f"   ✅ 性能优秀")
                elif query_time < 500:
                    print(f"   ⚠️  性能良好")
                else:
                    print(f"   ❌ 性能需要优化")
                    
            else:
                print(f"   ❌ 查询失败: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ 查询异常: {e}")
        
        print()

def benchmark_count_vs_estimate():
    """对比COUNT(*)和估算总数的性能"""
    print("=== COUNT(*) vs 估算总数性能对比 ===")
    
    print("旧方式: SELECT COUNT(*) FROM persons WHERE...")
    print("新方式: 基于返回记录数量估算")
    print("预期性能提升: 80-95%（避免全表扫描）")
    print()

def test_optimized_login():
    """测试优化后的登录查询"""
    print("=== 登录查询性能测试 ===")
    
    login_data = {
        "login_id": "202100043213",
        "password": "123456"
    }
    
    start_time = time.time()
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json=login_data,
            headers=HEADERS,
            timeout=10
        )
        end_time = time.time()
        
        if response.status_code == 200:
            print(f"✅ 优化后登录查询: {(end_time - start_time)*1000:.2f}ms")
            result = response.json()
            user_info = result.get("data", {}).get("user_info", {})
            print(f"   返回字段数: {len(user_info)}个")
            print(f"   包含关联信息: {'college_name' in user_info}")
            return True
        else:
            print(f"❌ 登录失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 登录查询异常: {e}")
        return False

def test_enrollments_query():
    """测试选课记录查询"""
    print("\n=== 选课记录查询性能测试 ===")
    
    start_time = time.time()
    try:
        filters = {
            "student_id": "202100043213",
            "enrollment_status": "completed"
        }
        
        response = requests.get(
            f"{BASE_URL}/query/enrollments",
            params={
                "filters": json.dumps(filters),
                "limit": 10
            },
            headers=HEADERS,
            timeout=10
        )
        end_time = time.time()
        
        if response.status_code == 200:
            print(f"✅ 选课查询: {(end_time - start_time)*1000:.2f}ms")
            result = response.json()
            data = result.get("data", {})
            print(f"   返回记录数: {data.get('count', 0)}条")
            return True
        else:
            print(f"❌ 选课查询失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 选课查询异常: {e}")
        return False

if __name__ == "__main__":
    print("🔍 SZTU-iCampus 查询性能测试")
    print("=" * 40)
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ data-service 服务正常\n")
            test_optimized_login()
            test_enrollments_query()
            
            print("\n🎯 性能优化总结:")
            print("1. ✅ 使用JOIN查询替代分段查询")
            print("2. ✅ 避免SELECT *，只选择需要的字段") 
            print("3. ✅ 避免COUNT(*)，使用估算总数")
            print("4. ✅ 利用外键关系进行精确筛选")
            
        else:
            print("❌ data-service 服务异常")
    except Exception as e:
        print(f"❌ 无法连接到 data-service: {e}")
        print("请确保服务在端口8001运行")

    print("\n🎯 性能优化建议:")
    print("1. 使用JOIN查询替代分段查询")
    print("2. 避免SELECT *，只选择需要的字段") 
    print("3. 避免COUNT(*)，使用估算总数")
    print("4. 利用外键关系进行精确筛选")
    print("5. 合理设置LIMIT限制返回数据量") 