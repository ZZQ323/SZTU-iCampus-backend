from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime

class ScheduleBase(BaseModel):
    # 课程基本信息
    course_name: str = Field(..., description="课程名称")
    course_code: Optional[str] = Field(None, description="课程代码")
    teacher: str = Field(..., description="授课教师")
    classroom: str = Field(..., description="教室")
    
    # 时间信息
    week_day: int = Field(..., ge=1, le=7, description="星期几(1-7, 1=周一)")
    time_slot: int = Field(..., ge=1, le=5, description="第几节课(1=第1-2节, 2=第3-4节, 3=第5-6节, 4=第7-8节, 5=第9-10节)")
    start_time: str = Field(..., description="开始时间(HH:MM)")
    end_time: str = Field(..., description="结束时间(HH:MM)")
    
    # 周次信息
    week_expression: str = Field(..., description="周次表达式(如:1-16,1,3,5,1-8+10-16)")
    start_week: int = Field(..., ge=1, le=30, description="开始周次")
    end_week: int = Field(..., ge=1, le=30, description="结束周次")
    odd_even: str = Field(default="all", description="单双周(all/odd/even)")
    
    # 课程属性
    course_type: str = Field(default="必修", description="课程类型(必修/选修/实验/实践)")
    credits: Optional[str] = Field(None, description="学分")
    course_hours: Optional[int] = Field(None, description="课时")
    course_nature: Optional[str] = Field(None, description="课程性质")
    
    # 学期和学生信息
    semester: str = Field(..., description="学期(如:2024-2025-1)")
    academic_year: str = Field(..., description="学年(如:2024-2025)")
    term: int = Field(..., ge=1, le=2, description="学期(1=上学期,2=下学期)")
    student_id: str = Field(..., description="学生学号")
    class_name: Optional[str] = Field(None, description="班级")
    major: Optional[str] = Field(None, description="专业")
    college: Optional[str] = Field(None, description="学院")
    
    # 课程描述
    course_description: Optional[str] = Field(None, description="课程描述")
    textbook: Optional[str] = Field(None, description="教材信息")
    requirements: Optional[str] = Field(None, description="课程要求")
    
    @validator('odd_even')
    def validate_odd_even(cls, v):
        if v not in ['all', 'odd', 'even']:
            raise ValueError('odd_even must be one of: all, odd, even')
        return v
    
    @validator('course_type')
    def validate_course_type(cls, v):
        if v not in ['必修', '选修', '实验', '实践']:
            raise ValueError('course_type must be one of: 必修, 选修, 实验, 实践')
        return v
    
    @validator('end_week')
    def validate_week_range(cls, v, values):
        if 'start_week' in values and v < values['start_week']:
            raise ValueError('end_week must be greater than or equal to start_week')
        return v

class ScheduleCreate(ScheduleBase):
    pass

class ScheduleUpdate(BaseModel):
    # 课程基本信息
    course_name: Optional[str] = None
    course_code: Optional[str] = None
    teacher: Optional[str] = None
    classroom: Optional[str] = None
    
    # 时间信息
    week_day: Optional[int] = Field(None, ge=1, le=7)
    time_slot: Optional[int] = Field(None, ge=1, le=5)
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    
    # 周次信息
    week_expression: Optional[str] = None
    start_week: Optional[int] = Field(None, ge=1, le=30)
    end_week: Optional[int] = Field(None, ge=1, le=30)
    odd_even: Optional[str] = None
    
    # 课程属性
    course_type: Optional[str] = None
    credits: Optional[str] = None
    course_hours: Optional[int] = None
    course_nature: Optional[str] = None
    
    # 学期和学生信息
    semester: Optional[str] = None
    academic_year: Optional[str] = None
    term: Optional[int] = Field(None, ge=1, le=2)
    class_name: Optional[str] = None
    major: Optional[str] = None
    college: Optional[str] = None
    
    # 课程描述
    course_description: Optional[str] = None
    textbook: Optional[str] = None
    requirements: Optional[str] = None

class Schedule(ScheduleBase):
    id: int
    is_active: bool = True
    is_deleted: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ScheduleInDB(Schedule):
    pass

# 课表查询相关模式
class ScheduleQuery(BaseModel):
    student_id: str
    semester: str
    week_number: Optional[int] = None
    week_day: Optional[int] = None

class WeekSchedule(BaseModel):
    """某一周的课表"""
    week_number: int
    start_date: str
    end_date: str
    courses: List[Schedule]

class TimeSlotInfo(BaseModel):
    """时间段信息"""
    slot: int
    period: str
    start_time: str
    end_time: str

class ScheduleGrid(BaseModel):
    """课表网格数据"""
    week_number: int
    semester: str
    time_slots: List[TimeSlotInfo]
    schedule_data: List[List[Optional[Schedule]]]  # [day][time_slot]
    
class BatchScheduleCreate(BaseModel):
    """批量创建课程"""
    courses: List[ScheduleCreate]
    
class ScheduleImport(BaseModel):
    """课程导入"""
    import_type: str = Field(..., description="导入类型(excel/教务系统)")
    file_data: Optional[str] = Field(None, description="文件数据")
    semester: str = Field(..., description="学期")
    student_id: str = Field(..., description="学生学号") 