#!/usr/bin/env python3
"""
SZTU-iCampus Mock数据生成脚本
用于生成完整的校园测试数据

使用方法:
python scripts/generate_mock_data.py
"""

import os
import sys
import time
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from loguru import logger
from config import MOCK_CONFIG
from database import db_manager, get_database_stats
from generators.base_generator import MockDataGenerator


def setup_logging():
    """配置日志"""
    # 创建日志目录
    os.makedirs("logs", exist_ok=True)
    
    # 移除默认处理器
    logger.remove()
    
    # 添加控制台输出
    logger.add(
        sys.stdout,
        level="INFO",
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        colorize=True
    )
    
    # 添加文件输出
    logger.add(
        "logs/mock_data_generation.log",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
        rotation="10 MB",
        retention="7 days"
    )


def print_generation_plan():
    """打印数据生成计划"""
    logger.info("🎯 Mock数据生成计划")
    logger.info("="*50)
    
    # 计算预期数据量
    colleges = MOCK_CONFIG['colleges']
    majors_per_college = MOCK_CONFIG['majors_per_college']
    classes_per_major = MOCK_CONFIG['classes_per_major']
    grades = MOCK_CONFIG['grades_per_major']
    students_per_class = MOCK_CONFIG['students_per_class']
    teachers_per_college = MOCK_CONFIG['teachers_per_college']
    admin_total = MOCK_CONFIG['admin_total']
    
    total_majors = colleges * majors_per_college
    total_classes = total_majors * classes_per_major * grades
    total_students = total_classes * students_per_class
    total_teachers = colleges * teachers_per_college
    total_persons = total_students + total_teachers + admin_total
    
    logger.info(f"📚 学院数量: {colleges}")
    logger.info(f"📖 专业数量: {total_majors}")
    logger.info(f"🏫 班级数量: {total_classes}")
    logger.info(f"👨‍🎓 学生数量: {total_students:,}")
    logger.info(f"👨‍🏫 教师数量: {total_teachers}")
    logger.info(f"👔 管理员数量: {admin_total}")
    logger.info(f"👥 总人数: {total_persons:,}")
    logger.info(f"📚 预计图书数量: {MOCK_CONFIG['books_count']:,}")
    logger.info(f"💳 预计交易记录: {total_persons * MOCK_CONFIG['transactions_per_person_monthly'] * MOCK_CONFIG['transaction_months']:,}")
    logger.info("="*50)
    
    # 预估生成时间
    estimated_minutes = max(5, total_persons // 1000)  # 每1000人大约1分钟
    logger.info(f"⏱️  预估生成时间: {estimated_minutes} 分钟")
    logger.info("="*50)


def check_database_connection():
    """检查数据库连接"""
    logger.info("🔍 检查数据库连接...")
    
    try:
        health_info = db_manager.health_check()
        if health_info.get("sync_connection", False):
            logger.info("✅ 数据库连接正常")
            
            # 显示数据库信息
            stats = get_database_stats()
            logger.info(f"📊 数据库类型: {stats.get('database_type', 'Unknown')}")
            logger.info(f"📍 数据库地址: {stats.get('database_url', 'Unknown')}")
            return True
        else:
            logger.error("❌ 数据库连接失败")
            return False
            
    except Exception as e:
        logger.error(f"❌ 数据库连接检查出错: {e}")
        return False


def confirm_generation():
    """确认是否开始生成"""
    logger.info("⚠️  警告: 此操作将清空现有数据并重新生成所有Mock数据")
    
    while True:
        try:
            confirm = input("是否继续? (y/N): ").strip().lower()
            if confirm in ['y', 'yes', '是']:
                return True
            elif confirm in ['n', 'no', '否', '']:
                return False
            else:
                print("请输入 'y' 或 'n'")
        except KeyboardInterrupt:
            print("\n用户取消操作")
            return False


def main():
    """主函数"""
    setup_logging()
    
    logger.info("🚀 SZTU-iCampus Mock数据生成器")
    logger.info(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 打印生成计划
    print_generation_plan()
    
    # 2. 检查数据库连接
    if not check_database_connection():
        logger.error("❌ 数据库连接失败，程序退出")
        return 1
    
    # 3. 确认生成
    if not confirm_generation():
        logger.info("📋 用户取消操作，程序退出")
        return 0
    
    # 4. 初始化数据库
    logger.info("🗄️ 初始化数据库结构...")
    try:
        db_manager.initialize()
        logger.info("✅ 数据库初始化完成")
    except Exception as e:
        logger.error(f"❌ 数据库初始化失败: {e}")
        return 1
    
    # 5. 生成Mock数据
    logger.info("🎯 开始生成Mock数据...")
    start_time = time.time()
    
    try:
        generator = MockDataGenerator()
        generator.generate_all_data()
        
        end_time = time.time()
        duration = end_time - start_time
        
        logger.info("="*50)
        logger.info("🎉 Mock数据生成成功完成!")
        logger.info(f"⏱️  总耗时: {duration:.2f} 秒 ({duration/60:.1f} 分钟)")
        logger.info(f"⏰ 完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("="*50)
        
        # 6. 显示最终统计
        final_stats = get_database_stats()
        logger.info("📊 最终数据库统计:")
        for key, value in final_stats.items():
            if isinstance(value, (int, float)):
                logger.info(f"   {key}: {value:,}")
            else:
                logger.info(f"   {key}: {value}")
        
        logger.info("✅ 数据生成完成，可以启动数据服务进行测试")
        return 0
        
    except KeyboardInterrupt:
        logger.warning("⚠️ 用户中断操作")
        return 130
    except Exception as e:
        logger.error(f"❌ 数据生成过程中出错: {e}")
        logger.exception("详细错误信息:")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 