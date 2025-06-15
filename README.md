# 说明
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



