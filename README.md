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

- 后端：FastAPI
- 数据库：Alembic+ SQLAlchemy + Pydantic + SQLite/PostgreSQL
- JWT认证
- 前端：miniprogramme+tdesign

## 开发环境设置

1. 创建虚拟环境：
```bash
python -m venv venv
venv\Scripts\activate  # Windows
conda activate icamp # anaconda
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 初始化数据库：
```bash
python -m setup_db.py
```

4. 运行开发服务器：
```bash
uvicorn main:app --reload
```

5. 使用postman或者其他工具保证路由正常；


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
│   ├── core/            # 核心配置（配置、安全、队列），被所有层调用
│   ├── crud/            # CRUD操作存取封装
│   ├── db/              # 数据库
│   ├── models/          # SQLAlchemy 使用 ORM 模型
│   └── schemas/         # Pydantic 模型，做数据验证用的
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

## 根目录

```
./
├── .git/                    # Git版本控制目录
├── README.md               # 项目主文档，包含项目说明和使用指南
├── miniprogram/            # 微信小程序前端代码
├── backend/                # FastAPI后端代码
├── QUICK_START.md          # 快速启动指南
├── .gitignore              # Git忽略文件配置
├── clean.bat               # Windows环境清理脚本
├── project.config.json     # 微信小程序项目配置文件
└── project.private.config.json  # 微信小程序私有配置文件
```

## 前端目录 (miniprogram/)

```
miniprogram/
├── project.config.json     # 小程序项目配置
├── project.private.config.json  # 小程序私有配置
├── utils/                  # 工具函数目录
│   └── stream.js          # 流式数据处理管理器
├── pages/                  # 页面文件目录
│   ├── index/             # 首页
│   ├── events/            # 活动页面
│   └── ...                # 其他页面
├── components/            # 可复用组件目录
├── assets/                # 静态资源目录（图片等）
├── miniprogram_npm/       # 小程序npm包目录
├── node_modules/          # Node.js依赖包目录
├── app.wxss              # 全局样式文件
├── app.json              # 小程序全局配置
├── app.js                # 小程序入口文件
└── sitemap.json          # 小程序站点地图配置
```

## 后端目录 (backend/)

```
backend/
├── main.py               # FastAPI主程序入口
├── sztu_icampus.db       # SQLite数据库文件
├── setup_db.py           # 数据库初始化脚本
├── run.py                # 服务器启动脚本
├── app/                  # 应用核心代码目录
│   ├──api/	    接口路由和分组,接口大门
│      ├──v1/	    版本号分组
│      └──deps.py	    依赖项
│   ├──core/	全局配置、安全,大脑和保险箱
│   ├──crud/	数据库操作封装,数据库工具箱
│   ├──db/	    数据库连接、模型注册,数据库入口和注册处
│   ├──models/	数据库表结构定义,表的蓝图
│   ├──schemas/	接口数据格式和校验,数据说明书
│   ├──utils.py	工具函数,小工具
│   └──queue.py	异步消息队列,消息中转站
├── init.bat              # Windows环境初始化脚本
├── requirements.txt      # Python依赖包列表
├── alembic/              # 数据库迁移工具目录
└── alembic.ini           # Alembic配置文件
```

## 贡献

欢迎提交Issue和Pull Request！

## 许可证

MIT 

## 参考

[坑：ssh: connect to host github.com port 22: Connection refused - 无忌的文章 - 知乎](https://zhuanlan.zhihu.com/p/521340971)

[全网最全面详细的Cursor使用教程，让开发变成聊天一样容易](https://blog.csdn.net/m0_68116052/article/details/142832657?fromshare=blogdetail&sharetype=blogdetail&sharerId=142832657&sharerefer=PC&sharesource=Shadowfight323&sharefrom=from_link)

[解决 Cursor 连接失败的小技巧 - 一个导航的文章 - 知乎](https://zhuanlan.zhihu.com/p/1907071064191771454)