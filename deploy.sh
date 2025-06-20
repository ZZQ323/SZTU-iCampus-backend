#!/bin/bash

# SZTU-iCampus 部署脚本
# 自动化部署胶水层和数据服务

set -e

echo "🚀 开始部署 SZTU-iCampus 系统"
echo "=================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检查 Docker 和 Docker Compose
check_dependencies() {
    echo -e "${BLUE}📋 检查依赖...${NC}"
    
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker 未安装，请先安装 Docker${NC}"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        echo -e "${RED}❌ Docker Compose 未安装，请先安装 Docker Compose${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ 依赖检查通过${NC}"
}

# 创建必要的目录
create_directories() {
    echo -e "${BLUE}📁 创建必要目录...${NC}"
    
    mkdir -p backend/logs
    mkdir -p data-service/logs
    mkdir -p nginx
    mkdir -p monitoring
    
    echo -e "${GREEN}✅ 目录创建完成${NC}"
}

# 构建和启动服务
start_services() {
    echo -e "${BLUE}🏗️ 构建和启动服务...${NC}"
    
    # 停止现有服务
    echo "停止现有服务..."
    docker-compose down --remove-orphans 2>/dev/null || true
    
    # 构建镜像
    echo "构建 Docker 镜像..."
    docker-compose build --no-cache
    
    # 启动核心服务
    echo "启动核心服务..."
    docker-compose up -d postgres redis
    
    # 等待数据库就绪
    echo "等待 PostgreSQL 就绪..."
    sleep 10
    
    # 启动数据服务
    echo "启动数据服务..."
    docker-compose up -d data-service
    
    # 等待数据服务就绪
    echo "等待数据服务就绪..."
    sleep 15
    
    # 启动胶水层
    echo "启动胶水层..."
    docker-compose up -d glue-layer
    
    echo -e "${GREEN}✅ 服务启动完成${NC}"
}

# 初始化数据
init_data() {
    echo -e "${BLUE}📊 初始化数据...${NC}"
    
    # 等待数据服务完全启动
    sleep 20
    
    # 初始化数据库
    echo "初始化数据库结构..."
    docker-compose exec -T data-service python -c "
import asyncio
from scripts.init_db import init_database
from generators.base_generator import generate_all_data
asyncio.run(init_database())
asyncio.run(generate_all_data())
print('数据库初始化完成')
" || echo "数据库初始化可能已存在，跳过..."
    
    echo -e "${GREEN}✅ 数据初始化完成${NC}"
}

# 检查服务状态
check_services() {
    echo -e "${BLUE}🔍 检查服务状态...${NC}"
    
    services=("postgres" "redis" "data-service" "glue-layer")
    
    for service in "${services[@]}"; do
        status=$(docker-compose ps -q $service)
        if [ -n "$status" ]; then
            echo -e "${GREEN}✅ $service: 运行中${NC}"
        else
            echo -e "${RED}❌ $service: 未运行${NC}"
        fi
    done
    
    echo ""
    echo -e "${BLUE}🌐 服务地址:${NC}"
    echo -e "${YELLOW}  胶水层:    http://localhost:8000${NC}"
    echo -e "${YELLOW}  数据服务:  http://localhost:8001${NC}"
    echo -e "${YELLOW}  API文档:   http://localhost:8000/docs${NC}"
    echo -e "${YELLOW}  数据文档:  http://localhost:8001/docs${NC}"
    echo ""
    
    # 健康检查
    echo -e "${BLUE}🏥 健康检查...${NC}"
    sleep 5
    
    # 检查数据服务
    if curl -s http://localhost:8001/health > /dev/null; then
        echo -e "${GREEN}✅ 数据服务健康检查通过${NC}"
    else
        echo -e "${YELLOW}⚠️ 数据服务健康检查失败，可能仍在启动中${NC}"
    fi
    
    # 检查胶水层
    if curl -s http://localhost:8000/health > /dev/null; then
        echo -e "${GREEN}✅ 胶水层健康检查通过${NC}"
    else
        echo -e "${YELLOW}⚠️ 胶水层健康检查失败，可能仍在启动中${NC}"
    fi
}

# 显示日志
show_logs() {
    echo -e "${BLUE}📜 显示服务日志 (Ctrl+C 退出)...${NC}"
    docker-compose logs -f glue-layer data-service
}

# 主函数
main() {
    case "${1:-deploy}" in
        "deploy")
            check_dependencies
            create_directories
            start_services
            init_data
            check_services
            echo ""
            echo -e "${GREEN}🎉 部署完成！${NC}"
            echo -e "${BLUE}💡 使用 './deploy.sh logs' 查看日志${NC}"
            echo -e "${BLUE}💡 使用 './deploy.sh stop' 停止服务${NC}"
            echo -e "${BLUE}💡 使用 './deploy.sh restart' 重启服务${NC}"
            ;;
        "stop")
            echo -e "${BLUE}🛑 停止服务...${NC}"
            docker-compose down
            echo -e "${GREEN}✅ 服务已停止${NC}"
            ;;
        "restart")
            echo -e "${BLUE}🔄 重启服务...${NC}"
            docker-compose restart
            echo -e "${GREEN}✅ 服务已重启${NC}"
            ;;
        "logs")
            show_logs
            ;;
        "status")
            check_services
            ;;
        "clean")
            echo -e "${BLUE}🧹 清理容器和数据...${NC}"
            docker-compose down -v --remove-orphans
            docker system prune -f
            echo -e "${GREEN}✅ 清理完成${NC}"
            ;;
        "update")
            echo -e "${BLUE}🔄 更新系统...${NC}"
            docker-compose down
            docker-compose build --no-cache
            docker-compose up -d
            echo -e "${GREEN}✅ 更新完成${NC}"
            ;;
        *)
            echo "使用方法: $0 [deploy|stop|restart|logs|status|clean|update]"
            echo ""
            echo "命令说明:"
            echo "  deploy   - 部署整个系统 (默认)"
            echo "  stop     - 停止所有服务"
            echo "  restart  - 重启所有服务"
            echo "  logs     - 查看服务日志"
            echo "  status   - 检查服务状态"
            echo "  clean    - 清理容器和数据"
            echo "  update   - 更新系统"
            ;;
    esac
}

# 执行主函数
main "$@" 