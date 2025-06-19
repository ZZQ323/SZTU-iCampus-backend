from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.database import get_db
from app.models.user import User
from app.models.announcement import Announcement
from app.models.notice import Notice
from app.schemas.user import User as UserSchema

router = APIRouter()

@router.get("/users", response_model=List[UserSchema])
def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_admin: User = Depends(deps.get_current_admin_user)
):
    """获取用户列表（管理员权限）"""
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@router.post("/users/{user_id}/toggle-admin")
def toggle_user_admin(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(deps.get_current_admin_user)
):
    """切换用户管理员状态"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_admin = not user.is_admin
    db.commit()
    db.refresh(user)
    
    return {"message": f"User {user.name} admin status updated to {user.is_admin}"}

@router.get("/announcements")
def get_admin_announcements(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_admin: User = Depends(deps.get_current_admin_user)
):
    """获取所有公告（管理员查看）"""
    announcements = db.query(Announcement).offset(skip).limit(limit).all()
    return {"announcements": announcements}

@router.delete("/announcements/{announcement_id}")
def delete_announcement(
    announcement_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(deps.get_current_admin_user)
):
    """删除公告"""
    announcement = db.query(Announcement).filter(Announcement.id == announcement_id).first()
    if not announcement:
        raise HTTPException(status_code=404, detail="Announcement not found")
    
    db.delete(announcement)
    db.commit()
    
    return {"message": "Announcement deleted successfully"}

@router.get("/notices")
def get_admin_notices(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_admin: User = Depends(deps.get_current_admin_user)
):
    """获取所有通知（管理员查看）"""
    notices = db.query(Notice).offset(skip).limit(limit).all()
    return {"notices": notices}

@router.delete("/notices/{notice_id}")
def delete_notice(
    notice_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(deps.get_current_admin_user)
):
    """删除通知"""
    notice = db.query(Notice).filter(Notice.id == notice_id).first()
    if not notice:
        raise HTTPException(status_code=404, detail="Notice not found")
    
    db.delete(notice)
    db.commit()
    
    return {"message": "Notice deleted successfully"}

@router.get("/stats")
def get_admin_stats(
    db: Session = Depends(get_db),
    current_admin: User = Depends(deps.get_current_admin_user)
):
    """获取系统统计信息"""
    user_count = db.query(User).count()
    admin_count = db.query(User).filter(User.is_admin == True).count()
    announcement_count = db.query(Announcement).count()
    notice_count = db.query(Notice).count()
    
    return {
        "user_count": user_count,
        "admin_count": admin_count,
        "announcement_count": announcement_count,
        "notice_count": notice_count
    } 