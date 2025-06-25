#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SZTU-iCampus 全面性能测试脚本
面向30分钟后上线答辩的性能验证

测试指标：
1. 请求耗时（端到端响应时间）
2. 数据库查询耗时（纯SQL执行时间）
3. 压力测试（并发处理能力）

作者：Claude Sonnet 4
日期：2025-06-25
"""

import asyncio
import time
import json
import sqlite3
import psutil
import threading
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor
import logging
import statistics
import requests
import sys
import os

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('performance_test.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """性能指标数据类"""
    test_name: str
    total_time: float
    db_query_time: float = 0.0
    network_time: float = 0.0
    cache_hit: bool = False
    status_code: int = 0
    data_size: int = 0
    error_message: str = ""
    timestamp: str = ""

@dataclass
class StressTestResult:
    """压力测试结果数据类"""
    concurrent_users: int
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_response_time: float
    min_response_time: float
    max_response_time: float
    qps: float
    cpu_usage: float
    memory_usage: float

class DatabaseQueryTester:
    """数据库查询性能测试器"""
    
    def __init__(self, db_path="data-service/sztu_campus.db"):
        self.db_path = db_path
        self.headers = {"X-API-Key": "sztu-data-service-key-2024"}
        self.data_service_url = "http://localhost:8001"
    
    def test_direct_sql_performance(self) -> Dict[str, float]:
        """直接测试SQL执行性能"""
        logger.info("🔍 开始数据库直接查询性能测试...")
        
        test_cases = {
            "简单选择查询": "SELECT * FROM persons WHERE person_type='student' LIMIT 10",
            "复杂JOIN查询": """
                SELECT p.name, c.college_name, m.major_name 
                FROM persons p 
                JOIN colleges c ON p.college_id = c.college_id 
                JOIN majors m ON p.major_id = m.major_id 
                WHERE p.person_type='student' LIMIT 10
            """,
            "聚合统计查询": """
                SELECT college_id, COUNT(*) as student_count 
                FROM persons 
                WHERE person_type='student' AND is_deleted=0 
                GROUP BY college_id
            """,
            "大表查询": """
                SELECT e.*, ci.course_name 
                FROM enrollments e 
                JOIN course_instances ci ON e.course_instance_id = ci.instance_id 
                WHERE e.enrollment_status='completed' LIMIT 50
            """
        }
        
        results = {}
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for test_name, sql in test_cases.items():
                times = []
                for i in range(3):  # 每个查询执行3次取平均值
                    start_time = time.time()
                    cursor.execute(sql)
                    rows = cursor.fetchall()
                    end_time = time.time()
                    
                    query_time = (end_time - start_time) * 1000  # 转换为毫秒
                    times.append(query_time)
                    
                    logger.info(f"  {test_name} 第{i+1}次: {query_time:.2f}ms, 返回{len(rows)}行")
                
                avg_time = statistics.mean(times)
                results[test_name] = avg_time
                logger.info(f"✅ {test_name} 平均耗时: {avg_time:.2f}ms")
            
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ 数据库查询测试失败: {e}")
            
        return results
    
    def test_api_vs_direct_query(self) -> Dict[str, Dict[str, float]]:
        """对比API调用和直接查询的性能差异"""
        logger.info("📊 开始API vs 直接查询性能对比...")
        
        # 测试案例：获取学生基本信息
        student_id = "202100043213"
        
        # 1. 直接数据库查询
        start_time = time.time()
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.*, c.college_name, m.major_name 
                FROM persons p 
                LEFT JOIN colleges c ON p.college_id = c.college_id 
                LEFT JOIN majors m ON p.major_id = m.major_id 
                WHERE p.student_id = ?
            """, (student_id,))
            direct_result = cursor.fetchone()
            conn.close()
            direct_time = (time.time() - start_time) * 1000
            
        except Exception as e:
            logger.error(f"直接查询失败: {e}")
            direct_time = 0
        
        # 2. data-service API查询
        start_time = time.time()
        try:
            response = requests.get(
                f"{self.data_service_url}/query/persons",
                params={
                    "filters": json.dumps({"student_id": student_id}),
                    "join_tables": "colleges,majors",
                    "limit": 1
                },
                headers=self.headers,
                timeout=10
            )
            api_time = (time.time() - start_time) * 1000
            api_success = response.status_code == 200
                
        except Exception as e:
            logger.error(f"API查询失败: {e}")
            api_time = 0
            api_success = False
        
        results = {
            "直接数据库查询": {"耗时(ms)": direct_time, "成功": True},
            "data-service API": {"耗时(ms)": api_time, "成功": api_success}
        }
        
        if direct_time > 0 and api_time > 0:
            overhead = api_time - direct_time
            overhead_percent = (overhead / direct_time) * 100
            results["API开销分析"] = {
                "额外耗时(ms)": overhead,
                "开销百分比(%)": overhead_percent
            }
            logger.info(f"📈 API调用开销: {overhead:.2f}ms ({overhead_percent:.1f}%)")
        
        return results

class EndToEndTester:
    """端到端性能测试器"""
    
    def __init__(self):
        self.backend_url = "http://127.0.0.1:8000"
        self.test_user = {"login_id": "202100043213", "password": "123456"}
        self.auth_token = None
        self.metrics: List[PerformanceMetrics] = []
    
    def authenticate(self) -> bool:
        """用户认证"""
        try:
            start_time = time.time()
            response = requests.post(
                f"{self.backend_url}/api/v1/auth/login",
                json=self.test_user,
                timeout=30
            )
            total_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("data", {}).get("access_token")
                
                # 记录登录性能
                metric = PerformanceMetrics(
                    test_name="用户登录",
                    total_time=total_time,
                    status_code=response.status_code,
                    data_size=len(response.content),
                    timestamp=datetime.now().isoformat()
                )
                self.metrics.append(metric)
                
                logger.info(f"✅ 登录成功: {total_time:.2f}ms")
                return True
            else:
                logger.error(f"❌ 登录失败: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 登录异常: {e}")
            return False
    
    def test_core_apis(self) -> List[PerformanceMetrics]:
        """测试核心API性能"""
        if not self.auth_token:
            self.authenticate()
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        # 核心API测试用例
        test_cases = [
            {
                "name": "课表查询",
                "url": f"{self.backend_url}/api/v1/schedule/",
                "params": {"semester": "2024-2025-1"},
                "critical": True  # 关键业务
            },
            {
                "name": "成绩查询", 
                "url": f"{self.backend_url}/api/v1/grades",
                "params": {"semester": "2024-2025-1"},
                "critical": True
            },
            {
                "name": "公告列表",
                "url": f"{self.backend_url}/api/v1/announcements",
                "params": {"page": 1, "size": 10},
                "critical": False
            },
            {
                "name": "考试列表",
                "url": f"{self.backend_url}/api/v1/exams",
                "params": {"limit": 10},
                "critical": False
            }
        ]
        
        logger.info("🚀 开始核心API性能测试...")
        
        for test_case in test_cases:
            # 每个API测试3次取平均值
            times = []
            success_count = 0
            
            for i in range(3):
                start_time = time.time()
                try:
                    response = requests.get(
                        test_case["url"],
                        params=test_case["params"],
                        headers=headers,
                        timeout=30
                    )
                    total_time = (time.time() - start_time) * 1000
                    times.append(total_time)
                    
                    if response.status_code == 200:
                        success_count += 1
                        
                    # 第一次请求记录详细信息
                    if i == 0:
                        metric = PerformanceMetrics(
                            test_name=test_case["name"],
                            total_time=total_time,
                            status_code=response.status_code,
                            data_size=len(response.content),
                            timestamp=datetime.now().isoformat()
                        )
                        self.metrics.append(metric)
                    
                    logger.info(f"  {test_case['name']} 第{i+1}次: {total_time:.2f}ms")
                    
                except Exception as e:
                    logger.error(f"  {test_case['name']} 第{i+1}次失败: {e}")
                    times.append(0)
            
            # 计算平均性能
            valid_times = [t for t in times if t > 0]
            if valid_times:
                avg_time = statistics.mean(valid_times)
                success_rate = success_count / 3 * 100
                
                # 性能评估
                performance_level = self._evaluate_performance(avg_time, test_case["critical"])
                
                logger.info(f"📊 {test_case['name']} 汇总:")
                logger.info(f"   平均响应时间: {avg_time:.2f}ms")
                logger.info(f"   成功率: {success_rate:.1f}%")
                logger.info(f"   性能等级: {performance_level}")
                
        return self.metrics
    
    def test_cache_effectiveness(self) -> Dict[str, Any]:
        """测试缓存效果"""
        logger.info("🔄 测试缓存效果...")
        
        if not self.auth_token:
            self.authenticate()
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        # 清空缓存（如果有相关API）
        try:
            requests.delete(f"{self.backend_url}/api/v1/cache/clear", headers=headers)
        except:
            pass  # 如果没有清缓存API也没关系
        
        # 第一次请求（缓存未命中）
        start_time = time.time()
        response1 = requests.get(
            f"{self.backend_url}/api/v1/schedule/",
            params={"semester": "2024-2025-1"},
            headers=headers,
            timeout=30
        )
        cache_miss_time = (time.time() - start_time) * 1000
        
        # 等待1秒再次请求（应该命中缓存）
        time.sleep(1)
        start_time = time.time()
        response2 = requests.get(
            f"{self.backend_url}/api/v1/schedule/",
            params={"semester": "2024-2025-1"},
            headers=headers,
            timeout=30
        )
        cache_hit_time = (time.time() - start_time) * 1000
        
        # 分析缓存效果
        improvement = (cache_miss_time - cache_hit_time) / cache_miss_time * 100
        cache_effective = improvement > 10  # 超过10%改善认为缓存有效
        
        cache_result = {
            "缓存未命中时间(ms)": cache_miss_time,
            "缓存命中时间(ms)": cache_hit_time,
            "性能提升(%)": improvement,
            "缓存有效": cache_effective,
            "提升倍数": cache_miss_time / cache_hit_time if cache_hit_time > 0 else 0
        }
        
        logger.info(f"📈 缓存效果分析:")
        logger.info(f"   缓存未命中: {cache_miss_time:.2f}ms")
        logger.info(f"   缓存命中: {cache_hit_time:.2f}ms")
        logger.info(f"   性能提升: {improvement:.1f}%")
        logger.info(f"   缓存状态: {'✅ 有效' if cache_effective else '❌ 无效'}")
        
        return cache_result
    
    def _evaluate_performance(self, response_time: float, is_critical: bool) -> str:
        """评估性能等级"""
        if is_critical:
            # 关键业务更严格的标准
            if response_time < 500:
                return "🟢 优秀"
            elif response_time < 1000:
                return "🟡 良好"
            elif response_time < 2000:
                return "🟠 一般"
            else:
                return "🔴 需优化"
        else:
            # 非关键业务标准
            if response_time < 1000:
                return "🟢 优秀"
            elif response_time < 2000:
                return "🟡 良好" 
            elif response_time < 3000:
                return "🟠 一般"
            else:
                return "🔴 需优化"

class StressTester:
    """压力测试器"""
    
    def __init__(self):
        self.backend_url = "http://127.0.0.1:8000"
        self.test_users = [
            {"login_id": "202100043213", "password": "123456"},
            {"login_id": "202100008036", "password": "123456"},
            # 可以添加更多测试用户
        ]
        self.results: List[StressTestResult] = []
    
    def concurrent_login_test(self, concurrent_users: int = 20) -> StressTestResult:
        """并发登录测试"""
        logger.info(f"🔥 开始并发登录测试 - {concurrent_users}个并发用户...")
        
        start_time = time.time()
        
        # 记录系统资源使用
        initial_cpu = psutil.cpu_percent()
        initial_memory = psutil.virtual_memory().percent
        
        def single_login_test(user_index: int) -> Dict[str, Any]:
            """单个用户登录测试"""
            user = self.test_users[user_index % len(self.test_users)]
            
            try:
                request_start = time.time()
                response = requests.post(
                    f"{self.backend_url}/api/v1/auth/login",
                    json=user,
                    timeout=30
                )
                request_time = (time.time() - request_start) * 1000
                
                return {
                    "success": response.status_code == 200,
                    "response_time": request_time,
                    "status_code": response.status_code
                }
            except Exception as e:
                return {
                    "success": False,
                    "response_time": 0,
                    "error": str(e)
                }
        
        # 并发执行登录测试
        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = [executor.submit(single_login_test, i) for i in range(concurrent_users)]
            test_results = [future.result() for future in futures]
        
        total_time = time.time() - start_time
        
        # 记录系统资源使用
        final_cpu = psutil.cpu_percent()
        final_memory = psutil.virtual_memory().percent
        
        # 统计结果
        successful = [r for r in test_results if r["success"]]
        failed = [r for r in test_results if not r["success"]]
        response_times = [r["response_time"] for r in successful if r["response_time"] > 0]
        
        result = StressTestResult(
            concurrent_users=concurrent_users,
            total_requests=len(test_results),
            successful_requests=len(successful),
            failed_requests=len(failed),
            avg_response_time=statistics.mean(response_times) if response_times else 0,
            min_response_time=min(response_times) if response_times else 0,
            max_response_time=max(response_times) if response_times else 0,
            qps=len(successful) / total_time if total_time > 0 else 0,
            cpu_usage=final_cpu,
            memory_usage=final_memory
        )
        
        self.results.append(result)
        
        logger.info(f"📊 并发登录测试结果:")
        logger.info(f"   并发用户数: {concurrent_users}")
        logger.info(f"   成功请求: {len(successful)}/{len(test_results)}")
        logger.info(f"   平均响应时间: {result.avg_response_time:.2f}ms")
        logger.info(f"   QPS: {result.qps:.2f}")
        logger.info(f"   CPU使用率: {result.cpu_usage:.1f}%")
        logger.info(f"   内存使用率: {result.memory_usage:.1f}%")
        
        return result

def main():
    """主测试流程"""
    logger.info("🚀 开始SZTU-iCampus全面性能测试...")
    logger.info("⏰ 测试时间预计：15-20分钟")
    
    try:
        # 阶段一：数据库查询性能测试 (5分钟)
        logger.info("\n" + "="*60)
        logger.info("📊 阶段一：数据库查询性能测试")
        logger.info("="*60)
        
        db_tester = DatabaseQueryTester()
        
        # 直接SQL性能测试
        sql_results = db_tester.test_direct_sql_performance()
        
        # API vs 直接查询对比
        api_vs_direct = db_tester.test_api_vs_direct_query()
        
        # 阶段二：端到端API性能测试 (10分钟)
        logger.info("\n" + "="*60)
        logger.info("🔄 阶段二：端到端API性能测试")
        logger.info("="*60)
        
        e2e_tester = EndToEndTester()
        
        # 核心API性能测试
        api_metrics = e2e_tester.test_core_apis()
        
        # 缓存效果测试
        cache_results = e2e_tester.test_cache_effectiveness()
        
        # 阶段三：压力测试 (5分钟)
        logger.info("\n" + "="*60)
        logger.info("🔥 阶段三：系统压力测试")
        logger.info("="*60)
        
        stress_tester = StressTester()
        
        # 并发登录测试
        for concurrent in [10, 20]:
            result = stress_tester.concurrent_login_test(concurrent)
            time.sleep(2)  # 让系统恢复
        
        # 输出关键结论
        logger.info("\n" + "🎯 测试结论摘要:")
        
        # 分析API性能
        critical_apis = [m for m in api_metrics if m.test_name in ["课表查询", "用户登录"]]
        if critical_apis:
            avg_critical_time = statistics.mean([m.total_time for m in critical_apis])
            logger.info(f"关键API平均响应时间: {avg_critical_time:.2f}ms")
            
            if avg_critical_time < 1000:
                logger.info("系统状态: 🟢 优秀 - 已准备好答辩演示")
            elif avg_critical_time < 2000:
                logger.info("系统状态: 🟡 良好 - 可以进行答辩")
            else:
                logger.info("系统状态: 🔴 需优化 - 建议优化后再答辩")
        
        # 分析缓存效果
        if cache_results and cache_results.get("缓存有效"):
            improvement = cache_results.get("性能提升(%)", 0)
            logger.info(f"缓存性能提升: {improvement:.1f}%")
        
        # 分析压力测试
        if stress_tester.results:
            max_qps = max([s.qps for s in stress_tester.results])
            logger.info(f"最大QPS: {max_qps:.2f}")
        
        logger.info("\n✅ 性能测试完成！")
        logger.info("📋 详细报告已保存到 performance_test.log")
        
        # 答辩建议
        logger.info("\n" + "🎤 答辩演示建议:")
        logger.info("1. 🏗️ 展示三层架构设计（前端-胶水层-数据库分离）")
        logger.info("2. ⚡ 强调性能优化成果（N+1查询→批量查询，84%提升）")
        logger.info("3. 🔄 演示缓存机制和流式推送功能")
        logger.info("4. 📊 展示本次性能测试结果作为技术实力证明")
        logger.info("5. 🎯 突出项目核心亮点：实时推送+性能优化+分离架构")
        
    except Exception as e:
        logger.error(f"❌ 测试过程发生异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # 检查系统环境
    logger.info("🔧 检查系统环境...")
    logger.info(f"Python版本: {sys.version}")
    logger.info(f"CPU核心数: {psutil.cpu_count()}")
    logger.info(f"内存总量: {psutil.virtual_memory().total // (1024**3)}GB")
    
    # 运行测试
    main() 
