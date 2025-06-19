from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime, timedelta
from app.crud.base import CRUDBase
from app.models.schedule import Schedule
from app.schemas.schedule import ScheduleCreate, ScheduleUpdate, ScheduleQuery
import re

class CRUDSchedule(CRUDBase[Schedule, ScheduleCreate, ScheduleUpdate]):
    def get_by_student(
        self, 
        db: Session, 
        student_id: str, 
        semester: str,
        is_active: bool = True
    ) -> List[Schedule]:
        """获取学生的所有课程"""
        query = db.query(self.model).filter(
            and_(
                self.model.student_id == student_id,
                self.model.semester == semester,
                self.model.is_active == is_active,
                self.model.is_deleted == False
            )
        )
        return query.all()
    
    def get_by_week(
        self, 
        db: Session, 
        student_id: str, 
        semester: str, 
        week_number: int,
        is_active: bool = True
    ) -> List[Schedule]:
        """获取指定周次的课程"""
        all_courses = self.get_by_student(db, student_id, semester, is_active)
        
        # 过滤出指定周次的课程
        week_courses = []
        for course in all_courses:
            if course.is_in_week(week_number):
                week_courses.append(course)
        
        return week_courses
    
    def get_by_week_day(
        self, 
        db: Session, 
        student_id: str, 
        semester: str, 
        week_number: int,
        week_day: int,
        is_active: bool = True
    ) -> List[Schedule]:
        """获取指定周次指定星期的课程"""
        week_courses = self.get_by_week(db, student_id, semester, week_number, is_active)
        
        # 过滤出指定星期的课程
        day_courses = [course for course in week_courses if course.week_day == week_day]
        
        # 按时间段排序
        day_courses.sort(key=lambda x: x.time_slot)
        
        return day_courses
    
    def get_schedule_grid(
        self, 
        db: Session, 
        student_id: str, 
        semester: str, 
        week_number: int,
        is_active: bool = True
    ) -> List[List[Optional[Schedule]]]:
        """获取课表网格数据 [day][time_slot]"""
        week_courses = self.get_by_week(db, student_id, semester, week_number, is_active)
        
        # 初始化7天x5时段的网格
        grid = [[None for _ in range(5)] for _ in range(7)]
        
        # 填充课程到网格中
        for course in week_courses:
            day_index = course.week_day - 1  # 转换为0-6
            time_index = course.time_slot - 1  # 转换为0-4
            
            if 0 <= day_index < 7 and 0 <= time_index < 5:
                grid[day_index][time_index] = course
        
        return grid
    
    def get_conflicts(
        self, 
        db: Session, 
        schedule_data: ScheduleCreate
    ) -> List[Schedule]:
        """检查课程时间冲突"""
        conflicts = []
        
        # 查询同一学生、同一学期的所有课程
        existing_courses = self.get_by_student(
            db, 
            schedule_data.student_id, 
            schedule_data.semester
        )
        
        for existing in existing_courses:
            # 检查是否在同一天同一时段
            if (existing.week_day == schedule_data.week_day and 
                existing.time_slot == schedule_data.time_slot):
                
                # 检查周次是否重叠
                if self._week_ranges_overlap(existing, schedule_data):
                    conflicts.append(existing)
        
        return conflicts
    
    def _week_ranges_overlap(self, course1: Schedule, course2: ScheduleCreate) -> bool:
        """检查两个课程的周次范围是否重叠"""
        # 简单的重叠检查：如果开始周次或结束周次在另一个课程范围内
        range1_start = course1.start_week
        range1_end = course1.end_week
        range2_start = course2.start_week
        range2_end = course2.end_week
        
        # 检查基本范围重叠
        if not (range1_end < range2_start or range2_end < range1_start):
            # 进一步检查具体周次
            for week in range(max(range1_start, range2_start), 
                            min(range1_end, range2_end) + 1):
                if (course1.is_in_week(week) and 
                    self._schedule_create_in_week(course2, week)):
                    return True
        
        return False
    
    def _schedule_create_in_week(self, schedule_data: ScheduleCreate, week_number: int) -> bool:
        """判断ScheduleCreate对象在指定周次是否有课"""
        if week_number < schedule_data.start_week or week_number > schedule_data.end_week:
            return False
        
        # 检查单双周
        if schedule_data.odd_even == "odd" and week_number % 2 == 0:
            return False
        if schedule_data.odd_even == "even" and week_number % 2 == 1:
            return False
        
        # 解析周次表达式
        if not schedule_data.week_expression:
            return schedule_data.start_week <= week_number <= schedule_data.end_week
        
        parts = schedule_data.week_expression.replace('+', ',').split(',')
        
        for part in parts:
            part = part.strip()
            if '-' in part and not part.startswith('-'):
                try:
                    start, end = map(int, part.split('-'))
                    if start <= week_number <= end:
                        return True
                except ValueError:
                    continue
            else:
                try:
                    if int(part) == week_number:
                        return True
                except ValueError:
                    continue
        
        return False
    
    def create_with_validation(
        self, 
        db: Session, 
        *, 
        obj_in: ScheduleCreate,
        check_conflicts: bool = True
    ) -> Schedule:
        """创建课程，可选择是否检查冲突"""
        if check_conflicts:
            conflicts = self.get_conflicts(db, obj_in)
            if conflicts:
                conflict_info = ", ".join([f"{c.course_name}({c.teacher})" for c in conflicts])
                raise ValueError(f"课程时间冲突：{conflict_info}")
        
        return self.create(db, obj_in=obj_in)
    
    def batch_create(
        self, 
        db: Session, 
        *, 
        courses: List[ScheduleCreate],
        check_conflicts: bool = True
    ) -> List[Schedule]:
        """批量创建课程"""
        created_courses = []
        
        for course_data in courses:
            try:
                course = self.create_with_validation(
                    db, 
                    obj_in=course_data, 
                    check_conflicts=check_conflicts
                )
                created_courses.append(course)
            except ValueError as e:
                # 可以选择跳过冲突的课程或者抛出异常
                print(f"跳过冲突课程 {course_data.course_name}: {e}")
                continue
        
        return created_courses
    
    def get_current_week_number(self, semester_start_date: str) -> int:
        """根据学期开始日期计算当前是第几周"""
        try:
            start_date = datetime.strptime(semester_start_date, "%Y-%m-%d")
            current_date = datetime.now()
            
            # 计算相差的天数
            delta = current_date - start_date
            
            # 计算周数（向上取整）
            week_number = (delta.days // 7) + 1
            
            # 确保周数在合理范围内
            return max(1, min(week_number, 30))
        except:
            # 如果计算失败，返回默认值
            return 1
    
    def get_time_slots(self) -> List[Dict[str, Any]]:
        """获取时间段信息"""
        return [
            {"slot": 1, "period": "1-2节", "start_time": "08:30", "end_time": "10:10"},
            {"slot": 2, "period": "3-4节", "start_time": "10:30", "end_time": "12:10"},
            {"slot": 3, "period": "5-6节", "start_time": "14:00", "end_time": "15:40"},
            {"slot": 4, "period": "7-8节", "start_time": "16:00", "end_time": "17:40"},
            {"slot": 5, "period": "9-10节", "start_time": "19:00", "end_time": "20:40"},
        ]
    
    def soft_delete(self, db: Session, *, id: int) -> Schedule:
        """软删除课程"""
        db_obj = self.get(db, id)
        if db_obj:
            db_obj.is_deleted = True
            db_obj.updated_at = datetime.now()
            db.commit()
            db.refresh(db_obj)
        return db_obj
    
    def activate(self, db: Session, *, id: int) -> Schedule:
        """激活课程"""
        db_obj = self.get(db, id)
        if db_obj:
            db_obj.is_active = True
            db_obj.updated_at = datetime.now()
            db.commit()
            db.refresh(db_obj)
        return db_obj
    
    def deactivate(self, db: Session, *, id: int) -> Schedule:
        """停用课程"""
        db_obj = self.get(db, id)
        if db_obj:
            db_obj.is_active = False
            db_obj.updated_at = datetime.now()
            db.commit()
            db.refresh(db_obj)
        return db_obj

schedule = CRUDSchedule(Schedule) 