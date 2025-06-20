@echo off
setlocal enabledelayedexpansion

REM SZTU-iCampus Windows 部署脚本
REM 自动化部署胶水层和数据服务

echo.
echo 🚀 开始部署 SZTU-iCampus 系统
echo ==================================

REM 检查 Docker 和 Docker Compose
:check_dependencies
echo 📋 检查依赖...

docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker 未安装，请先安装 Docker Desktop
    pause
    exit /b 1
)

docker-compose --version >nul 2>&1
if errorlevel 1 (
    docker compose version >nul 2>&1
    if errorlevel 1 (
        echo ❌ Docker Compose 未安装，请先安装 Docker Compose
        pause
        exit /b 1
    )
)

echo ✅ 依赖检查通过

REM 创建必要的目录
:create_directories
echo 📁 创建必要目录...

if not exist "backend\logs" mkdir "backend\logs"
if not exist "data-service\logs" mkdir "data-service\logs"
if not exist "nginx" mkdir "nginx"
if not exist "monitoring" mkdir "monitoring"

echo ✅ 目录创建完成

REM 根据参数执行不同操作
set action=%1
if "%action%"=="" set action=deploy

if "%action%"=="deploy" goto deploy
if "%action%"=="stop" goto stop
if "%action%"=="restart" goto restart
if "%action%"=="logs" goto logs
if "%action%"=="status" goto status
if "%action%"=="clean" goto clean
if "%action%"=="update" goto update
goto usage

:deploy
echo 🏗️ 构建和启动服务...

REM 停止现有服务
echo 停止现有服务...
docker-compose down --remove-orphans >nul 2>&1

REM 构建镜像
echo 构建 Docker 镜像...
docker-compose build --no-cache

REM 启动核心服务
echo 启动核心服务...
docker-compose up -d postgres redis

REM 等待数据库就绪
echo 等待 PostgreSQL 就绪...
timeout /t 10 /nobreak >nul

REM 启动数据服务
echo 启动数据服务...
docker-compose up -d data-service

REM 等待数据服务就绪
echo 等待数据服务就绪...
timeout /t 15 /nobreak >nul

REM 启动胶水层
echo 启动胶水层...
docker-compose up -d glue-layer

echo ✅ 服务启动完成

REM 初始化数据
echo 📊 初始化数据...
timeout /t 20 /nobreak >nul

echo 初始化数据库结构...
docker-compose exec -T data-service python -c "import asyncio; from scripts.init_db import init_database; from generators.base_generator import generate_all_data; asyncio.run(init_database()); asyncio.run(generate_all_data()); print('数据库初始化完成')" 2>nul || echo 数据库初始化可能已存在，跳过...

echo ✅ 数据初始化完成

goto check_services

:stop
echo 🛑 停止服务...
docker-compose down
echo ✅ 服务已停止
goto end

:restart
echo 🔄 重启服务...
docker-compose restart
echo ✅ 服务已重启
goto end

:logs
echo 📜 显示服务日志 (Ctrl+C 退出)...
docker-compose logs -f glue-layer data-service
goto end

:status
goto check_services

:clean
echo 🧹 清理容器和数据...
docker-compose down -v --remove-orphans
docker system prune -f
echo ✅ 清理完成
goto end

:update
echo 🔄 更新系统...
docker-compose down
docker-compose build --no-cache
docker-compose up -d
echo ✅ 更新完成
goto end

:check_services
echo 🔍 检查服务状态...

for %%s in (postgres redis data-service glue-layer) do (
    for /f %%i in ('docker-compose ps -q %%s 2^>nul') do (
        if "%%i"=="" (
            echo ❌ %%s: 未运行
        ) else (
            echo ✅ %%s: 运行中
        )
    )
)

echo.
echo 🌐 服务地址:
echo   胶水层:    http://localhost:8000
echo   数据服务:  http://localhost:8001
echo   API文档:   http://localhost:8000/docs
echo   数据文档:  http://localhost:8001/docs
echo.

echo 🏥 健康检查...
timeout /t 5 /nobreak >nul

REM 检查数据服务
curl -s http://localhost:8001/health >nul 2>&1
if errorlevel 1 (
    echo ⚠️ 数据服务健康检查失败，可能仍在启动中
) else (
    echo ✅ 数据服务健康检查通过
)

REM 检查胶水层
curl -s http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    echo ⚠️ 胶水层健康检查失败，可能仍在启动中
) else (
    echo ✅ 胶水层健康检查通过
)

if "%action%"=="deploy" (
    echo.
    echo 🎉 部署完成！
    echo 💡 使用 'deploy.bat logs' 查看日志
    echo 💡 使用 'deploy.bat stop' 停止服务
    echo 💡 使用 'deploy.bat restart' 重启服务
)
goto end

:usage
echo 使用方法: deploy.bat [deploy^|stop^|restart^|logs^|status^|clean^|update]
echo.
echo 命令说明:
echo   deploy   - 部署整个系统 ^(默认^)
echo   stop     - 停止所有服务
echo   restart  - 重启所有服务
echo   logs     - 查看服务日志
echo   status   - 检查服务状态
echo   clean    - 清理容器和数据
echo   update   - 更新系统
goto end

:end
pause 