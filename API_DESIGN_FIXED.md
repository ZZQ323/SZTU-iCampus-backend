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
- `GET /api/v1/library/my-reservations` - 获取我的座位预约

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

## 6. 详细数据格式规范

### 6.1 成绩查询响应 `GET /api/v1/grades`
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "semester_info": {
      "current_semester": "2024-2025-1",
      "academic_year": "2024-2025"
    },
    "student_id": "202100043213",
    "grades": [
      {
        "course_id": "MATH001",
        "course_name": "高等数学A",
        "course_code": "MATH001",
        "credits": 4.0,
        "teacher": "张教授",
        "regular_score": 85.0,
        "midterm_score": 88.0,
        "final_score": 92.0,
        "lab_score": 0.0,
        "homework_score": 0.0,
        "total_score": 89.2,
        "grade_level": "A",
        "gpa_points": 4.0,
        "course_type": "required",
        "semester": "2024-2025-1",
        "academic_year": "2024-2025",
        "is_passed": true,
        "teacher_comment": null
      }
    ],
    "summary": {
      "total_courses": 8,
      "passed_courses": 8,
      "total_credits": 24.5,
      "avg_score": 87.3,
      "gpa": 3.67,
      "pass_rate": 100.0
    }
  },
  "timestamp": "2024-03-01T12:30:00Z",
  "version": "v1.0"
}
```

### 6.2 成绩统计响应 `GET /api/v1/grades/statistics`
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "student_id": "202100043213",
    "overall": {
      "total_semesters": 3,
      "total_courses": 24,
      "total_credits": 72.0,
      "overall_gpa": 3.8,
      "overall_avg_score": 86.5
    },
    "semester_trends": [
      {
        "semester": "2024-2025-1",
        "academic_year": "2024-2025",
        "course_count": 8,
        "total_credits": 24.0,
        "avg_score": 87.3,
        "gpa": 3.67,
        "pass_rate": 100.0
      }
    ],
    "course_type_analysis": {
      "required": {
        "count": 15,
        "total_credits": 45.0,
        "avg_score": 86.8,
        "gpa": 3.7
      },
      "elective": {
        "count": 6,
        "total_credits": 18.0,
        "avg_score": 89.2,
        "gpa": 4.0
      }
    },
    "performance_analysis": {
      "excellent_count": 18,
      "good_count": 5,
      "average_count": 1,
      "poor_count": 0
    }
  },
  "timestamp": "2024-03-01T12:30:00Z",
  "version": "v1.0"
}
```

### 6.3 公告列表响应 `GET /api/v1/announcements`
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "announcements": [
      {
        "announcement_id": "ANN2025001",
        "title": "关于2024年寒假放假安排的通知",
        "content": "各位同学：根据学校校历安排...",
        "summary": "2024年寒假放假安排通知",
        "publisher_id": "P2025063441",
        "publisher_name": "何平",
        "department": "教务处",
        "category": "education",
        "priority": "high",
        "is_urgent": true,
        "is_pinned": true,
        "publish_time": "2025-06-03T22:59:55.149634",
        "view_count": 476,
        "like_count": 0,
        "comment_count": 0
      }
    ],
    "total": 8,
    "page": 1,
    "size": 10,
    "pages": 1
  },
  "timestamp": "2024-03-01T12:30:00Z",
  "version": "v1.0"
}
```

### 6.4 公告详情响应 `GET /api/v1/announcements/{id}`
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "announcement_id": "ANN2025001",
    "title": "关于2024年寒假放假安排的通知",
    "content": "各位同学：根据学校校历安排...",
    "summary": "2024年寒假放假安排通知",
    "publisher_id": "P2025063441",
    "publisher_name": "何平",
    "department": "教务处",
    "category": "education",
    "priority": "high",
    "is_urgent": true,
    "is_pinned": true,
    "publish_time": "2025-06-03T22:59:55.149634",
    "view_count": 476,
    "like_count": 0,
    "comment_count": 0,
    "is_read": false,
    "is_bookmarked": false
  },
  "timestamp": "2024-03-01T12:30:00Z",
  "version": "v1.0"
}
```

### 6.5 用户登录响应 `POST /api/v1/auth/login`
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "user_info": {
      "person_id": "P2025043213",
      "name": "宋文",
      "person_type": "student",
      "student_id": "202100043213",
      "employee_id": null,
      "college_name": "计算机与软件学院",
      "major_name": "软件工程",
      "class_name": "软工2021-1班",
      "department_name": null
    }
  },
  "timestamp": "2024-03-01T12:30:00Z",
  "version": "v1.0"
}
```

### 6.6 图书搜索响应 `GET /api/v1/library/books/search`
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "books": [
      {
        "book_id": "B001",
        "id": "B001",
        "isbn": "978-7-111-54742-6",
        "title": "深入理解计算机系统",
        "subtitle": "原书第3版",
        "author": "Randal E. Bryant, David R. O'Hallaron",
        "publisher": "机械工业出版社",
        "publish_date": "2016-11-01",
        "category": "计算机科学",
        "call_number": "TP3/B877",
        "total_copies": 5,
        "available_copies": 2,
        "borrowed_copies": 3,
        "location": "计算机类图书区",
        "floor": "三楼",
        "description": "系统性地介绍了计算机系统的各个方面",
        "borrow_count": 156,
        "borrowCount": 156,
        "rating": 4.5,
        "status": "available",
        "cover": "https://via.placeholder.com/120x160?text=深入理解\n计算机系统",
        "is_new": false,
        "arrivalDate": null
      }
    ],
    "pagination": {
      "page": 1,
      "size": 20,
      "total": 1,
      "pages": 1
    },
    "search_info": {
      "keyword": "计算机",
      "category": "popular",
      "author": null
    }
  },
  "timestamp": "2024-06-24T12:30:00Z",
  "version": "v1.0"
}
```

### 6.7 借阅记录响应 `GET /api/v1/library/borrows`
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "borrow_records": [
      {
        "record_id": "BR001",
        "book_id": "B001",
        "id": "BR001",
        "title": "深入理解计算机系统",
        "book_title": "深入理解计算机系统",
        "isbn": "978-7-111-54742-6",
        "author": "Randal E. Bryant",
        "borrow_date": "2024-05-30",
        "borrowDate": "2024-05-30",
        "due_date": "2024-06-29T23:59:59",
        "dueDate": "2024-06-29",
        "return_date": null,
        "status": "borrowed",
        "renewal_count": 1,
        "renewCount": 1,
        "max_renewals": 2,
        "maxRenew": 2,
        "fine_amount": 0.0,
        "location": "计算机类图书区",
        "daysLeft": 5,
        "isOverdue": false,
        "cover": "https://via.placeholder.com/120x160?text=深入理解\n计算机系统"
      }
    ],
    "pagination": {
      "page": 1,
      "size": 20,
      "total": 1,
      "pages": 1
    },
    "statistics": {
      "total_borrowed": 2,
      "total_returned": 1,
      "total_overdue": 1
    }
  },
  "timestamp": "2024-06-24T12:30:00Z",
  "version": "v1.0"
}
```

### 6.8 图书馆座位信息响应 `GET /api/v1/library/seats`
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "seats": [
      {
        "seat_id": "L1-A-001",
        "floor": 1,
        "area": "A区",
        "seat_number": "001",
        "seat_type": "普通座位",
        "is_available": true,
        "has_power": true,
        "has_network": true,
        "equipment": ["台灯", "电源插座"],
        "current_user": null,
        "reserved_until": null
      }
    ],
    "statistics": {
      "total_seats": 300,
      "available_seats": 66,
      "occupied_seats": 234,
      "occupancy_rate": 78.0
    },
    "areas": [
      {
        "id": "floor1_a",
        "floor": 1,
        "area": "A区",
        "name": "一楼A区",
        "description": "安静学习区域",
        "total": 50,
        "available": 12,
        "availableSeats": 12,
        "occupancyRate": 76.0
      }
    ]
  },
  "timestamp": "2024-06-24T12:30:00Z",
  "version": "v1.0"
}
```

### 6.9 座位预约响应 `POST /api/v1/library/seats/reserve`
```json
{
  "code": 0,
  "message": "座位预约成功",
  "data": {
    "reservation_id": "RSV20240624130000",
    "seat_id": "L1-A-001",
    "user_id": "P2025043213",
    "start_time": "2024-06-24T13:00:00Z",
    "end_time": "2024-06-24T17:00:00Z",
    "duration": 4,
    "status": "confirmed"
  },
  "timestamp": "2024-06-24T12:30:00Z",
  "version": "v1.0"
}
```

### 6.10 我的座位预约响应 `GET /api/v1/library/my-reservations`
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "reservations": [
      {
        "reservation_id": "RSV20240624130000",
        "seat_id": "L1-A-001",
        "seat_info": {
          "floor": 1,
          "area": "A区",
          "seat_number": "001"
        },
        "start_time": "2024-06-24T13:00:00",
        "end_time": "2024-06-24T17:00:00",
        "duration": 4,
        "status": "active",
        "created_at": "2024-06-24T12:55:00"
      }
    ]
  },
  "timestamp": "2024-06-24T12:30:00Z",
  "version": "v1.0"
}
```

### 6.11 借阅图书响应 `POST /api/v1/library/borrows/{book_id}`
```json
{
  "code": 0,
  "message": "借阅成功",
  "data": {
    "record_id": "BR20240624130000",
    "user_id": "P2025043213",
    "book_id": "B001",
    "borrow_date": "2024-06-24T13:00:00Z",
    "due_date": "2024-07-24T23:59:59Z",
    "status": "borrowed"
  },
  "timestamp": "2024-06-24T12:30:00Z",
  "version": "v1.0"
}
```

### 6.12 续借图书响应 `PUT /api/v1/library/borrows/{record_id}/renew`
```json
{
  "code": 0,
  "message": "续借成功",
  "data": {
    "record_id": "BR001",
    "old_due_date": "2024-07-01T23:59:59",
    "new_due_date": "2024-07-31T23:59:59Z",
    "renewal_count": 2,
    "renew_date": "2024-06-24T13:00:00Z"
  },
  "timestamp": "2024-06-24T12:30:00Z",
  "version": "v1.0"
}
```

## 7. 开发规范

### 7.1 数据格式一致性原则
1. **严格遵循统一响应格式**：所有接口必须返回 `{code, message, data, timestamp, version}` 结构
2. **data字段内容标准化**：按照本文档第6章的详细格式规范实现
3. **字段命名规范**：使用snake_case命名，保持前后端一致
4. **必需字段与可选字段明确标识**
5. **冗余字段处理**：为兼容前端不同命名习惯，可保留必要的冗余字段（如borrowCount和borrow_count）

### 7.2 开发流程规范
1. **设计阶段**：先定义数据格式，写入API文档
2. **开发阶段**：前后端严格按照文档实现
3. **测试阶段**：使用真实数据测试
4. **上线前**：必须进行前后端联调，确保数据格式一致

### 7.3 防错机制
1. **类型检查**：前端使用TypeScript定义接口类型
2. **Schema验证**：后端返回数据前进行格式验证
3. **单元测试**：为每个API编写响应格式测试用例
4. **集成测试**：前后端联调时重点测试数据格式匹配

### 7.4 常见问题解决方案

#### 问题1：前端期望字段A，后端返回字段B
**解决方案**：
- 立即检查API文档，确认标准格式
- 修改后端代码，使用文档规定的字段名
- 前端代码也要对应调整

#### 问题2：嵌套层级不一致（如 response.data vs response.data.data）
**解决方案**：
- 统一使用 `response.data.xxx` 格式访问业务数据
- 检查胶水层是否正确包装了data字段
- 确保所有API返回的data字段在同一层级

#### 问题3：模拟数据与真实数据格式不一致
**解决方案**：
- 废弃所有模拟数据，全部使用真实API
- 真实API返回空数据时，返回符合文档格式的空结构
- 禁止在生产环境使用模拟数据

#### 问题4：图书馆数据缺失或格式不匹配
**解决方案**：
- 按照6.6-6.12节的规范实现图书馆模块API
- 确保返回的数据包含前端需要的所有字段
- 特别关注日期格式、状态字段和嵌套对象结构

### 7.5 学期格式标准
- **统一格式**：`YYYY-YYYY-S` （如：`2024-2025-1`）
- **学年表示**：开始年份-结束年份
- **学期编号**：1表示第一学期，2表示第二学期
- **示例**：
  - `2024-2025-1`：2024-2025学年第一学期
  - `2023-2024-2`：2023-2024学年第二学期

### 7.6 图书馆模块特殊说明
1. **图书状态**：`available`（可借）、`borrowed`（已借）、`reserved`（已预约）
2. **借阅状态**：`borrowed`（借阅中）、`returned`（已归还）、`overdue`（逾期）
3. **日期字段**：同时提供ISO格式和简化格式以兼容不同显示需求
4. **座位数据**：必须包含楼层区域信息和实时统计数据
5. **评分系统**：图书评分使用1-5分制，支持小数点

## 8. 图书馆模块详细数据格式规范

### 8.1 图书搜索响应 `GET /api/v1/library/books/search`
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "books": [
      {
        "book_id": "B001",
        "id": "B001",
        "isbn": "978-7-111-54742-6",
        "title": "深入理解计算机系统",
        "subtitle": "原书第3版",
        "author": "Randal E. Bryant, David R. O'Hallaron",
        "publisher": "机械工业出版社",
        "publish_date": "2016-11-01",
        "category": "计算机科学",
        "call_number": "TP3/B877",
        "total_copies": 5,
        "available_copies": 2,
        "borrowed_copies": 3,
        "location": "计算机类图书区",
        "floor": "三楼",
        "description": "系统性地介绍了计算机系统的各个方面",
        "borrow_count": 156,
        "borrowCount": 156,
        "rating": 4.5,
        "status": "available",
        "cover": "https://via.placeholder.com/120x160?text=深入理解\n计算机系统",
        "is_new": false,
        "arrivalDate": null
      }
    ],
    "pagination": {
      "page": 1,
      "size": 20,
      "total": 1,
      "pages": 1
    },
    "search_info": {
      "keyword": "计算机",
      "category": "popular",
      "author": null
    }
  },
  "timestamp": "2024-06-24T12:30:00Z",
  "version": "v1.0"
}
```

### 8.2 借阅记录响应 `GET /api/v1/library/borrows`
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "borrow_records": [
      {
        "record_id": "BR001",
        "book_id": "B001",
        "id": "BR001",
        "title": "深入理解计算机系统",
        "book_title": "深入理解计算机系统",
        "isbn": "978-7-111-54742-6",
        "author": "Randal E. Bryant",
        "borrow_date": "2024-05-30",
        "borrowDate": "2024-05-30",
        "due_date": "2024-06-29T23:59:59",
        "dueDate": "2024-06-29",
        "return_date": null,
        "status": "borrowed",
        "renewal_count": 1,
        "renewCount": 1,
        "max_renewals": 2,
        "maxRenew": 2,
        "fine_amount": 0.0,
        "location": "计算机类图书区",
        "daysLeft": 5,
        "isOverdue": false,
        "cover": "https://via.placeholder.com/120x160?text=深入理解\n计算机系统"
      }
    ],
    "pagination": {
      "page": 1,
      "size": 20,
      "total": 1,
      "pages": 1
    },
    "statistics": {
      "total_borrowed": 2,
      "total_returned": 1,
      "total_overdue": 1
    }
  },
  "timestamp": "2024-06-24T12:30:00Z",
  "version": "v1.0"
}
```

### 8.3 图书馆座位信息响应 `GET /api/v1/library/seats`
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "seats": [
      {
        "seat_id": "L1-A-001",
        "floor": 1,
        "area": "A区",
        "seat_number": "001",
        "seat_type": "普通座位",
        "is_available": true,
        "has_power": true,
        "has_network": true,
        "equipment": ["台灯", "电源插座"],
        "current_user": null,
        "reserved_until": null
      }
    ],
    "statistics": {
      "total_seats": 300,
      "available_seats": 66,
      "occupied_seats": 234,
      "occupancy_rate": 78.0
    },
    "areas": [
      {
        "id": "floor1_a",
        "floor": 1,
        "area": "A区",
        "name": "一楼A区",
        "description": "安静学习区域",
        "total": 50,
        "available": 12,
        "availableSeats": 12,
        "occupancyRate": 76.0
      }
    ]
  },
  "timestamp": "2024-06-24T12:30:00Z",
  "version": "v1.0"
}
```

### 8.4 座位预约响应 `POST /api/v1/library/seats/reserve`
```json
{
  "code": 0,
  "message": "座位预约成功",
  "data": {
    "reservation_id": "RSV20240624130000",
    "seat_id": "L1-A-001",
    "user_id": "P2025043213",
    "start_time": "2024-06-24T13:00:00Z",
    "end_time": "2024-06-24T17:00:00Z",
    "duration": 4,
    "status": "confirmed"
  },
  "timestamp": "2024-06-24T12:30:00Z",
  "version": "v1.0"
}
```

### 8.5 我的座位预约响应 `GET /api/v1/library/my-reservations`
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "reservations": [
      {
        "reservation_id": "RSV20240624130000",
        "seat_id": "L1-A-001",
        "seat_info": {
          "floor": 1,
          "area": "A区",
          "seat_number": "001"
        },
        "start_time": "2024-06-24T13:00:00",
        "end_time": "2024-06-24T17:00:00",
        "duration": 4,
        "status": "active",
        "created_at": "2024-06-24T12:55:00"
      }
    ]
  },
  "timestamp": "2024-06-24T12:30:00Z",
  "version": "v1.0"
}
```

### 8.6 借阅图书响应 `POST /api/v1/library/borrows/{book_id}`
```json
{
  "code": 0,
  "message": "借阅成功",
  "data": {
    "record_id": "BR20240624130000",
    "user_id": "P2025043213",
    "book_id": "B001",
    "borrow_date": "2024-06-24T13:00:00Z",
    "due_date": "2024-07-24T23:59:59Z",
    "status": "borrowed"
  },
  "timestamp": "2024-06-24T12:30:00Z",
  "version": "v1.0"
}
```

### 8.7 续借图书响应 `PUT /api/v1/library/borrows/{record_id}/renew`
```json
{
  "code": 0,
  "message": "续借成功",
  "data": {
    "record_id": "BR001",
    "old_due_date": "2024-07-01T23:59:59",
    "new_due_date": "2024-07-31T23:59:59Z",
    "renewal_count": 2,
    "renew_date": "2024-06-24T13:00:00Z"
  },
  "timestamp": "2024-06-24T12:30:00Z",
  "version": "v1.0"
}
```

## 9. 图书馆模块特殊说明

### 9.1 数据格式一致性原则
1. **冗余字段兼容性**：为确保前后端兼容，图书馆模块采用双字段策略
   - `borrow_count` 和 `borrowCount`（借阅次数）
   - `dueDate` 和 `due_date`（到期日期）
   - `renewCount` 和 `renewal_count`（续借次数）
2. **日期格式标准**：
   - ISO格式用于API传输：`2024-06-24T13:00:00Z`
   - 简化格式用于显示：`2024-06-24`
3. **状态字段标准化**：
   - 图书状态：`available`、`borrowed`、`reserved`
   - 借阅状态：`borrowed`、`returned`、`overdue`
   - 座位状态：`available`、`occupied`、`reserved`

### 9.2 前端显示字段映射
```javascript
// 前端期望的字段映射
const bookDisplayFields = {
  id: item.id || item.book_id,
  title: item.title || item.book_title,
  borrowCount: item.borrowCount || item.borrow_count,
  daysLeft: item.daysLeft,
  isOverdue: item.isOverdue,
  renewCount: item.renewCount || item.renewal_count,
  maxRenew: item.maxRenew || item.max_renewals
};
```

### 9.3 API一致性检查清单
✅ **路径一致性**：
- API文档：`/api/v1/library/books/search`
- 后端实现：`@router.get("/books/search")` + `/library` 前缀
- 前端调用：`BASE_URL + '/library/books/search'`

✅ **响应格式一致性**：
- 统一响应结构：`{code, message, data, timestamp, version}`
- data字段包含业务数据
- 分页信息包含在pagination对象中

✅ **字段命名一致性**：
- 主要字段使用snake_case
- 兼容字段使用camelCase
- 前端可选择使用任一格式

### 9.4 错误处理标准
```json
{
  "code": 500,
  "message": "图书搜索失败: 服务器内部错误",
  "data": null,
  "timestamp": "2024-06-24T12:30:00Z",
  "version": "v1.0"
}
```

常见错误码：
- `400`：参数错误
- `401`：未授权
- `404`：资源不存在
- `422`：参数验证失败
- `500`：服务器内部错误 