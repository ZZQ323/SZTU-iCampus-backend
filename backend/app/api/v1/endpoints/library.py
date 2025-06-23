"""
图书馆接口
提供图书搜索、借阅记录、座位预约等功能
"""
import sqlite3
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from app.api.deps import get_current_user

router = APIRouter()

def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect('../../data-service/sztu_campus.db')
    conn.row_factory = sqlite3.Row
    return conn

@router.get("/books/search", summary="图书搜索")
async def search_books(
    q: str = Query(..., description="搜索关键词"),
    category: Optional[str] = Query(None, description="图书分类"),
    author: Optional[str] = Query(None, description="作者"),
    publisher: Optional[str] = Query(None, description="出版社"),
    limit: int = Query(20, description="返回条数"),
    offset: int = Query(0, description="偏移量")
):
    """图书搜索"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 构建搜索条件
        where_conditions = ["is_deleted = 0", "book_status = 'available'"]
        params = []
        
        # 关键词搜索（标题、作者、ISBN）
        if q:
            where_conditions.append("(title LIKE ? OR author LIKE ? OR isbn LIKE ?)")
            search_term = f"%{q}%"
            params.extend([search_term, search_term, search_term])
        
        if category:
            where_conditions.append("category = ?")
            params.append(category)
        
        if author:
            where_conditions.append("author LIKE ?")
            params.append(f"%{author}%")
        
        if publisher:
            where_conditions.append("publisher LIKE ?")
            params.append(f"%{publisher}%")
        
        where_clause = " AND ".join(where_conditions)
        
        # 查询总数
        count_sql = f"SELECT COUNT(*) FROM books WHERE {where_clause}"
        cursor.execute(count_sql, params)
        total = cursor.fetchone()[0]
        
        # 查询图书列表
        sql = f"""
            SELECT book_id, isbn, title, author, publisher, publication_date,
                   category, pages, price, language, total_copies, available_copies,
                   borrowed_copies, location_code, borrowable, loan_period_days,
                   rating, review_count
            FROM books 
            WHERE {where_clause}
            ORDER BY popularity_score DESC, publication_date DESC
            LIMIT ? OFFSET ?
        """
        cursor.execute(sql, params + [limit, offset])
        books = [dict(row) for row in cursor.fetchall()]
        
        return {
            "code": 0,
            "message": "success",
            "data": {
                "books": books,
                "search_params": {
                    "query": q,
                    "category": category,
                    "author": author,
                    "publisher": publisher
                },
                "pagination": {
                    "total": total,
                    "limit": limit,
                    "offset": offset,
                    "has_more": offset + limit < total
                }
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")
    finally:
        conn.close()


@router.get("/borrows", summary="获取借阅记录")
async def get_borrow_records(
    status: Optional[str] = Query(None, description="借阅状态: borrowed, returned, overdue"),
    limit: int = Query(20, description="返回条数"),
    offset: int = Query(0, description="偏移量"),
    current_user = Depends(get_current_user)
):
    """获取借阅记录"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        person_id = current_user.get("person_id")
        
        # 构建查询条件
        where_conditions = ["br.borrower_id = ?", "br.is_deleted = 0"]
        params = [person_id]
        
        if status:
            where_conditions.append("br.record_status = ?")
            params.append(status)
        
        where_clause = " AND ".join(where_conditions)
        
        # 查询借阅记录
        sql = f"""
            SELECT br.record_id, br.book_id, br.borrow_date, br.due_date, br.return_date,
                   br.renewal_count, br.max_renewals, br.record_status, br.is_overdue,
                   br.overdue_days, br.overdue_fine, br.total_fee,
                   b.title, b.author, b.isbn, b.publisher, b.location_code
            FROM borrow_records br
            JOIN books b ON br.book_id = b.book_id
            WHERE {where_clause}
            ORDER BY br.borrow_date DESC
            LIMIT ? OFFSET ?
        """
        cursor.execute(sql, params + [limit, offset])
        records = [dict(row) for row in cursor.fetchall()]
        
        # 计算统计信息
        cursor.execute(f"""
            SELECT 
                COUNT(*) as total_records,
                COUNT(CASE WHEN record_status = 'borrowed' THEN 1 END) as current_borrowed,
                COUNT(CASE WHEN is_overdue = 1 THEN 1 END) as overdue_count,
                COALESCE(SUM(total_fee), 0) as total_fees
            FROM borrow_records 
            WHERE borrower_id = ? AND is_deleted = 0
        """, (person_id,))
        
        stats = dict(cursor.fetchone())
        
        return {
            "code": 0,
            "message": "success",
            "data": {
                "records": records,
                "stats": stats,
                "pagination": {
                    "limit": limit,
                    "offset": offset,
                    "has_more": len(records) == limit
                }
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"数据库查询失败: {str(e)}")
    finally:
        conn.close()


@router.post("/borrows/{book_id}", summary="借阅图书")
async def borrow_book(
    book_id: str,
    current_user = Depends(get_current_user)
):
    """借阅图书"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        person_id = current_user.get("person_id")
        
        # 检查图书是否存在且可借阅
        cursor.execute("""
            SELECT book_id, title, available_copies, borrowable, loan_period_days
            FROM books 
            WHERE book_id = ? AND is_deleted = 0
        """, (book_id,))
        
        book = cursor.fetchone()
        if not book:
            raise HTTPException(status_code=404, detail="图书不存在")
        
        if not book["borrowable"]:
            raise HTTPException(status_code=400, detail="该图书不可外借")
        
        if book["available_copies"] <= 0:
            raise HTTPException(status_code=400, detail="图书已全部借出")
        
        # 检查用户是否已借阅此书
        cursor.execute("""
            SELECT record_id FROM borrow_records 
            WHERE borrower_id = ? AND book_id = ? AND record_status = 'borrowed' AND is_deleted = 0
        """, (person_id, book_id))
        
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="您已借阅此书")
        
        # 创建借阅记录
        record_id = f"BR{datetime.now().strftime('%Y%m%d%H%M%S')}{person_id[-4:]}"
        borrow_date = datetime.now()
        due_date = borrow_date + timedelta(days=book["loan_period_days"])
        
        cursor.execute("""
            INSERT INTO borrow_records 
            (record_id, book_id, borrower_id, borrow_date, due_date, max_renewals,
             record_status, is_overdue, condition_on_borrow, created_at, updated_at, is_deleted, status, is_active)
            VALUES (?, ?, ?, ?, ?, 2, 'borrowed', 0, 'good', 
                    CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0, 'active', 1)
        """, (record_id, book_id, person_id, borrow_date, due_date))
        
        # 更新图书可借数量
        cursor.execute("""
            UPDATE books 
            SET available_copies = available_copies - 1,
                borrowed_copies = borrowed_copies + 1,
                borrow_count = borrow_count + 1
            WHERE book_id = ?
        """, (book_id,))
        
        conn.commit()
        
        return {
            "code": 0,
            "message": "借阅成功",
            "data": {
                "record_id": record_id,
                "book_title": book["title"],
                "borrow_date": borrow_date.isoformat(),
                "due_date": due_date.isoformat(),
                "loan_period_days": book["loan_period_days"]
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"借阅失败: {str(e)}")
    finally:
        conn.close()


@router.put("/borrows/{record_id}/renew", summary="续借图书")
async def renew_book(
    record_id: str,
    current_user = Depends(get_current_user)
):
    """续借图书"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        person_id = current_user.get("person_id")
        
        # 查询借阅记录
        cursor.execute("""
            SELECT br.record_id, br.book_id, br.due_date, br.renewal_count, br.max_renewals,
                   br.record_status, b.title, b.loan_period_days
            FROM borrow_records br
            JOIN books b ON br.book_id = b.book_id
            WHERE br.record_id = ? AND br.borrower_id = ? AND br.is_deleted = 0
        """, (record_id, person_id))
        
        record = cursor.fetchone()
        if not record:
            raise HTTPException(status_code=404, detail="借阅记录不存在")
        
        if record["record_status"] != "borrowed":
            raise HTTPException(status_code=400, detail="只能续借未归还的图书")
        
        if record["renewal_count"] >= record["max_renewals"]:
            raise HTTPException(status_code=400, detail="已达到最大续借次数")
        
        # 计算新的到期日期
        current_due_date = datetime.fromisoformat(record["due_date"])
        new_due_date = current_due_date + timedelta(days=record["loan_period_days"])
        
        # 更新借阅记录
        cursor.execute("""
            UPDATE borrow_records 
            SET due_date = ?, 
                renewal_count = renewal_count + 1,
                last_renewal_date = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP
            WHERE record_id = ?
        """, (new_due_date, record_id))
        
        conn.commit()
        
        return {
            "code": 0,
            "message": "续借成功",
            "data": {
                "record_id": record_id,
                "book_title": record["title"],
                "new_due_date": new_due_date.isoformat(),
                "renewal_count": record["renewal_count"] + 1,
                "max_renewals": record["max_renewals"]
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"续借失败: {str(e)}")
    finally:
        conn.close()


@router.get("/seats", summary="获取座位信息")
async def get_seats():
    """获取座位信息（模拟数据）"""
    
    # 模拟座位数据
    seats_data = {
        "floors": [
            {
                "floor": 1,
                "name": "一楼阅览区",
                "total_seats": 200,
                "available_seats": 156,
                "areas": [
                    {"area_id": "1A", "name": "期刊阅览区", "total": 50, "available": 35},
                    {"area_id": "1B", "name": "普通阅览区", "total": 150, "available": 121}
                ]
            },
            {
                "floor": 2,
                "name": "二楼自习区",
                "total_seats": 300,
                "available_seats": 89,
                "areas": [
                    {"area_id": "2A", "name": "安静自习区", "total": 200, "available": 45},
                    {"area_id": "2B", "name": "讨论学习区", "total": 100, "available": 44}
                ]
            }
        ],
        "update_time": datetime.now().isoformat()
    }
    
    return {
        "code": 0,
        "message": "success",
        "data": seats_data,
        "timestamp": datetime.now().isoformat()
    }


@router.post("/seats/reserve", summary="预约座位")
async def reserve_seat(
    area_id: str,
    duration_hours: int = 4,
    current_user = Depends(get_current_user)
):
    """预约座位（模拟实现）"""
    
    # 模拟预约逻辑
    seat_number = f"{area_id}-{datetime.now().strftime('%H%M%S')}"
    start_time = datetime.now()
    end_time = start_time + timedelta(hours=duration_hours)
    
    return {
        "code": 0,
        "message": "座位预约成功",
        "data": {
            "reservation_id": f"RSV{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "area_id": area_id,
            "seat_number": seat_number,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_hours": duration_hours
        },
        "timestamp": datetime.now().isoformat()
    } 