"""
校园卡接口
提供校园卡信息查询、消费记录、充值等功能
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

@router.get("/info", summary="获取校园卡信息")
async def get_campus_card_info(current_user = Depends(get_current_user)):
    """获取当前用户的校园卡信息"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        person_id = current_user.get("person_id")
        
        # 查询校园卡信息
        sql = """
            SELECT card_id, physical_card_number, card_status, is_active, issue_date, 
                   expire_date, balance, credit_limit, available_balance, frozen_amount,
                   daily_limit, daily_spent, last_spent_date, total_recharge, 
                   total_consumption, transaction_count, card_type, last_used_date
            FROM campus_cards 
            WHERE holder_id = ? AND is_deleted = 0
        """
        cursor.execute(sql, (person_id,))
        card_info = cursor.fetchone()
        
        if not card_info:
            raise HTTPException(status_code=404, detail="校园卡不存在")
        
        card_dict = dict(card_info)
        
        # 查询今日消费统计
        today = datetime.now().date()
        cursor.execute("""
            SELECT COUNT(*) as transaction_count, 
                   COALESCE(SUM(CASE WHEN transaction_type = 'consumption' THEN amount ELSE 0 END), 0) as daily_consumption,
                   COALESCE(SUM(CASE WHEN transaction_type = 'recharge' THEN amount ELSE 0 END), 0) as daily_recharge
            FROM transactions 
            WHERE person_id = ? AND DATE(transaction_time) = ?
        """, (person_id, today))
        
        daily_stats = cursor.fetchone()
        card_dict.update({
            "daily_stats": dict(daily_stats)
        })
        
        return {
            "code": 0,
            "message": "success",
            "data": {
                "card_info": card_dict
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"数据库查询失败: {str(e)}")
    finally:
        conn.close()


@router.get("/transactions", summary="获取消费记录")
async def get_campus_card_transactions(
    transaction_type: Optional[str] = Query(None, description="交易类型: consumption, recharge, transfer"),
    start_date: Optional[str] = Query(None, description="开始日期 YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期 YYYY-MM-DD"),
    limit: int = Query(20, description="返回条数"),
    offset: int = Query(0, description="偏移量"),
    current_user = Depends(get_current_user)
):
    """获取校园卡消费记录"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        person_id = current_user.get("person_id")
        
        # 构建查询条件
        where_conditions = ["person_id = ?", "is_deleted = 0"]
        params = [person_id]
        
        if transaction_type:
            where_conditions.append("transaction_type = ?")
            params.append(transaction_type)
        
        if start_date:
            where_conditions.append("DATE(transaction_time) >= ?")
            params.append(start_date)
        
        if end_date:
            where_conditions.append("DATE(transaction_time) <= ?")
            params.append(end_date)
        
        where_clause = " AND ".join(where_conditions)
        
        # 查询总数
        count_sql = f"SELECT COUNT(*) FROM transactions WHERE {where_clause}"
        cursor.execute(count_sql, params)
        total = cursor.fetchone()[0]
        
        # 查询交易记录
        sql = f"""
            SELECT transaction_id, transaction_type, amount, balance_before, balance_after,
                   transaction_time, location_id, merchant_name, description, category,
                   transaction_status, payment_method
            FROM transactions 
            WHERE {where_clause}
            ORDER BY transaction_time DESC
            LIMIT ? OFFSET ?
        """
        cursor.execute(sql, params + [limit, offset])
        transactions = [dict(row) for row in cursor.fetchall()]
        
        # 计算统计信息
        cursor.execute(f"""
            SELECT 
                COUNT(*) as total_count,
                COALESCE(SUM(CASE WHEN transaction_type = 'consumption' THEN amount ELSE 0 END), 0) as total_consumption,
                COALESCE(SUM(CASE WHEN transaction_type = 'recharge' THEN amount ELSE 0 END), 0) as total_recharge
            FROM transactions 
            WHERE {where_clause}
        """, params)
        
        stats = dict(cursor.fetchone())
        
        return {
            "code": 0,
            "message": "success",
            "data": {
                "transactions": transactions,
                "pagination": {
                    "total": total,
                    "limit": limit,
                    "offset": offset,
                    "has_more": offset + limit < total
                },
                "stats": stats
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"数据库查询失败: {str(e)}")
    finally:
        conn.close()


@router.get("/balance", summary="获取余额信息")
async def get_balance_info(current_user = Depends(get_current_user)):
    """获取校园卡余额信息"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        person_id = current_user.get("person_id")
        
        # 查询余额信息
        cursor.execute("""
            SELECT balance, available_balance, frozen_amount, daily_limit, daily_spent,
                   last_spent_date, total_recharge, total_consumption
            FROM campus_cards 
            WHERE holder_id = ? AND is_deleted = 0
        """, (person_id,))
        
        balance_info = cursor.fetchone()
        if not balance_info:
            raise HTTPException(status_code=404, detail="校园卡不存在")
        
        balance_dict = dict(balance_info)
        
        # 查询最近7天消费趋势
        seven_days_ago = datetime.now() - timedelta(days=7)
        cursor.execute("""
            SELECT DATE(transaction_time) as date, 
                   COALESCE(SUM(CASE WHEN transaction_type = 'consumption' THEN amount ELSE 0 END), 0) as daily_amount
            FROM transactions 
            WHERE person_id = ? AND transaction_time >= ? AND transaction_type = 'consumption'
            GROUP BY DATE(transaction_time)
            ORDER BY date
        """, (person_id, seven_days_ago))
        
        consumption_trend = [dict(row) for row in cursor.fetchall()]
        
        return {
            "code": 0,
            "message": "success",
            "data": {
                "balance_info": balance_dict,
                "consumption_trend": consumption_trend
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"数据库查询失败: {str(e)}")
    finally:
        conn.close()


@router.get("/statistics", summary="获取消费统计")
async def get_consumption_statistics(
    period: str = Query("month", description="统计周期: week, month, semester"),
    current_user = Depends(get_current_user)
):
    """获取消费统计信息"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        person_id = current_user.get("person_id")
        
        # 根据周期确定时间范围
        now = datetime.now()
        if period == "week":
            start_date = now - timedelta(days=7)
        elif period == "month":
            start_date = now - timedelta(days=30)
        else:  # semester
            start_date = now - timedelta(days=120)
        
        # 查询消费统计
        cursor.execute("""
            SELECT 
                COUNT(*) as transaction_count,
                COALESCE(SUM(CASE WHEN transaction_type = 'consumption' THEN amount ELSE 0 END), 0) as total_consumption,
                COALESCE(AVG(CASE WHEN transaction_type = 'consumption' THEN amount ELSE NULL END), 0) as avg_consumption,
                COALESCE(MAX(CASE WHEN transaction_type = 'consumption' THEN amount ELSE 0 END), 0) as max_consumption
            FROM transactions 
            WHERE person_id = ? AND transaction_time >= ? AND is_deleted = 0
        """, (person_id, start_date))
        
        stats = dict(cursor.fetchone())
        
        # 查询分类消费统计
        cursor.execute("""
            SELECT category, 
                   COUNT(*) as count,
                   COALESCE(SUM(amount), 0) as total_amount
            FROM transactions 
            WHERE person_id = ? AND transaction_time >= ? 
                  AND transaction_type = 'consumption' AND is_deleted = 0
            GROUP BY category
            ORDER BY total_amount DESC
        """, (person_id, start_date))
        
        category_stats = [dict(row) for row in cursor.fetchall()]
        
        # 查询商户消费统计
        cursor.execute("""
            SELECT merchant_name, 
                   COUNT(*) as count,
                   COALESCE(SUM(amount), 0) as total_amount
            FROM transactions 
            WHERE person_id = ? AND transaction_time >= ? 
                  AND transaction_type = 'consumption' AND is_deleted = 0
                  AND merchant_name IS NOT NULL
            GROUP BY merchant_name
            ORDER BY total_amount DESC
            LIMIT 10
        """, (person_id, start_date))
        
        merchant_stats = [dict(row) for row in cursor.fetchall()]
        
        return {
            "code": 0,
            "message": "success",
            "data": {
                "period": period,
                "date_range": {
                    "start_date": start_date.isoformat(),
                    "end_date": now.isoformat()
                },
                "overall_stats": stats,
                "category_stats": category_stats,
                "merchant_stats": merchant_stats
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"数据库查询失败: {str(e)}")
    finally:
        conn.close()


@router.get("/merchants", summary="获取商户列表")
async def get_merchants():
    """获取校园内商户列表"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 查询商户列表及其消费统计
        cursor.execute("""
            SELECT merchant_name, 
                   COUNT(*) as transaction_count,
                   COALESCE(SUM(amount), 0) as total_amount,
                   location_id
            FROM transactions 
            WHERE merchant_name IS NOT NULL AND is_deleted = 0 
                  AND transaction_type = 'consumption'
            GROUP BY merchant_name, location_id
            ORDER BY total_amount DESC
        """)
        
        merchants = [dict(row) for row in cursor.fetchall()]
        
        return {
            "code": 0,
            "message": "success",
            "data": {
                "merchants": merchants
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"数据库查询失败: {str(e)}")
    finally:
        conn.close() 