@echo off
echo 🚀 SZTU-iCampus 快速启动（本地模式）
echo =======================================

REM 检查Python环境
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python 未安装或未添加到PATH
    pause
    exit /b 1
)

echo ✅ Python 环境检查通过

REM 启动PostgreSQL和Redis（仅Docker）
echo 📦 启动数据库服务...
docker-compose up -d postgres redis

echo ⏳ 等待数据库启动...
timeout /t 10 /nobreak >nul

REM 启动数据服务（本地）
echo 🗄️ 启动数据服务（本地模式）...
cd data-service

REM 检查虚拟环境
if not exist "venv" (
    echo 📦 创建虚拟环境...
    python -m venv venv
)

REM 激活虚拟环境并安装依赖
echo 📥 安装依赖...
call venv\Scripts\activate.bat
pip install -r requirements.txt >nul 2>&1

REM 设置环境变量
set DATABASE_URL=postgresql://postgres:postgres123@localhost:5432/sztu_data
set REDIS_URL=redis://localhost:6379/0
set API_KEY=sztu-data-service-key-2024

echo 🚀 启动数据服务...
start /b python main.py

cd ..

REM 启动胶水层（本地）
echo 🌐 启动胶水层（本地模式）...
cd backend

REM 检查虚拟环境
if not exist "venv" (
    echo 📦 创建虚拟环境...
    python -m venv venv
)

REM 激活虚拟环境并安装依赖
echo 📥 安装依赖...
call venv\Scripts\activate.bat
pip install -r requirements.txt >nul 2>&1

REM 设置环境变量
set DATA_SERVICE_URL=http://localhost:8001
set DATA_SERVICE_API_KEY=sztu-data-service-key-2024
set REDIS_URL=redis://localhost:6379/1
set DATABASE_URL=sqlite:///./sztu_icampus.db

echo 🚀 启动胶水层...
start /b uvicorn main:app --reload --host 0.0.0.0 --port 8000

cd ..

echo ⏳ 等待服务启动...
timeout /t 15 /nobreak >nul

echo 🎉 启动完成！
echo 🌐 服务地址:
echo   胶水层:    http://localhost:8000
echo   数据服务:  http://localhost:8001  
echo   API文档:   http://localhost:8000/docs
echo.
echo 💡 按任意键停止所有服务...
pause >nul

REM 停止服务
echo 🛑 停止服务...
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im uvicorn.exe >nul 2>&1
docker-compose down

echo ✅ 所有服务已停止
pause 