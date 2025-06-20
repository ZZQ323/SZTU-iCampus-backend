"""
简化API端点 - 专为微信小程序优化
提供最核心的功能，简单快速
"""
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, HTTPException, Depends, Query
from datetime import datetime, timedelta

# 模拟用户认证（简化版）
def get_current_user_simple() -> Dict:
    """简化版用户认证 - 返回模拟用户"""
    return {
        "id": 20241001001,
        "name": "张三",
        "role": "student",
        "student_id": "20241001001",
        "college": "计算机学院",
        "major": "软件工程",
        "class": "软工2024-1班"
    }

router = APIRouter()

# ============================================================================
# 首页数据 - 一次性获取所有需要的数据
# ============================================================================

@router.get("/home")
async def get_home_data(user=Depends(get_current_user_simple)):
    """
    获取首页数据 - 微信小程序首页一次性加载
    包含：公告、课表、通知、活动等核心信息
    """
    
    # 模拟数据 - 实际项目中从数据服务获取
    home_data = {
        "user_info": {
            "name": user["name"],
            "student_id": user["student_id"],
            "avatar": "/assets/test/man.png",
            "college": user["college"],
            "unread_count": 3
        },
        
        # 最新公告（首页显示3条）
        "announcements": [
            {
                "id": 1,
                "title": "关于2024年寒假放假安排的通知",
                "department": "教务处",
                "date": "2024-12-18",
                "urgent": True,
                "category": "教学"
            },
            {
                "id": 2, 
                "title": "深圳技术大学第十二届运动会开幕式通知",
                "department": "体育部",
                "date": "2024-12-17",
                "urgent": False,
                "category": "活动"
            },
            {
                "id": 3,
                "title": "图书馆系统维护通知",
                "department": "图书馆",
                "date": "2024-12-16", 
                "urgent": False,
                "category": "服务"
            }
        ],
        
        # 今日课表
        "today_schedule": [
            {
                "id": 1,
                "course_name": "数据结构与算法",
                "teacher": "李教授",
                "time": "08:30-10:10",
                "location": "C2-301",
                "status": "upcoming"
            },
            {
                "id": 2,
                "course_name": "软件工程",
                "teacher": "王教授", 
                "time": "10:30-12:10",
                "location": "C2-305",
                "status": "current"
            },
            {
                "id": 3,
                "course_name": "数据库原理",
                "teacher": "张教授",
                "time": "14:30-16:10", 
                "location": "C2-302",
                "status": "upcoming"
            }
        ],
        
        # 快捷功能
        "quick_actions": [
            {"name": "课表查询", "icon": "schedule", "path": "/pages/schedule/schedule"},
            {"name": "成绩查询", "icon": "grade", "path": "/pages/grades/grades"},
            {"name": "图书馆", "icon": "library", "path": "/pages/library/library"},
            {"name": "校园卡", "icon": "card", "path": "/pages/card/card"},
            {"name": "考试安排", "icon": "exam", "path": "/pages/exams/exams"},
            {"name": "活动报名", "icon": "event", "path": "/pages/events/events"},
            {"name": "通讯录", "icon": "contact", "path": "/pages/address_book/address_book"},
            {"name": "通知中心", "icon": "notice", "path": "/pages/notifications/notifications"}
        ],
        
        # 今日统计
        "today_stats": {
            "courses": 4,
            "completed_courses": 1,
            "library_books": 2,
            "announcements": 5
        }
    }
    
    return {
        "success": True,
        "data": home_data,
        "message": "首页数据获取成功"
    }

# ============================================================================
# 公告相关
# ============================================================================

@router.get("/announcements")
async def get_announcements(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    category: str = Query(None),
    user=Depends(get_current_user_simple)
):
    """获取公告列表"""
    
    # 模拟公告数据
    all_announcements = [
        {
            "id": i,
            "title": f"公告标题 {i}",
            "content": f"这是第{i}条公告的内容...",
            "department": ["教务处", "学生处", "图书馆", "体育部"][i % 4],
            "category": ["教学", "生活", "服务", "活动"][i % 4],
            "date": (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d"),
            "time": "10:30",
            "urgent": i <= 2,
            "read": i > 5
        }
        for i in range(1, 21)
    ]
    
    # 分页
    start = (page - 1) * limit
    end = start + limit
    announcements = all_announcements[start:end]
    
    return {
        "success": True,
        "data": {
            "announcements": announcements,
            "total": len(all_announcements),
            "page": page,
            "limit": limit,
            "has_more": end < len(all_announcements)
        }
    }

@router.get("/announcements/{announcement_id}")
async def get_announcement_detail(
    announcement_id: int,
    user=Depends(get_current_user_simple)
):
    """获取公告详情"""
    
    announcement = {
        "id": announcement_id,
        "title": "关于2024年寒假放假安排的通知",
        "content": """各位同学：
        
根据学校校历安排，现将2024年寒假放假时间安排通知如下：

一、放假时间
学生放假时间：2024年1月15日（星期一）
开学时间：2024年2月26日（星期一）

二、注意事项
1. 请同学们合理安排假期时间，注意人身安全
2. 假期期间图书馆开放时间调整，详见图书馆通知
3. 宿舍管理相关事宜请联系宿管办

三、联系方式
如有疑问，请联系教务处：0755-12345678

教务处
2024年12月18日""",
        "department": "教务处",
        "category": "教学",
        "date": "2024-12-18",
        "time": "10:30",
        "urgent": True,
        "attachments": [
            {"name": "放假安排详细说明.pdf", "url": "#", "size": "2.1MB"},
            {"name": "假期安全提醒.docx", "url": "#", "size": "500KB"}
        ],
        "read_count": 1523,
        "publish_time": "2024-12-18 10:30:00"
    }
    
    return {
        "success": True,
        "data": announcement
    }

# ============================================================================
# 课表相关
# ============================================================================

@router.get("/schedule")
async def get_schedule(
    week: int = Query(None, description="周数，不传则返回当前周"),
    user=Depends(get_current_user_simple)
):
    """获取课表"""
    
    current_week = week or 15  # 当前第15周
    
    # 模拟课表数据 - 标准大学课表格式
    schedule_data = {
        "week_info": {
            "current_week": current_week,
            "total_weeks": 18,
            "semester": "2024-2025学年第一学期"
        },
        "schedule": {
            "monday": [
                {
                    "id": 1,
                    "course_name": "数据结构与算法",
                    "teacher": "李教授",
                    "location": "C2-301", 
                    "time_slot": "1-2节",
                    "time": "08:30-10:10",
                    "weeks": "1-16周",
                    "course_type": "必修"
                },
                {
                    "id": 2,
                    "course_name": "软件工程",
                    "teacher": "王教授",
                    "location": "C2-305",
                    "time_slot": "3-4节", 
                    "time": "10:30-12:10",
                    "weeks": "1-16周",
                    "course_type": "必修"
                },
                {
                    "id": 3,
                    "course_name": "数据库原理",
                    "teacher": "张教授",
                    "location": "C2-302",
                    "time_slot": "6-7节",
                    "time": "14:30-16:10",
                    "weeks": "1-16周", 
                    "course_type": "必修"
                }
            ],
            "tuesday": [
                {
                    "id": 4,
                    "course_name": "计算机网络",
                    "teacher": "陈教授",
                    "location": "C3-201",
                    "time_slot": "1-2节",
                    "time": "08:30-10:10", 
                    "weeks": "1-16周",
                    "course_type": "必修"
                },
                {
                    "id": 5,
                    "course_name": "操作系统",
                    "teacher": "赵教授",
                    "location": "C3-205",
                    "time_slot": "6-7节",
                    "time": "14:30-16:10",
                    "weeks": "1-16周",
                    "course_type": "必修"
                }
            ],
            "wednesday": [
                {
                    "id": 6,
                    "course_name": "软件测试",
                    "teacher": "刘教授", 
                    "location": "E2-501",
                    "time_slot": "3-4节",
                    "time": "10:30-12:10",
                    "weeks": "1-16周",
                    "course_type": "选修"
                }
            ],
            "thursday": [
                {
                    "id": 7,
                    "course_name": "人工智能导论",
                    "teacher": "孙教授",
                    "location": "C2-401",
                    "time_slot": "1-2节",
                    "time": "08:30-10:10",
                    "weeks": "1-16周",
                    "course_type": "选修"
                }
            ],
            "friday": [
                {
                    "id": 8,
                    "course_name": "项目实践",
                    "teacher": "周教授",
                    "location": "E3-机房1",
                    "time_slot": "6-8节",
                    "time": "14:30-17:00",
                    "weeks": "1-16周",
                    "course_type": "实践"
                }
            ],
            "saturday": [],
            "sunday": []
        }
    }
    
    return {
        "success": True,
        "data": schedule_data
    }

# ============================================================================
# 成绩相关
# ============================================================================

@router.get("/grades")
async def get_grades(
    semester: str = Query(None, description="学期，如：2024-1"),
    user=Depends(get_current_user_simple)
):
    """获取成绩"""
    
    current_semester = semester or "2024-1"
    
    grades_data = {
        "semester_info": {
            "current_semester": current_semester,
            "academic_year": "2024-2025"
        },
        "summary": {
            "total_courses": 8,
            "total_credits": 24.5,
            "avg_score": 87.3,
            "gpa": 3.67,
            "rank": 5,
            "total_students": 35
        },
        "grades": [
            {
                "id": 1,
                "course_name": "数据结构与算法",
                "course_code": "CS001",
                "credits": 4.0,
                "teacher": "李教授",
                "regular_score": 85,
                "midterm_score": 88,
                "final_score": 92,
                "total_score": 90,
                "grade_level": "A-",
                "gpa_points": 3.7,
                "course_type": "必修"
            },
            {
                "id": 2,
                "course_name": "软件工程",
                "course_code": "CS002", 
                "credits": 3.5,
                "teacher": "王教授",
                "regular_score": 90,
                "midterm_score": 85,
                "final_score": 88,
                "total_score": 88,
                "grade_level": "B+",
                "gpa_points": 3.3,
                "course_type": "必修"
            },
            {
                "id": 3,
                "course_name": "数据库原理", 
                "course_code": "CS003",
                "credits": 3.0,
                "teacher": "张教授",
                "regular_score": 88,
                "midterm_score": 90,
                "final_score": 85,
                "total_score": 87,
                "grade_level": "B+",
                "gpa_points": 3.3,
                "course_type": "必修"
            }
        ]
    }
    
    return {
        "success": True,
        "data": grades_data
    }

# ============================================================================
# 图书馆相关  
# ============================================================================

@router.get("/library")
async def get_library_info(user=Depends(get_current_user_simple)):
    """获取图书馆信息"""
    
    library_data = {
        "user_info": {
            "borrowed_books": 2,
            "max_books": 10,
            "overdue_books": 0,
            "total_fine": 0.0
        },
        "borrowed_books": [
            {
                "id": 1,
                "title": "算法导论（第三版）",
                "author": "Thomas H. Cormen",
                "isbn": "9787111407010",
                "borrow_date": "2024-11-20",
                "due_date": "2024-12-20",
                "location": "图书馆三楼计算机类",
                "renewable": True,
                "days_left": 2
            },
            {
                "id": 2,
                "title": "深入理解计算机系统",
                "author": "Randal E. Bryant",
                "isbn": "9787111321312", 
                "borrow_date": "2024-11-25",
                "due_date": "2024-12-25",
                "location": "图书馆三楼计算机类",
                "renewable": True,
                "days_left": 7
            }
        ],
        "library_hours": {
            "weekday": "08:00-22:00",
            "weekend": "09:00-21:00",
            "today_status": "开放中",
            "close_time": "22:00"
        },
        "quick_search": [
            "数据结构", "算法", "Java编程", "Python", "数据库", "计算机网络"
        ]
    }
    
    return {
        "success": True, 
        "data": library_data
    }

# ============================================================================
# 校园卡相关
# ============================================================================

@router.get("/campus-card")
async def get_campus_card_info(user=Depends(get_current_user_simple)):
    """获取校园卡信息"""
    
    card_data = {
        "card_info": {
            "card_number": "20241001001",
            "balance": 156.80,
            "status": "正常",
            "last_update": "2024-12-18 12:30:15"
        },
        "today_consumption": {
            "total": 28.50,
            "count": 4,
            "details": [
                {
                    "time": "12:15",
                    "location": "第一食堂二楼",
                    "amount": -15.50,
                    "balance": 156.80,
                    "type": "餐饮"
                },
                {
                    "time": "10:30", 
                    "location": "图书馆咖啡厅",
                    "amount": -8.00,
                    "balance": 172.30,
                    "type": "餐饮"
                },
                {
                    "time": "08:45",
                    "location": "便利店",
                    "amount": -3.50,
                    "balance": 180.30,
                    "type": "购物"
                },
                {
                    "time": "07:30",
                    "location": "早餐店",
                    "amount": -1.50,
                    "balance": 183.80,
                    "type": "餐饮"
                }
            ]
        },
        "quick_actions": [
            {"name": "充值", "icon": "add", "action": "recharge"},
            {"name": "挂失", "icon": "lock", "action": "report_loss"},
            {"name": "交易记录", "icon": "list", "action": "transactions"},
            {"name": "余额提醒", "icon": "bell", "action": "reminder"}
        ]
    }
    
    return {
        "success": True,
        "data": card_data
    } 