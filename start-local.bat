@echo off
chcp 65001 >nul
echo SZTU-iCampus Quick Start (Local Mode)
echo =====================================

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found
    pause
    exit /b 1
)
echo OK: Python environment ready

REM Start databases only (Docker)
echo Starting database services...
docker-compose up -d postgres redis

echo Waiting for databases...
timeout /t 8 /nobreak >nul

REM Start data service (local)
echo Starting data service locally...
cd data-service

if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

echo Installing dependencies...
call venv\Scripts\activate.bat
pip install -q fastapi uvicorn sqlalchemy psycopg[binary] asyncpg loguru python-dotenv httpx redis

REM Set environment variables
set DATABASE_URL=postgresql://postgres:postgres123@localhost:5432/sztu_data
set REDIS_URL=redis://localhost:6379/0
set API_KEY=sztu-data-service-key-2024

echo Starting data service on port 8001...
start "Data Service" cmd /k "venv\Scripts\activate.bat && python main.py"

cd ..

REM Wait a bit
timeout /t 3 /nobreak >nul

REM Start glue layer (local)
echo Starting glue layer locally...
cd backend

if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

echo Installing dependencies...
call venv\Scripts\activate.bat
pip install -q fastapi uvicorn sqlalchemy pydantic python-multipart python-jose passlib httpx redis loguru

REM Set environment variables
set DATA_SERVICE_URL=http://localhost:8001
set DATA_SERVICE_API_KEY=sztu-data-service-key-2024
set REDIS_URL=redis://localhost:6379/1
set DATABASE_URL=sqlite:///./sztu_icampus.db

echo Starting glue layer on port 8000...
start "Glue Layer" cmd /k "venv\Scripts\activate.bat && uvicorn main:app --reload --host 0.0.0.0 --port 8000"

cd ..

echo.
echo ===== STARTUP COMPLETE =====
echo Services:
echo   Glue Layer:  http://localhost:8000
echo   Data Service: http://localhost:8001
echo   API Docs:    http://localhost:8000/docs
echo.
echo Press any key to stop all services...
pause >nul

REM Stop services
echo Stopping services...
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im cmd.exe /fi "WINDOWTITLE:Data Service*" >nul 2>&1
taskkill /f /im cmd.exe /fi "WINDOWTITLE:Glue Layer*" >nul 2>&1
docker-compose down

echo All services stopped
pause 