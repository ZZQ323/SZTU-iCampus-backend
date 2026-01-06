# SZTU-icampus 校园服务流式封装

## 项目简介

内容简介：开发一个微信小程序，它将作为校园内各种Web服务的统一入口，利用流式处理技术实时加载内容，保证数据的安全性和隐私性，同时不占用服务器存储资源。

功能包括：校园公告+部门通知、课表查询、活动日历等。

技术框架：fastapi + playwright

项目结构：
```
school-auth-proxy/
├── src/
│   ├── config/settings.py          # 配置
│   ├── domain/                      # 领域层
│   │   ├── entities/auth.py         # 实体
│   │   ├── repositories/            # 仓储接口
│   │   └── services/                # 服务接口
│   ├── infrastructure/              # 基础设施层
│   │   ├── http/school_auth_client.py   # 核心 HTTP 客户端
│   │   └── repositories/            # Redis 实现
│   ├── application/use_cases/       # 应用层
│   └── api/                         # 接口层
└── main.py
```

## 项目亮点

- 结合爬虫与推送技术，组织一个联合多平台的信息聚合平台，简化用户登录多个平台并总结信息的操作
- 包含校园小程序常用功能
- 采用DDD框架组织代码，利于维护

## 项目开始

配置环境

```bash
pip install -r requirementsV1.txt
playwright install
```

启动项目

```bash
python run.py
```

## Reference

