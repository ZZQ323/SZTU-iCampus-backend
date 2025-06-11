from fastapi import FastAPI, HTTPException, Depends, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import List
import json
import uvicorn

from app.database import get_db, engine
from app.models import announcement as models
from app.schemas import announcement as schemas

# 创建数据库表
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SZTU iCampus API",
    description="深圳技术大学校园服务统一入口API",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该限制为特定域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 安全配置
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.get("/")
async def root():
    return {"message": "欢迎使用深圳技术大学校园服务API"}

@app.get("/api/announcements", response_model=List[schemas.Announcement])
async def get_announcements(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    获取校园公告列表
    - **skip**: 跳过的记录数
    - **limit**: 返回的最大记录数
    """
    announcements = db.query(models.Announcement).offset(skip).limit(limit).all()
    return announcements

@app.get("/api/announcements/stream")
async def get_announcements_stream(
    db: Session = Depends(get_db)
):
    """
    使用流式响应获取校园公告
    """
    async def generate():
        announcements = db.query(models.Announcement).all()
        for announcement in announcements:
            yield f"data: {json.dumps(announcement.__dict__)}\n\n"
    
    return Response(
        generate(),
        media_type="text/event-stream"
    )

@app.post("/api/announcements", response_model=schemas.Announcement)
async def create_announcement(
    announcement: schemas.AnnouncementCreate,
    db: Session = Depends(get_db)
):
    """
    创建新的校园公告
    """
    db_announcement = models.Announcement(**announcement.dict())
    db.add(db_announcement)
    db.commit()
    db.refresh(db_announcement)
    return db_announcement

@app.get("/api/schedule")
async def get_schedule():
    """
    获取课表信息
    """
    # TODO: 实现课表获取逻辑
    return {"schedule": []}

@app.get("/api/department-notices")
async def get_department_notices():
    """
    获取部门通知
    """
    # TODO: 实现部门通知获取逻辑
    return {"notices": []}

@app.get("/api/events")
async def get_events():
    """
    获取活动日历
    """
    # TODO: 实现活动日历获取逻辑
    return {"events": []}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 