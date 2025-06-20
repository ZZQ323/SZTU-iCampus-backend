# SZTU-iCampus 数据库服务

独立的数据库服务，负责数据存储和Mock数据生成，与胶水层分离部署。

## 目录结构

```
data-service/
├── README.md                 # 项目说明
├── requirements.txt          # Python依赖
├── main.py                   # 数据服务主程序
├── config.py                 # 配置文件
├── models/                   # 数据库模型
│   ├── __init__.py
│   ├── base.py              # 基础模型
│   ├── person.py            # 人员相关模型
│   ├── organization.py      # 组织架构模型
│   ├── course.py            # 课程相关模型
│   ├── research.py          # 科研相关模型
│   ├── asset.py             # 资产管理模型
│   ├── library.py           # 图书馆模型
│   ├── finance.py           # 财务相关模型
│   └── permission.py        # 权限管理模型
├── generators/               # Mock数据生成器
│   ├── __init__.py
│   ├── base_generator.py    # 基础生成器
│   ├── person_generator.py  # 人员数据生成
│   ├── course_generator.py  # 课程数据生成
│   ├── research_generator.py # 科研数据生成
│   └── asset_generator.py   # 资产数据生成
├── database.py              # 数据库连接配置
├── crud/                    # CRUD操作
│   ├── __init__.py
│   ├── base.py
│   └── operations.py
└── scripts/                 # 初始化脚本
    ├── init_db.py          # 数据库初始化
    ├── generate_mock.py    # Mock数据生成
    └── reset_db.py         # 数据库重置
```

## 功能特性

### 数据模型
- 25张核心数据表的完整定义
- 基于SQLAlchemy ORM的模型设计
- 完整的外键关系和约束

### Mock数据生成
- 真实的中文姓名和地址生成
- 符合业务逻辑的关联数据
- 可配置的数据量和分布
- 时间序列数据生成

### 数据服务API
- RESTful API接口
- 支持复杂查询和聚合
- 数据分页和排序
- 批量操作支持

## 部署说明

### 开发环境

```bash
# 创建虚拟环境
conda create -n data-service python=3.9
conda activate data-service

# 安装依赖
pip install -r requirements.txt

# 初始化数据库
python scripts/init_db.py

# 生成Mock数据
python scripts/generate_mock.py

# 启动数据服务
python main.py
```

### 生产环境
```bash
# 使用Docker部署
docker build -t sztu-dataservice .
docker run -d -p 8001:8001 sztu-dataservice

# 或使用docker-compose
docker-compose up -d
```

## API接口

### 基础接口
- `GET /health` - 健康检查
- `GET /stats` - 数据统计
- `POST /reset` - 重置数据

### 数据查询接口
- `GET /persons` - 人员查询
- `GET /courses` - 课程查询  
- `GET /research` - 科研项目查询
- `GET /assets` - 资产查询

### 批量操作接口
- `POST /batch/persons` - 批量创建人员
- `PUT /batch/update` - 批量更新
- `DELETE /batch/delete` - 批量删除

## 配置说明

### 数据库配置
```python
DATABASE_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "sztu_campus",
    "username": "postgres", 
    "password": "password"
}
```

### Mock数据配置
```python
MOCK_CONFIG = {
    "colleges": 13,           # 学院数量
    "majors_per_college": 6,  # 每学院专业数
    "classes_per_major": 4,   # 每专业班级数
    "students_per_class": 35, # 每班学生数
    "teachers_per_college": 50, # 每学院教师数
    "courses_per_semester": 200, # 每学期课程数
}
```

## 监控与日志

### 性能监控
- 数据库连接池监控
- API响应时间统计
- 内存和CPU使用率

### 日志记录
- 结构化日志输出
- 错误日志追踪
- 操作审计日志

## 数据安全

### 数据脱敏
- 敏感信息自动脱敏
- 可配置的脱敏规则
- 开发/生产环境隔离

### 访问控制
- API密钥认证
- IP白名单限制
- 操作权限控制 