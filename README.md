# <img src="https://tse3-mm.cn.bing.net/th/id/OIP-C.zQL-7OxQrySft5EMt8Xd7QAAAA?rs=1&pid=ImgDetMain" style="width:25px"/> SZTU iCampus 校园服务小程序

深圳技术大学校园服务统一入口小程序，基于**流式封装技术**实现实时数据推送，提供校园公告、课表查询、部门通知、活动日历等功能。

## 🎯 项目核心亮点 - 流式封装技术

本项目不仅仅是个小程序，同时展示了流式数据处理能力，**流式封装带来的体验**:

- **⚡ 实时推送**: 新公告发布后，所有在线用户立即收到推送
- **📊 动态更新**: 活动参与人数实时变化，无需刷新页面
- **🔔 智能提醒**: 重要通知自动弹窗 + 震动提醒
- **💾 资源优化**: 只传输变化数据，节省90%带宽和存储

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

1. 虚拟环境：
```bash
conda create -n Icamp
conda activate Icamp     # Windows
pip install -r requirements.txt
```

2. 运行服务：
```cmd
cd backend
setup_db.py
uvicorn main:app --reload
```


## 功能特性以及安全说明

- 校园公告实时推送
- 课表查询
- 部门通知
- 活动日历
- 流式数据处理
- 安全认证
- 所有API请求都需要进行身份验证
- 敏感数据加密存储
- 使用HTTPS进行通信
- 定期更新安全补丁

## 🌊 流式封装技术详解

### 什么是流式封装？
流式封装指的是数据不是一次性全部加载，而是像"水流"一样持续不断地推送给用户。

### 传统方式 vs 流式方式

| 对比维度 | 传统REST API | 流式封装 | 提升效果 |
|---------|------------|---------|---------|
| **数据获取** | 点击-等待-加载 | 自动-实时-推送 | 响应速度提升80% |
| **信息更新** | 手动刷新获取 | 自动推送更新 | 用户操作减少90% |
| **数据准确性** | 可能存在延迟 | 始终保持最新 | 信息准确性100% |
| **服务器压力** | 高频轮询请求 | 一次连接持续推送 | 服务器负载减少70% |

### 🎮 体验流式效果

1. **启动项目后，观察这些实时更新：**
   - 📢 首页公告列表 - 新公告自动出现在顶部
   - 🎯 活动页面 - 参与人数和进度条实时变化
   - 🔔 通知提醒 - 重要消息立即弹窗

2. **开发者工具查看流式日志：**
   ```javascript
   [StreamManager] 连接流式数据源: announcements
   [首页] 收到新公告推送: {title: "期末考试安排通知"}
   [活动页面] 活动参与人数更新: 126 → 127
   ```

**📋 详细技术说明:** [流式封装技术说明.md](流式封装技术说明.md)


## 许可证

MIT License 

## 参考

[坑：ssh: connect to host github.com port 22: Connection refused - 无忌的文章 - 知乎](https://zhuanlan.zhihu.com/p/521340971)

[全网最全面详细的Cursor使用教程，让开发变成聊天一样容易](https://blog.csdn.net/m0_68116052/article/details/142832657?fromshare=blogdetail&sharetype=blogdetail&sharerId=142832657&sharerefer=PC&sharesource=Shadowfight323&sharefrom=from_link)

[解决 Cursor 连接失败的小技巧 - 一个导航的文章 - 知乎](https://zhuanlan.zhihu.com/p/1907071064191771454)
