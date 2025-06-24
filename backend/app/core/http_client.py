"""
HTTP客户端 - 胶水层与data-service的HTTP通信
严格架构分离：胶水层通过HTTP请求调用data-service，绝不直接导入模块
"""
import httpx
import json
from typing import Dict, Any, Optional
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class DataServiceHTTPClient:
    """data-service HTTP客户端 - 纯HTTP通信"""
    
    def __init__(self):
        self.base_url = settings.DATA_SERVICE_URL  # http://127.0.0.1:8001
        self.api_key = settings.DATA_SERVICE_API_KEY
        self.headers = {
            "Content-Type": "application/json",
            "X-API-Key": self.api_key
        }
        self.timeout = 30.0
    
    async def _request(
        self, 
        method: str, 
        endpoint: str, 
        params: Optional[Dict] = None,
        json_data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """发送HTTP请求到data-service"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=self.headers,
                    params=params,
                    json=json_data
                )
                
                response.raise_for_status()
                return response.json()
                
        except httpx.TimeoutException:
            logger.error(f"data-service请求超时: {method} {endpoint}")
            raise Exception("data-service请求超时")
        except httpx.HTTPStatusError as e:
            logger.error(f"data-service返回错误: {e.response.status_code} - {e.response.text}")
            raise Exception(f"data-service错误: {e.response.status_code}")
        except Exception as e:
            logger.error(f"data-service请求失败: {str(e)}")
            raise Exception(f"data-service请求失败: {str(e)}")
    
    async def query_table(
        self, 
        table_name: str,
        filters: Optional[Dict] = None,
        limit: int = 20,
        offset: int = 0,
        order_by: Optional[str] = None
    ) -> Dict[str, Any]:
        """HTTP请求：查询表数据"""
        params = {
            "limit": limit,
            "offset": offset
        }
        
        if filters:
            params["filters"] = json.dumps(filters)
        if order_by:
            params["order_by"] = order_by
        
        return await self._request("GET", f"/query/{table_name}", params=params)
    
    async def authenticate_user(self, login_id: str, password: str) -> Optional[Dict[str, Any]]:
        """HTTP请求：用户认证"""
        try:
            result = await self._request(
                "POST",
                "/auth/login",
                json_data={"login_id": login_id, "password": password}
            )
            
            if result.get("status") == "success":
                return result.get("data", {}).get("user_info")
            return None
            
        except Exception as e:
            logger.error(f"用户认证失败: {e}")
            return None
    
    async def get_person_by_id(self, person_id: str) -> Optional[Dict[str, Any]]:
        """HTTP请求：根据ID获取用户信息"""
        try:
            logger.info(f"查询用户信息: person_id={person_id}")
            result = await self.query_table(
                "persons",
                filters={"person_id": person_id, "is_deleted": False},
                limit=1
            )
            
            logger.info(f"查询结果: {result}")
            records = result.get("data", {}).get("records", [])
            user = records[0] if records else None
            logger.info(f"用户信息: {user}")
            return user
            
        except Exception as e:
            logger.error(f"获取用户信息失败: {e}")
            return None
    
    async def get_student_schedule(
        self, 
        student_id: str, 
        semester: Optional[str] = None,
        week_number: Optional[int] = None
    ) -> Dict[str, Any]:
        """HTTP请求：获取学生课表"""
        try:
            if not semester:
                semester = "2024-2025-1"
            
            # 第一步：获取学生的选课记录
            enrollments_result = await self.query_table(
                "enrollments", 
                filters={
                    "student_id": student_id,
                    "enrollment_status": "completed",
                    "is_deleted": False
                },
                limit=50
            )
            
            enrollments = enrollments_result.get("data", {}).get("records", [])
            
            if not enrollments:
                return {
                    "semester": semester,
                    "week_number": week_number,
                    "student_info": {"student_id": student_id},
                    "courses": []
                }
            
            # 第二步：获取课程实例详情
            course_instance_ids = [e.get("course_instance_id") for e in enrollments if e.get("course_instance_id")]
            
            courses = []
            for instance_id in course_instance_ids:
                try:
                    instance_result = await self.query_table(
                        "course_instances",
                        filters={"instance_id": instance_id, "is_deleted": False},
                        limit=1
                    )
                    
                    instances = instance_result.get("data", {}).get("records", [])
                    if instances:
                        instance = instances[0]
                        logger.info(f"课程实例数据: {instance}")  # 🔍 调试日志
                        
                        # 获取课程基本信息
                        course_result = await self.query_table(
                            "courses",
                            filters={"course_id": instance.get("course_id"), "is_deleted": False},
                            limit=1
                        )
                        
                        course_records = course_result.get("data", {}).get("records", [])
                        if course_records:
                            course = course_records[0]
                            
                            # 优先查询class_schedules表获取课表信息
                            schedule_result = await self.query_table(
                                "class_schedules",
                                filters={"course_instance_id": instance_id, "is_deleted": False},
                                limit=5  # 可能有多个时间段
                            )
                            
                            schedules = schedule_result.get("data", {}).get("records", [])
                            if schedules:
                                # 如果在class_schedules表中找到课表信息
                                for schedule_item in schedules:
                                    course_info = {
                                        "instance_id": instance_id,
                                        "course_code": course.get("course_code", "UNKNOWN"),
                                        "course_name": course.get("course_name", "未知课程"),
                                        "teacher_name": schedule_item.get("teacher_id", "未知教师"),
                                        "credits": course.get("credit_hours", 0),
                                        "schedule": {
                                            "weekday": schedule_item.get("day_of_week", 1),
                                            "start_time": schedule_item.get("start_time", "08:30"),
                                            "end_time": schedule_item.get("end_time", "10:10"),
                                            "location": schedule_item.get("classroom", "待定"),
                                            "building_name": schedule_item.get("building", ""),
                                            "weeks": schedule_item.get("week_range", "1-16周")
                                        },
                                        "course_type": course.get("course_type", "required")
                                    }
                                    courses.append(course_info)
                            else:
                                # 如果class_schedules表中没有数据，尝试从schedule_info字段获取
                                schedule_info_raw = instance.get("schedule_info", "[]")
                                try:
                                    if isinstance(schedule_info_raw, str):
                                        schedule_info_list = json.loads(schedule_info_raw)
                                    else:
                                        schedule_info_list = schedule_info_raw if schedule_info_raw else []
                                    
                                    if schedule_info_list and len(schedule_info_list) > 0:
                                        schedule_item = schedule_info_list[0]
                                        course_info = {
                                            "instance_id": instance_id,
                                            "course_code": course.get("course_code", "UNKNOWN"),
                                            "course_name": course.get("course_name", "未知课程"),
                                            "teacher_name": instance.get("teacher_id", "未知教师"),
                                            "credits": course.get("credit_hours", 0),
                                            "schedule": {
                                                "weekday": schedule_item.get("day_of_week", 1),
                                                "start_time": schedule_item.get("start_time", "08:30"),
                                                "end_time": schedule_item.get("end_time", "10:10"),
                                                "location": schedule_item.get("classroom", "待定"),
                                                "building_name": schedule_item.get("building", ""),
                                                "weeks": schedule_item.get("week_range", "1-16周")
                                            },
                                            "course_type": course.get("course_type", "required")
                                        }
                                        courses.append(course_info)
                                    else:
                                        logger.warning(f"课程实例 {instance_id} 没有课表信息")
                                        
                                except (json.JSONDecodeError, TypeError) as e:
                                    logger.warning(f"解析课程实例 {instance_id} 的schedule_info失败: {e}")
                                    continue
                
                except Exception as e:
                    logger.warning(f"获取课程实例 {instance_id} 失败: {e}")
                    continue
            
            return {
                "semester": semester,
                "week_number": week_number,
                "student_info": {"student_id": student_id},
                "courses": courses
            }
            
        except Exception as e:
            logger.error(f"获取学生课表失败: {e}")
            return {
                "semester": semester or "2024-2025-1",
                "week_number": week_number,
                "student_info": {"student_id": student_id},
                "courses": []
            }
    
    async def search_books(
        self,
        keyword: Optional[str] = None,
        category: Optional[str] = None,
        author: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> Dict[str, Any]:
        """HTTP请求：搜索图书"""
        try:
            filters = {"is_deleted": False}
            
            if keyword:
                # 简化搜索：在title中查找关键词
                filters["title__contains"] = keyword
            if category:
                filters["category"] = category
            if author:
                filters["author__contains"] = author
            
            result = await self.query_table(
                "books",
                filters=filters,
                limit=limit,
                offset=offset,
                order_by="borrow_count DESC"
            )
            
            books = result.get("data", {}).get("records", [])
            
            # 格式化图书数据以符合前端期望
            formatted_books = []
            for book in books:
                formatted_book = {
                    "book_id": book.get("book_id"),
                    "id": book.get("book_id"),
                    "isbn": book.get("isbn"),
                    "title": book.get("title"),
                    "subtitle": book.get("subtitle", ""),
                    "author": book.get("author"),
                    "publisher": book.get("publisher"),
                    "publish_date": book.get("publish_date"),
                    "category": book.get("category"),
                    "call_number": book.get("call_number"),
                    "total_copies": book.get("total_copies", 0),
                    "available_copies": book.get("available_copies", 0),
                    "borrowed_copies": book.get("borrowed_copies", 0),
                    "location": book.get("location"),
                    "floor": book.get("floor"),
                    "description": book.get("description", ""),
                    "borrow_count": book.get("borrow_count", 0),
                    "borrowCount": book.get("borrow_count", 0),
                    "rating": book.get("rating", 0.0),
                    "status": "available" if book.get("available_copies", 0) > 0 else "borrowed",
                    "cover": book.get("cover") or f"https://via.placeholder.com/120x160?text={book.get('title', '图书')}",
                    "is_new": book.get("is_new", False),
                    "arrivalDate": book.get("arrival_date")
                }
                formatted_books.append(formatted_book)
            
            return {
                "books": formatted_books,
                "pagination": {
                    "page": (offset // limit) + 1,
                    "size": limit,
                    "total": len(formatted_books),
                    "pages": (len(formatted_books) + limit - 1) // limit
                },
                "search_info": {
                    "keyword": keyword,
                    "category": category,
                    "author": author
                }
            }
            
        except Exception as e:
            logger.error(f"搜索图书失败: {e}")
            return {
                "books": [],
                "pagination": {"page": 1, "size": limit, "total": 0, "pages": 0},
                "search_info": {"keyword": keyword, "category": category, "author": author}
            }
    
    async def get_user_borrow_records(
        self,
        user_id: str,
        status: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> Dict[str, Any]:
        """HTTP请求：获取用户借阅记录"""
        try:
            filters = {
                "borrower_id": user_id,
                "is_deleted": False
            }
            
            if status:
                filters["status"] = status
            
            result = await self.query_table(
                "borrow_records",
                filters=filters,
                limit=limit,
                offset=offset,
                order_by="borrow_date DESC"
            )
            
            records = result.get("data", {}).get("records", [])
            
            # 格式化借阅记录
            formatted_records = []
            for record in records:
                formatted_record = {
                    "record_id": record.get("record_id"),
                    "book_id": record.get("book_id"),
                    "id": record.get("record_id"),
                    "title": record.get("book_title", "未知图书"),
                    "book_title": record.get("book_title", "未知图书"),
                    "isbn": record.get("isbn", ""),
                    "author": record.get("author", ""),
                    "borrow_date": record.get("borrow_date"),
                    "borrowDate": record.get("borrow_date"),
                    "due_date": record.get("due_date"),
                    "dueDate": record.get("due_date"),
                    "return_date": record.get("return_date"),
                    "status": record.get("status", "borrowed"),
                    "renewal_count": record.get("renewal_count", 0),
                    "renewCount": record.get("renewal_count", 0),
                    "max_renewals": record.get("max_renewals", 2),
                    "maxRenew": record.get("max_renewals", 2),
                    "fine_amount": record.get("fine_amount", 0.0),
                    "location": record.get("location", ""),
                    "daysLeft": 5,  # 这里需要计算实际剩余天数
                    "isOverdue": record.get("status") == "overdue",
                    "cover": record.get("cover") or f"https://via.placeholder.com/120x160?text={record.get('book_title', '图书')}"
                }
                formatted_records.append(formatted_record)
            
            return {
                "borrow_records": formatted_records,
                "pagination": {
                    "page": (offset // limit) + 1,
                    "size": limit,
                    "total": len(formatted_records),
                    "pages": (len(formatted_records) + limit - 1) // limit
                },
                "statistics": {
                    "total_borrowed": len(formatted_records),
                    "total_returned": len([r for r in formatted_records if r["status"] == "returned"]),
                    "total_overdue": len([r for r in formatted_records if r["status"] == "overdue"])
                }
            }
            
        except Exception as e:
            logger.error(f"获取借阅记录失败: {e}")
            return {
                "borrow_records": [],
                "pagination": {"page": 1, "size": limit, "total": 0, "pages": 0},
                "statistics": {"total_borrowed": 0, "total_returned": 0, "total_overdue": 0}
            }

# 创建全局HTTP客户端实例
http_client = DataServiceHTTPClient() 