#!/usr/bin/env python3
"""
快速启动Mock数据生成
"""

import subprocess
import sys
import os

def main():
    """运行Mock数据生成脚本"""
    script_path = os.path.join("scripts", "generate_mock_data.py")
    
    if not os.path.exists(script_path):
        print(f"❌ 脚本文件不存在: {script_path}")
        return 1
    
    print("🚀 启动Mock数据生成...")
    print("📍 位置: data-service/")
    print("-" * 50)
    
    try:
        # 运行生成脚本
        result = subprocess.run([sys.executable, script_path], cwd=".")
        return result.returncode
        
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断操作")
        return 130
    except Exception as e:
        print(f"❌ 运行失败: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
 