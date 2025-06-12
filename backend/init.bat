@echo off
echo 正在初始化 SZTU-iCampus 后端项目...

REM 创建虚拟环境
echo 创建虚拟环境...
python -m venv venv
call venv\Scripts\activate

REM 安装依赖
echo 安装项目依赖...
pip install -r requirements.txt

REM 初始化数据库
echo 初始化数据库...
alembic upgrade head

REM 创建超级管理员
echo 创建超级管理员...
python -c "from app.db.init_db import init_db; init_db()"

echo 初始化完成！
echo 使用 'python run.py' 启动服务器 