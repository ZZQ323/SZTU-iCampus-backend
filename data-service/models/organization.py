"""
组织架构相关数据模型
包含College（学院）、Major（专业）、Department（部门）、Location（地点）、RoomOccupation（教室占用）
"""
from sqlalchemy import (
    Column, Integer, String, Boolean, Date, DateTime, Time,
    Text, ForeignKey, JSON, Enum as SQLEnum, Numeric
)
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Index

from .base import BaseModel, ROOM_TYPES


class College(BaseModel):
    """
    学院表 - 管理学院信息
    """
    __tablename__ = "colleges"
    
    # 基础信息
    college_id = Column(String(10), unique=True, nullable=False, comment="学院编码，如C001")
    college_name = Column(String(50), nullable=False, comment="学院名称")
    college_code = Column(String(10), nullable=False, comment="学院简称，如CS、MATH")
    
    # 联系信息
    phone = Column(String(20), nullable=True, comment="联系电话")
    email = Column(String(100), nullable=True, comment="邮箱地址")
    website = Column(String(200), nullable=True, comment="学院官网")
    
    # 地址信息
    office_location = Column(String(100), nullable=True, comment="办公地点")
    main_building = Column(String(20), nullable=True, comment="主要教学楼")
    
    # 人员配置
    dean_id = Column(String(10), ForeignKey("persons.employee_id"), nullable=True, comment="院长")
    vice_dean_id = Column(String(10), ForeignKey("persons.employee_id"), nullable=True, comment="副院长")
    secretary_id = Column(String(10), ForeignKey("persons.employee_id"), nullable=True, comment="秘书")
    
    # 统计信息
    total_teachers = Column(Integer, default=0, comment="教师总数")
    total_students = Column(Integer, default=0, comment="学生总数")
    total_majors = Column(Integer, default=0, comment="专业总数")
    
    # 描述信息
    description = Column(Text, nullable=True, comment="学院简介")
    mission = Column(Text, nullable=True, comment="使命愿景")
    
    # 关联关系
    majors = relationship("Major", back_populates="college")
    persons = relationship("Person", foreign_keys="Person.college_id", back_populates="college")
    classes = relationship("Class", foreign_keys="Class.college_id", back_populates="college")
    departments = relationship("Department", foreign_keys="Department.college_id", back_populates="college")
    dean = relationship("Person", foreign_keys=[dean_id])
    vice_dean = relationship("Person", foreign_keys=[vice_dean_id])
    secretary = relationship("Person", foreign_keys=[secretary_id])
    
    # 索引
    __table_args__ = (
        Index("idx_college_code", "college_code"),
        Index("idx_college_dean", "dean_id"),
    )
    
    def __repr__(self):
        return f"<College(id={self.college_id}, name={self.college_name})>"


class Major(BaseModel):
    """
    专业表 - 管理专业信息
    """
    __tablename__ = "majors"
    
    # 基础信息
    major_id = Column(String(10), unique=True, nullable=False, comment="专业编码，如080901")
    major_name = Column(String(50), nullable=False, comment="专业名称")
    major_code = Column(String(20), nullable=False, comment="专业代码")
    
    # 所属学院
    college_id = Column(String(10), ForeignKey("colleges.college_id"), nullable=False, comment="所属学院")
    
    # 学制信息
    duration_years = Column(Integer, default=4, comment="学制年限")
    degree_type = Column(String(20), default="本科", comment="学位类型：本科/硕士/博士")
    
    # 人员配置
    director_id = Column(String(10), ForeignKey("persons.employee_id"), nullable=True, comment="专业主任")
    
    # 统计信息
    total_teachers = Column(Integer, default=0, comment="专业教师数")
    total_students = Column(Integer, default=0, comment="专业学生数")
    total_classes = Column(Integer, default=0, comment="班级数量")
    total_courses = Column(Integer, default=0, comment="课程数量")
    
    # 招生信息
    enrollment_quota = Column(Integer, nullable=True, comment="招生名额")
    tuition_fee = Column(Numeric(10, 2), nullable=True, comment="学费（元/年）")
    
    # 专业特色
    description = Column(Text, nullable=True, comment="专业介绍")
    career_prospects = Column(Text, nullable=True, comment="就业前景")
    core_courses = Column(JSON, default=list, comment="核心课程列表")
    
    # 认证信息
    accreditation = Column(String(100), nullable=True, comment="专业认证")
    ranking = Column(String(50), nullable=True, comment="专业排名")
    
    # 关联关系
    college = relationship("College", foreign_keys=[college_id], back_populates="majors")
    persons = relationship("Person", foreign_keys="Person.major_id", back_populates="major")
    classes = relationship("Class", foreign_keys="Class.major_id", back_populates="major")
    courses = relationship("Course", foreign_keys="Course.major_id", back_populates="major")
    director = relationship("Person", foreign_keys=[director_id])
    
    # 索引
    __table_args__ = (
        Index("idx_major_college", "college_id"),
        Index("idx_major_director", "director_id"),
        Index("idx_major_code", "major_code"),
    )
    
    def __repr__(self):
        return f"<Major(id={self.major_id}, name={self.major_name})>"


class Department(BaseModel):
    """
    部门表 - 管理行政部门信息
    """
    __tablename__ = "departments"
    
    # 基础信息
    department_id = Column(String(10), unique=True, nullable=False, comment="部门编码")
    department_name = Column(String(50), nullable=False, comment="部门名称")
    department_type = Column(String(20), nullable=False, comment="部门类型：学院/行政/后勤")
    
    # 所属学院（可选，行政部门可能不属于特定学院）
    college_id = Column(String(10), ForeignKey("colleges.college_id"), nullable=True, comment="所属学院")
    
    # 层级关系
    parent_department_id = Column(String(10), ForeignKey("departments.department_id"), nullable=True, comment="上级部门")
    level = Column(Integer, default=1, comment="部门层级")
    
    # 联系信息
    phone = Column(String(20), nullable=True, comment="部门电话")
    email = Column(String(100), nullable=True, comment="部门邮箱")
    office_location = Column(String(100), nullable=True, comment="办公地点")
    
    # 人员配置
    head_id = Column(String(10), ForeignKey("persons.employee_id"), nullable=True, comment="部门负责人")
    deputy_head_id = Column(String(10), ForeignKey("persons.employee_id"), nullable=True, comment="副负责人")
    
    # 统计信息
    total_staff = Column(Integer, default=0, comment="部门人员数")
    
    # 职能描述
    description = Column(Text, nullable=True, comment="部门职能")
    responsibilities = Column(JSON, default=list, comment="职责列表")
    
    # 关联关系
    college = relationship("College", foreign_keys=[college_id], back_populates="departments")
    persons = relationship("Person", foreign_keys="Person.department_id", back_populates="department")
    head = relationship("Person", foreign_keys=[head_id])
    deputy_head = relationship("Person", foreign_keys=[deputy_head_id])
    parent_department = relationship("Department", remote_side=[department_id])
    
    # 索引
    __table_args__ = (
        Index("idx_department_college", "college_id"),
        Index("idx_department_head", "head_id"),
        Index("idx_department_parent", "parent_department_id"),
        Index("idx_department_type", "department_type"),
    )
    
    def __repr__(self):
        return f"<Department(id={self.department_id}, name={self.department_name})>"


class Location(BaseModel):
    """
    地点表 - 管理校园内各种场所信息
    """
    __tablename__ = "locations"
    
    # 基础信息
    location_id = Column(String(20), unique=True, nullable=False, comment="地点编码")
    location_name = Column(String(50), nullable=False, comment="地点名称")
    location_type = Column(SQLEnum(*ROOM_TYPES, name="location_type_enum"), nullable=False, comment="地点类型")
    
    # 位置信息
    building_code = Column(String(10), nullable=False, comment="建筑编码，如C1、D1")
    building_name = Column(String(50), nullable=False, comment="建筑名称")
    floor = Column(Integer, nullable=True, comment="楼层")
    room_number = Column(String(20), nullable=True, comment="房间号")
    
    # 容量信息
    capacity = Column(Integer, nullable=True, comment="容纳人数")
    area = Column(Numeric(8, 2), nullable=True, comment="面积（平方米）")
    
    # 设施信息
    facilities = Column(JSON, default=list, comment="设施列表")
    equipment_list = Column(JSON, default=list, comment="设备清单")
    
    # 使用信息
    is_available = Column(Boolean, default=True, comment="是否可用")
    usage_restrictions = Column(Text, nullable=True, comment="使用限制")
    booking_required = Column(Boolean, default=False, comment="是否需要预约")
    
    # 管理信息
    manager_id = Column(String(10), ForeignKey("persons.employee_id"), nullable=True, comment="管理员")
    contact_phone = Column(String(20), nullable=True, comment="联系电话")
    
    # 维护信息
    last_maintenance = Column(Date, nullable=True, comment="上次维护日期")
    next_maintenance = Column(Date, nullable=True, comment="下次维护日期")
    maintenance_notes = Column(Text, nullable=True, comment="维护备注")
    
    # 关联关系
    manager = relationship("Person", foreign_keys=[manager_id])
    room_occupations = relationship("RoomOccupation", back_populates="location")
    assets = relationship("Asset", back_populates="location")
    
    # 索引
    __table_args__ = (
        Index("idx_location_building", "building_code"),
        Index("idx_location_type", "location_type"),
        Index("idx_location_available", "is_available"),
        Index("idx_location_manager", "manager_id"),
    )
    
    def __repr__(self):
        return f"<Location(id={self.location_id}, name={self.location_name})>"
    
    @property
    def full_address(self):
        """完整地址"""
        address_parts = [self.building_name]
        if self.floor:
            address_parts.append(f"{self.floor}楼")
        if self.room_number:
            address_parts.append(self.room_number)
        return "".join(address_parts)


class RoomOccupation(BaseModel):
    """
    教室占用表 - 管理教室/场地的占用情况
    """
    __tablename__ = "room_occupations"
    
    # 基础信息
    occupation_id = Column(String(20), unique=True, nullable=False, comment="占用记录ID")
    
    # 关联信息
    location_id = Column(String(20), ForeignKey("locations.location_id"), nullable=False, comment="地点")
    course_instance_id = Column(String(20), ForeignKey("course_instances.instance_id"), nullable=True, comment="课程实例")
    event_id = Column(String(20), nullable=True, comment="活动ID（暂不关联）")
    
    # 时间信息
    start_time = Column(DateTime, nullable=False, comment="开始时间")
    end_time = Column(DateTime, nullable=False, comment="结束时间")
    weekday = Column(Integer, nullable=True, comment="星期几（1-7）")
    time_slot = Column(Integer, nullable=True, comment="时间段（1-5）")
    
    # 重复信息
    is_recurring = Column(Boolean, default=False, comment="是否重复")
    recurring_pattern = Column(String(20), nullable=True, comment="重复模式：weekly/monthly")
    recurring_weeks = Column(String(50), nullable=True, comment="重复周次，如1-16")
    
    # 占用信息
    occupant_type = Column(String(20), nullable=False, comment="占用类型：course/event/meeting")
    occupant_id = Column(String(20), nullable=True, comment="占用者ID")
    occupant_name = Column(String(50), nullable=True, comment="占用者姓名")
    
    # 状态信息
    occupation_status = Column(String(20), default="confirmed", comment="占用状态：pending/confirmed/cancelled")
    approval_required = Column(Boolean, default=False, comment="是否需要审批")
    approved_by = Column(String(10), ForeignKey("persons.employee_id"), nullable=True, comment="审批人")
    approved_at = Column(DateTime, nullable=True, comment="审批时间")
    
    # 使用信息
    actual_attendees = Column(Integer, nullable=True, comment="实际参与人数")
    equipment_needed = Column(JSON, default=list, comment="所需设备")
    special_requirements = Column(Text, nullable=True, comment="特殊要求")
    
    # 关联关系
    location = relationship("Location", back_populates="room_occupations")
    course_instance = relationship("CourseInstance", back_populates="room_occupations")
    approver = relationship("Person", foreign_keys=[approved_by])
    
    # 索引
    __table_args__ = (
        Index("idx_occupation_location", "location_id"),
        Index("idx_occupation_time", "start_time", "end_time"),
        Index("idx_occupation_course", "course_instance_id"),
        Index("idx_occupation_status", "occupation_status"),
        Index("idx_occupation_weekday", "weekday", "time_slot"),
    )
    
    def __repr__(self):
        return f"<RoomOccupation(id={self.occupation_id}, location={self.location_id})>"
    
    @property
    def duration_hours(self):
        """占用时长（小时）"""
        if self.start_time and self.end_time:
            delta = self.end_time - self.start_time
            return delta.total_seconds() / 3600
        return 0
    
    def has_conflict(self, other_start, other_end):
        """检查是否与指定时间段冲突"""
        return not (self.end_time <= other_start or self.start_time >= other_end)
    
    @classmethod
    def check_availability(cls, location_id, start_time, end_time, exclude_id=None):
        """检查指定时间段的可用性"""
        from database import SessionLocal
        
        db = SessionLocal()
        try:
            query = db.query(cls).filter(
                cls.location_id == location_id,
                cls.occupation_status == "confirmed",
                cls.start_time < end_time,
                cls.end_time > start_time
            )
            
            if exclude_id:
                query = query.filter(cls.occupation_id != exclude_id)
            
            conflicts = query.all()
            return len(conflicts) == 0
            
        finally:
            db.close() 