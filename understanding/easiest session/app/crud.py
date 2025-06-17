from sqlalchemy.orm import Session
from app.models import User

def create_user(db: Session, name: str, email: str):
    db_user = User(name=name, email=email)
    db.add(db_user)
    db.commit()  # 提交事务
    db.refresh(db_user)  # 刷新以获取数据库中自动生成的字段（如ID）
    return db_user

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def update_user(db: Session, user_id: int, name: str):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        db_user.name = name
        db.commit()  # 提交事务
        db.refresh(db_user)  # 刷新对象
    return db_user

def delete_user(db: Session, user_id: int):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()  # 提交事务
    return db_user
