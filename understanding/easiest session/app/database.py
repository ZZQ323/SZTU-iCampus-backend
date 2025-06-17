from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
# 其实就是： sqlite:/// + 本地路径
#   sqlite:////path/to/db/test.db
# SQLite 的连接字符串依赖于数据库文件的位置
# 远程创建： postgresql://<username>:<password>@<host>:<port>/<database_name>

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    # get_db() 是一个生成器函数，它会创建一个新的 Session 对象
    # 你果然是来自 sqlalchemy 的 session
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
