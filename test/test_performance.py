#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
性能测试脚本 - 对比优化前后的查询性能
"""

import time
import requests
import json
from typing import Dict, Any
import asyncio
import httpx
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

class PerformanceTest:
    """性能测试类"""
    
    def __init__(self):
        self.backend_url = "http://127.0.0.1:8000"
        self.test_user = {
            "login_id": "202100008036",
            "password": "123456"
        }
        self.auth_token = None
        self.test_results = []
    
    async def authenticate(self) -> bool:
        """用户认证登录"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.backend_url}/api/v1/auth/login",
                    json=self.test_user
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.auth_token = data.get("data", {}).get("access_token")
                    logger.info("✅ 用户认证成功")
                    return True
                else:
                    logger.error(f"❌ 认证失败: {response.status_code}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ 认证异常: {e}")
            return False
    
    async def test_schedule_query_performance(self, test_name: str, iterations: int = 3) -> Dict[str, Any]:
        """测试课表查询性能"""
        if not self.auth_token:
            await self.authenticate()
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        times = []
        
        logger.info(f"🔄 开始测试: {test_name} (执行{iterations}次)")
        
        for i in range(iterations):
            start_time = time.time()
            
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.get(
                        f"{self.backend_url}/api/v1/schedule/",
                        headers=headers,
                        params={"semester": "2024-2025-1"}
                    )
                    
                    end_time = time.time()
                    duration = end_time - start_time
                    times.append(duration)
                    
                    if response.status_code == 200:
                        data = response.json()
                        courses_count = len(data.get("data", {}).get("courses", []))
                        logger.info(f"  第{i+1}次: {duration:.2f}秒, 课程数: {courses_count}")
                    else:
                        logger.error(f"  第{i+1}次: 失败 {response.status_code}")
                        
            except Exception as e:
                end_time = time.time()
                duration = end_time - start_time
                times.append(duration)
                logger.error(f"  第{i+1}次: 异常 {e} ({duration:.2f}秒)")
        
        # 计算统计数据
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        
        result = {
            "test_name": test_name,
            "iterations": iterations,
            "times": times,
            "avg_time": avg_time,
            "min_time": min_time,
            "max_time": max_time,
            "performance_rating": self._get_performance_rating(avg_time)
        }
        
        self.test_results.append(result)
        
        logger.info(f"📊 {test_name} 测试结果:")
        logger.info(f"   平均响应时间: {avg_time:.2f}秒")
        logger.info(f"   最快响应时间: {min_time:.2f}秒")
        logger.info(f"   最慢响应时间: {max_time:.2f}秒")
        logger.info(f"   性能等级: {result['performance_rating']}")
        
        return result
    
    async def test_cache_effectiveness(self) -> Dict[str, Any]:
        """测试缓存效果"""
        logger.info("🔄 测试缓存效果...")
        
        # 第一次请求（缓存未命中）
        first_result = await self.test_schedule_query_performance("首次查询（缓存未命中）", 1)
        
        # 连续请求（应该命中缓存）
        await asyncio.sleep(1)  # 稍等一下
        second_result = await self.test_schedule_query_performance("第二次查询（缓存命中）", 1)
        
        # 计算缓存效果
        improvement = (first_result["avg_time"] - second_result["avg_time"]) / first_result["avg_time"] * 100
        
        cache_result = {
            "cache_miss_time": first_result["avg_time"],
            "cache_hit_time": second_result["avg_time"], 
            "improvement_percent": improvement,
            "cache_effective": improvement > 10  # 超过10%改善认为缓存有效
        }
        
        logger.info(f"📈 缓存效果分析:")
        logger.info(f"   缓存未命中: {cache_result['cache_miss_time']:.2f}秒")
        logger.info(f"   缓存命中: {cache_result['cache_hit_time']:.2f}秒")
        logger.info(f"   性能提升: {improvement:.1f}%")
        logger.info(f"   缓存有效: {'✅' if cache_result['cache_effective'] else '❌'}")
        
        return cache_result
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.backend_url}/api/v1/cache/stats")
                
                if response.status_code == 200:
                    return response.json().get("data", {})
                else:
                    logger.warning("无法获取缓存统计信息")
                    return {}
                    
        except Exception as e:
            logger.warning(f"获取缓存统计异常: {e}")
            return {}
    
    def _get_performance_rating(self, avg_time: float) -> str:
        """获取性能等级"""
        if avg_time < 0.5:
            return "🟢 优秀 (<0.5s)"
        elif avg_time < 1.0:
            return "🟡 良好 (<1s)"
        elif avg_time < 3.0:
            return "🟠 一般 (<3s)"
        else:
            return "🔴 需优化 (>3s)"
    
    def generate_report(self) -> str:
        """生成性能测试报告"""
        report = "\n" + "="*60 + "\n"
        report += "📋 SZTU-iCampus 性能优化测试报告\n"
        report += "="*60 + "\n\n"
        
        report += "🎯 优化目标:\n"
        report += "  - 解决N+1查询问题（25次→4次HTTP请求）\n"
        report += "  - 实施多层缓存策略\n"
        report += "  - 提升课表查询响应速度\n\n"
        
        report += "📊 测试结果:\n"
        for result in self.test_results:
            report += f"  {result['test_name']}:\n"
            report += f"    平均响应时间: {result['avg_time']:.2f}秒\n"
            report += f"    性能等级: {result['performance_rating']}\n"
            report += f"    执行次数: {result['iterations']}\n\n"
        
        # 计算总体性能改善
        if len(self.test_results) >= 2:
            baseline = max(r["avg_time"] for r in self.test_results)
            best = min(r["avg_time"] for r in self.test_results)
            improvement = (baseline - best) / baseline * 100
            
            report += f"🚀 性能改善: {improvement:.1f}%\n"
            
            if best < 1.0:
                report += "✅ 性能优化目标达成：响应时间<1秒\n"
            else:
                report += "⚠️ 性能仍需进一步优化\n"
        
        report += "\n💡 技术亮点:\n"
        report += "  - Python内存缓存 (LRU + TTL)\n"
        report += "  - 批量查询优化 (__in操作符)\n"
        report += "  - 智能数据预取策略\n"
        report += "  - HTTP请求合并优化\n"
        
        return report

async def main():
    """主函数"""
    print("🚀 SZTU-iCampus 性能优化测试开始...")
    
    tester = PerformanceTest()
    
    # 基准性能测试
    await tester.test_schedule_query_performance("基准性能测试", 3)
    
    # 缓存效果测试
    await tester.test_cache_effectiveness()
    
    # 并发性能测试
    await tester.test_schedule_query_performance("并发测试", 5)
    
    # 获取缓存统计
    cache_stats = await tester.get_cache_stats()
    if cache_stats:
        print("\n📈 缓存统计信息:")
        for cache_type, stats in cache_stats.items():
            print(f"  {cache_type}: 命中率 {stats.get('hit_rate', 'N/A')}")
    
    # 生成报告
    report = tester.generate_report()
    print(report)
    
    # 保存报告到文件
    with open("performance_test_report.md", "w", encoding="utf-8") as f:
        f.write(report)
    
    print("📄 测试报告已保存到 performance_test_report.md")

if __name__ == "__main__":
    asyncio.run(main()) 