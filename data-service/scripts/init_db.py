#!/usr/bin/env python3
"""
数据库初始化脚本
创建数据库和表结构
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from loguru import logger
from database import db_manager


def main():
    """主函数"""
    try:
        logger.info("Starting database initialization...")
        
        # 初始化数据库
        db_manager.initialize()
        
        logger.info("Database initialization completed successfully!")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 