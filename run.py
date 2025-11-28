import uvicorn
from config import settings

if __name__ == "__main__":
    uvicorn.run(
        "main:app",              # main.py 中的 FastAPI 实例
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )

