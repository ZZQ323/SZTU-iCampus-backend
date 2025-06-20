# SZTU-iCampus 微信小程序项目

## 项目概述

开发一个微信小程序，作为校园内各种Web服务的统一入口，利用流式处理技术实时加载内容，保证数据的安全性和隐私性，同时不占用服务器存储资源。

功能包括：校园公告、课表查询、部门通知、活动日历等。

## 技术架构

- **前端**: 微信小程序 + TDesign-MiniProgram UI组件库
- **后端**: FastAPI框架
- **数据服务**: 独立的数据库服务（胶水层设计）
- **数据库**: PostgreSQL
- **流式处理**: SSE (Server-Sent Events)

## 项目结构

```
SZTU-iCampus/
├── backend/                    # 胶水层后端服务
│   ├── app/                   # FastAPI应用
│   ├── main.py               # 主程序入口
│   └── requirements.txt      # 依赖文件
├── data-service/              # 独立数据库服务 ⭐ 新增
│   ├── models/               # 数据模型（25张表）
│   ├── generators/           # Mock数据生成器
│   ├── scripts/             # 初始化脚本
│   ├── main.py              # 数据服务主程序
│   ├── config.py            # 配置文件
│   ├── database.py          # 数据库连接
│   └── requirements.txt     # 依赖文件
├── miniprogram/              # 微信小程序前端
│   ├── pages/               # 页面文件
│   ├── components/          # 组件文件
│   └── utils/              # 工具函数
└── README.md               # 项目说明
```

## 数据服务实现 🚀

### 架构设计特点

✅ **胶水层设计**: 数据服务与业务逻辑分离，不占用存储资源  
✅ **25张核心数据表**: 覆盖人员、课程、科研、资产、图书、财务、权限等全校园业务  
✅ **真实数据模型**: 基于SZTU实际业务需求设计，包含完整编号系统  
✅ **Mock数据生成**: 支持生成大量真实的中文测试数据  
✅ **API接口**: RESTful API + 流式推送（SSE）  
✅ **权限控制**: 基于角色的细粒度权限管理  
✅ **数据脱敏**: 自动处理敏感信息（手机号、身份证等）  

### 数据模型概览

#### 核心实体（25张表）
| 类别 | 表名 | 说明 |
|------|------|------|
| 人员系统 | persons, classes | 统一人员管理、班级管理 |
| 组织架构 | colleges, majors, departments, locations | 学院-专业-部门-地点体系 |
| 课程体系 | courses, course_instances, grades, grade_statistics | 课程基础信息与开课实例分离 |
| 科研系统 | research_projects, research_applications, paper_library | 项目申请到成果发表全流程 |
| 资产管理 | assets | 6大类校园资产管理 |
| 图书馆 | books, borrow_records | 完整借阅管理系统 |
| 财务系统 | transactions, campus_cards | 校园卡消费流水管理 |
| 权限管理 | network_permissions, system_access, platform_configs | 网络使用、多平台登录、审计日志 |

#### 编号系统设计
- **学院编码**: C001-C013（13个学院）
- **专业编码**: 基于国标代码，覆盖理工经管文等全学科
- **学生学号**: 年份(4位)+专业编码(4位)+班级号(2位)+学生序号(2位)
- **教职工工号**: 年份(4位)+专业编号(4位)+序号(2位)
- **建筑编码**: C1-C5(教学)、D1-D3(经管)、E0-E3(实验)、L1-L3(图书馆)、S1-S10(宿舍)

### 快速开始 🚀

#### 🎯 一键部署（推荐）

使用我们提供的自动化部署脚本，零配置启动整个系统：

**Linux/macOS:**
```bash
# 克隆项目
git clone <repository-url>
cd SZTU-iCampus

# 赋予执行权限并部署
chmod +x deploy.sh
./deploy.sh
```

**Windows:**
```cmd
# 克隆项目
git clone <repository-url>
cd SZTU-iCampus

# 运行部署脚本
deploy.bat
```

🎉 **部署完成！访问服务:**
- 胶水层: http://localhost:8000
- 数据服务: http://localhost:8001  
- API文档: http://localhost:8000/docs

#### 🐳 Docker Compose 部署

```bash
# 启动所有服务（PostgreSQL + Redis + 数据服务 + 胶水层）
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看实时日志
docker-compose logs -f glue-layer data-service

# 停止服务
docker-compose down
```

#### 🔧 手动开发部署

1. **启动数据服务**
```bash
cd data-service
conda create -n dataservice python=3.11
conda activate dataservice
pip install -r requirements.txt
python main.py
```

2. **启动胶水层**
```bash
cd backend
conda activate icamp
pip install -r requirements.txt
uvicorn main:app --reload
```

#### 📡 服务地址

| 服务 | 地址 | 说明 |
|------|------|------|
| 🌐 胶水层 | http://localhost:8000 | 主要业务逻辑层 |
| 🗄️ 数据服务 | http://localhost:8001 | 数据库服务层 |
| 📚 API文档 | http://localhost:8000/docs | 胶水层API文档 |
| 📖 数据文档 | http://localhost:8001/docs | 数据服务API文档 |
| 🗃️ PostgreSQL | localhost:5432 | 数据库 |
| 💾 Redis | localhost:6379 | 缓存服务 |

#### 🛠️ 部署脚本命令

**Linux/macOS:**
```bash
./deploy.sh [deploy|status|logs|restart|stop|clean|update]
```

**Windows:**
```cmd
deploy.bat [deploy|status|logs|restart|stop|clean|update]
```

**命令说明:**
- `deploy` - 部署整个系统（默认）
- `status` - 查看服务状态
- `logs` - 查看实时日志
- `restart` - 重启服务
- `stop` - 停止服务
- `clean` - 清理环境
- `update` - 更新系统

### 配置说明

#### 数据库配置
```python
DATABASE_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "sztu_campus",
    "username": "postgres",
    "password": "password"
}
```

#### Mock数据配置
```python
MOCK_CONFIG = {
    "colleges": 13,                    # 学院数量
    "majors_per_college": 6,           # 每学院专业数
    "classes_per_major": 4,            # 每专业班级数
    "students_per_class": 35,          # 每班学生数
    "teachers_per_college": 50,        # 每学院教师数
    "books_count": 50000,              # 图书总数
}
```

### Docker部署

```bash
# 构建镜像
cd data-service
docker build -t sztu-dataservice .

# 运行容器
docker run -d -p 8001:8001 \
  -e DATABASE_URL=postgresql://postgres:password@host.docker.internal:5432/sztu_campus \
  sztu-dataservice
```

## 开发进度

### ✅ 已完成

#### 第二步：数据服务实现
1. **数据模型设计**: 25张核心数据表完整设计
2. **数据服务实现**: 独立的FastAPI数据服务
3. **Mock数据生成**: 真实中文数据生成器
4. **API接口**: RESTful API + 流式推送
5. **容器化部署**: Docker配置完成
6. **权限控制**: 基于角色的权限管理
7. **数据脱敏**: 敏感信息自动处理

#### 第三步：胶水层重构与容器化 🚀 NEW
1. **数据服务客户端**: 无缝集成数据服务，支持Mock/Real开关
2. **Redis缓存机制**: 多级缓存提升性能，自动过期和清理
3. **流式推送优化**: SSE事件驱动推送，心跳检测和重连机制
4. **胶水层容器化**: 完整的Docker配置和健康检查
5. **一键部署脚本**: 自动化部署脚本，支持多种部署模式
6. **Docker Compose**: 统一管理所有服务（数据库、缓存、服务层）
7. **监控和日志**: 结构化日志、服务监控和健康检查
8. **配置管理**: 环境变量配置、动态开关切换

### 🚧 进行中（第四步）

1. **微信小程序前端**: 完整的前端界面开发
2. **真实数据对接**: 替换Mock数据为真实接口
3. **性能优化**: 大规模数据处理优化
4. **安全加固**: 完善的身份验证和授权

### 📋 计划中

1. **生产环境部署**: K8s部署、监控告警、备份策略
2. **前端完善**: 微信小程序全功能实现
3. **数据同步**: 与现有系统的数据同步机制
4. **压力测试**: 性能测试和优化

## API密钥

开发环境API密钥: `sztu-data-service-key-2024`

所有需要认证的接口都需要传入此参数：
```
GET /stats?api_key=sztu-data-service-key-2024
```

## 项目特色

🎯 **最小信息呈现原则**: 只传输必要数据，支持流式推送  
🏗️ **胶水层架构**: 后端与数据库服务分离，灵活可扩展  
🔐 **安全传输**: 完整的权限控制和数据脱敏机制  
🌊 **流式处理**: SSE实时推送，支持增量更新  
🎨 **配置驱动**: Mock/Real API一键切换  
📊 **真实数据**: 基于SZTU实际业务需求设计  

## 注意事项

1. **首次运行**: 需要先启动数据服务，再启动胶水层后端
2. **数据库**: 确保PostgreSQL服务正常运行
3. **端口占用**: 数据服务默认使用8001端口，胶水层使用8000端口
4. **日志文件**: 日志保存在`data-service/logs/`目录下
5. **Mock数据**: 生成大量数据时可能需要较长时间，建议后台运行

## 贡献指南

1. Fork 项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

---

**项目状态**: 🟢 活跃开发中  
**最后更新**: 2024年12月  
**技术栈**: FastAPI + 微信小程序 + PostgreSQL + Redis