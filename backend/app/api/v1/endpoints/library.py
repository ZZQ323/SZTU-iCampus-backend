"""
图书馆管理API端点
提供图书查询、借阅管理、座位预约、图书荐购等功能
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date, timedelta

from app.api import deps

router = APIRouter(tags=["library"])

@router.get("/borrow-info")
async def get_borrow_info(
    student_id: str = Query("2024001", description="学生学号"),
    db: Session = Depends(deps.get_db)
):
    """获取学生借阅信息"""
    borrow_data = {
        "student_id": student_id,
        "current_borrow": 2,
        "max_borrow": 10,
        "borrow_list": [
            {
                "id": 1,
                "book_name": "高等数学（第七版）",
                "borrow_date": "2024-03-01",
                "return_date": "2024-06-01"
            }
        ]
    }
    
    return {"code": 0, "message": "success", "data": borrow_data}

@router.get("/search")
async def search_books(
    keyword: str = Query(..., description="搜索关键词"),
    search_type: str = Query("all", description="搜索类型：title, author, isbn, all"),
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(20, ge=1, le=100, description="返回记录数"),
    db: Session = Depends(deps.get_db)
):
    """
    图书搜索
    """
    # 模拟搜索结果
    mock_books = [
        {
            "id": 1,
            "title": "高等数学（第七版）",
            "author": "同济大学数学系",
            "isbn": "9787040396638",
            "publisher": "高等教育出版社",
            "publish_year": "2014",
            "category": "数学",
            "location": "理工图书区A区3层",
            "call_number": "O13/T56",
            "total_copies": 50,
            "available_copies": 15,
            "status": "available"
        },
        {
            "id": 2,
            "title": "线性代数（第六版）",
            "author": "同济大学数学系",
            "isbn": "9787040396652",
            "publisher": "高等教育出版社",
            "publish_year": "2014",
            "category": "数学",
            "location": "理工图书区A区3层",
            "call_number": "O151.2/T56",
            "total_copies": 30,
            "available_copies": 8,
            "status": "available"
        }
    ]
    
    # 简单的关键词匹配
    filtered_books = []
    for book in mock_books:
        if keyword.lower() in book["title"].lower() or keyword.lower() in book["author"].lower():
            filtered_books.append(book)
    
    total = len(filtered_books)
    books = filtered_books[skip:skip + limit]
    
    return {
        "code": 0,
        "message": "success",
        "data": {
            "books": books,
            "total": total,
            "keyword": keyword,
            "search_type": search_type
        }
    }

@router.get("/seats")
async def get_seat_info(db: Session = Depends(deps.get_db)):
    """获取座位信息"""
    seat_data = {
        "floors": [
            {"id": 1, "name": "一楼阅览室", "available_seats": 45},
            {"id": 2, "name": "二楼阅览室", "available_seats": 38}
        ]
    }
    
    return {"code": 0, "message": "success", "data": seat_data}

@router.post("/seat-reservation")
async def reserve_seat(
    floor_id: int,
    seat_number: str,
    start_time: str,
    end_time: str,
    student_id: str = Query("2024001", description="学生学号"),
    db: Session = Depends(deps.get_db)
):
    """
    预约座位
    """
    # 模拟预约逻辑
    reservation_data = {
        "reservation_id": f"RES{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "student_id": student_id,
        "floor_id": floor_id,
        "seat_number": seat_number,
        "start_time": start_time,
        "end_time": end_time,
        "status": "confirmed",
        "qr_code": f"library_seat_{floor_id}_{seat_number}_{datetime.now().timestamp()}",
        "created_at": datetime.now().isoformat()
    }
    
    return {
        "code": 0,
        "message": "座位预约成功",
        "data": reservation_data
    }

@router.get("/reservations")
async def get_reservations(
    student_id: str = Query("2024001", description="学生学号"),
    status: Optional[str] = Query(None, description="预约状态：active, completed, cancelled"),
    db: Session = Depends(deps.get_db)
):
    """
    获取座位预约记录
    """
    # 模拟预约记录
    reservations = [
        {
            "reservation_id": "RES20240320143000",
            "floor_name": "一楼阅览室",
            "seat_number": "A001",
            "date": "2024-03-20",
            "start_time": "14:30",
            "end_time": "18:30",
            "status": "active",
            "created_at": "2024-03-20T10:00:00"
        },
        {
            "reservation_id": "RES20240319090000",
            "floor_name": "四楼自习室",
            "seat_number": "D045",
            "date": "2024-03-19",
            "start_time": "09:00",
            "end_time": "17:00",
            "status": "completed",
            "created_at": "2024-03-18T20:00:00"
        }
    ]
    
    # 状态筛选
    if status:
        reservations = [r for r in reservations if r["status"] == status]
    
    return {
        "code": 0,
        "message": "success",
        "data": {
            "reservations": reservations,
            "total": len(reservations)
        }
    }

@router.post("/recommend")
async def recommend_book(
    title: str,
    author: Optional[str] = None,
    isbn: Optional[str] = None,
    publisher: Optional[str] = None,
    reason: Optional[str] = None,
    student_id: str = Query("2024001", description="学生学号"),
    db: Session = Depends(deps.get_db)
):
    """
    图书荐购
    """
    # 模拟荐购提交
    recommendation_data = {
        "recommendation_id": f"REC{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "student_id": student_id,
        "title": title,
        "author": author,
        "isbn": isbn,
        "publisher": publisher,
        "reason": reason,
        "status": "submitted",
        "submit_time": datetime.now().isoformat(),
        "expected_review_time": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
    }
    
    return {
        "code": 0,
        "message": "荐购申请提交成功",
        "data": recommendation_data
    }

@router.get("/recommendations")
async def get_recommendations(
    student_id: str = Query("2024001", description="学生学号"),
    status: Optional[str] = Query(None, description="荐购状态：submitted, approved, rejected, purchased"),
    db: Session = Depends(deps.get_db)
):
    """
    获取荐购记录
    """
    # 模拟荐购记录
    recommendations = [
        {
            "recommendation_id": "REC20240315100000",
            "title": "深度学习（花书）",
            "author": "Ian Goodfellow",
            "status": "approved",
            "submit_time": "2024-03-15T10:00:00",
            "review_time": "2024-03-18T15:30:00",
            "reviewer": "图书馆采编部",
            "feedback": "该书具有较高的学术价值，已纳入采购计划"
        },
        {
            "recommendation_id": "REC20240310140000",
            "title": "算法导论（第四版）",
            "author": "Thomas H. Cormen",
            "status": "purchased",
            "submit_time": "2024-03-10T14:00:00",
            "review_time": "2024-03-12T09:00:00",
            "purchase_time": "2024-03-20T11:00:00",
            "call_number": "TP301.6/C81",
            "location": "理工图书区A区2层"
        }
    ]
    
    # 状态筛选
    if status:
        recommendations = [r for r in recommendations if r["status"] == status]
    
    return {
        "code": 0,
        "message": "success",
        "data": {
            "recommendations": recommendations,
            "total": len(recommendations)
        }
    }

@router.post("/renew")
async def renew_book(
    borrow_id: int,
    student_id: str = Query("2024001", description="学生学号"),
    db: Session = Depends(deps.get_db)
):
    """
    图书续借
    """
    # 模拟续借逻辑
    new_return_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    
    renew_data = {
        "borrow_id": borrow_id,
        "student_id": student_id,
        "new_return_date": new_return_date,
        "renewal_count": 1,
        "max_renewal": 2,
        "renew_time": datetime.now().isoformat()
    }
    
    return {
        "code": 0,
        "message": f"续借成功，新归还日期：{new_return_date}",
        "data": renew_data
    } 