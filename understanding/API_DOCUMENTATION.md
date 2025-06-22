# SZTU-iCampus API 文档

深圳技术大学校园服务小程序API文档

总共包含40+个API端点，涵盖校园生活的各个方面，前后端完全开源

### 开源地址

前端: 微信小程序 (miniprogram/)  
后端: FastAPI (backend/)

### 项目特色

- 🌊 **流式数据推送**: 实时公告推送，无需刷新页面
- 📚 **完整课表系统**: 支持复杂周次表达式，智能冲突检测
- 🎯 **管理员系统**: 完整的后台管理功能
- 📱 **现代化UI**: 基于TDesign小程序组件库

### 技术栈

- **后端**: FastAPI + SQLAlchemy + SQLite
- **前端**: 微信小程序 + TDesign-MiniProgram
- **认证**: JWT Token
- **数据库**: SQLite (开发) / PostgreSQL (生产)

### Mock地址

```
开发环境: http://127.0.0.1:8000
生产环境: https://your-domain.com
```

### Auth 认证

使用JWT进行认证，需要认证的接口在Header中添加：

```
Authorization: Bearer <your_jwt_token>
```

**接口旁边带 🔒 图标表示需要Token，无图标表示公开接口**

### 返回格式

所有接口统一返回格式：

```json
{
    "code": 0,           // 0为成功，其他为错误码
    "message": "success", // 返回消息
    "data": {}           // 具体数据
}
```

---

## 📱 基础接口

### 欢迎页面
**GET** `/`

返回API基本信息和服务状态

**响应示例:**
```json
{
    "message": "🌊 欢迎使用深圳技术大学校园服务API",
    "features": ["实时数据推送", "智能缓存", "增量更新"],
    "stream_active_connections": 0
}
```

---

## 🔐 认证模块 (Auth)

### 用户登录
**POST** `/api/v1/auth/login`

**请求参数:**
```json
{
    "student_id": "2024001",
    "password": "your_password"
}
```

**响应示例:**
```json
{
    "code": 0,
    "message": "登录成功",
    "data": {
        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "token_type": "bearer",
        "user_info": {
            "student_id": "2024001",
            "full_name": "张三",
            "is_admin": false
        }
    }
}
```

### 用户注册
**POST** `/api/v1/auth/register`

**请求参数:**
```json
{
    "student_id": "2024001",
    "password": "your_password",
    "full_name": "张三",
    "email": "zhangsan@sztu.edu.cn"
}
```

---

## 👥 用户模块 (Users) 🔒

### 获取用户信息
**GET** `/api/v1/users/me`

**响应示例:**
```json
{
    "code": 0,
    "message": "success",
    "data": {
        "id": 1,
        "student_id": "2024001",
        "full_name": "张三",
        "email": "zhangsan@sztu.edu.cn",
        "is_admin": false,
        "created_at": "2024-01-01T10:00:00"
    }
}
```

---

## 📢 公告模块 (Announcements)

### 获取公告列表
**GET** `/api/announcements`

**查询参数:**
- `skip`: 跳过条数 (默认: 0)
- `limit`: 返回条数 (默认: 10)

**响应示例:**
```json
{
    "code": 0,
    "message": "success",
    "data": {
        "announcements": [
            {
                "id": 1,
                "title": "关于2024年春季学期开学安排的通知",
                "content": "各位同学：根据学校安排...",
                "department": "教务处",
                "date": "2024-02-01",
                "time": "10:00"
            }
        ],
        "total": 5,
        "cached": false,
        "stream_connections": 0
    }
}
```

### 公告流式推送
**GET** `/api/announcements/stream`

基于Server-Sent Events的实时推送，新公告发布后立即推送到前端

**响应类型:** `text/event-stream`

---

## 📋 通知模块 (Notices)

### 获取通知列表
**GET** `/api/notices`

**查询参数:**
- `skip`: 跳过条数
- `limit`: 返回条数
- `department`: 部门筛选
- `notice_type`: 通知类型筛选

**响应示例:**
```json
{
    "code": 0,
    "message": "success",
    "data": {
        "notices": [
            {
                "id": 1,
                "title": "【紧急通知】期末考试时间调整",
                "content": "各位同学注意：由于教学安排调整...",
                "department": "教务处",
                "notice_type": "urgent",
                "priority": "high",
                "target_audience": "全体学生",
                "date": "2024-01-10",
                "time": "09:00",
                "effective_date": "2024-01-10 09:00",
                "expire_date": "2024-01-25 18:00"
            }
        ],
        "total": 5
    }
}
```

---

## 📚 课表模块 (Schedule) 🔒

### 获取课表网格
**GET** `/api/v1/schedule/grid/{week_number}`

**路径参数:**
- `week_number`: 周次 (1-30)

**查询参数:**
- `semester`: 学期 (默认: "2024-2025-1")

**响应示例:**
```json
{
    "week_number": 1,
    "semester": "2024-2025-1",
    "time_slots": [
        {
            "slot": 1,
            "name": "第1-2节",
            "start_time": "08:30",
            "end_time": "10:10"
        }
    ],
    "schedule_data": [
        [null, "高等数学A", null, "大学英语", null, null, null],
        [null, "线性代数", null, "程序设计", null, null, null]
    ],
    "student_info": {
        "student_id": "2024001",
        "full_name": "张三"
    }
}
```

### 获取当前周课表
**GET** `/api/v1/schedule/current-week`

自动计算当前周次并返回课表

### 创建新课程
**POST** `/api/v1/schedule/`

**请求参数:**
```json
{
    "course_name": "高等数学A",
    "course_code": "MATH001",
    "teacher": "张教授",
    "classroom": "教学楼A101",
    "week_day": 1,
    "time_slot": 1,
    "start_time": "08:30",
    "end_time": "10:10",
    "start_week": 1,
    "end_week": 16,
    "odd_even": "all",
    "course_type": "必修",
    "credits": 4,
    "semester": "2024-2025-1"
}
```

### 获取时间段信息
**GET** `/api/v1/schedule/time-slots/info`

返回标准时间段配置

---

## 📝 考试模块 (Exams)

### 获取考试列表
**GET** `/api/v1/exams/`

**查询参数:**
- `student_id`: 学生学号
- `exam_type`: 考试类型 (final, midterm, makeup)
- `semester`: 学期
- `skip`: 跳过条数
- `limit`: 返回条数

**响应示例:**
```json
{
    "code": 0,
    "message": "success",
    "data": {
        "exams": [
            {
                "id": 1,
                "course_name": "高等数学A",
                "course_code": "MATH001",
                "exam_type": "final",
                "exam_date": "2024-01-15",
                "start_time": "14:30",
                "end_time": "16:30",
                "duration": 120,
                "location": "教学楼A101",
                "seat_number": "A001",
                "teacher": "张教授",
                "exam_form": "闭卷",
                "total_score": 100,
                "status": "scheduled"
            }
        ],
        "total": 3,
        "next_exam": {...},
        "student_id": "2024001"
    }
}
```

### 获取考试详情
**GET** `/api/v1/exams/{exam_id}`

### 获取考试倒计时
**GET** `/api/v1/exams/countdown/{exam_id}`

**响应示例:**
```json
{
    "code": 0,
    "message": "success",
    "data": {
        "status": "countdown",
        "days": 5,
        "hours": 14,
        "minutes": 30,
        "seconds": 15,
        "total_seconds": 466815,
        "formatted": "5天14小时30分15秒"
    }
}
```

---

## 📖 图书馆模块 (Library)

### 获取借阅信息
**GET** `/api/v1/library/borrow-info`

**查询参数:**
- `student_id`: 学生学号

**响应示例:**
```json
{
    "code": 0,
    "message": "success",
    "data": {
        "student_id": "2024001",
        "current_borrow": 2,
        "max_borrow": 10,
        "borrow_list": [
            {
                "id": 1,
                "book_name": "高等数学（第七版）",
                "borrow_date": "2024-03-01",
                "return_date": "2024-06-01"
            }
        ]
    }
}
```

### 获取座位信息
**GET** `/api/v1/library/seats`

**响应示例:**
```json
{
    "code": 0,
    "message": "success",
    "data": {
        "floors": [
            {
                "id": 1,
                "name": "一楼阅览室",
                "available_seats": 45
            },
            {
                "id": 2,
                "name": "二楼阅览室",
                "available_seats": 38
            }
        ]
    }
}
```

---

## 🛂 管理员模块 (Admin) 🔒

### 获取系统统计
**GET** `/api/v1/admin/stats`

**响应示例:**
```json
{
    "code": 0,
    "message": "success",
    "data": {
        "total_users": 1520,
        "total_admins": 5,
        "total_announcements": 25,
        "total_notices": 40,
        "system_uptime": "72小时15分钟"
    }
}
```

### 获取用户列表
**GET** `/api/v1/admin/users`

### 切换用户管理员状态
**POST** `/api/v1/admin/users/{user_id}/toggle-admin`

### 删除公告
**DELETE** `/api/v1/admin/announcements/{id}`

### 删除通知
**DELETE** `/api/v1/admin/notices/{id}`

---

## 📱 小程序页面结构

### 底部Tab页面
1. **首页** (`pages/index/index`)
   - 用户信息展示
   - 快捷服务入口
   - 最新公告预览
   - 后勤联系电话

2. **公告** (`pages/announcements/announcements`)
   - 公告列表展示
   - 搜索和筛选功能
   - 公告详情查看

3. **课表** (`pages/schedule/schedule`)  
   - 7×5网格课表
   - 周次切换
   - 当前时间高亮
   - 课程添加和编辑

4. **通讯录** (`pages/address_book/address_book`)
   - 简化的占位页面

5. **校园卡** (`pages/campus-card/campus-card`)
   - 余额查询
   - 充值功能
   - 消费记录

### 功能页面
- **考试安排** (`pages/exams/exams`) - 考试列表和倒计时
- **图书馆** (`pages/library/library`) - 借阅信息、座位查询  
- **通知** (`pages/notifications/notifications`) - 部门通知管理
- **管理员** (`pages/admin/admin`) - 后台管理功能

---

## 🔧 开发环境

### 后端启动
```bash
conda activate icamp
cd backend
uvicorn main:app --reload
```

### 前端开发
```bash
# 使用微信开发者工具打开 miniprogram 目录
```

### 接口文档
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

---

## 📊 项目特色功能

### 1. 流式数据推送
- 基于Server-Sent Events
- 新公告实时推送
- 减少客户端轮询

### 2. 智能课表系统
- 支持复杂周次表达式 (如: "1-8+10-16")
- 自动冲突检测
- 7×5网格可视化
- 今日课程高亮

### 3. 完整管理员系统
- 用户权限管理
- 内容审核删除
- 系统数据统计

### 4. 现代化UI设计
- TDesign组件库
- 响应式布局
- 优雅的交互动画

---

## 📄 许可证

MIT License

---

## 🤝 贡献

欢迎提交Issue和Pull Request！

**开发规范:**
- 遵循RESTful API设计
- 使用TypeScript类型注解
- 编写完整的单元测试
- 保持代码简洁易读 