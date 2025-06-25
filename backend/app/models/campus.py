"""
校园服务相关数据模型
包含公告、活动、校园卡、交易等校园服务数据
"""
from datetime import datetime, date
from typing import Optional
from decimal import Decimal
from pydantic import Field, validator
from .base import BaseModel


class Announcement(BaseModel):
    """公告模型"""
    
    announcement_id: str = Field(..., description="公告ID")
    title: str = Field(..., description="标题")
    content: str = Field(..., description="内容")
    content_html: Optional[str] = Field(None, description="HTML格式内容")
    summary: Optional[str] = Field(None, description="摘要")
    
    # 发布信息
    publisher_id: str = Field(..., description="发布者ID")
    publisher_name: str = Field(..., description="发布者姓名")
    department: str = Field(..., description="发布部门")
    
    # 分类信息
    category: str = Field("general", description="公告类别")
    priority: str = Field("normal", description="优先级：low/normal/high/urgent")
    
    # 状态控制
    is_urgent: bool = Field(False, description="是否紧急")
    is_pinned: bool = Field(False, description="是否置顶")
    
    # 时间控制
    publish_time: datetime = Field(..., description="发布时间")
    effective_date: Optional[datetime] = Field(None, description="生效时间")
    expire_date: Optional[datetime] = Field(None, description="过期时间")
    
    # 目标受众
    target_audience: str = Field("all", description="目标受众")
    target_colleges: Optional[str] = Field(None, description="目标学院JSON")
    target_majors: Optional[str] = Field(None, description="目标专业JSON")
    target_grades: Optional[str] = Field(None, description="目标年级JSON")
    
    # 互动统计
    view_count: int = Field(0, description="浏览次数")
    like_count: int = Field(0, description="点赞次数")
    comment_count: int = Field(0, description="评论次数")
    
    # 附件信息
    attachments: Optional[str] = Field(None, description="附件JSON")
    cover_image_url: Optional[str] = Field(None, description="封面图片URL")
    
    # 审核信息
    reviewed_by: Optional[str] = Field(None, description="审核人")
    review_time: Optional[datetime] = Field(None, description="审核时间")
    review_status: str = Field("approved", description="审核状态")
    
    @property
    def primary_key(self) -> str:
        return self.announcement_id
    
    @property
    def is_active(self) -> bool:
        """是否有效"""
        now = datetime.now()
        if self.effective_date and now < self.effective_date:
            return False
        if self.expire_date and now > self.expire_date:
            return False
        return True
    
    @validator('priority')
    def validate_priority(cls, v):
        allowed_priorities = ['low', 'normal', 'high', 'urgent']
        if v not in allowed_priorities:
            raise ValueError(f'priority must be one of {allowed_priorities}')
        return v


class Event(BaseModel):
    """活动模型"""
    
    event_id: str = Field(..., description="活动ID")
    title: str = Field(..., description="活动标题")
    description: str = Field(..., description="活动描述")
    short_description: Optional[str] = Field(None, description="简短描述")
    
    # 活动分类
    event_type: str = Field("general", description="活动类型")
    category: Optional[str] = Field(None, description="活动分类")
    
    # 组织信息
    organizer_id: str = Field(..., description="组织者ID")
    organizer_name: str = Field(..., description="组织者名称")
    co_organizers: Optional[str] = Field(None, description="协办方JSON")
    
    # 时间安排
    start_time: datetime = Field(..., description="开始时间")
    end_time: datetime = Field(..., description="结束时间")
    registration_start: Optional[datetime] = Field(None, description="报名开始时间")
    registration_end: Optional[datetime] = Field(None, description="报名结束时间")
    duration_hours: Optional[int] = Field(None, description="活动时长(小时)")
    
    # 地点信息
    location_id: Optional[str] = Field(None, description="地点ID")
    location_name: Optional[str] = Field(None, description="地点名称")
    venue_details: Optional[str] = Field(None, description="场地详情")
    address: Optional[str] = Field(None, description="详细地址")
    
    # 容量管理
    capacity: Optional[int] = Field(None, description="活动容量")
    registration_required: bool = Field(False, description="是否需要报名")
    max_participants: Optional[int] = Field(None, description="最大参与人数")
    current_participants: int = Field(0, description="当前参与人数")
    registration_fee: Optional[Decimal] = Field(Decimal("0.00"), description="报名费用")
    
    # 参与要求
    requirements: Optional[str] = Field(None, description="参与要求")
    eligibility_criteria: Optional[str] = Field(None, description="资格标准")
    
    # 目标受众
    target_audience: str = Field("all", description="目标受众")
    target_colleges: Optional[str] = Field(None, description="目标学院JSON")
    target_majors: Optional[str] = Field(None, description="目标专业JSON")
    target_grades: Optional[str] = Field(None, description="目标年级JSON")
    
    # 状态控制
    is_public: bool = Field(True, description="是否公开")
    approval_status: str = Field("approved", description="审批状态")
    
    # 媒体资源
    poster_url: Optional[str] = Field(None, description="海报URL")
    images: Optional[str] = Field(None, description="图片JSON")
    video_url: Optional[str] = Field(None, description="视频URL")
    
    # 联系信息
    contact_person: Optional[str] = Field(None, description="联系人")
    contact_phone: Optional[str] = Field(None, description="联系电话")
    contact_email: Optional[str] = Field(None, description="联系邮箱")
    
    # 统计信息
    view_count: int = Field(0, description="浏览次数")
    interest_count: int = Field(0, description="感兴趣人数")
    
    @property
    def primary_key(self) -> str:
        return self.event_id
    
    @property
    def is_upcoming(self) -> bool:
        """是否即将到来"""
        return self.start_time > datetime.now()
    
    @property
    def is_ongoing(self) -> bool:
        """是否正在进行"""
        now = datetime.now()
        return self.start_time <= now <= self.end_time
    
    @property
    def registration_open(self) -> bool:
        """是否可以报名"""
        if not self.registration_required:
            return False
        now = datetime.now()
        if self.registration_start and now < self.registration_start:
            return False
        if self.registration_end and now > self.registration_end:
            return False
        return True


class CampusCard(BaseModel):
    """校园卡模型"""
    
    card_id: str = Field(..., description="校园卡ID")
    physical_card_number: Optional[str] = Field(None, description="实体卡号")
    holder_id: str = Field(..., description="持卡人ID")
    
    # 卡片状态
    card_status: Optional[str] = Field(None, description="卡片状态")
    issue_date: Optional[date] = Field(None, description="发卡日期")
    expire_date: Optional[date] = Field(None, description="过期日期")
    
    # 余额信息
    balance: Optional[Decimal] = Field(None, description="余额")
    credit_limit: Optional[Decimal] = Field(None, description="信用额度")
    available_balance: Optional[Decimal] = Field(None, description="可用余额")
    frozen_amount: Optional[Decimal] = Field(None, description="冻结金额")
    
    # 密码信息
    pin_hash: Optional[str] = Field(None, description="密码哈希")
    pin_attempts: int = Field(0, description="密码尝试次数")
    is_pin_locked: bool = Field(False, description="密码是否锁定")
    last_pin_change: Optional[datetime] = Field(None, description="最后密码修改时间")
    
    # 限额设置
    daily_limit: Optional[Decimal] = Field(None, description="日限额")
    daily_spent: Optional[Decimal] = Field(None, description="今日已消费")
    last_spent_date: Optional[date] = Field(None, description="最后消费日期")
    recharge_limit: Optional[Decimal] = Field(None, description="充值限额")
    monthly_recharge_limit: Optional[Decimal] = Field(None, description="月充值限额")
    monthly_recharged: Optional[Decimal] = Field(None, description="本月已充值")
    
    # 统计信息
    total_recharge: Optional[Decimal] = Field(None, description="累计充值")
    total_consumption: Optional[Decimal] = Field(None, description="累计消费")
    transaction_count: Optional[int] = Field(None, description="交易次数")
    
    # 卡片信息
    card_type: Optional[str] = Field(None, description="卡片类型")
    chip_id: Optional[str] = Field(None, description="芯片ID")
    
    # 使用记录
    last_used_date: Optional[datetime] = Field(None, description="最后使用时间")
    last_used_location: Optional[str] = Field(None, description="最后使用地点")
    
    # 挂失信息
    is_reported_lost: bool = Field(False, description="是否挂失")
    lost_report_date: Optional[datetime] = Field(None, description="挂失日期")
    replacement_card_id: Optional[str] = Field(None, description="补办卡ID")
    
    @property
    def primary_key(self) -> str:
        return self.card_id
    
    @property
    def is_valid(self) -> bool:
        """是否有效"""
        if self.card_status in ["suspended", "lost", "expired"]:
            return False
        if self.expire_date and self.expire_date < date.today():
            return False
        return True


class Transaction(BaseModel):
    """交易记录模型"""
    
    transaction_id: str = Field(..., description="交易ID")
    person_id: str = Field(..., description="人员ID")
    campus_card_id: Optional[str] = Field(None, description="校园卡ID")
    
    # 交易基本信息
    transaction_type: str = Field(..., description="交易类型")
    payment_method: str = Field(..., description="支付方式")
    amount: Decimal = Field(..., description="交易金额")
    
    # 余额信息
    balance_before: Optional[Decimal] = Field(None, description="交易前余额")
    balance_after: Optional[Decimal] = Field(None, description="交易后余额")
    
    # 时间信息
    transaction_time: datetime = Field(..., description="交易时间")
    process_time: Optional[datetime] = Field(None, description="处理时间")
    
    # 地点信息
    location_id: Optional[str] = Field(None, description="交易地点ID")
    merchant_name: Optional[str] = Field(None, description="商户名称")
    terminal_id: Optional[str] = Field(None, description="终端ID")
    
    # 交易状态
    transaction_status: Optional[str] = Field(None, description="交易状态")
    description: Optional[str] = Field(None, description="交易描述")
    category: Optional[str] = Field(None, description="交易分类")
    subcategory: Optional[str] = Field(None, description="子分类")
    
    # 订单信息
    order_id: Optional[str] = Field(None, description="订单ID")
    external_transaction_id: Optional[str] = Field(None, description="外部交易ID")
    
    # 费用信息
    fee_amount: Optional[Decimal] = Field(None, description="手续费")
    actual_amount: Optional[Decimal] = Field(None, description="实际金额")
    
    # 对方信息
    counterparty_id: Optional[str] = Field(None, description="对方ID")
    counterparty_name: Optional[str] = Field(None, description="对方名称")
    
    # 退款信息
    refund_amount: Optional[Decimal] = Field(None, description="退款金额")
    refund_reason: Optional[str] = Field(None, description="退款原因")
    refund_date: Optional[datetime] = Field(None, description="退款日期")
    
    # 风控信息
    risk_level: Optional[str] = Field(None, description="风险等级")
    is_suspicious: bool = Field(False, description="是否可疑")
    verification_required: bool = Field(False, description="是否需要验证")
    
    # 设备信息
    device_info: Optional[str] = Field(None, description="设备信息JSON")
    ip_address: Optional[str] = Field(None, description="IP地址")
    user_agent: Optional[str] = Field(None, description="用户代理")
    
    @property
    def primary_key(self) -> str:
        return self.transaction_id
    
    @property
    def is_income(self) -> bool:
        """是否为收入"""
        return self.transaction_type in ["recharge", "refund", "transfer_in"]
    
    @property
    def is_expense(self) -> bool:
        """是否为支出"""
        return self.transaction_type in ["consumption", "transfer_out", "fee"] 