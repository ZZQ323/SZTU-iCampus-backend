# SZTU-iCampus Backend

深圳技术大学校园服务小程序后端API服务

## 功能特性

- 用户认证与授权
- 校园公告管理
- 课表查询
- 部门通知
- 活动日历
- 成绩查询
- 考试安排
- 校园卡服务
- 图书馆服务

## 技术栈

- FastAPI
- SQLAlchemy
- Pydantic
- JWT认证
- SQLite/PostgreSQL

## 开发环境设置

1. 创建虚拟环境：
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 初始化数据库：
```bash
alembic upgrade head
```

4. 运行开发服务器：
```bash
uvicorn app.main:app --reload
```

## API文档

启动服务器后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 项目结构

```
backend/
├── alembic/              # 数据库迁移
├── app/
│   ├── api/             # API路由
│   ├── core/            # 核心配置
│   ├── crud/            # CRUD操作
│   ├── db/              # 数据库
│   ├── models/          # SQLAlchemy模型
│   └── schemas/         # Pydantic模型
├── tests/               # 测试
├── requirements.txt     # 依赖
└── README.md           # 文档
```

## 部署

1. 设置环境变量：
```bash
export SECRET_KEY="your-secret-key"
export DATABASE_URL="postgresql://user:password@localhost/dbname"
```

2. 运行生产服务器：
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 贡献

欢迎提交Issue和Pull Request！

## 许可证

MIT 