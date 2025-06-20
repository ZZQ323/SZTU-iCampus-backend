"""
图书馆相关数据模型
包含Book（图书）、BorrowRecord（借阅记录）模型
"""
from sqlalchemy import (
    Column, Integer, String, Boolean, Date, DateTime,
    Text, ForeignKey, JSON, Enum as SQLEnum, Numeric
)
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Index

from .base import BaseModel


class Book(BaseModel):
    """
    图书表 - 管理图书馆图书信息
    """
    __tablename__ = "books"
    
    # 基础信息
    book_id = Column(String(20), unique=True, nullable=False, comment="图书编号")
    isbn = Column(String(20), nullable=True, comment="ISBN号")
    title = Column(String(200), nullable=False, comment="书名")
    title_en = Column(String(300), nullable=True, comment="英文书名")
    subtitle = Column(String(200), nullable=True, comment="副标题")
    
    # 作者信息
    author = Column(String(100), nullable=True, comment="作者")
    translator = Column(String(100), nullable=True, comment="译者")
    editor = Column(String(100), nullable=True, comment="编者")
    
    # 出版信息
    publisher = Column(String(100), nullable=True, comment="出版社")
    publication_date = Column(Date, nullable=True, comment="出版日期")
    edition = Column(String(20), nullable=True, comment="版次")
    print_count = Column(Integer, nullable=True, comment="印次")
    
    # 分类信息
    category = Column(String(50), nullable=False, comment="图书类别")
    subcategory = Column(String(50), nullable=True, comment="子类别")
    classification_number = Column(String(20), nullable=True, comment="分类号")
    subject_keywords = Column(JSON, default=list, comment="主题关键词")
    
    # 物理属性
    pages = Column(Integer, nullable=True, comment="页数")
    binding = Column(String(20), nullable=True, comment="装帧方式")
    format_size = Column(String(20), nullable=True, comment="开本")
    price = Column(Numeric(8, 2), nullable=True, comment="定价")
    
    # 语言和地区
    language = Column(String(20), default="中文", comment="语言")
    origin_country = Column(String(30), nullable=True, comment="原版国家")
    
    # 内容描述
    abstract = Column(Text, nullable=True, comment="内容摘要")
    table_of_contents = Column(Text, nullable=True, comment="目录")
    keywords = Column(JSON, default=list, comment="关键词")
    
    # 馆藏信息
    total_copies = Column(Integer, default=1, comment="馆藏总数")
    available_copies = Column(Integer, default=1, comment="可借数量")
    borrowed_copies = Column(Integer, default=0, comment="已借数量")
    reserved_copies = Column(Integer, default=0, comment="预约数量")
    damaged_copies = Column(Integer, default=0, comment="损坏数量")
    
    # 位置信息
    location_code = Column(String(20), nullable=True, comment="位置代码")
    shelf_number = Column(String(20), nullable=True, comment="书架号")
    floor = Column(Integer, nullable=True, comment="楼层")
    reading_room = Column(String(50), nullable=True, comment="阅览室")
    
    # 借阅规则
    borrowable = Column(Boolean, default=True, comment="是否可借")
    loan_period_days = Column(Integer, default=30, comment="借阅期限（天）")
    renewable_times = Column(Integer, default=2, comment="续借次数")
    reservation_allowed = Column(Boolean, default=True, comment="是否允许预约")
    
    # 使用统计
    borrow_count = Column(Integer, default=0, comment="借阅次数")
    reservation_count = Column(Integer, default=0, comment="预约次数")
    popularity_score = Column(Numeric(5, 2), default=0, comment="受欢迎程度")
    
    # 状态信息
    book_status = Column(String(20), default="available", comment="图书状态")
    acquisition_date = Column(Date, nullable=True, comment="入藏日期")
    last_inventory_date = Column(Date, nullable=True, comment="最后盘点日期")
    
    # 数字资源
    has_ebook = Column(Boolean, default=False, comment="是否有电子书")
    ebook_url = Column(String(300), nullable=True, comment="电子书链接")
    has_audiobook = Column(Boolean, default=False, comment="是否有有声书")
    audiobook_url = Column(String(300), nullable=True, comment="有声书链接")
    
    # 评价信息
    rating = Column(Numeric(3, 2), nullable=True, comment="评分（1-5）")
    review_count = Column(Integer, default=0, comment="评论数量")
    
    # 关联关系
    borrow_records = relationship("BorrowRecord", back_populates="book")
    
    # 索引
    __table_args__ = (
        Index("idx_book_isbn", "isbn"),
        Index("idx_book_title", "title"),
        Index("idx_book_author", "author"),
        Index("idx_book_category", "category"),
        Index("idx_book_status", "book_status"),
        Index("idx_book_location", "location_code"),
        Index("idx_book_available", "available_copies"),
    )
    
    def __repr__(self):
        return f"<Book(id={self.book_id}, title={self.title}, author={self.author})>"
    
    @property
    def is_available(self):
        """是否可借"""
        return self.borrowable and self.available_copies > 0
    
    @property
    def utilization_rate(self):
        """利用率"""
        if self.total_copies > 0:
            return (self.borrowed_copies + self.reserved_copies) / self.total_copies
        return 0
    
    def update_availability(self):
        """更新可借数量"""
        self.available_copies = max(0, 
            self.total_copies - self.borrowed_copies - self.reserved_copies - self.damaged_copies
        )


class BorrowRecord(BaseModel):
    """
    借阅记录表 - 管理图书借阅历史
    """
    __tablename__ = "borrow_records"
    
    # 基础信息
    record_id = Column(String(20), unique=True, nullable=False, comment="借阅记录ID")
    
    # 关联信息
    book_id = Column(String(20), ForeignKey("books.book_id"), nullable=False, comment="图书")
    borrower_id = Column(String(20), ForeignKey("persons.person_id"), nullable=False, comment="借阅者")
    librarian_id = Column(String(10), ForeignKey("persons.employee_id"), nullable=True, comment="办理员")
    
    # 借阅信息
    borrow_date = Column(DateTime, nullable=False, comment="借阅日期")
    due_date = Column(DateTime, nullable=False, comment="应还日期")
    return_date = Column(DateTime, nullable=True, comment="实际归还日期")
    
    # 续借信息
    renewal_count = Column(Integer, default=0, comment="续借次数")
    last_renewal_date = Column(DateTime, nullable=True, comment="最后续借日期")
    max_renewals = Column(Integer, default=2, comment="最大续借次数")
    
    # 状态信息
    record_status = Column(String(20), default="borrowed", comment="借阅状态：borrowed/returned/overdue/lost")
    is_overdue = Column(Boolean, default=False, comment="是否逾期")
    overdue_days = Column(Integer, default=0, comment="逾期天数")
    
    # 费用信息
    overdue_fine = Column(Numeric(8, 2), default=0, comment="逾期罚金")
    damage_fee = Column(Numeric(8, 2), default=0, comment="损坏赔偿费")
    lost_fee = Column(Numeric(8, 2), default=0, comment="遗失赔偿费")
    total_fee = Column(Numeric(8, 2), default=0, comment="总费用")
    
    # 图书状态
    condition_on_borrow = Column(String(20), default="good", comment="借出时状态")
    condition_on_return = Column(String(20), nullable=True, comment="归还时状态")
    damage_description = Column(Text, nullable=True, comment="损坏描述")
    
    # 操作信息
    borrow_location = Column(String(50), nullable=True, comment="借阅地点")
    return_location = Column(String(50), nullable=True, comment="归还地点")
    
    # 预约信息（如果是预约借阅）
    reservation_date = Column(DateTime, nullable=True, comment="预约日期")
    pickup_deadline = Column(DateTime, nullable=True, comment="取书截止日期")
    
    # 评价信息
    borrower_rating = Column(Integer, nullable=True, comment="借阅者评分（1-5）")
    borrower_review = Column(Text, nullable=True, comment="借阅者评价")
    
    # 关联关系
    book = relationship("Book", back_populates="borrow_records")
    borrower = relationship("Person", foreign_keys=[borrower_id])
    librarian = relationship("Person", foreign_keys=[librarian_id])
    
    # 索引
    __table_args__ = (
        Index("idx_borrow_book", "book_id"),
        Index("idx_borrow_borrower", "borrower_id"),
        Index("idx_borrow_date", "borrow_date"),
        Index("idx_borrow_due_date", "due_date"),
        Index("idx_borrow_status", "record_status"),
        Index("idx_borrow_overdue", "is_overdue"),
    )
    
    def __repr__(self):
        return f"<BorrowRecord(id={self.record_id}, book={self.book_id}, borrower={self.borrower_id})>"
    
    def check_overdue(self):
        """检查是否逾期"""
        from datetime import datetime
        now = datetime.now()
        
        if self.record_status == "borrowed" and self.due_date < now:
            self.is_overdue = True
            self.overdue_days = (now - self.due_date).days
            self.record_status = "overdue"
            
            # 计算逾期罚金（假设每天1元）
            self.overdue_fine = self.overdue_days * 1.0
            self.total_fee = self.overdue_fine + self.damage_fee + self.lost_fee
    
    def renew_book(self, extension_days=30):
        """续借图书"""
        if self.renewal_count < self.max_renewals and not self.is_overdue:
            from datetime import timedelta
            self.due_date += timedelta(days=extension_days)
            self.renewal_count += 1
            self.last_renewal_date = datetime.now()
            return True
        return False
    
    def return_book(self, condition="good", damage_desc=None):
        """归还图书"""
        from datetime import datetime
        
        self.return_date = datetime.now()
        self.condition_on_return = condition
        self.record_status = "returned"
        
        if condition != "good":
            self.damage_description = damage_desc
            # 计算损坏赔偿费（根据损坏程度）
            if condition == "damaged":
                self.damage_fee = 10.0  # 轻微损坏
            elif condition == "severely_damaged":
                self.damage_fee = 50.0  # 严重损坏
            
        self.total_fee = self.overdue_fine + self.damage_fee + self.lost_fee 