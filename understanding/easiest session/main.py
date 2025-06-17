from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app import crud, models
from app.schemas import UserCreate  # 导入 Pydantic 模型

from app.database import engine, Base
# 创建所有数据库表
Base.metadata.create_all(bind=engine)


app = FastAPI()

@app.post("/users/")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # 期望注入的变量 db 是一个 SQLAlchemy 的 Session 实例
    # 这个 Session 用于管理与数据库的交互，执行 SQL以及其他的一些管理。 
    return crud.create_user(db=db, name=user.name, email=user.email)

@app.get("/users/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    return crud.get_user(db=db, user_id=user_id)

@app.put("/users/{user_id}")
def update_user(user_id: int, name: str, db: Session = Depends(get_db)):
    return crud.update_user(db=db, user_id=user_id, name=name)

@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    return crud.delete_user(db=db, user_id=user_id)
