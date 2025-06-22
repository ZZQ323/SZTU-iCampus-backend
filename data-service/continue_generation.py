#!/usr/bin/env python3
"""
继续生成剩余的Mock数据
从成绩数据开始
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from loguru import logger
from generators.base_generator import MockDataGenerator
from database import db_manager

def main():
    logger.info("🔄 继续生成剩余的Mock数据...")
    
    try:
        # 初始化生成器
        generator = MockDataGenerator()
        
        # 恢复已生成的数据到缓存
        logger.info("📥 恢复已生成的数据...")
        generator.restore_cache_from_database()
        
        # 继续从成绩数据开始生成
        logger.info("📊 [5/10] 生成成绩数据...")
        generator.generate_grade_data()
        
        # 继续生成其他数据
        logger.info("📖 [6/10] 生成图书馆数据...")
        generator.generate_library_data()
        
        logger.info("💰 [7/10] 生成财务数据...")
        generator.generate_finance_data()
        
        logger.info("🔬 [8/10] 生成科研和权限数据...")
        generator.generate_research_data()
        generator.generate_permission_data()
        
        logger.info("🏫 [9/10] 生成教室占用数据...")
        generator.generate_room_occupation_data()
        
        logger.info("⚙️ [10/10] 生成工作流和其他数据...")
        generator.generate_workflow_data()
        
        logger.info("✅ 剩余数据生成完成！")
        generator.print_generation_summary()
        
    except Exception as e:
        logger.error(f"❌ 继续生成数据失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
        
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 