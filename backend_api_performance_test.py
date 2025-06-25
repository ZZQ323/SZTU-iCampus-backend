#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
后端API性能专项测试
重点测试：人员表格查询、登录过程时长、各API端点性能

日期：2025-06-25
"""

import asyncio
import aiohttp
import time
import json
import statistics
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import random

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('backend_api_test.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BackendAPIPerformanceTester:
    """后端API专项性能测试"""
    
    def __init__(self):
        self.backend_url = "http://127.0.0.1:8000"
        self.data_service_url = "http://127.0.0.1:8001"
        self.api_key = "sztu-data-service-key-2024"
        self.session = None
        self.test_accounts = []  # 存储测试账号
        
    async def __aenter__(self):
        """异步上下文管理器进入"""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器退出"""
        if self.session:
            await self.session.close()
    
    async def prepare_test_accounts(self) -> List[Dict[str, Any]]:
        """准备测试账号 - 使用数据库中的真实账号"""
        # 直接使用从数据库查询到的真实账号信息
        self.test_accounts = [
            # 管理员账号
            {"login_id": "2025000001", "password": "Admin001HP1dbd10", "person_type": "admin", "name": "何平", "person_id": "P2025063441"},
            {"login_id": "2025000002", "password": "Admin002LGQ17e222", "person_type": "admin", "name": "梁国强", "person_id": "P2025063442"},
            {"login_id": "2025000003", "password": "Admin003YGQf87252", "person_type": "admin", "name": "于国强", "person_id": "P2025063443"},
            {"login_id": "2025000004", "password": "Admin004LQfdc75c", "person_type": "admin", "name": "罗强", "person_id": "P2025063444"},
            {"login_id": "2025000005", "password": "Admin005GJG074ca3", "person_type": "admin", "name": "郭建国", "person_id": "P2025063445"},
            
            # 学生账号
            {"login_id": "202100000001", "password": "000001Ty901StuwA", "person_type": "student", "name": "唐勇", "person_id": "P2025000001"},
            {"login_id": "202100000002", "password": "000002Gw901StuK6", "person_type": "student", "name": "郭文", "person_id": "P2025000002"},
            {"login_id": "202100000003", "password": "000003Zp901Stul1", "person_type": "student", "name": "周平", "person_id": "P2025000003"},
            {"login_id": "202100000004", "password": "000004Hq901StuHz", "person_type": "student", "name": "黄强", "person_id": "P2025000004"},
            {"login_id": "202100000005", "password": "000005Xl901Stu1v", "person_type": "student", "name": "徐丽", "person_id": "P2025000005"},
            {"login_id": "202100000006", "password": "000006Sxl901StuO", "person_type": "student", "name": "宋秀兰", "person_id": "P2025000006"},
            {"login_id": "202100000007", "password": "000007Lh901Stu7v", "person_type": "student", "name": "梁华", "person_id": "P2025000007"},
            {"login_id": "202100000008", "password": "000008Zx901StuEB", "person_type": "student", "name": "郑霞", "person_id": "P2025000008"},
            {"login_id": "202100000009", "password": "000009Xg901StuFT", "person_type": "student", "name": "徐刚", "person_id": "P2025000009"},
            {"login_id": "202100000010", "password": "000010Ly901Stu8k", "person_type": "student", "name": "林洋", "person_id": "P2025000010"},
            
            # 教师账号
            {"login_id": "2025001001", "password": "1001GaojSztu2024", "person_type": "teacher", "name": "高军", "person_id": "P2025062401"},
            {"login_id": "2025001002", "password": "1002ChenSztu2024", "person_type": "teacher", "name": "陈建华", "person_id": "P2025062402"},
            {"login_id": "2025001003", "password": "1003SungSztu2024", "person_type": "teacher", "name": "孙国强", "person_id": "P2025062403"},
            {"login_id": "2025001004", "password": "1004XiaoSztu2024", "person_type": "teacher", "name": "萧杰", "person_id": "P2025062404"},
            {"login_id": "2025001005", "password": "1005FengSztu2024", "person_type": "teacher", "name": "冯洋", "person_id": "P2025062405"},
        ]
        
        logger.info(f"✅ 准备了 {len(self.test_accounts)} 个真实测试账号")
        return self.test_accounts
    
    async def test_real_login_query_performance(self) -> Dict[str, Any]:
        """测试真实登录验证查询性能 - 完全模拟登录时的4表JOIN查询"""
        logger.info("🧪 开始测试真实登录验证查询性能...")
        
        # 确保有测试账号
        if not self.test_accounts:
            await self.prepare_test_accounts()
        
        if not self.test_accounts:
            return {"error": "没有可用的测试账号"}
        
        results = []
        test_count = min(50, len(self.test_accounts))  # 测试50次或所有账号
        
        for i in range(test_count):
            account = random.choice(self.test_accounts)
            
            try:
                # 构建与登录时完全相同的查询条件
                auth_query_data = {
                    "login_id": account["login_id"],
                    "password": account["password"]
                }
                
                headers = {"X-API-Key": self.api_key, "Content-Type": "application/json"}
                start_time = time.time()
                
                # 直接调用data-service的auth/login端点（与登录逻辑完全一致）
                async with self.session.post(
                    f"{self.data_service_url}/auth/login",
                    headers=headers,
                    json=auth_query_data
                ) as response:
                    end_time = time.time()
                    response_time = (end_time - start_time) * 1000
                    
                    if response.status == 200:
                        result_data = await response.json()
                        user_info = result_data.get("data", {}).get("user_info", {})
                        
                        # 验证返回的完整信息（模拟真实登录验证）
                        expected_fields = [
                            "person_id", "person_type", "name", "phone", "email",
                            "academic_status", "employment_status", "college_name", 
                            "major_name", "class_name", "department_name"
                        ]
                        
                        field_count = sum(1 for field in expected_fields if user_info.get(field))
                        
                        results.append({
                            "response_time": response_time,
                            "status": "success",
                            "person_type": user_info.get("person_type", "unknown"),
                            "fields_returned": field_count,
                            "has_college_info": bool(user_info.get("college_name")),
                            "has_major_info": bool(user_info.get("major_name")),
                            "has_class_info": bool(user_info.get("class_name")),
                            "has_department_info": bool(user_info.get("department_name")),
                            "login_id": account["login_id"],
                            "response_size": len(json.dumps(user_info).encode('utf-8'))
                        })
                        
                        logger.info(f"✅ 真实登录查询 {i+1}/{test_count}: {response_time:.2f}ms "
                                  f"- {user_info.get('person_type')} {user_info.get('name', '')} "
                                  f"- 字段: {field_count}/{len(expected_fields)}")
                    else:
                        results.append({
                            "response_time": response_time,
                            "status": "failed",
                            "error": f"HTTP {response.status}"
                        })
                        logger.warning(f"⚠️ 真实登录查询失败 {i+1}: HTTP {response.status}")
                
            except Exception as e:
                results.append({
                    "response_time": 0,
                    "status": "error",
                    "error": str(e)
                })
                logger.error(f"❌ 真实登录查询异常 {i+1}: {e}")
            
            # 控制请求频率
            await asyncio.sleep(0.1)
        
        # 统计分析
        successful_results = [r for r in results if r["status"] == "success"]
        
        if successful_results:
            response_times = [r["response_time"] for r in successful_results]
            
            stats = {
                "test_name": "真实登录验证查询性能测试",
                "description": "完全模拟登录时的4表JOIN查询(persons+colleges+majors+classes+departments)",
                "total_tests": len(results),
                "successful_tests": len(successful_results),
                "success_rate": f"{len(successful_results)/len(results)*100:.1f}%",
                "avg_response_time": f"{statistics.mean(response_times):.2f}ms",
                "min_response_time": f"{min(response_times):.2f}ms",
                "max_response_time": f"{max(response_times):.2f}ms",
                "median_response_time": f"{statistics.median(response_times):.2f}ms",
                "p95_response_time": f"{sorted(response_times)[int(len(response_times)*0.95)]:.2f}ms",
                "avg_fields_returned": f"{statistics.mean([r['fields_returned'] for r in successful_results]):.1f}",
                "avg_response_size": f"{statistics.mean([r['response_size'] for r in successful_results]):.0f} bytes",
                "join_completeness": {
                    "college_info_rate": f"{sum(1 for r in successful_results if r['has_college_info'])/len(successful_results)*100:.1f}%",
                    "major_info_rate": f"{sum(1 for r in successful_results if r['has_major_info'])/len(successful_results)*100:.1f}%",
                    "class_info_rate": f"{sum(1 for r in successful_results if r['has_class_info'])/len(successful_results)*100:.1f}%",
                    "department_info_rate": f"{sum(1 for r in successful_results if r['has_department_info'])/len(successful_results)*100:.1f}%"
                },
                "person_type_distribution": {
                    "student": sum(1 for r in successful_results if r.get('person_type') == 'student'),
                    "teacher": sum(1 for r in successful_results if r.get('person_type') == 'teacher'),
                    "admin": sum(1 for r in successful_results if r.get('person_type') == 'admin'),
                    "other": sum(1 for r in successful_results if r.get('person_type') not in ['student', 'teacher', 'admin'])
                }
            }
            
            # 性能评级
            avg_time = statistics.mean(response_times)
            if avg_time < 100:
                performance_grade = "🟢 优秀"
            elif avg_time < 300:
                performance_grade = "🟡 良好"
            elif avg_time < 500:
                performance_grade = "🟠 一般"
            else:
                performance_grade = "🔴 需优化"
            
            stats["performance_grade"] = performance_grade
            
            return stats
        else:
            return {"error": "所有查询都失败了"}
    
    async def test_login_stress_performance(self, duration_seconds: int = 60) -> Dict[str, Any]:
        """登录压力测试 - 模拟高并发登录场景"""
        logger.info(f"🚀 开始登录压力测试 - 持续 {duration_seconds} 秒...")
        
        # 确保有测试账号
        if not self.test_accounts:
            await self.prepare_test_accounts()
        
        if not self.test_accounts:
            return {"error": "没有可用的测试账号"}
        
        results = []
        start_time = time.time()
        end_time = start_time + duration_seconds
        
        # 并发任务列表
        tasks = []
        
        async def single_login_test():
            """单次登录测试"""
            account = random.choice(self.test_accounts)
            
            try:
                login_data = {
                    "login_id": account["login_id"],
                    "password": account["password"]
                }
                
                request_start = time.time()
                
                # 通过胶水层进行登录（更真实的测试）
                async with self.session.post(
                    f"{self.backend_url}/api/v1/auth/login",
                    json=login_data
                ) as response:
                    request_end = time.time()
                    response_time = (request_end - request_start) * 1000
                    
                    result = {
                        "response_time": response_time,
                        "timestamp": request_start,
                        "account_type": account["person_type"],
                        "login_id": account["login_id"]
                    }
                    
                    if response.status == 200:
                        response_data = await response.json()
                        if response_data.get("status") == "success":
                            result["status"] = "success"
                            result["token_received"] = bool(response_data.get("data", {}).get("access_token"))
                            result["user_info_complete"] = bool(response_data.get("data", {}).get("user_info"))
                        else:
                            result["status"] = "failed"
                            result["error"] = response_data.get("message", "登录失败")
                    else:
                        result["status"] = "failed"
                        result["error"] = f"HTTP {response.status}"
                    
                    return result
                    
            except Exception as e:
                return {
                    "response_time": 0,
                    "timestamp": time.time(),
                    "status": "error",
                    "error": str(e),
                    "account_type": account["person_type"],
                    "login_id": account["login_id"]
                }
        
        # 执行压力测试
        test_count = 0
        while time.time() < end_time:
            # 每秒发送5-10个并发登录请求
            batch_size = random.randint(5, 10)
            
            # 创建并发任务
            batch_tasks = [single_login_test() for _ in range(batch_size)]
            
            # 执行批次
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            # 收集结果
            for result in batch_results:
                if isinstance(result, dict):
                    results.append(result)
                    test_count += 1
            
            logger.info(f"🔄 压力测试进行中... 已完成 {test_count} 次登录尝试")
            
            # 控制频率，避免过载
            await asyncio.sleep(0.2)
        
        # 统计分析
        successful_results = [r for r in results if r.get("status") == "success"]
        failed_results = [r for r in results if r.get("status") == "failed"]
        error_results = [r for r in results if r.get("status") == "error"]
        
        if results:
            response_times = [r["response_time"] for r in successful_results if r["response_time"] > 0]
            
            # 时间序列分析
            time_series = []
            for i in range(0, duration_seconds, 10):  # 每10秒统计一次
                window_start = start_time + i
                window_end = window_start + 10
                window_results = [r for r in results 
                                if window_start <= r["timestamp"] < window_end]
                
                if window_results:
                    window_success = [r for r in window_results if r.get("status") == "success"]
                    time_series.append({
                        "time_window": f"{i}-{i+10}s",
                        "total_requests": len(window_results),
                        "successful_requests": len(window_success),
                        "success_rate": f"{len(window_success)/len(window_results)*100:.1f}%",
                        "avg_response_time": f"{statistics.mean([r['response_time'] for r in window_success]):.2f}ms" if window_success else "N/A"
                    })
            
            stats = {
                "test_name": "登录压力测试",
                "description": f"在 {duration_seconds} 秒内进行高并发登录测试",
                "test_duration": f"{duration_seconds}s",
                "total_requests": len(results),
                "successful_requests": len(successful_results),
                "failed_requests": len(failed_results),
                "error_requests": len(error_results),
                "overall_success_rate": f"{len(successful_results)/len(results)*100:.1f}%",
                "requests_per_second": f"{len(results)/duration_seconds:.1f}",
                "successful_rps": f"{len(successful_results)/duration_seconds:.1f}",
                "performance_metrics": {
                    "avg_response_time": f"{statistics.mean(response_times):.2f}ms" if response_times else "N/A",
                    "min_response_time": f"{min(response_times):.2f}ms" if response_times else "N/A",
                    "max_response_time": f"{max(response_times):.2f}ms" if response_times else "N/A",
                    "median_response_time": f"{statistics.median(response_times):.2f}ms" if response_times else "N/A",
                    "p95_response_time": f"{sorted(response_times)[int(len(response_times)*0.95)]:.2f}ms" if response_times else "N/A",
                    "p99_response_time": f"{sorted(response_times)[int(len(response_times)*0.99)]:.2f}ms" if response_times else "N/A",
                },
                "account_type_performance": {},
                "time_series_analysis": time_series
            }
            
            # 按账号类型分析性能
            for account_type in ["student", "teacher", "admin"]:
                type_results = [r for r in successful_results if r.get("account_type") == account_type]
                if type_results:
                    type_times = [r["response_time"] for r in type_results]
                    stats["account_type_performance"][account_type] = {
                        "count": len(type_results),
                        "avg_response_time": f"{statistics.mean(type_times):.2f}ms",
                        "success_rate": f"{len(type_results)/len([r for r in results if r.get('account_type') == account_type])*100:.1f}%"
                    }
            
            # 压力测试评级
            overall_success_rate = len(successful_results)/len(results)*100
            avg_response_time = statistics.mean(response_times) if response_times else float('inf')
            
            if overall_success_rate >= 95 and avg_response_time < 200:
                stress_grade = "🟢 优秀 - 系统能很好地处理高并发登录"
            elif overall_success_rate >= 90 and avg_response_time < 500:
                stress_grade = "🟡 良好 - 系统能较好地处理并发登录"
            elif overall_success_rate >= 80:
                stress_grade = "🟠 一般 - 系统在高负载下有一定压力"
            else:
                stress_grade = "🔴 需优化 - 系统难以承受高并发登录"
            
            stats["stress_grade"] = stress_grade
            
            return stats
        else:
            return {"error": "压力测试中没有获得任何结果"}
    
    async def test_backend_api_comprehensive(self) -> Dict[str, Any]:
        """后端API综合性能测试"""
        logger.info("🔬 开始后端API综合性能测试...")
        
        # 确保有认证信息
        if not self.test_accounts:
            await self.prepare_test_accounts()
        
        # 准备认证token
        auth_token = None
        if self.test_accounts:
            admin_account = next((acc for acc in self.test_accounts if acc["person_type"] == "admin"), None)
            if admin_account:
                try:
                    async with self.session.post(
                        f"{self.backend_url}/api/v1/auth/login",
                        json={"login_id": admin_account["login_id"], "password": admin_account["password"]}
                    ) as response:
                        if response.status == 200:
                            result = await response.json()
                            auth_token = result.get("data", {}).get("access_token")
                except Exception as e:
                    logger.warning(f"获取认证token失败: {e}")
        
        headers = {}
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"
        
        # API测试配置 - 使用真实的学生ID
        test_student_id = "202100000001"  # 使用真实的学生学号
        api_tests = [
            {
                "name": "公告列表",
                "url": f"{self.backend_url}/api/v1/announcements",
                "method": "GET",
                "params": {"page": 1, "size": 10}
            },
            {
                "name": "课表查询",
                "url": f"{self.backend_url}/api/v1/schedule/student/{test_student_id}",
                "method": "GET",
                "params": {"semester": "2024-2025-1"}
            },
            {
                "name": "成绩查询", 
                "url": f"{self.backend_url}/api/v1/grades/student/{test_student_id}",
                "method": "GET",
                "params": {"semester": "2024-2025-1"}
            },
            {
                "name": "考试列表",
                "url": f"{self.backend_url}/api/v1/exams",
                "method": "GET",
                "params": {"page": 1, "size": 10}
            },
            {
                "name": "考试统计",
                "url": f"{self.backend_url}/api/v1/exams/statistics",
                "method": "GET"
            }
        ]
        
        all_results = {}
        
        for api_test in api_tests:
            logger.info(f"🧪 测试 {api_test['name']} API...")
            
            test_results = []
            test_count = 20  # 每个API测试20次
            
            for i in range(test_count):
                try:
                    start_time = time.time()
                    
                    async with self.session.request(
                        api_test["method"],
                        api_test["url"],
                        headers=headers,
                        params=api_test.get("params", {})
                    ) as response:
                        end_time = time.time()
                        response_time = (end_time - start_time) * 1000
                        
                        result = {
                            "response_time": response_time,
                            "status_code": response.status
                        }
                        
                        if response.status == 200:
                            response_data = await response.json()
                            result["status"] = "success"
                            result["data_size"] = len(json.dumps(response_data).encode('utf-8'))
                            
                            # 检查响应数据质量
                            if response_data.get("status") == "success":
                                data = response_data.get("data")
                                if isinstance(data, list):
                                    result["records_count"] = len(data)
                                elif isinstance(data, dict):
                                    result["records_count"] = len(data.get("records", []))
                        else:
                            result["status"] = "failed"
                        
                        test_results.append(result)
                        
                except Exception as e:
                    test_results.append({
                        "response_time": 0,
                        "status": "error",
                        "error": str(e)
                    })
                
                await asyncio.sleep(0.05)  # 控制频率
            
            # 统计API测试结果
            successful_results = [r for r in test_results if r.get("status") == "success"]
            
            if successful_results:
                response_times = [r["response_time"] for r in successful_results]
                
                api_stats = {
                    "total_tests": len(test_results),
                    "successful_tests": len(successful_results),
                    "success_rate": f"{len(successful_results)/len(test_results)*100:.1f}%",
                    "avg_response_time": f"{statistics.mean(response_times):.2f}ms",
                    "min_response_time": f"{min(response_times):.2f}ms",
                    "max_response_time": f"{max(response_times):.2f}ms",
                    "median_response_time": f"{statistics.median(response_times):.2f}ms"
                }
                
                if successful_results and "data_size" in successful_results[0]:
                    api_stats["avg_data_size"] = f"{statistics.mean([r['data_size'] for r in successful_results]):.0f} bytes"
                
                if successful_results and "records_count" in successful_results[0]:
                    api_stats["avg_records"] = f"{statistics.mean([r['records_count'] for r in successful_results]):.1f}"
                
                all_results[api_test["name"]] = api_stats
            else:
                all_results[api_test["name"]] = {"error": "所有请求都失败"}
        
        # 综合评级
        successful_apis = [name for name, stats in all_results.items() if "error" not in stats]
        if successful_apis:
            avg_response_times = []
            for name in successful_apis:
                try:
                    avg_time = float(all_results[name]["avg_response_time"].replace("ms", ""))
                    avg_response_times.append(avg_time)
                except:
                    pass
            
            if avg_response_times:
                overall_avg = statistics.mean(avg_response_times)
                if overall_avg < 200:
                    grade = "🟢 优秀"
                elif overall_avg < 500:
                    grade = "🟡 良好"
                else:
                    grade = "🟠 需优化"
            else:
                grade = "❓ 无法评级"
        else:
            grade = "🔴 系统异常"
        
        return {
            "test_name": "后端API综合性能测试",
            "overall_grade": grade,
            "overall_avg_response_time": f"{statistics.mean(avg_response_times):.2f}ms" if avg_response_times else "N/A",
            "api_results": all_results,
            "successful_apis": f"{len(successful_apis)}/{len(api_tests)}"
        }

async def run_comprehensive_backend_test():
    """运行后端API综合性能测试"""
    async with BackendAPIPerformanceTester() as tester:
        print("=" * 80)
        print("🚀 后端API专项性能测试")
        print("=" * 80)
        
        # 准备测试账号
        print("\n📋 准备测试账号...")
        accounts = await tester.prepare_test_accounts()
        if accounts:
            print(f"✅ 成功准备 {len(accounts)} 个测试账号")
            print(f"   - 学生账号: {len([a for a in accounts if a['person_type'] == 'student'])} 个")
            print(f"   - 教师账号: {len([a for a in accounts if a['person_type'] == 'teacher'])} 个")
            print(f"   - 管理员账号: {len([a for a in accounts if a['person_type'] == 'admin'])} 个")
        else:
            print("❌ 无法获取测试账号，部分测试可能失败")
        
        # 1. 真实登录验证查询性能测试
        print("\n" + "=" * 50)
        print("📊 1. 真实登录验证查询性能测试")
        print("=" * 50)
        login_query_result = await tester.test_real_login_query_performance()
        
        if "error" not in login_query_result:
            print(f"📈 测试结果: {login_query_result['performance_grade']}")
            print(f"   - 平均响应时间: {login_query_result['avg_response_time']}")
            print(f"   - 成功率: {login_query_result['success_rate']}")
            print(f"   - P95响应时间: {login_query_result['p95_response_time']}")
            print(f"   - 平均返回字段数: {login_query_result['avg_fields_returned']}")
            print(f"   - 平均响应大小: {login_query_result['avg_response_size']}")
            print(f"   - JOIN完整性:")
            for join_type, rate in login_query_result['join_completeness'].items():
                print(f"     · {join_type}: {rate}")
            print(f"   - 人员类型分布: {login_query_result['person_type_distribution']}")
        else:
            print(f"❌ 测试失败: {login_query_result['error']}")
        
        # 2. 登录压力测试
        print("\n" + "=" * 50)
        print("🚀 2. 登录压力测试 (60秒)")
        print("=" * 50)
        stress_result = await tester.test_login_stress_performance(60)
        
        if "error" not in stress_result:
            print(f"📈 压力测试结果: {stress_result['stress_grade']}")
            print(f"   - 总请求数: {stress_result['total_requests']}")
            print(f"   - 成功请求数: {stress_result['successful_requests']}")
            print(f"   - 整体成功率: {stress_result['overall_success_rate']}")
            print(f"   - 每秒请求数: {stress_result['requests_per_second']}")
            print(f"   - 成功RPS: {stress_result['successful_rps']}")
            print(f"   - 平均响应时间: {stress_result['performance_metrics']['avg_response_time']}")
            print(f"   - P95响应时间: {stress_result['performance_metrics']['p95_response_time']}")
            print(f"   - P99响应时间: {stress_result['performance_metrics']['p99_response_time']}")
            
            print("\n   📊 分账号类型性能:")
            for acc_type, perf in stress_result['account_type_performance'].items():
                print(f"     · {acc_type}: {perf['avg_response_time']} (成功率: {perf['success_rate']})")
            
            print("\n   ⏱️ 时间序列分析:")
            for window in stress_result['time_series_analysis'][:6]:  # 只显示前6个窗口
                print(f"     · {window['time_window']}: {window['successful_requests']}/{window['total_requests']} "
                      f"({window['success_rate']}) - {window['avg_response_time']}")
        else:
            print(f"❌ 压力测试失败: {stress_result['error']}")
        
        # 3. 后端API综合测试
        print("\n" + "=" * 50)
        print("🔬 3. 后端API综合性能测试")
        print("=" * 50)
        api_result = await tester.test_backend_api_comprehensive()
        
        print(f"📈 综合测试结果: {api_result['overall_grade']}")
        print(f"   - 整体平均响应时间: {api_result['overall_avg_response_time']}")
        print(f"   - 成功API数量: {api_result['successful_apis']}")
        
        print("\n   📋 各API详细性能:")
        for api_name, stats in api_result['api_results'].items():
            if "error" not in stats:
                print(f"     · {api_name}: {stats['avg_response_time']} "
                      f"(成功率: {stats['success_rate']}) "
                      f"[{stats.get('avg_records', 'N/A')}条记录]")
            else:
                print(f"     · {api_name}: ❌ {stats['error']}")
        
        print("\n" + "=" * 80)
        print("🎯 测试总结")
        print("=" * 80)
        print("✅ 后端API专项性能测试完成！")
        print(f"📊 真实登录查询: {login_query_result.get('performance_grade', '❌ 失败')}")
        print(f"🚀 登录压力测试: {stress_result.get('stress_grade', '❌ 失败')}")
        print(f"🔬 API综合测试: {api_result.get('overall_grade', '❌ 失败')}")
        
        # 保存详细结果
        detailed_results = {
            "timestamp": datetime.now().isoformat(),
            "real_login_query_test": login_query_result,
            "login_stress_test": stress_result,
            "api_comprehensive_test": api_result
        }
        
        with open("backend_api_performance_results.json", "w", encoding="utf-8") as f:
            json.dump(detailed_results, f, ensure_ascii=False, indent=2)
        
        print(f"📄 详细结果已保存到: backend_api_performance_results.json")

if __name__ == "__main__":
    asyncio.run(run_comprehensive_backend_test()) 