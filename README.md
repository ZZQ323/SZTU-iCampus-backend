# SZTU iCampus 校园服务小程序

深圳技术大学校园服务统一入口小程序，提供校园公告、课表查询、部门通知、活动日历等功能。

## 项目结构

```
SZTU-iCampus/
├── backend/                # FastAPI 后端服务
│   ├── main.py            # 主入口文件
│   └── requirements.txt   # Python 依赖
├── miniprogram/           # 微信小程序前端
│   ├── pages/            # 页面文件
│   ├── components/       # 组件
│   └── project.config.json # 项目配置
└── README.md             # 项目说明
```

## 技术栈

- 后端：FastAPI
- 前端：微信小程序 + TDesign
- 数据库：待定
- 认证：JWT

## 开发环境设置

### 后端

1. 创建虚拟环境：
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 运行服务：
```bash
cd backend
uvicorn main:app --reload
```

### 小程序

1. 下载并安装[微信开发者工具](https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html)
2. 导入项目，选择 `miniprogram` 目录
3. 在 `project.config.json` 中填入你的小程序 AppID

## 功能特性

- 校园公告实时推送
- 课表查询
- 部门通知
- 活动日历
- 流式数据处理
- 安全认证

## 安全说明

- 所有API请求都需要进行身份验证
- 敏感数据加密存储
- 使用HTTPS进行通信
- 定期更新安全补丁

## 贡献指南

1. Fork 项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证

MIT License 

## 参考

坑：ssh: connect to host github.com port 22: Connection refused - 无忌的文章 - 知乎
https://zhuanlan.zhihu.com/p/521340971

https://blog.csdn.net/m0_68116052/article/details/142832657?fromshare=blogdetail&sharetype=blogdetail&sharerId=142832657&sharerefer=PC&sharesource=Shadowfight323&sharefrom=from_link

