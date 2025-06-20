"""
权限管理相关数据模型
包含NetworkPermission、SystemAccess、PlatformConfig、AuditLog、DeviceRegistration、WorkflowInstance等模型
"""
from sqlalchemy import (
    Column, Integer, String, Boolean, Date, DateTime,
    Text, ForeignKey, JSON, Enum as SQLEnum, Numeric
)
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Index

from .base import BaseModel, NETWORK_TYPES, DEVICE_TYPES, SYSTEM_CODES


class NetworkPermission(BaseModel):
    """
    网络权限表 - 管理网络使用权限
    """
    __tablename__ = "network_permissions"
    
    # 基础信息
    permission_id = Column(String(20), unique=True, nullable=False, comment="权限ID")
    
    # 用户信息
    person_id = Column(String(20), ForeignKey("persons.person_id"), nullable=False, comment="用户")
    
    # 网络类型
    network_type = Column(SQLEnum(*NETWORK_TYPES, name="network_type_enum"), nullable=False, comment="网络类型")
    
    # 账户信息
    username = Column(String(50), nullable=False, comment="网络账户名")
    password_hash = Column(String(128), nullable=True, comment="密码哈希")
    
    # 设备限制
    max_devices = Column(Integer, default=3, comment="最大设备数")
    current_devices = Column(Integer, default=0, comment="当前设备数")
    
    # 流量限制
    monthly_quota_mb = Column(Integer, default=50000, comment="月流量限额（MB）")
    used_quota_mb = Column(Integer, default=0, comment="已用流量（MB）")
    daily_quota_mb = Column(Integer, default=2000, comment="日流量限额（MB）")
    daily_used_mb = Column(Integer, default=0, comment="日已用流量（MB）")
    
    # 时间限制
    access_start_time = Column(String(8), default="00:00:00", comment="允许访问开始时间")
    access_end_time = Column(String(8), default="23:59:59", comment="允许访问结束时间")
    weekend_access = Column(Boolean, default=True, comment="是否允许周末访问")
    
    # 访问控制
    allowed_ip_ranges = Column(JSON, default=list, comment="允许的IP范围")
    blocked_websites = Column(JSON, default=list, comment="屏蔽网站列表")
    allowed_applications = Column(JSON, default=list, comment="允许的应用列表")
    
    # 服务商信息
    provider = Column(String(20), nullable=False, comment="网络服务商")
    package_type = Column(String(20), default="basic", comment="套餐类型")
    monthly_fee = Column(Numeric(8, 2), default=0, comment="月费")
    
    # 状态信息
    permission_status = Column(String(20), default="active", comment="权限状态")
    activation_date = Column(Date, nullable=True, comment="激活日期")
    expiration_date = Column(Date, nullable=True, comment="到期日期")
    
    # 使用统计
    last_login_time = Column(DateTime, nullable=True, comment="最后登录时间")
    total_online_hours = Column(Integer, default=0, comment="总在线时长（小时）")
    login_count = Column(Integer, default=0, comment="登录次数")
    
    # 关联关系
    person = relationship("Person")
    device_registrations = relationship("DeviceRegistration", back_populates="network_permission")
    
    # 索引
    __table_args__ = (
        Index("idx_network_person", "person_id"),
        Index("idx_network_type", "network_type"),
        Index("idx_network_username", "username"),
        Index("idx_network_status", "permission_status"),
        Index("idx_network_provider", "provider"),
    )
    
    def __repr__(self):
        return f"<NetworkPermission(id={self.permission_id}, user={self.username}, type={self.network_type})>"
    
    @property
    def quota_utilization_rate(self):
        """流量使用率"""
        if self.monthly_quota_mb > 0:
            return (self.used_quota_mb / self.monthly_quota_mb) * 100
        return 0
    
    @property
    def is_quota_exceeded(self):
        """是否超出流量限额"""
        return self.used_quota_mb >= self.monthly_quota_mb
    
    @property
    def can_add_device(self):
        """是否可以添加设备"""
        return self.current_devices < self.max_devices
    
    def reset_daily_quota(self):
        """重置日流量统计"""
        self.daily_used_mb = 0
    
    def reset_monthly_quota(self):
        """重置月流量统计"""
        self.used_quota_mb = 0


class SystemAccess(BaseModel):
    """
    系统访问权限表 - 管理各系统平台访问权限
    """
    __tablename__ = "system_access"
    
    # 基础信息
    access_id = Column(String(20), unique=True, nullable=False, comment="访问权限ID")
    
    # 用户信息
    person_id = Column(String(20), ForeignKey("persons.person_id"), nullable=False, comment="用户")
    
    # 系统信息
    system_code = Column(SQLEnum(*SYSTEM_CODES, name="system_code_enum"), nullable=False, comment="系统代码")
    system_name = Column(String(50), nullable=False, comment="系统名称")
    
    # 账户信息
    system_username = Column(String(50), nullable=False, comment="系统用户名")
    password_hash = Column(String(128), nullable=True, comment="密码哈希")
    
    # 权限级别
    access_level = Column(String(20), default="user", comment="访问级别：admin/manager/user/readonly")
    role_permissions = Column(JSON, default=list, comment="角色权限列表")
    
    # 多平台支持
    platform_configs = Column(JSON, default=dict, comment="平台配置")
    max_concurrent_sessions = Column(Integer, default=1, comment="最大并发会话数")
    current_sessions = Column(Integer, default=0, comment="当前会话数")
    
    # 时间控制
    access_start_date = Column(Date, nullable=True, comment="访问开始日期")
    access_end_date = Column(Date, nullable=True, comment="访问结束日期")
    daily_access_hours = Column(Integer, default=24, comment="日访问时长限制（小时）")
    
    # 状态信息
    access_status = Column(String(20), default="active", comment="访问状态")
    is_locked = Column(Boolean, default=False, comment="是否锁定")
    lock_reason = Column(String(200), nullable=True, comment="锁定原因")
    
    # 审批信息
    approved_by = Column(String(10), ForeignKey("persons.employee_id"), nullable=True, comment="审批人")
    approval_date = Column(Date, nullable=True, comment="审批日期")
    approval_notes = Column(Text, nullable=True, comment="审批备注")
    
    # 使用统计
    last_access_time = Column(DateTime, nullable=True, comment="最后访问时间")
    total_access_count = Column(Integer, default=0, comment="总访问次数")
    failed_login_attempts = Column(Integer, default=0, comment="失败登录次数")
    
    # 安全设置
    two_factor_enabled = Column(Boolean, default=False, comment="是否启用双因子认证")
    ip_restrictions = Column(JSON, default=list, comment="IP访问限制")
    device_binding = Column(Boolean, default=False, comment="是否绑定设备")
    
    # 关联关系
    person = relationship("Person")
    approver = relationship("Person", foreign_keys=[approved_by])
    
    # 索引
    __table_args__ = (
        Index("idx_system_person", "person_id"),
        Index("idx_system_code", "system_code"),
        Index("idx_system_username", "system_username"),
        Index("idx_system_status", "access_status"),
        Index("idx_system_level", "access_level"),
    )
    
    def __repr__(self):
        return f"<SystemAccess(id={self.access_id}, user={self.system_username}, system={self.system_code})>"
    
    @property
    def is_admin(self):
        """是否为管理员"""
        return self.access_level == "admin"
    
    @property
    def can_login(self):
        """是否可以登录"""
        return self.access_status == "active" and not self.is_locked
    
    def lock_account(self, reason=""):
        """锁定账户"""
        self.is_locked = True
        self.lock_reason = reason
    
    def unlock_account(self):
        """解锁账户"""
        self.is_locked = False
        self.lock_reason = None
        self.failed_login_attempts = 0


class PlatformConfig(BaseModel):
    """
    平台配置表 - 管理多平台登录配置
    """
    __tablename__ = "platform_configs"
    
    # 基础信息
    config_id = Column(String(20), unique=True, nullable=False, comment="配置ID")
    
    # 用户信息
    person_id = Column(String(20), ForeignKey("persons.person_id"), nullable=False, comment="用户")
    
    # 平台信息
    platform_name = Column(String(50), nullable=False, comment="平台名称")
    platform_type = Column(String(20), nullable=False, comment="平台类型：web/mobile/desktop")
    platform_url = Column(String(200), nullable=True, comment="平台URL")
    
    # 认证配置
    auth_method = Column(String(20), default="password", comment="认证方式")
    sso_enabled = Column(Boolean, default=False, comment="是否启用单点登录")
    oauth_config = Column(JSON, default=dict, comment="OAuth配置")
    
    # 权限映射
    permission_mapping = Column(JSON, default=dict, comment="权限映射配置")
    role_mapping = Column(JSON, default=dict, comment="角色映射配置")
    
    # 会话管理
    session_timeout = Column(Integer, default=3600, comment="会话超时时间（秒）")
    max_idle_time = Column(Integer, default=1800, comment="最大空闲时间（秒）")
    remember_me_duration = Column(Integer, default=604800, comment="记住我时长（秒）")
    
    # 安全配置
    force_password_change = Column(Boolean, default=False, comment="是否强制修改密码")
    password_policy = Column(JSON, default=dict, comment="密码策略")
    login_retry_limit = Column(Integer, default=5, comment="登录重试限制")
    
    # 状态信息
    config_status = Column(String(20), default="active", comment="配置状态")
    last_sync_time = Column(DateTime, nullable=True, comment="最后同步时间")
    
    # 关联关系
    person = relationship("Person")
    
    # 索引
    __table_args__ = (
        Index("idx_platform_person", "person_id"),
        Index("idx_platform_name", "platform_name"),
        Index("idx_platform_type", "platform_type"),
        Index("idx_platform_status", "config_status"),
    )
    
    def __repr__(self):
        return f"<PlatformConfig(id={self.config_id}, platform={self.platform_name})>"


class DeviceRegistration(BaseModel):
    """
    设备注册表 - 管理用户设备注册信息
    """
    __tablename__ = "device_registrations"
    
    # 基础信息
    registration_id = Column(String(20), unique=True, nullable=False, comment="注册ID")
    
    # 关联信息
    person_id = Column(String(20), ForeignKey("persons.person_id"), nullable=False, comment="用户")
    network_permission_id = Column(String(20), ForeignKey("network_permissions.permission_id"), nullable=True, comment="网络权限")
    
    # 设备信息
    device_type = Column(SQLEnum(*DEVICE_TYPES, name="device_type_enum"), nullable=False, comment="设备类型")
    device_name = Column(String(100), nullable=False, comment="设备名称")
    device_model = Column(String(50), nullable=True, comment="设备型号")
    mac_address = Column(String(20), unique=True, nullable=False, comment="MAC地址")
    
    # 网络信息
    ip_address = Column(String(50), nullable=True, comment="分配的IP地址")
    dns_settings = Column(JSON, default=list, comment="DNS设置")
    
    # 状态信息
    registration_status = Column(String(20), default="pending", comment="注册状态")
    registration_date = Column(DateTime, nullable=False, comment="注册时间")
    last_online_time = Column(DateTime, nullable=True, comment="最后在线时间")
    
    # 使用统计
    total_online_hours = Column(Integer, default=0, comment="总在线时长")
    data_usage_mb = Column(Integer, default=0, comment="数据使用量（MB）")
    
    # 关联关系
    person = relationship("Person")
    network_permission = relationship("NetworkPermission", back_populates="device_registrations")
    
    # 索引
    __table_args__ = (
        Index("idx_device_person", "person_id"),
        Index("idx_device_network_permission", "network_permission_id"),
        Index("idx_device_mac", "mac_address"),
        Index("idx_device_type", "device_type"),
        Index("idx_device_status", "registration_status"),
    )
    
    def __repr__(self):
        return f"<DeviceRegistration(id={self.registration_id}, device={self.device_name}, mac={self.mac_address})>"


class AuditLog(BaseModel):
    """
    审计日志表 - 记录系统操作日志
    """
    __tablename__ = "audit_logs"
    
    # 基础信息
    log_id = Column(String(30), unique=True, nullable=False, comment="日志ID")
    
    # 操作信息
    person_id = Column(String(20), ForeignKey("persons.person_id"), nullable=True, comment="操作人")
    operation_type = Column(String(20), nullable=False, comment="操作类型")
    operation_description = Column(String(200), nullable=False, comment="操作描述")
    
    # 系统信息
    system_code = Column(String(10), nullable=True, comment="系统代码")
    module_name = Column(String(50), nullable=True, comment="模块名称")
    function_name = Column(String(50), nullable=True, comment="功能名称")
    
    # 时间信息
    operation_time = Column(DateTime, nullable=False, comment="操作时间")
    
    # 网络信息
    ip_address = Column(String(50), nullable=True, comment="操作IP")
    user_agent = Column(String(200), nullable=True, comment="用户代理")
    session_id = Column(String(50), nullable=True, comment="会话ID")
    
    # 操作结果
    operation_result = Column(String(20), default="success", comment="操作结果")
    error_message = Column(Text, nullable=True, comment="错误信息")
    
    # 操作详情
    before_data = Column(JSON, nullable=True, comment="操作前数据")
    after_data = Column(JSON, nullable=True, comment="操作后数据")
    operation_params = Column(JSON, nullable=True, comment="操作参数")
    
    # 风险评级
    risk_level = Column(String(20), default="low", comment="风险等级")
    is_sensitive = Column(Boolean, default=False, comment="是否敏感操作")
    
    # 关联关系
    person = relationship("Person")
    
    # 索引
    __table_args__ = (
        Index("idx_audit_person", "person_id"),
        Index("idx_audit_operation_type", "operation_type"),
        Index("idx_audit_time", "operation_time"),
        Index("idx_audit_system", "system_code"),
        Index("idx_audit_result", "operation_result"),
        Index("idx_audit_risk", "risk_level"),
        Index("idx_audit_sensitive", "is_sensitive"),
    )
    
    def __repr__(self):
        return f"<AuditLog(id={self.log_id}, operation={self.operation_type}, time={self.operation_time})>"


class WorkflowInstance(BaseModel):
    """
    工作流实例表 - 管理审批流程实例
    """
    __tablename__ = "workflow_instances"
    
    # 基础信息
    instance_id = Column(String(20), unique=True, nullable=False, comment="实例ID")
    workflow_name = Column(String(50), nullable=False, comment="工作流名称")
    workflow_version = Column(String(10), default="1.0", comment="工作流版本")
    
    # 申请信息
    applicant_id = Column(String(20), ForeignKey("persons.person_id"), nullable=False, comment="申请人")
    application_data = Column(JSON, nullable=False, comment="申请数据")
    
    # 流程状态
    current_step = Column(String(50), nullable=False, comment="当前步骤")
    workflow_status = Column(String(20), default="pending", comment="流程状态")
    
    # 时间信息
    start_time = Column(DateTime, nullable=False, comment="开始时间")
    end_time = Column(DateTime, nullable=True, comment="结束时间")
    
    # 审批历史
    approval_history = Column(JSON, default=list, comment="审批历史")
    current_approvers = Column(JSON, default=list, comment="当前审批人")
    
    # 结果信息
    final_result = Column(String(20), nullable=True, comment="最终结果")
    result_comments = Column(Text, nullable=True, comment="结果备注")
    
    # 关联关系
    applicant = relationship("Person")
    
    # 索引
    __table_args__ = (
        Index("idx_workflow_applicant", "applicant_id"),
        Index("idx_workflow_name", "workflow_name"),
        Index("idx_workflow_status", "workflow_status"),
        Index("idx_workflow_start_time", "start_time"),
    )
    
    def __repr__(self):
        return f"<WorkflowInstance(id={self.instance_id}, workflow={self.workflow_name}, status={self.workflow_status})>" 