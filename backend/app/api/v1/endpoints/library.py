"""
图书馆模块 API
提供图书搜索、借阅记录、座位预约等功能 - 通过HTTP请求data-service获取数据
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query, Depends
from app.api.deps import get_current_user
# 🔄 使用HTTP客户端进行真正的HTTP请求，不导入Python模块
from app.core.http_client import http_client

router = APIRouter()

@router.get("/books/search", summary="图书搜索")
async def search_books(
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    category: Optional[str] = Query(None, description="图书分类"),
    author: Optional[str] = Query(None, description="作者"),
    page: int = Query(1, description="页码"),
    size: int = Query(20, description="每页数量"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """图书搜索"""
    try:
        offset = (page - 1) * size
        
        # 🔄 HTTP请求data-service搜索图书
        search_result = await http_client.search_books(
            keyword=keyword,
            category=category,
            author=author,
            limit=size,
            offset=offset
        )
        
        return {
            "code": 0,
            "message": "success",
            "data": search_result,
            "timestamp": datetime.now().isoformat(),
            "version": "v1.0"
        }
        
    except Exception as e:
        return {
            "code": 500,
            "message": f"图书搜索失败: {str(e)}",
            "data": None,
            "timestamp": datetime.now().isoformat(),
            "version": "v1.0"
        }

@router.get("/borrows", summary="获取借阅记录")
async def get_borrow_records(
    user_id: Optional[str] = Query(None, description="用户ID"),
    status: Optional[str] = Query(None, description="借阅状态"),
    page: int = Query(1, description="页码"),
    size: int = Query(20, description="每页数量"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """获取借阅记录"""
    try:
        # 使用当前用户ID或指定用户ID
        target_user_id = user_id or current_user["person_id"]
        
        # 权限检查：只能查看自己的记录，除非是管理员
        if target_user_id != current_user["person_id"] and current_user["person_type"] != "admin":
            raise HTTPException(status_code=403, detail="权限不足")
        
        offset = (page - 1) * size
        
        # 🔄 HTTP请求data-service获取借阅记录
        borrow_result = await http_client.get_user_borrow_records(
            user_id=target_user_id,
            status=status,
            limit=size,
            offset=offset
        )
        
        return {
            "code": 0,
            "message": "success",
            "data": borrow_result,
            "timestamp": datetime.now().isoformat(),
            "version": "v1.0"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        return {
            "code": 500,
            "message": f"获取借阅记录失败: {str(e)}",
            "data": None,
            "timestamp": datetime.now().isoformat(),
            "version": "v1.0"
        }

@router.post("/borrows/{book_id}", summary="借阅图书")
async def borrow_book(
    book_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """借阅图书"""
    try:
        # 🔄 HTTP请求data-service进行借阅
        borrow_data = {
            "record_id": f"BR{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "borrower_id": current_user["person_id"],
            "book_id": book_id,
            "borrow_date": datetime.now().isoformat(),
            "due_date": (datetime.now() + timedelta(days=30)).isoformat(),
            "status": "borrowed",
            "renewal_count": 0,
            "is_deleted": False
        }
        
        result = await http_client._request(
            "POST",
            "/insert/borrow_records",
            json_data=borrow_data
        )
        
        if result.get("status") == "success":
            return {
                "code": 0,
                "message": "借阅成功",
                "data": {
                    "record_id": borrow_data["record_id"],
                    "user_id": current_user["person_id"],
                    "book_id": book_id,
                    "borrow_date": borrow_data["borrow_date"],
                    "due_date": borrow_data["due_date"],
                    "status": "borrowed"
                },
                "timestamp": datetime.now().isoformat(),
                "version": "v1.0"
            }
        else:
            raise HTTPException(status_code=500, detail="借阅失败")
        
    except HTTPException:
        raise
    except Exception as e:
        return {
            "code": 500,
            "message": f"借阅失败: {str(e)}",
            "data": None,
            "timestamp": datetime.now().isoformat(),
            "version": "v1.0"
        }

@router.put("/borrows/{record_id}/renew", summary="续借图书")
async def renew_book(
    record_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """续借图书"""
    try:
        # 🔄 HTTP请求data-service进行续借
        new_due_date = (datetime.now() + timedelta(days=30)).isoformat()
        
        result = await http_client._request(
            "POST",
            "/update/borrow_records",
            json_data={
                "filters": {"record_id": record_id, "borrower_id": current_user["person_id"]},
                "updates": {
                    "due_date": new_due_date,
                    "renewal_count": "renewal_count + 1",  # 这需要数据库层处理
                    "updated_at": datetime.now().isoformat()
                }
            }
        )
        
        if result.get("status") == "success":
            return {
                "code": 0,
                "message": "续借成功",
                "data": {
                    "record_id": record_id,
                    "new_due_date": new_due_date,
                    "renew_date": datetime.now().isoformat()
                },
                "timestamp": datetime.now().isoformat(),
                "version": "v1.0"
            }
        else:
            raise HTTPException(status_code=500, detail="续借失败")
        
    except HTTPException:
        raise
    except Exception as e:
        return {
            "code": 500,
            "message": f"续借失败: {str(e)}",
            "data": None,
            "timestamp": datetime.now().isoformat(),
            "version": "v1.0"
        }

@router.get("/seats", summary="获取座位信息")
async def get_seats(
    floor: Optional[int] = Query(None, description="楼层"),
    area: Optional[str] = Query(None, description="区域"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """获取座位信息"""
    try:
        # 没有数据就生成数据，草拟吗的
        try:
            filters = {"is_deleted": False}
            if floor:
                filters["floor"] = floor
            if area:
                filters["area"] = area
            
            result = await http_client.query_table(
                "library_seats",
                filters=filters,
                limit=100,
                order_by="floor ASC, area ASC, seat_number ASC"
            )
            
            seats = result.get("data", {}).get("records", [])
        except Exception as e:
            # 没有数据就生成数据，草拟吗的
            print(e)
        # 构建座位统计
        total_seats = len(seats)
        available_seats = len([s for s in seats if s.get("is_available", True)])
        occupied_seats = total_seats - available_seats
        
        # 构建区域统计
        areas = {}
        for seat in seats:
            area_key = f"floor{seat.get('floor', 1)}_{seat.get('area', 'A')}"
            if area_key not in areas:
                areas[area_key] = {
                    "id": area_key,
                    "floor": seat.get("floor", 1),
                    "area": seat.get("area", "A区"),
                    "name": f"{seat.get('floor', 1)}楼{seat.get('area', 'A')}区",
                    "description": "学习区域",
                    "total": 0,
                    "available": 0
                }
            
            areas[area_key]["total"] += 1
            if seat.get("is_available", True):
                areas[area_key]["available"] += 1
        
        # 计算占用率
        for area in areas.values():
            area["availableSeats"] = area["available"]
            area["occupancyRate"] = round((area["total"] - area["available"]) / area["total"] * 100, 1) if area["total"] > 0 else 0
        
        seat_data = {
            "seats": seats,
            "statistics": {
                "total_seats": total_seats,
                "available_seats": available_seats,
                "occupied_seats": occupied_seats,
                "occupancy_rate": round(occupied_seats / total_seats * 100, 1) if total_seats > 0 else 0
            },
            "areas": list(areas.values())
        }
        
        return {
            "code": 0,
            "message": "success",
            "data": seat_data,
            "timestamp": datetime.now().isoformat(),
            "version": "v1.0"
        }
        
    except Exception as e:
        return {
            "code": 500,
            "message": f"获取座位信息失败: {str(e)}",
            "data": None,
            "timestamp": datetime.now().isoformat(),
            "version": "v1.0"
        }

@router.post("/seats/reserve", summary="预约座位")
async def reserve_seat(
    seat_id: str,
    duration: int = 4,  # 默认4小时
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """预约座位"""
    try:
        # 🔄 HTTP请求data-service进行座位预约
        start_time = datetime.now()
        end_time = start_time + timedelta(hours=duration)
        
        reservation_data = {
            "reservation_id": f"RSV{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "seat_id": seat_id,
            "user_id": current_user["person_id"],
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration": duration,
            "status": "confirmed",
            "created_at": datetime.now().isoformat(),
            "is_deleted": False
        }
        
        result = await http_client._request(
            "POST",
            "/insert/seat_reservations",
            json_data=reservation_data
        )
        
        if result.get("status") == "success":
            return {
                "code": 0,
                "message": "座位预约成功",
                "data": {
                    "reservation_id": reservation_data["reservation_id"],
                    "seat_id": seat_id,
                    "user_id": current_user["person_id"],
                    "start_time": reservation_data["start_time"],
                    "end_time": reservation_data["end_time"],
                    "duration": duration,
                    "status": "confirmed"
                },
                "timestamp": datetime.now().isoformat(),
                "version": "v1.0"
            }
        else:
            raise HTTPException(status_code=500, detail="座位预约失败")
        
    except HTTPException:
        raise
    except Exception as e:
        return {
            "code": 500,
            "message": f"座位预约失败: {str(e)}",
            "data": None,
            "timestamp": datetime.now().isoformat(),
            "version": "v1.0"
        }

@router.get("/my-reservations", summary="获取我的座位预约")
async def get_my_reservations(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """获取我的座位预约"""
    try:
        # 🔄 HTTP请求data-service获取用户的座位预约
        result = await http_client.query_table(
            "seat_reservations",
            filters={
                "user_id": current_user["person_id"],
                "is_deleted": False
            },
            limit=20,
            order_by="created_at DESC"
        )
        
        reservations = result.get("data", {}).get("records", [])
        
        return {
            "code": 0,
            "message": "success",
            "data": {
                "reservations": reservations
            },
            "timestamp": datetime.now().isoformat(),
            "version": "v1.0"
        }
        
    except Exception as e:
        return {
            "code": 500,
            "message": f"获取预约记录失败: {str(e)}",
            "data": None,
            "timestamp": datetime.now().isoformat(),
            "version": "v1.0"
        } 