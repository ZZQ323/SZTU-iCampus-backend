# SZTU-iCampus API设计规范 v2.0

## 1. 统一响应格式

```json
{
    "code": 0,           // 0为成功，其他为错误码
    "message": "success", // 返回消息
    "data": {},          // 具体数据
    "timestamp": "2024-03-01T12:30:00Z", // ISO 8601格式时间戳
    "version": "v1.0"
}
```

## 2. RESTful API设计规范

### 2.1 认证模块 `/api/v1/auth`
- `POST /api/v1/auth/login` - 用户登录
- `POST /api/v1/auth/logout` - 用户登出
- `POST /api/v1/auth/wechat/bind` - 绑定微信
- `DELETE /api/v1/auth/wechat/unbind` - 解绑微信
- `GET /api/v1/auth/wechat/status` - 查询绑定状态

### 2.2 用户模块 `/api/v1/users`
- `GET /api/v1/users/me` - 获取当前用户信息
- `PUT /api/v1/users/me` - 更新用户信息
- `GET /api/v1/users/me/permissions` - 获取用户权限

### 2.3 课表模块 `/api/v1/schedule`
- `GET /api/v1/schedule` - 获取课表列表
- `GET /api/v1/schedule/week/{week_number}` - 获取指定周课表
- `GET /api/v1/schedule/current-week` - 获取当前周课表
- `GET /api/v1/schedule/grid/{week_number}` - 获取课表网格数据
- `POST /api/v1/schedule` - 添加课程（学生选课）
- `DELETE /api/v1/schedule/{schedule_id}` - 删除课程

### 2.4 成绩模块 `/api/v1/grades`
- `GET /api/v1/grades` - 获取成绩列表
- `GET /api/v1/grades/semester/{semester}` - 获取指定学期成绩
- `GET /api/v1/grades/statistics` - 获取成绩统计

### 2.5 考试模块 `/api/v1/exams`
- `GET /api/v1/exams` - 获取考试列表
- `GET /api/v1/exams/{exam_id}` - 获取考试详情
- `GET /api/v1/exams/{exam_id}/countdown` - 获取考试倒计时

### 2.6 图书馆模块 `/api/v1/library`
- `GET /api/v1/library/books/search` - 图书搜索
- `GET /api/v1/library/borrows` - 获取借阅记录
- `POST /api/v1/library/borrows/{book_id}` - 借阅图书
- `PUT /api/v1/library/borrows/{record_id}/renew` - 续借图书
- `GET /api/v1/library/seats` - 获取座位信息
- `POST /api/v1/library/seats/reserve` - 预约座位

### 2.7 校园卡模块 `/api/v1/campus-card`
- `GET /api/v1/campus-card/info` - 获取校园卡信息
- `GET /api/v1/campus-card/transactions` - 获取消费记录
- `POST /api/v1/campus-card/recharge` - 校园卡充值

### 2.8 公告模块 `/api/v1/announcements`
- `GET /api/v1/announcements` - 获取公告列表
- `GET /api/v1/announcements/{id}` - 获取公告详情
- `POST /api/v1/announcements` - 发布公告（管理员）
- `PUT /api/v1/announcements/{id}` - 更新公告（管理员）
- `DELETE /api/v1/announcements/{id}` - 删除公告（管理员）
- `POST /api/v1/announcements/{id}/read` - 标记公告已读
- `GET /api/v1/announcements/{id}/readers` - 获取阅读统计
- `POST /api/v1/announcements/{id}/confirm` - 确认已阅读（需确认类公告）

### 2.9 活动模块 `/api/v1/events`
- `GET /api/v1/events` - 获取活动列表
- `GET /api/v1/events/{id}` - 获取活动详情
- `POST /api/v1/events` - 创建活动（教师/管理员）
- `PUT /api/v1/events/{id}` - 更新活动信息
- `DELETE /api/v1/events/{id}` - 删除活动
- `POST /api/v1/events/{id}/register` - 报名活动
- `DELETE /api/v1/events/{id}/register` - 取消报名
- `GET /api/v1/events/{id}/registrations` - 获取报名列表（组织者）
- `PUT /api/v1/events/{id}/registrations/{reg_id}` - 更新报名状态
- `POST /api/v1/events/{id}/checkin` - 活动签到
- `GET /api/v1/events/{id}/statistics` - 活动统计信息

### 2.10 基础数据模块 `/api/v1/base`
- `GET /api/v1/base/colleges` - 获取学院列表
- `GET /api/v1/base/colleges/{id}/majors` - 获取学院专业列表
- `GET /api/v1/base/majors` - 获取专业列表
- `GET /api/v1/base/majors/{id}/classes` - 获取专业班级列表
- `GET /api/v1/base/classes` - 获取班级列表
- `GET /api/v1/base/departments` - 获取部门列表
- `GET /api/v1/base/locations` - 获取场所列表
- `GET /api/v1/base/locations/{id}/occupations` - 获取场所占用情况

### 2.11 课程管理模块 `/api/v1/courses`
- `GET /api/v1/courses` - 获取课程列表
- `GET /api/v1/courses/{id}` - 获取课程详情
- `POST /api/v1/courses` - 创建课程（管理员）
- `PUT /api/v1/courses/{id}` - 更新课程信息
- `DELETE /api/v1/courses/{id}` - 删除课程
- `GET /api/v1/courses/{id}/instances` - 获取课程开课实例
- `POST /api/v1/courses/{id}/instances` - 创建开课实例
- `PUT /api/v1/courses/instances/{instance_id}` - 更新开课实例
- `GET /api/v1/courses/instances/{instance_id}/students` - 获取选课学生列表
- `POST /api/v1/courses/instances/{instance_id}/grades` - 录入成绩
- `GET /api/v1/courses/instances/{instance_id}/statistics` - 获取课程统计

### 2.12 科研管理模块 `/api/v1/research`
- `GET /api/v1/research/projects` - 获取科研项目列表
- `GET /api/v1/research/projects/{id}` - 获取项目详情
- `POST /api/v1/research/projects` - 创建科研项目
- `PUT /api/v1/research/projects/{id}` - 更新项目信息
- `DELETE /api/v1/research/projects/{id}` - 删除项目
- `POST /api/v1/research/projects/{id}/members` - 添加项目成员
- `DELETE /api/v1/research/projects/{id}/members/{member_id}` - 移除项目成员
- `GET /api/v1/research/applications` - 获取项目申请列表
- `POST /api/v1/research/applications` - 提交项目申请
- `PUT /api/v1/research/applications/{id}` - 更新申请信息
- `POST /api/v1/research/applications/{id}/review` - 审核申请
- `GET /api/v1/research/papers` - 获取论文库列表
- `POST /api/v1/research/papers` - 添加论文
- `PUT /api/v1/research/papers/{id}` - 更新论文信息
- `DELETE /api/v1/research/papers/{id}` - 删除论文

### 2.13 资产管理模块 `/api/v1/assets`
- `GET /api/v1/assets` - 获取资产列表
- `GET /api/v1/assets/{id}` - 获取资产详情
- `POST /api/v1/assets` - 添加资产
- `PUT /api/v1/assets/{id}` - 更新资产信息
- `DELETE /api/v1/assets/{id}` - 删除资产
- `POST /api/v1/assets/{id}/transfer` - 资产调拨
- `POST /api/v1/assets/{id}/maintenance` - 报修资产
- `GET /api/v1/assets/{id}/history` - 获取资产履历
- `GET /api/v1/assets/categories` - 获取资产分类
- `GET /api/v1/assets/statistics` - 获取资产统计

### 2.14 权限管理模块 `/api/v1/permissions`
- `GET /api/v1/permissions/network` - 获取网络权限信息
- `POST /api/v1/permissions/network/apply` - 申请网络权限
- `PUT /api/v1/permissions/network/{id}` - 更新网络权限
- `GET /api/v1/permissions/devices` - 获取设备注册列表
- `POST /api/v1/permissions/devices` - 注册新设备
- `PUT /api/v1/permissions/devices/{id}` - 更新设备信息
- `DELETE /api/v1/permissions/devices/{id}` - 注销设备
- `GET /api/v1/permissions/audit-logs` - 获取审计日志
- `GET /api/v1/permissions/system-access` - 获取系统访问权限

### 2.15 工作流模块 `/api/v1/workflows`
- `GET /api/v1/workflows/instances` - 获取工作流实例列表
- `GET /api/v1/workflows/instances/{id}` - 获取工作流详情
- `POST /api/v1/workflows/instances` - 创建工作流实例
- `PUT /api/v1/workflows/instances/{id}` - 更新工作流状态
- `POST /api/v1/workflows/instances/{id}/approve` - 审批工作流
- `POST /api/v1/workflows/instances/{id}/reject` - 拒绝工作流
- `GET /api/v1/workflows/templates` - 获取工作流模板
- `GET /api/v1/workflows/my-tasks` - 获取我的待办任务
- `GET /api/v1/workflows/my-applications` - 获取我的申请

### 2.16 统计报表模块 `/api/v1/statistics`
- `GET /api/v1/statistics/overview` - 获取系统概览统计
- `GET /api/v1/statistics/students` - 获取学生统计
- `GET /api/v1/statistics/teachers` - 获取教师统计
- `GET /api/v1/statistics/courses` - 获取课程统计
- `GET /api/v1/statistics/grades` - 获取成绩统计
- `GET /api/v1/statistics/research` - 获取科研统计
- `GET /api/v1/statistics/assets` - 获取资产统计
- `GET /api/v1/statistics/library` - 获取图书馆统计
- `GET /api/v1/statistics/events` - 获取活动统计
- `POST /api/v1/statistics/export` - 导出统计报表

### 2.17 文件管理模块 `/api/v1/files`
- `POST /api/v1/files/upload` - 上传文件
- `GET /api/v1/files/{file_id}` - 下载文件
- `DELETE /api/v1/files/{file_id}` - 删除文件
- `GET /api/v1/files/{file_id}/info` - 获取文件信息
- `POST /api/v1/files/batch-upload` - 批量上传文件
- `GET /api/v1/files/my-files` - 获取我的文件列表

### 2.18 阅读记录模块 `/api/v1/reading`
- `POST /api/v1/reading/record` - 记录阅读行为
- `GET /api/v1/reading/history` - 获取阅读历史
- `POST /api/v1/reading/bookmark` - 添加书签
- `DELETE /api/v1/reading/bookmark/{id}` - 删除书签
- `GET /api/v1/reading/bookmarks` - 获取书签列表
- `POST /api/v1/reading/share` - 分享内容
- `GET /api/v1/reading/analytics` - 获取阅读分析

### 2.19 流式推送模块 `/api/v1/stream`
- `GET /api/v1/stream/events` - 用户事件流（SSE）
- `GET /api/v1/stream/events/guest` - 公开事件流（SSE）
- `GET /api/v1/stream/sync` - 增量事件同步
- `GET /api/v1/stream/status` - 推送系统状态

### 2.20 管理员模块 `/api/v1/admin`
- `GET /api/v1/admin/stats` - 系统统计
- `GET /api/v1/admin/users` - 用户列表
- `POST /api/v1/admin/users/{id}/toggle-admin` - 切换管理员状态
- `GET /api/v1/admin/system-health` - 系统健康检查
- `POST /api/v1/admin/system/backup` - 系统备份
- `POST /api/v1/admin/system/maintenance` - 系统维护模式
- `GET /api/v1/admin/logs` - 系统日志
- `POST /api/v1/admin/notifications/broadcast` - 广播通知

## 3. 标准响应示例

### 3.1 课表查询响应
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "semester": "2024-2025-1",
    "week_number": 1,
    "student_info": {
      "student_id": "202408090101",
      "name": "张三",
      "class_name": "软工2024-1班"
    },
    "courses": [
      {
        "instance_id": "CI2024001",
        "course_code": "MATH001",
        "course_name": "高等数学A",
        "teacher_name": "张教授",
        "credits": 4,
        "schedule": {
          "weekday": 1,
          "start_time": "08:30",
          "end_time": "10:10",
          "location": "C1-101",
          "building_name": "计算机学院1号楼",
          "weeks": "1-16周"
        },
        "course_type": "required"
      }
    ]
  },
  "timestamp": "2024-03-01T12:30:00Z",
  "version": "v1.0"
}
```

### 3.2 校园卡消费响应
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "card_info": {
      "card_number": "202408090101",
      "balance": 287.50,
      "status": "active",
      "last_update": "2024-03-01T12:30:00Z"
    },
    "recent_transactions": [
      {
        "transaction_id": "TXN20240301001",
        "type": "consumption",
        "amount": -12.50,
        "merchant": "学生食堂一楼",
        "location": "D1-1F",
        "time": "2024-03-01T12:30:00Z",
        "balance_after": 287.50
      }
    ],
    "monthly_stats": {
      "month": "2024-03",
      "total_consumption": 456.80,
      "avg_daily": 15.23,
      "most_frequent_location": "学生食堂一楼"
    }
  },
  "timestamp": "2024-03-01T12:30:00Z",
  "version": "v1.0"
}
```

## 4. 权限控制矩阵

```json
{
  "student": {
    "read": ["own_data", "own_schedule", "own_grades", "own_borrow_records", "public_announcements", "course_info"],
    "write": ["own_profile", "course_evaluation", "event_registration"],
    "share": ["schedule", "contact_info"]
  },
  "teacher": {
    "read": ["own_courses", "student_grades", "course_schedules", "teaching_announcements"],
    "write": ["student_grades", "course_content", "announcements"],
    "share": ["course_materials", "grades"]
  },
  "department_head": {
    "read": ["department_stats", "all_courses", "teacher_info", "student_info"],
    "write": ["course_approval", "teacher_assignment", "department_announcements"],
    "share": ["department_reports"]
  },
  "admin": {
    "read": ["*"],
    "write": ["user_management", "system_config", "all_announcements"],
    "share": ["system_reports"]
  }
}
```

## 5. 流式推送事件类型

```json
{
  "event_types": {
    "announcement": "校园公告",
    "grade_update": "成绩更新",
    "course_change": "课程变更",
    "exam_reminder": "考试提醒",
    "library_reminder": "图书到期提醒",
    "transaction": "消费流水",
    "system_message": "系统消息"
  }
}
``` 