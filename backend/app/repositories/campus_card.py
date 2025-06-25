"""
校园卡Repository
处理校园卡和交易记录的数据访问逻辑
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal
import logging

from .base import BaseRepository
from app.models.campus import CampusCard, Transaction

logger = logging.getLogger(__name__)


class CampusCardRepository(BaseRepository[CampusCard]):
    """校园卡Repository"""
    
    def __init__(self):
        super().__init__(CampusCard, "campus_cards")
    
    def _get_primary_key_field(self) -> str:
        return "card_id"
    
    async def find_by_person_id(self, person_id: str) -> Optional[CampusCard]:
        """根据人员ID查询校园卡"""
        try:
            return await self.find_one_by_filters({
                "holder_id": person_id,
                "is_active": True
            })
        except Exception as e:
            logger.error(f"根据人员ID查询校园卡失败: {e}")
            return None
    
    async def find_transactions(
        self,
        person_id: str,
        transaction_type: Optional[str] = None,
        date_range: Optional[Dict[str, datetime]] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Transaction]:
        """查询交易记录"""
        try:
            filters = {"person_id": person_id}
            
            if transaction_type:
                filters["transaction_type"] = transaction_type
            
            if date_range:
                if date_range.get("start"):
                    filters["transaction_time"] = {"$gte": date_range["start"]}
                if date_range.get("end"):
                    filters.setdefault("transaction_time", {})["$lte"] = date_range["end"]
            
            # 查询交易记录表
            result = await self.client.query_table(
                table_name="transactions",
                filters=filters,
                limit=limit,
                offset=offset,
                order_by="transaction_time DESC"
            )
            
            records = result.get("data", {}).get("records", [])
            return Transaction.from_list(records)
            
        except Exception as e:
            logger.error(f"查询交易记录失败: {e}")
            return []
    
    async def get_transaction_statistics(
        self,
        person_id: str,
        month: Optional[date] = None
    ) -> Dict[str, Any]:
        """获取交易统计信息"""
        try:
            base_filters = {"person_id": person_id}
            
            # 月份过滤
            if month:
                start_date = datetime(month.year, month.month, 1)
                if month.month == 12:
                    end_date = datetime(month.year + 1, 1, 1)
                else:
                    end_date = datetime(month.year, month.month + 1, 1)
                
                base_filters["transaction_time"] = {
                    "$gte": start_date,
                    "$lt": end_date
                }
            
            # 分类统计
            total_transactions = await self._count_transactions(base_filters)
            
            # 收入统计
            income_filters = {**base_filters, "transaction_type": {"$in": ["recharge", "refund", "transfer_in"]}}
            total_income = await self._sum_transaction_amount(income_filters)
            
            # 支出统计
            expense_filters = {**base_filters, "transaction_type": {"$in": ["consumption", "transfer_out", "fee"]}}
            total_expense = await self._sum_transaction_amount(expense_filters)
            
            # 各类别统计
            category_stats = await self._get_category_statistics(base_filters)
            
            return {
                "total_transactions": total_transactions,
                "total_income": float(total_income),
                "total_expense": float(total_expense),
                "net_change": float(total_income - total_expense),
                "category_statistics": category_stats,
                "period": month.strftime("%Y-%m") if month else "all_time"
            }
            
        except Exception as e:
            logger.error(f"获取交易统计失败: {e}")
            return {
                "total_transactions": 0,
                "total_income": 0,
                "total_expense": 0,
                "net_change": 0,
                "category_statistics": {},
                "period": "unknown"
            }
    
    async def get_daily_spending(
        self,
        person_id: str,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """获取每日消费统计"""
        try:
            # 计算日期范围
            end_date = datetime.now()
            start_date = datetime(end_date.year, end_date.month, end_date.day) - \
                        datetime.timedelta(days=days)
            
            filters = {
                "person_id": person_id,
                "transaction_type": "consumption",
                "transaction_time": {
                    "$gte": start_date,
                    "$lte": end_date
                }
            }
            
            transactions = await self.find_transactions(person_id, "consumption", {
                "start": start_date,
                "end": end_date
            }, limit=1000)
            
            # 按日期分组统计
            daily_stats = {}
            for transaction in transactions:
                date_key = transaction.transaction_time.date().isoformat()
                if date_key not in daily_stats:
                    daily_stats[date_key] = {
                        "date": date_key,
                        "total_amount": 0,
                        "transaction_count": 0
                    }
                
                daily_stats[date_key]["total_amount"] += float(transaction.amount)
                daily_stats[date_key]["transaction_count"] += 1
            
            # 转换为列表并排序
            result = list(daily_stats.values())
            result.sort(key=lambda x: x["date"])
            
            return result
            
        except Exception as e:
            logger.error(f"获取每日消费统计失败: {e}")
            return []
    
    async def find_frequent_merchants(
        self,
        person_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """查询常用商户"""
        try:
            transactions = await self.find_transactions(
                person_id, 
                "consumption", 
                limit=1000
            )
            
            # 按商户统计
            merchant_stats = {}
            for transaction in transactions:
                merchant = transaction.merchant_name or "未知商户"
                if merchant not in merchant_stats:
                    merchant_stats[merchant] = {
                        "merchant_name": merchant,
                        "total_amount": 0,
                        "transaction_count": 0,
                        "avg_amount": 0
                    }
                
                merchant_stats[merchant]["total_amount"] += float(transaction.amount)
                merchant_stats[merchant]["transaction_count"] += 1
            
            # 计算平均金额并排序
            for merchant, stats in merchant_stats.items():
                stats["avg_amount"] = stats["total_amount"] / stats["transaction_count"]
            
            result = list(merchant_stats.values())
            result.sort(key=lambda x: x["transaction_count"], reverse=True)
            
            return result[:limit]
            
        except Exception as e:
            logger.error(f"查询常用商户失败: {e}")
            return []
    
    async def _count_transactions(self, filters: Dict[str, Any]) -> int:
        """统计交易数量"""
        try:
            result = await self.client.query_table(
                table_name="transactions",
                filters=filters,
                limit=1
            )
            return result.get("data", {}).get("estimated_total", 0)
        except Exception as e:
            logger.error(f"统计交易数量失败: {e}")
            return 0
    
    async def _sum_transaction_amount(self, filters: Dict[str, Any]) -> Decimal:
        """计算交易金额总和"""
        try:
            # 这里应该使用聚合查询，简化实现
            transactions = await self.find_transactions(
                person_id=filters.get("person_id", ""),
                transaction_type=filters.get("transaction_type"),
                limit=10000  # 大数量查询用于统计
            )
            
            total = sum(t.amount for t in transactions if t.amount)
            return Decimal(str(total))
            
        except Exception as e:
            logger.error(f"计算交易金额总和失败: {e}")
            return Decimal("0")
    
    async def _get_category_statistics(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """获取分类统计"""
        try:
            # 简化实现，按交易类型分类
            stats = {}
            
            transaction_types = ["consumption", "recharge", "transfer_in", "transfer_out", "fee"]
            
            for t_type in transaction_types:
                type_filters = {**filters, "transaction_type": t_type}
                count = await self._count_transactions(type_filters)
                amount = await self._sum_transaction_amount(type_filters)
                
                if count > 0:
                    stats[t_type] = {
                        "count": count,
                        "total_amount": float(amount),
                        "avg_amount": float(amount) / count if count > 0 else 0
                    }
            
            return stats
            
        except Exception as e:
            logger.error(f"获取分类统计失败: {e}")
            return {}
    
    # === 新增方法：支持重构后的Controller ===
    
    async def find_transactions_paginated(
        self,
        person_id: str,
        filters: Dict[str, Any] = None,
        page: int = 1,
        size: int = 20
    ) -> Dict[str, Any]:
        """分页查询交易记录"""
        try:
            # 构建查询条件
            query_filters = {"person_id": person_id, "is_deleted": False}
            
            if filters:
                if filters.get("transaction_type"):
                    query_filters["transaction_type"] = filters["transaction_type"]
                if filters.get("date_from"):
                    query_filters["transaction_time__gte"] = filters["date_from"]
                if filters.get("date_to"):
                    query_filters["transaction_time__lte"] = filters["date_to"]
            
            offset = (page - 1) * size
            
            # 查询交易记录
            result = await self.client.query_table(
                table_name="transactions",
                filters=query_filters,
                limit=size,
                offset=offset,
                order_by="transaction_time DESC"
            )
            
            records = result.get("data", {}).get("records", [])
            
            # 转换为Transaction模型
            transactions = []
            for record in records:
                try:
                    transaction = Transaction.from_dict(record)
                    transactions.append(transaction.to_dict())
                except Exception as e:
                    logger.warning(f"转换交易记录失败: {e}")
                    transactions.append(record)  # 降级处理
            
            return {
                "transactions": transactions,
                "total": len(transactions),
                "page": page,
                "size": size,
                "pages": (len(transactions) + size - 1) // size if transactions else 0
            }
            
        except Exception as e:
            logger.error(f"分页查询交易记录失败: {e}")
            return {
                "transactions": [],
                "total": 0,
                "page": page,
                "size": size,
                "pages": 0
            }
    
    async def get_balance_info(self, person_id: str) -> Dict[str, Any]:
        """获取余额信息"""
        try:
            # 查询校园卡信息
            card = await self.find_by_person_id(person_id)
            
            if not card:
                return {
                    "balance": 0.0,
                    "frozen_amount": 0.0,
                    "available_balance": 0.0,
                    "_notice": "🚧 未找到校园卡信息"
                }
            
            card_dict = card.to_dict()
            
            # 计算可用余额
            balance = float(card_dict.get("balance", 0))
            frozen_amount = float(card_dict.get("frozen_amount", 0))
            available_balance = balance - frozen_amount
            
            return {
                "card_number": card_dict.get("card_number"),
                "balance": balance,
                "frozen_amount": frozen_amount,
                "available_balance": available_balance,
                "last_transaction_time": card_dict.get("last_transaction_time"),
                "status": card_dict.get("status", "active")
            }
            
        except Exception as e:
            logger.error(f"获取余额信息失败: {e}")
            return {
                "balance": 0.0,
                "frozen_amount": 0.0,
                "available_balance": 0.0,
                "_notice": "🚧 获取余额信息失败"
            }
    
    async def get_consumption_statistics(
        self,
        person_id: str,
        period: str = "month"
    ) -> Dict[str, Any]:
        """获取消费统计"""
        try:
            # 🚧 [未实现] 复杂的统计分析功能
            # TODO: 实现按时间周期的详细消费统计
            
            # 获取最近的交易记录进行简单统计
            recent_transactions_result = await self.client.query_table(
                table_name="transactions",
                filters={
                    "person_id": person_id,
                    "transaction_type": "consumption",
                    "is_deleted": False
                },
                limit=100,
                order_by="transaction_time DESC"
            )
            
            transactions = recent_transactions_result.get("data", {}).get("records", [])
            
            # 简单统计计算
            total_consumption = sum(float(t.get("amount", 0)) for t in transactions if float(t.get("amount", 0)) > 0)
            transaction_count = len(transactions)
            avg_consumption = total_consumption / transaction_count if transaction_count > 0 else 0
            
            # 分类统计（演示数据）
            category_stats = {
                "dining": {"amount": total_consumption * 0.6, "count": int(transaction_count * 0.6)},
                "shopping": {"amount": total_consumption * 0.2, "count": int(transaction_count * 0.2)},
                "transport": {"amount": total_consumption * 0.1, "count": int(transaction_count * 0.1)},
                "other": {"amount": total_consumption * 0.1, "count": int(transaction_count * 0.1)}
            }
            
            return {
                "period": period,
                "total_consumption": round(total_consumption, 2),
                "transaction_count": transaction_count,
                "avg_consumption": round(avg_consumption, 2),
                "category_statistics": category_stats,
                "_notice": f"🚧 {period}统计分析功能正在完善中，当前为简化版本"
            }
            
        except Exception as e:
            logger.error(f"获取消费统计失败: {e}")
            return {
                "period": period,
                "total_consumption": 0.0,
                "transaction_count": 0,
                "avg_consumption": 0.0,
                "category_statistics": {},
                "_notice": "🚧 统计计算失败，返回演示数据"
            }
    
    async def find_recent_transactions(
        self,
        person_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """获取最近交易记录"""
        try:
            result = await self.client.query_table(
                table_name="transactions",
                filters={
                    "person_id": person_id,
                    "is_deleted": False
                },
                limit=limit,
                order_by="transaction_time DESC"
            )
            
            records = result.get("data", {}).get("records", [])
            
            # 转换为标准格式
            transactions = []
            for record in records:
                try:
                    transaction = Transaction.from_dict(record)
                    transactions.append(transaction.to_dict())
                except Exception as e:
                    logger.warning(f"转换交易记录失败: {e}")
                    transactions.append(record)  # 降级处理
            
            return transactions
            
        except Exception as e:
            logger.error(f"获取最近交易记录失败: {e}")
            return [] 