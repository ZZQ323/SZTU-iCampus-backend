# API数据模板设计

## 1. 统一响应格式（不变）

```json
{
  "status": 0,
  "msg": "success",
  "data": {},
  "timestamp": 1640995200000,
  "version": "v1.0"
}
```

## 2. 用户认证响应
**API**：
- `POST {backend_URL}/app/api/v1/endpoints/login` - 微信登录
- `POST {backend_URL}/app/api/v1/endpoints/bind` - 绑定微信号
- `POST {backend_URL}/app/api/v1/endpoints/unbind` - 解绑微信号
- `GET {backend_URL}/app/api/v1/endpoints/status` - 查询绑定状态

集成微信登录的小程序登录认证
```json
{
  "status": 0,
  "msg": "登录成功",
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer",
    "expires_in": 7200,
    "user": {
      "person_id": "P2024001",
      "name": "张三",
      "person_type": "student",
      "college_name": "计算机学院",
      "major_name": "软件工程",
      "wechat_bound": true,          // 是否已绑定微信账号
      "permissions": {
        "read": ["own_data", "public_announcements"],
        "write": ["own_profile"],
        "share": ["schedule"]
      }
    }
  }
}
```


## 3. 课表查询响应
API:`{backend_URL}/app/api/v1/endpoints/schedule.py`
```json
{
  "status": 0,
  "msg": "success",
  "data": {
    "semester": "2024-2025-1",
    "week_number": 1,
    "student_info": {
      "student_id": "2024001",
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
        "course_type": "required",
        "exam_info": {
          "exam_date": "2024-01-15",
          "exam_time": "14:30-16:30",
          "exam_location": "C1-102"
        }
      }
    ]
  }
}
```

## 4. 成绩查询响应
API:`{backend_URL}/app/api/v1/endpoints/exams.py`
```json
{
  "status": 0,
  "msg": "success",
  "data": {
    "student_info": {
      "student_id": "2024001",
      "name": "张三",
      "major_name": "软件工程",
      "current_semester": "2024-2025-1"
    },
    "semester_stats": {
      "semester": "2024-2025-1",
      "total_credits": 24,
      "earned_credits": 24,
      "gpa": 3.8,
      "average_score": 87.5,
      "ranking": {
        "class_rank": 5,
        "class_total": 58,
        "major_rank": 15,
        "major_total": 230
      }
    },
    "courses": [
      {
        "course_code": "MATH001",
        "course_name": "高等数学A",
        "teacher_name": "张教授",
        "credits": 4,
        "course_type": "required",
        "scores": {
          "attendance": 95,
          "homework": 88,
          "midterm": 92,
          "final": 89,
          "total": 90
        },
        "grade_point": 4.0,
        "grade_level": "A",
        "exam_times": 1
      }
    ]
  }
}
```

## 5. 图书馆服务响应
API:`{backend_URL}/app/api/v1/endpoints/library.py`
```json
{
  "status": 0,
  "msg": "success",
  "data": {
    "user_info": {
      "student_id": "2024001",
      "name": "张三",
      "max_borrow": 10,
      "current_borrow": 2,
      "overdue_count": 0,
      "total_fine": 0.00
    },
    "borrowed_books": [
      {
        "record_id": "BR2024001",
        "book_id": "B001",
        "title": "算法导论",
        "authors": ["Thomas H. Cormen"],
        "borrow_date": "2024-03-01",
        "due_date": "2024-06-01",
        "days_left": 45,
        "renew_times": 0,
        "can_renew": true
      }
    ]
  }
}
```

## 6. 校园卡消费响应
API:`{backend_URL}/app/api/v1/endpoints/simple.py`
```json
{
  "status": 0,
  "msg": "success",
  "data": {
    "card_info": {
      "card_number": "2024001",
      "balance": 287.50,
      "status": "active"
    },
    "recent_transactions": [
      {
        "transaction_id": "T2024001",
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
  }
}
```

## 7. 权限控制矩阵
API:`{backend_URL}/app/api/v1/endpoints/admin.py `
```json
{
  "student": {
    "read": ["own_schedule", "own_grades", "own_borrow_records", "public_announcements", "course_info"],
    "write": ["own_profile", "course_evaluation"],
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

## 其他说明

### 微信号绑定机制

**绑定策略**：
- **可选绑定**: 微信号不是必需字段，用户可以选择绑定或不绑定
- **登录后绑定**: 支持用户首次使用时通过学号/工号登录，然后选择绑定微信
- **自动绑定**: 当用户通过微信小程序登录时，系统自动关联微信OpenID
- **解绑重绑**: 支持用户解绑当前微信号并重新绑定新的微信号

**绑定流程**：
1. 用户通过微信小程序授权获取OpenID
2. 系统检查该OpenID是否已绑定账号
3. 如已绑定，直接登录；如未绑定，提示用户输入学号/工号进行绑定
4. 绑定成功后，用户可通过微信一键登录

**数据结构**：
```json
{
  "person_id": "P2024001",
  "wechat_openid": "wx_123456_202408090101",  // 微信OpenID，可为null
  "wechat_bound_date": "2024-09-01T10:00:00Z", // 绑定时间，可为null
  "wechat_nickname": "小明同学",               // 微信昵称（可选）
  "login_method": "wechat",                   // 登录方式：wechat/password/both
}
```
