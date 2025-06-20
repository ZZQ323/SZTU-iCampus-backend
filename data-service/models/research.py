"""
科研相关数据模型
包含ResearchProject（科研项目）、ResearchApplication（科研申请）、PaperLibrary（论文库）模型
"""
from sqlalchemy import (
    Column, Integer, String, Boolean, Date, DateTime,
    Text, ForeignKey, JSON, Enum as SQLEnum, Numeric
)
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Index

from .base import BaseModel, PROJECT_TYPES, PROJECT_LEVELS, THESIS_TYPES, JOURNAL_LEVELS


class ResearchProject(BaseModel):
    """
    科研项目表 - 管理科研项目信息
    """
    __tablename__ = "research_projects"
    
    # 基础信息
    project_id = Column(String(20), unique=True, nullable=False, comment="项目编号")
    project_name = Column(String(200), nullable=False, comment="项目名称")
    project_name_en = Column(String(300), nullable=True, comment="英文名称")
    
    # 项目分类
    project_type = Column(SQLEnum(*PROJECT_TYPES, name="project_type_enum"), nullable=False, comment="项目类型")
    project_level = Column(SQLEnum(*PROJECT_LEVELS, name="project_level_enum"), nullable=False, comment="项目级别")
    project_category = Column(String(50), nullable=True, comment="项目类别")
    
    # 负责人信息
    principal_investigator_id = Column(String(10), ForeignKey("persons.employee_id"), nullable=False, comment="项目负责人")
    co_investigators = Column(JSON, default=list, comment="共同研究者列表")
    
    # 所属单位
    college_id = Column(String(10), ForeignKey("colleges.college_id"), nullable=False, comment="所属学院")
    department_id = Column(String(10), ForeignKey("departments.department_id"), nullable=True, comment="所属部门")
    
    # 项目描述
    project_abstract = Column(Text, nullable=True, comment="项目摘要")
    objectives = Column(Text, nullable=True, comment="研究目标")
    methodology = Column(Text, nullable=True, comment="研究方法")
    innovation_points = Column(Text, nullable=True, comment="创新点")
    expected_outcomes = Column(Text, nullable=True, comment="预期成果")
    
    # 时间信息
    start_date = Column(Date, nullable=False, comment="开始日期")
    end_date = Column(Date, nullable=False, comment="结束日期")
    duration_months = Column(Integer, nullable=True, comment="项目周期（月）")
    
    # 资金信息
    total_funding = Column(Numeric(12, 2), nullable=True, comment="总经费")
    allocated_funding = Column(Numeric(12, 2), default=0, comment="已拨付经费")
    spent_funding = Column(Numeric(12, 2), default=0, comment="已使用经费")
    funding_source = Column(String(100), nullable=True, comment="资助机构")
    
    # 状态信息
    project_status = Column(String(20), default="pending", comment="项目状态：pending/approved/ongoing/completed/terminated/suspended")
    approval_date = Column(Date, nullable=True, comment="批准日期")
    completion_date = Column(Date, nullable=True, comment="完成日期")
    
    # 关键词和学科
    keywords = Column(JSON, default=list, comment="关键词")
    research_fields = Column(JSON, default=list, comment="研究领域")
    disciplines = Column(JSON, default=list, comment="学科分类")
    
    # 成果信息
    papers_published = Column(Integer, default=0, comment="发表论文数")
    patents_applied = Column(Integer, default=0, comment="申请专利数")
    awards_received = Column(JSON, default=list, comment="获奖情况")
    
    # 评价信息
    peer_review_score = Column(Numeric(3, 2), nullable=True, comment="同行评议分数")
    progress_reports = Column(JSON, default=list, comment="进展报告列表")
    
    # 管理信息
    contract_number = Column(String(50), nullable=True, comment="合同编号")
    administrative_department = Column(String(50), nullable=True, comment="管理部门")
    contact_person = Column(String(50), nullable=True, comment="联系人")
    contact_phone = Column(String(20), nullable=True, comment="联系电话")
    
    # 关联关系
    principal_investigator = relationship("Person", foreign_keys=[principal_investigator_id])
    college = relationship("College")
    department = relationship("Department")
    applications = relationship("ResearchApplication", back_populates="project")
    papers = relationship("PaperLibrary", back_populates="project")
    
    # 索引
    __table_args__ = (
        Index("idx_project_pi", "principal_investigator_id"),
        Index("idx_project_college", "college_id"),
        Index("idx_project_type", "project_type"),
        Index("idx_project_level", "project_level"),
        Index("idx_project_status", "project_status"),
        Index("idx_project_start_date", "start_date"),
    )
    
    def __repr__(self):
        return f"<ResearchProject(id={self.project_id}, name={self.project_name})>"
    
    @property
    def is_active(self):
        """项目是否进行中"""
        return self.project_status in ["approved", "ongoing"]
    
    @property
    def funding_utilization_rate(self):
        """经费使用率"""
        if self.total_funding and self.total_funding > 0:
            return (self.spent_funding / self.total_funding) * 100
        return 0
    
    @property
    def remaining_funding(self):
        """剩余经费"""
        return (self.allocated_funding or 0) - (self.spent_funding or 0)


class ResearchApplication(BaseModel):
    """
    科研申请表 - 管理科研项目申请
    """
    __tablename__ = "research_applications"
    
    # 基础信息
    application_id = Column(String(20), unique=True, nullable=False, comment="申请编号")
    
    # 申请信息
    applicant_id = Column(String(10), ForeignKey("persons.employee_id"), nullable=False, comment="申请人")
    project_id = Column(String(20), ForeignKey("research_projects.project_id"), nullable=True, comment="关联项目")
    
    # 申请类型
    application_type = Column(String(20), nullable=False, comment="申请类型：new_project/funding/extension/modification/termination")
    funding_agency = Column(String(100), nullable=True, comment="申请机构")
    program_name = Column(String(100), nullable=True, comment="资助计划")
    
    # 申请内容
    application_title = Column(String(200), nullable=False, comment="申请标题")
    application_abstract = Column(Text, nullable=True, comment="申请摘要")
    research_proposal = Column(Text, nullable=True, comment="研究方案")
    budget_plan = Column(JSON, default=dict, comment="预算计划")
    requested_amount = Column(Numeric(12, 2), nullable=True, comment="申请金额")
    
    # 时间信息
    submission_date = Column(Date, nullable=False, comment="提交日期")
    deadline_date = Column(Date, nullable=True, comment="截止日期")
    review_start_date = Column(Date, nullable=True, comment="评审开始日期")
    decision_date = Column(Date, nullable=True, comment="决定日期")
    
    # 状态信息
    application_status = Column(String(20), default="draft", comment="申请状态：draft/submitted/under_review/approved/rejected/withdrawn")
    review_stage = Column(String(20), nullable=True, comment="评审阶段")
    
    # 评审信息
    reviewers = Column(JSON, default=list, comment="评审专家列表")
    review_scores = Column(JSON, default=dict, comment="评审分数")
    review_comments = Column(Text, nullable=True, comment="评审意见")
    final_score = Column(Numeric(5, 2), nullable=True, comment="最终得分")
    
    # 结果信息
    approval_amount = Column(Numeric(12, 2), nullable=True, comment="批准金额")
    approval_conditions = Column(Text, nullable=True, comment="批准条件")
    rejection_reason = Column(Text, nullable=True, comment="拒绝原因")
    
    # 附件信息
    supporting_documents = Column(JSON, default=list, comment="支撑材料列表")
    cv_attachments = Column(JSON, default=list, comment="简历附件")
    
    # 关联关系
    applicant = relationship("Person", foreign_keys=[applicant_id])
    project = relationship("ResearchProject", back_populates="applications")
    
    # 索引
    __table_args__ = (
        Index("idx_application_applicant", "applicant_id"),
        Index("idx_application_project", "project_id"),
        Index("idx_application_type", "application_type"),
        Index("idx_application_status", "application_status"),
        Index("idx_application_submission", "submission_date"),
    )
    
    def __repr__(self):
        return f"<ResearchApplication(id={self.application_id}, title={self.application_title})>"


class PaperLibrary(BaseModel):
    """
    论文库表 - 管理学术论文信息
    """
    __tablename__ = "paper_library"
    
    # 基础信息
    paper_id = Column(String(20), unique=True, nullable=False, comment="论文编号")
    title = Column(String(300), nullable=False, comment="论文标题")
    title_en = Column(String(500), nullable=True, comment="英文标题")
    
    # 作者信息
    first_author_id = Column(String(10), ForeignKey("persons.employee_id"), nullable=False, comment="第一作者")
    corresponding_author_id = Column(String(10), ForeignKey("persons.employee_id"), nullable=True, comment="通讯作者")
    all_authors = Column(JSON, default=list, comment="所有作者列表")
    author_affiliations = Column(JSON, default=list, comment="作者单位")
    
    # 论文分类
    paper_type = Column(SQLEnum(*THESIS_TYPES, name="paper_type_enum"), nullable=False, comment="论文类型")
    research_field = Column(String(100), nullable=True, comment="研究领域")
    subject_classification = Column(String(100), nullable=True, comment="学科分类")
    
    # 发表信息
    journal_name = Column(String(200), nullable=True, comment="期刊名称")
    journal_level = Column(SQLEnum(*JOURNAL_LEVELS, name="journal_level_enum"), nullable=True, comment="期刊级别")
    conference_name = Column(String(200), nullable=True, comment="会议名称")
    publisher = Column(String(100), nullable=True, comment="出版社")
    
    # 发表细节
    publication_date = Column(Date, nullable=True, comment="发表日期")
    volume = Column(String(20), nullable=True, comment="卷号")
    issue = Column(String(20), nullable=True, comment="期号")
    pages = Column(String(20), nullable=True, comment="页码")
    doi = Column(String(100), nullable=True, comment="DOI")
    issn = Column(String(20), nullable=True, comment="ISSN")
    isbn = Column(String(20), nullable=True, comment="ISBN")
    
    # 关联项目
    project_id = Column(String(20), ForeignKey("research_projects.project_id"), nullable=True, comment="关联项目")
    funding_info = Column(JSON, default=list, comment="资助信息")
    
    # 论文内容
    abstract = Column(Text, nullable=True, comment="摘要")
    keywords = Column(JSON, default=list, comment="关键词")
    methodology = Column(Text, nullable=True, comment="研究方法")
    conclusions = Column(Text, nullable=True, comment="结论")
    
    # 质量指标
    impact_factor = Column(Numeric(6, 3), nullable=True, comment="影响因子")
    citation_count = Column(Integer, default=0, comment="被引次数")
    download_count = Column(Integer, default=0, comment="下载次数")
    h_index = Column(Integer, nullable=True, comment="H指数")
    
    # 状态信息
    publication_status = Column(String(20), default="draft", comment="发表状态：draft/submitted/under_review/accepted/published/rejected")
    submission_date = Column(Date, nullable=True, comment="投稿日期")
    acceptance_date = Column(Date, nullable=True, comment="接收日期")
    
    # 访问信息
    is_open_access = Column(Boolean, default=False, comment="是否开放获取")
    access_url = Column(String(300), nullable=True, comment="访问链接")
    pdf_url = Column(String(300), nullable=True, comment="PDF链接")
    
    # 评价信息
    peer_review_score = Column(Numeric(3, 2), nullable=True, comment="同行评议分数")
    academic_impact = Column(String(20), nullable=True, comment="学术影响力")
    
    # 版权信息
    copyright_holder = Column(String(100), nullable=True, comment="版权所有者")
    license_type = Column(String(50), nullable=True, comment="许可证类型")
    
    # 关联关系
    first_author = relationship("Person", foreign_keys=[first_author_id])
    corresponding_author = relationship("Person", foreign_keys=[corresponding_author_id])
    project = relationship("ResearchProject", back_populates="papers")
    
    # 索引
    __table_args__ = (
        Index("idx_paper_first_author", "first_author_id"),
        Index("idx_paper_corresponding_author", "corresponding_author_id"),
        Index("idx_paper_project", "project_id"),
        Index("idx_paper_type", "paper_type"),
        Index("idx_paper_journal", "journal_name"),
        Index("idx_paper_publication_date", "publication_date"),
        Index("idx_paper_status", "publication_status"),
    )
    
    def __repr__(self):
        return f"<PaperLibrary(id={self.paper_id}, title={self.title[:50]}...)>"
    
    @property
    def is_published(self):
        """是否已发表"""
        return self.publication_status == "published"
    
    @property
    def is_high_impact(self):
        """是否高影响力论文"""
        if self.journal_level in ["SCI", "EI"]:
            return True
        if self.impact_factor and self.impact_factor > 3.0:
            return True
        if self.citation_count and self.citation_count > 10:
            return True
        return False 