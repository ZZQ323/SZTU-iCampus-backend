#!/usr/bin/env python3
import uvicorn
from src.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD and settings.ENVIRONMENT == "development",
        log_level="debug" if settings.DEBUG else "info",
    )