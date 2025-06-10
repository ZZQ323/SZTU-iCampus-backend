from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from typing import List, Optional
import uvicorn

app = FastAPI(title="SZTU iCampus API")

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

@app.get("/api/announcements")
async def get_announcements():
    """
    获取校园公告
    使用流式响应返回数据
    """
    # TODO: 实现公告获取逻辑
    return {"announcements": []}

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