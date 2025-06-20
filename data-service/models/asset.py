"""
资产管理数据模型
包含Asset（资产）模型
"""
from sqlalchemy import (
    Column, Integer, String, Boolean, Date, DateTime,
    Text, ForeignKey, JSON, Enum as SQLEnum, Numeric
)
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Index

from .base import BaseModel, ASSET_STATUSES


class Asset(BaseModel):
    """
    资产表 - 管理校园内各类资产信息
    """
    __tablename__ = "assets"
    
    # 基础信息
    asset_id = Column(String(20), unique=True, nullable=False, comment="资产编号")
    asset_name = Column(String(100), nullable=False, comment="资产名称")
    asset_model = Column(String(50), nullable=True, comment="型号规格")
    asset_brand = Column(String(50), nullable=True, comment="品牌")
    
    # 分类信息
    category = Column(String(30), nullable=False, comment="资产类别")
    subcategory = Column(String(50), nullable=True, comment="子类别")
    asset_type = Column(String(50), nullable=False, comment="资产类型")
    
    # 位置信息
    location_id = Column(String(20), ForeignKey("locations.location_id"), nullable=True, comment="所在位置")
    building_code = Column(String(10), nullable=True, comment="建筑编码")
    room_number = Column(String(20), nullable=True, comment="房间号")
    
    # 财务信息
    purchase_price = Column(Numeric(12, 2), nullable=True, comment="购买价格")
    current_value = Column(Numeric(12, 2), nullable=True, comment="当前价值")
    depreciation_rate = Column(Numeric(5, 2), default=0, comment="折旧率（%）")
    
    # 购买信息
    purchase_date = Column(Date, nullable=True, comment="购买日期")
    supplier = Column(String(100), nullable=True, comment="供应商")
    purchase_contract = Column(String(50), nullable=True, comment="采购合同号")
    warranty_period = Column(Integer, nullable=True, comment="保修期（月）")
    warranty_end_date = Column(Date, nullable=True, comment="保修到期日期")
    
    # 使用信息
    asset_status = Column(SQLEnum(*ASSET_STATUSES, name="asset_status_enum"), default="in_use", comment="资产状态")
    user_id = Column(String(20), ForeignKey("persons.person_id"), nullable=True, comment="使用人")
    manager_id = Column(String(10), ForeignKey("persons.employee_id"), nullable=True, comment="管理员")
    
    # 技术规格
    specifications = Column(JSON, default=dict, comment="技术规格")
    configuration = Column(JSON, default=dict, comment="配置信息")
    
    # 维护信息
    last_maintenance = Column(Date, nullable=True, comment="上次维护日期")
    next_maintenance = Column(Date, nullable=True, comment="下次维护日期")
    maintenance_cycle = Column(Integer, nullable=True, comment="维护周期（天）")
    maintenance_cost = Column(Numeric(10, 2), default=0, comment="维护费用")
    maintenance_notes = Column(Text, nullable=True, comment="维护记录")
    
    # 安全信息
    security_level = Column(String(20), default="normal", comment="安全等级")
    access_restrictions = Column(JSON, default=list, comment="访问限制")
    
    # 网络信息（仅适用于网络设备）
    ip_address = Column(String(50), nullable=True, comment="IP地址")
    mac_address = Column(String(20), nullable=True, comment="MAC地址")
    network_info = Column(JSON, default=dict, comment="网络配置信息")
    
    # 环境要求
    temperature_range = Column(String(20), nullable=True, comment="温度要求")
    humidity_range = Column(String(20), nullable=True, comment="湿度要求")
    power_requirements = Column(String(50), nullable=True, comment="电力要求")
    
    # 处置信息
    disposal_date = Column(Date, nullable=True, comment="处置日期")
    disposal_method = Column(String(50), nullable=True, comment="处置方式")
    disposal_value = Column(Numeric(10, 2), nullable=True, comment="处置价值")
    
    # 附件信息
    photos = Column(JSON, default=list, comment="照片列表")
    documents = Column(JSON, default=list, comment="相关文档")
    
    # 关联关系
    location = relationship("Location", back_populates="assets")
    user = relationship("Person", foreign_keys=[user_id])
    manager = relationship("Person", foreign_keys=[manager_id])
    
    # 索引
    __table_args__ = (
        Index("idx_asset_category", "category"),
        Index("idx_asset_status", "asset_status"),
        Index("idx_asset_location", "location_id"),
        Index("idx_asset_user", "user_id"),
        Index("idx_asset_manager", "manager_id"),
        Index("idx_asset_purchase_date", "purchase_date"),
    )
    
    def __repr__(self):
        return f"<Asset(id={self.asset_id}, name={self.asset_name}, status={self.asset_status})>"
    
    @property
    def age_years(self):
        """资产使用年限"""
        if self.purchase_date:
            from datetime import date
            today = date.today()
            return today.year - self.purchase_date.year
        return None
    
    @property
    def is_under_warranty(self):
        """是否在保修期内"""
        if self.warranty_end_date:
            from datetime import date
            return date.today() <= self.warranty_end_date
        return False
    
    @property
    def needs_maintenance(self):
        """是否需要维护"""
        if self.next_maintenance:
            from datetime import date
            return date.today() >= self.next_maintenance
        return False
    
    def calculate_depreciation(self):
        """计算当前价值（考虑折旧）"""
        if self.purchase_price and self.depreciation_rate and self.purchase_date:
            from datetime import date
            years = self.age_years or 0
            depreciation_amount = self.purchase_price * (self.depreciation_rate / 100) * years
            self.current_value = max(0, self.purchase_price - depreciation_amount)
    
    def schedule_next_maintenance(self):
        """安排下次维护"""
        if self.maintenance_cycle and self.last_maintenance:
            from datetime import timedelta
            self.next_maintenance = self.last_maintenance + timedelta(days=self.maintenance_cycle) 