from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, date

from app import crud, models, schemas
from app.api import deps
from app.core.config import settings

router = APIRouter()

@router.get("/", response_model=List[schemas.Schedule])
def read_schedules(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    获取当前用户的所有课程
    """
    # 默认使用当前学期 
    semester = "2024-2025-1"  # 可以从配置或数据库获取
    schedules = crud.schedule.get_by_student(
        db, 
        student_id=current_user.student_id, 
        semester=semester
    )
    return schedules

@router.get("/week/{week_number}", response_model=List[schemas.Schedule])
def read_week_schedule(
    week_number: int,
    semester: str = Query(default="2024-2025-1", description="学期"),
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    获取指定周次的课表
    """
    if week_number < 1 or week_number > 30:
        raise HTTPException(status_code=400, detail="周次必须在1-30之间")
    
    schedules = crud.schedule.get_by_week(
        db, 
        student_id=current_user.student_id, 
        semester=semester,
        week_number=week_number
    )
    return schedules

@router.get("/grid/{week_number}")
def read_schedule_grid(
    week_number: int,
    semester: str = Query(default="2024-2025-1", description="学期"),
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    获取指定周次的课表网格数据
    """
    if week_number < 1 or week_number > 30:
        raise HTTPException(status_code=400, detail="周次必须在1-30之间")
    
    # 获取网格数据
    grid = crud.schedule.get_schedule_grid(
        db, 
        student_id=current_user.student_id, 
        semester=semester,
        week_number=week_number
    )
    
    # 获取时间段信息
    time_slots = crud.schedule.get_time_slots()
    
    return {
        "week_number": week_number,
        "semester": semester,
        "time_slots": time_slots,
        "schedule_data": grid,
        "student_info": {
            "student_id": current_user.student_id,
            "full_name": current_user.full_name
        }
    }

@router.get("/current-week")
def read_current_week_schedule(
    semester: str = Query(default="2024-2025-1", description="学期"),
    semester_start: str = Query(default="2024-09-02", description="学期开始日期"),
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    获取当前周次的课表
    """
    # 计算当前周次
    current_week = crud.schedule.get_current_week_number(semester_start)
    
    # 获取当前周课表
    schedules = crud.schedule.get_by_week(
        db, 
        student_id=current_user.student_id, 
        semester=semester,
        week_number=current_week
    )
    
    return {
        "current_week": current_week,
        "semester": semester,
        "courses": schedules
    }

@router.post("/", response_model=schemas.Schedule)
def create_schedule(
    *,
    db: Session = Depends(deps.get_db),
    schedule_in: schemas.ScheduleCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    创建新课程
    """
    # 设置学生ID为当前用户
    schedule_in.student_id = current_user.student_id
    
    try:
        schedule = crud.schedule.create_with_validation(
            db, 
            obj_in=schedule_in,
            check_conflicts=True
        )
        return schedule
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{schedule_id}", response_model=schemas.Schedule)
def read_schedule(
    *,
    db: Session = Depends(deps.get_db),
    schedule_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    获取单个课程详情
    """
    schedule = crud.schedule.get(db, id=schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="课程不存在")
    
    # 检查权限：只能查看自己的课程
    if schedule.student_id != current_user.student_id:
        raise HTTPException(status_code=403, detail="无权限查看此课程")
    
    return schedule

@router.get("/time-slots/info")
def get_time_slots_info() -> Any:
    """
    获取时间段信息
    """
    time_slots = crud.schedule.get_time_slots()
    return {
        "time_slots": time_slots,
        "total_slots": len(time_slots)
    }