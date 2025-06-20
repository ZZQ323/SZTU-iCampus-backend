"""
人员相关数据模型
包含Person（人员）和Class（班级）模型
"""
from sqlalchemy import (
    Column, Integer, String, Boolean, Date, DateTime, 
    Text, ForeignKey, JSON, Enum as SQLEnum, Numeric
)
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Index

from .base import BaseModel, PERSON_TYPES, GENDERS, ACADEMIC_STATUSES, EMPLOYMENT_STATUSES


class Person(BaseModel):
    """
    人员表 - 统一管理学生、教师、管理员等所有人员信息
    """
    __tablename__ = "persons"
    
    # 基础信息
    person_id = Column(String(20), unique=True, nullable=False, comment="统一人员ID，格式：P+年份+序号")
    person_type = Column(SQLEnum(*PERSON_TYPES, name="person_type_enum"), nullable=False, comment="人员类型")
    
    # 身份标识
    student_id = Column(String(12), unique=True, nullable=True, comment="学号（学生专用），格式：年份+专业编号+班级+序号")
    employee_id = Column(String(10), unique=True, nullable=True, comment="工号（教职工专用），格式：年份+专业编号+序号")
    
    # 个人信息
    name = Column(String(50), nullable=False, comment="真实姓名")
    name_en = Column(String(100), nullable=True, comment="英文姓名")
    gender = Column(SQLEnum(*GENDERS, name="gender_enum"), nullable=False, comment="性别")
    birth_date = Column(Date, nullable=True, comment="出生日期")
    id_card = Column(String(50), nullable=True, comment="身份证号（脱敏）")
    nationality = Column(String(20), default="中国", comment="国籍")
    ethnicity = Column(String(20), default="汉族", comment="民族")
    
    # 联系信息
    phone = Column(String(20), nullable=True, comment="联系电话（脱敏）")
    email = Column(String(100), nullable=True, comment="邮箱地址")
    wechat_openid = Column(String(50), nullable=True, comment="微信OpenID")
    qq_number = Column(String(20), nullable=True, comment="QQ号码")
    
    # 地址信息
    home_address = Column(Text, nullable=True, comment="家庭住址")
    current_address = Column(Text, nullable=True, comment="现居住地址")
    postal_code = Column(String(10), nullable=True, comment="邮政编码")
    
    # 时间属性
    admission_date = Column(Date, nullable=True, comment="入学时间（学生）")
    employment_date = Column(Date, nullable=True, comment="入职时间（教职工）")
    graduation_date = Column(Date, nullable=True, comment="预计毕业时间")
    
    # 状态属性
    academic_status = Column(SQLEnum(*ACADEMIC_STATUSES, name="academic_status_enum"), default="active", comment="学籍状态")
    employment_status = Column(SQLEnum(*EMPLOYMENT_STATUSES, name="employment_status_enum"), default="active", comment="就职状态")
    
    # 权限属性（JSON格式存储）
    permissions = Column(JSON, default=lambda: {"read": [], "write": [], "share": []}, comment="权限设置")
    
    # 关联属性（外键）
    college_id = Column(String(10), ForeignKey("colleges.college_id"), nullable=True, comment="所属学院")
    major_id = Column(String(10), ForeignKey("majors.major_id"), nullable=True, comment="所属专业")
    department_id = Column(String(10), ForeignKey("departments.department_id"), nullable=True, comment="所属部门")
    class_id = Column(String(20), ForeignKey("classes.class_id"), nullable=True, comment="所属班级")
    
    # 学术信息（主要用于教师）
    academic_title = Column(String(20), nullable=True, comment="职称：教授/副教授/讲师/助教")
    research_field = Column(String(100), nullable=True, comment="研究方向")
    education_background = Column(String(20), nullable=True, comment="学历：博士/硕士/学士")
    graduate_school = Column(String(100), nullable=True, comment="毕业院校")
    
    # 紧急联系人
    emergency_contact_name = Column(String(50), nullable=True, comment="紧急联系人姓名")
    emergency_contact_phone = Column(String(20), nullable=True, comment="紧急联系人电话")
    emergency_contact_relation = Column(String(20), nullable=True, comment="紧急联系人关系")
    
    # 财务信息
    bank_account = Column(String(50), nullable=True, comment="银行账号（脱敏）")
    bank_name = Column(String(50), nullable=True, comment="开户银行")
    
    # 照片信息
    avatar_url = Column(String(200), nullable=True, comment="头像URL")
    id_photo_url = Column(String(200), nullable=True, comment="证件照URL")
    
    # 关联关系
    college = relationship("College", back_populates="persons")
    major = relationship("Major", back_populates="persons")
    department = relationship("Department", back_populates="persons")
    class_ = relationship("Class", back_populates="students")
    
    # 索引
    __table_args__ = (
        Index("idx_person_student_id", "student_id"),
        Index("idx_person_employee_id", "employee_id"),
        Index("idx_person_type", "person_type"),
        Index("idx_person_college", "college_id"),
        Index("idx_person_major", "major_id"),
        Index("idx_person_class", "class_id"),
        Index("idx_person_status", "academic_status", "employment_status"),
    )
    
    def __repr__(self):
        return f"<Person(id={self.person_id}, name={self.name}, type={self.person_type})>"
    
    @property
    def is_student(self):
        """是否为学生"""
        return self.person_type == "student"
    
    @property
    def is_teacher(self):
        """是否为教师"""
        return self.person_type in ["teacher", "assistant_teacher"]
    
    @property
    def is_admin(self):
        """是否为管理员"""
        return self.person_type in ["admin", "department_head", "dean", "major_director"]
    
    @property
    def age(self):
        """计算年龄"""
        if self.birth_date:
            from datetime import date
            today = date.today()
            return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        return None
    
    @property
    def display_phone(self):
        """显示脱敏手机号"""
        if self.phone and len(self.phone) >= 11:
            return f"{self.phone[:3]}****{self.phone[-4:]}"
        return self.phone
    
    @property
    def display_id_card(self):
        """显示脱敏身份证号"""
        if self.id_card and len(self.id_card) >= 10:
            return f"{self.id_card[:3]}***{self.id_card[-4:]}"
        return self.id_card


class Class(BaseModel):
    """
    班级表 - 管理学生班级信息
    """
    __tablename__ = "classes"
    
    # 基础信息
    class_id = Column(String(20), unique=True, nullable=False, comment="班级ID，格式：CL+年份+序号")
    class_name = Column(String(50), nullable=False, comment="班级名称")
    class_code = Column(String(20), nullable=False, comment="班级代码")
    grade = Column(Integer, nullable=False, comment="年级，4位数字")
    semester_enrolled = Column(String(20), nullable=False, comment="入学学期")
    
    # 关联信息
    major_id = Column(String(10), ForeignKey("majors.major_id"), nullable=False, comment="所属专业")
    college_id = Column(String(10), ForeignKey("colleges.college_id"), nullable=False, comment="所属学院")
    
    # 人员配置
    class_advisor_id = Column(String(10), ForeignKey("persons.employee_id"), nullable=True, comment="班主任（教师工号）")
    counselor_id = Column(String(10), ForeignKey("persons.employee_id"), nullable=True, comment="辅导员")
    
    # 班级统计
    total_students = Column(Integer, default=0, comment="总学生数")
    male_count = Column(Integer, default=0, comment="男生人数")
    female_count = Column(Integer, default=0, comment="女生人数")
    
    # 班级状态
    graduation_date = Column(Date, nullable=True, comment="预计毕业时间")
    
    # 班级信息
    classroom_location = Column(String(50), nullable=True, comment="主要上课教室")
    class_motto = Column(Text, nullable=True, comment="班级格言")
    class_description = Column(Text, nullable=True, comment="班级简介")
    
    # 关联关系
    major = relationship("Major", back_populates="classes")
    college = relationship("College", back_populates="classes")
    students = relationship("Person", back_populates="class_")
    class_advisor = relationship("Person", foreign_keys=[class_advisor_id])
    counselor = relationship("Person", foreign_keys=[counselor_id])
    
    # 索引
    __table_args__ = (
        Index("idx_class_major", "major_id"),
        Index("idx_class_college", "college_id"),
        Index("idx_class_grade", "grade"),
        Index("idx_class_advisor", "class_advisor_id"),
        Index("idx_class_counselor", "counselor_id"),
    )
    
    def __repr__(self):
        return f"<Class(id={self.class_id}, name={self.class_name}, grade={self.grade})>"
    
    @property
    def enrollment_year(self):
        """入学年份"""
        return self.grade
    
    @property
    def current_grade_level(self):
        """当前年级（几年级）"""
        from datetime import date
        current_year = date.today().year
        # 假设9月为新学年开始
        current_month = date.today().month
        if current_month >= 9:
            academic_year = current_year
        else:
            academic_year = current_year - 1
        
        return academic_year - self.grade + 1
    
    @property
    def is_graduated(self):
        """是否已毕业"""
        if self.graduation_date:
            from datetime import date
            return date.today() > self.graduation_date
        return False
    
    def get_student_list(self):
        """获取班级学生列表"""
        return [student for student in self.students if student.person_type == "student"]
    
    def update_student_count(self):
        """更新学生统计数据"""
        students = self.get_student_list()
        self.total_students = len(students)
        self.male_count = len([s for s in students if s.gender == "male"])
        self.female_count = len([s for s in students if s.gender == "female"]) 