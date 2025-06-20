"""
财务相关数据模型
包含Transaction（交易记录）、CampusCard（校园卡）模型
"""
from sqlalchemy import (
    Column, Integer, String, Boolean, Date, DateTime,
    Text, ForeignKey, JSON, Enum as SQLEnum, Numeric
)
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Index

from .base import BaseModel, TRANSACTION_TYPES, PAYMENT_METHODS


class CampusCard(BaseModel):
    """
    校园卡表 - 管理校园卡信息
    """
    __tablename__ = "campus_cards"
    
    # 基础信息
    card_id = Column(String(20), unique=True, nullable=False, comment="卡号")
    physical_card_number = Column(String(20), unique=True, nullable=True, comment="物理卡号")
    
    # 持卡人信息
    holder_id = Column(String(20), ForeignKey("persons.person_id"), nullable=False, comment="持卡人")
    
    # 卡片状态
    card_status = Column(String(20), default="active", comment="卡片状态：active/suspended/lost/damaged/expired")
    is_active = Column(Boolean, default=True, comment="是否激活")
    issue_date = Column(Date, nullable=False, comment="发卡日期")
    expire_date = Column(Date, nullable=True, comment="到期日期")
    
    # 账户信息
    balance = Column(Numeric(10, 2), default=0, comment="余额")
    credit_limit = Column(Numeric(10, 2), default=0, comment="透支额度")
    available_balance = Column(Numeric(10, 2), default=0, comment="可用余额")
    frozen_amount = Column(Numeric(10, 2), default=0, comment="冻结金额")
    
    # 密码信息
    pin_hash = Column(String(128), nullable=True, comment="密码哈希")
    pin_attempts = Column(Integer, default=0, comment="密码错误次数")
    is_pin_locked = Column(Boolean, default=False, comment="是否密码锁定")
    last_pin_change = Column(DateTime, nullable=True, comment="最后修改密码时间")
    
    # 使用限制
    daily_limit = Column(Numeric(8, 2), default=1000, comment="日消费限额")
    daily_spent = Column(Numeric(8, 2), default=0, comment="日消费金额")
    last_spent_date = Column(Date, nullable=True, comment="最后消费日期")
    
    # 充值限制
    recharge_limit = Column(Numeric(8, 2), default=5000, comment="单次充值限额")
    monthly_recharge_limit = Column(Numeric(10, 2), default=10000, comment="月充值限额")
    monthly_recharged = Column(Numeric(10, 2), default=0, comment="月充值金额")
    
    # 统计信息
    total_recharge = Column(Numeric(12, 2), default=0, comment="累计充值")
    total_consumption = Column(Numeric(12, 2), default=0, comment="累计消费")
    transaction_count = Column(Integer, default=0, comment="交易次数")
    
    # 卡片物理信息
    card_type = Column(String(20), default="standard", comment="卡片类型")
    chip_id = Column(String(50), nullable=True, comment="芯片ID")
    
    # 操作记录
    last_used_date = Column(DateTime, nullable=True, comment="最后使用时间")
    last_used_location = Column(String(50), nullable=True, comment="最后使用地点")
    
    # 挂失补卡
    is_reported_lost = Column(Boolean, default=False, comment="是否挂失")
    lost_report_date = Column(DateTime, nullable=True, comment="挂失时间")
    replacement_card_id = Column(String(20), nullable=True, comment="补办新卡号")
    
    # 关联关系
    holder = relationship("Person")
    transactions = relationship("Transaction", back_populates="campus_card")
    
    # 索引
    __table_args__ = (
        Index("idx_card_holder", "holder_id"),
        Index("idx_card_status", "card_status"),
        Index("idx_card_physical", "physical_card_number"),
        Index("idx_card_active", "is_active"),
    )
    
    def __repr__(self):
        return f"<CampusCard(id={self.card_id}, holder={self.holder_id}, balance={self.balance})>"
    
    def update_available_balance(self):
        """更新可用余额"""
        self.available_balance = self.balance + self.credit_limit - self.frozen_amount
    
    def can_consume(self, amount):
        """检查是否可以消费"""
        if not self.is_active or self.card_status != "active":
            return False
        
        # 检查可用余额
        if amount > self.available_balance:
            return False
        
        # 检查日限额
        from datetime import date
        today = date.today()
        if self.last_spent_date != today:
            self.daily_spent = 0
            self.last_spent_date = today
        
        if self.daily_spent + amount > self.daily_limit:
            return False
        
        return True
    
    def consume(self, amount, description="消费"):
        """消费"""
        if self.can_consume(amount):
            self.balance -= amount
            self.daily_spent += amount
            self.total_consumption += amount
            self.transaction_count += 1
            self.update_available_balance()
            return True
        return False
    
    def recharge(self, amount):
        """充值"""
        self.balance += amount
        self.total_recharge += amount
        self.transaction_count += 1
        self.update_available_balance()


class Transaction(BaseModel):
    """
    交易记录表 - 管理所有财务交易
    """
    __tablename__ = "transactions"
    
    # 基础信息
    transaction_id = Column(String(30), unique=True, nullable=False, comment="交易流水号")
    
    # 关联信息
    person_id = Column(String(20), ForeignKey("persons.person_id"), nullable=False, comment="交易人")
    campus_card_id = Column(String(20), ForeignKey("campus_cards.card_id"), nullable=True, comment="校园卡")
    
    # 交易信息
    transaction_type = Column(SQLEnum(*TRANSACTION_TYPES, name="transaction_type_enum"), nullable=False, comment="交易类型")
    payment_method = Column(SQLEnum(*PAYMENT_METHODS, name="payment_method_enum"), nullable=False, comment="支付方式")
    
    # 金额信息
    amount = Column(Numeric(10, 2), nullable=False, comment="交易金额")
    balance_before = Column(Numeric(10, 2), nullable=True, comment="交易前余额")
    balance_after = Column(Numeric(10, 2), nullable=True, comment="交易后余额")
    
    # 时间信息
    transaction_time = Column(DateTime, nullable=False, comment="交易时间")
    process_time = Column(DateTime, nullable=True, comment="处理时间")
    
    # 地点信息
    location_id = Column(String(20), ForeignKey("locations.location_id"), nullable=True, comment="交易地点")
    merchant_name = Column(String(100), nullable=True, comment="商户名称")
    terminal_id = Column(String(20), nullable=True, comment="终端编号")
    
    # 交易状态
    transaction_status = Column(String(20), default="pending", comment="交易状态：pending/success/failed/cancelled/refunded")
    
    # 交易描述
    description = Column(String(200), nullable=True, comment="交易描述")
    category = Column(String(50), nullable=True, comment="消费类别")
    subcategory = Column(String(50), nullable=True, comment="消费子类")
    
    # 订单信息
    order_id = Column(String(30), nullable=True, comment="订单号")
    external_transaction_id = Column(String(50), nullable=True, comment="外部交易号")
    
    # 手续费信息
    fee_amount = Column(Numeric(8, 2), default=0, comment="手续费")
    actual_amount = Column(Numeric(10, 2), nullable=True, comment="实际到账金额")
    
    # 对方信息（转账时）
    counterparty_id = Column(String(20), nullable=True, comment="对方账户")
    counterparty_name = Column(String(50), nullable=True, comment="对方姓名")
    
    # 退款信息
    refund_amount = Column(Numeric(10, 2), default=0, comment="已退款金额")
    refund_reason = Column(String(200), nullable=True, comment="退款原因")
    refund_date = Column(DateTime, nullable=True, comment="退款时间")
    
    # 风控信息
    risk_level = Column(String(20), default="low", comment="风险等级")
    is_suspicious = Column(Boolean, default=False, comment="是否可疑交易")
    verification_required = Column(Boolean, default=False, comment="是否需要验证")
    
    # 设备信息
    device_info = Column(JSON, default=dict, comment="设备信息")
    ip_address = Column(String(50), nullable=True, comment="IP地址")
    user_agent = Column(String(200), nullable=True, comment="用户代理")
    
    # 关联关系
    person = relationship("Person")
    campus_card = relationship("CampusCard", back_populates="transactions")
    location = relationship("Location")
    
    # 索引
    __table_args__ = (
        Index("idx_transaction_person", "person_id"),
        Index("idx_transaction_card", "campus_card_id"),
        Index("idx_transaction_time", "transaction_time"),
        Index("idx_transaction_type", "transaction_type"),
        Index("idx_transaction_status", "transaction_status"),
        Index("idx_transaction_amount", "amount"),
        Index("idx_transaction_location", "location_id"),
    )
    
    def __repr__(self):
        return f"<Transaction(id={self.transaction_id}, type={self.transaction_type}, amount={self.amount})>"
    
    @property
    def is_income(self):
        """是否为收入"""
        return self.transaction_type in ["recharge", "refund", "subsidy", "transfer_in"]
    
    @property
    def is_expense(self):
        """是否为支出"""
        return self.transaction_type in ["consumption", "transfer_out"]
    
    def process_transaction(self):
        """处理交易"""
        from datetime import datetime
        
        if self.transaction_status != "pending":
            return False
        
        try:
            if self.campus_card:
                if self.is_income:
                    self.campus_card.recharge(self.amount)
                elif self.is_expense:
                    if not self.campus_card.consume(self.amount, self.description):
                        self.transaction_status = "failed"
                        return False
                
                self.balance_before = self.campus_card.balance + (self.amount if self.is_expense else -self.amount)
                self.balance_after = self.campus_card.balance
            
            self.transaction_status = "success"
            self.process_time = datetime.now()
            return True
            
        except Exception as e:
            self.transaction_status = "failed"
            return False
    
    def refund_transaction(self, refund_amount=None, reason=""):
        """退款"""
        if self.transaction_status != "success" or self.transaction_type != "consumption":
            return False
        
        refund_amount = refund_amount or self.amount
        
        if refund_amount > (self.amount - self.refund_amount):
            return False
        
        # 创建退款交易记录
        # 这里应该创建新的Transaction记录
        self.refund_amount += refund_amount
        self.refund_reason = reason
        
        if self.refund_amount >= self.amount:
            self.transaction_status = "refunded"
        
        return True 