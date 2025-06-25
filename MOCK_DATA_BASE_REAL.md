# SZTU-iCampus 数据模型与API设计

## 测试账号信息

### 主要测试账号
- **202100008036** - 主要测试学生（有完整选课、成绩数据）
- **2025123456** - 测试学生1  
- **2025123457** - 测试学生2
- **2025123458** - 测试学生3

### 数据概览
- 总用户数：63,460+ 人
- 课程数：3,120 门
- 选课记录：406,807 条
- 成绩记录：406,807 条  
- 公告：11+ 条
- 活动：10+ 条
- 考试：13+ 条

## 基础实体表

### persons 表
数据量: 63,460 条记录

```json
{
  "person_id": "VARCHAR(20)",  // 人员ID, 必填
  "person_type": "VARCHAR(17)",  // 必填
  "student_id": "VARCHAR(12)",  // 学生ID
  "employee_id": "VARCHAR(10)",  // 员工ID
  "name": "VARCHAR(50)",  // 姓名, 必填
  "name_en": "VARCHAR(100)",
  "gender": "VARCHAR(6)",  // 性别, 必填
  "birth_date": "DATE",
  "id_card": "VARCHAR(50)",
  "nationality": "VARCHAR(20)",
  "ethnicity": "VARCHAR(20)",
  "phone": "VARCHAR(20)",  // 电话
  "email": "VARCHAR(100)",  // 邮箱
  "wechat_openid": "VARCHAR(50)",
  "qq_number": "VARCHAR(20)",
  "home_address": "TEXT",
  "current_address": "TEXT",
  "postal_code": "VARCHAR(10)",
  "admission_date": "DATE",
  "employment_date": "DATE",
  "graduation_date": "DATE",
  "academic_status": "VARCHAR(12)",
  "employment_status": "VARCHAR(9)",
  "permissions": "JSON",
  "college_id": "VARCHAR(10)",
  "major_id": "VARCHAR(10)",
  "department_id": "VARCHAR(10)",
  "class_id": "VARCHAR(20)",
  "academic_title": "VARCHAR(20)",
  "research_field": "VARCHAR(100)",
  "education_background": "VARCHAR(20)",
  "graduate_school": "VARCHAR(100)",
  "emergency_contact_name": "VARCHAR(50)",
  "emergency_contact_phone": "VARCHAR(20)",
  "emergency_contact_relation": "VARCHAR(20)",
  "bank_account": "VARCHAR(50)",
  "bank_name": "VARCHAR(50)",
  "avatar_url": "VARCHAR(200)",
  "id_photo_url": "VARCHAR(200)",
  "id": "INTEGER",  // 自增ID, 主键, 必填
  "created_at": "DATETIME",  // 创建时间, 必填, 默认值:CURRENT_TIMESTAMP
  "updated_at": "DATETIME",  // 更新时间, 必填, 默认值:CURRENT_TIMESTAMP
  "is_deleted": "BOOLEAN",  // 删除标记, 必填
  "deleted_at": "DATETIME",  // 删除时间
  "status": "VARCHAR(20)",  // 状态, 必填
  "is_active": "BOOLEAN",  // 激活状态, 必填
  "notes": "TEXT",  // 备注
  "password_hash": "VARCHAR(128)",
  "password_salt": "VARCHAR(32)",
  "password_plain": "VARCHAR(50)",
  "last_login": "DATETIME",
  "login_attempts": "INTEGER",  // 默认值:0
  "account_locked": "BOOLEAN"  // 默认值:0
}
```

**外键关系:**
- class_id → classes.class_id
- department_id → departments.department_id
- major_id → majors.major_id
- college_id → colleges.college_id

**样本数据:**
```json
{
  "person_id": "P2025000001",
  "person_type": "student",
  "student_id": "202100000001",
  "employee_id": null,
  "name": "唐勇",
  "name_en": null,
  "gender": "female",
  "birth_date": "2005-06-24",
  "id_card": null,
  "nationality": "中国",
  "ethnicity": "土家族",
  "phone": "131****9524",
  "email": "202100000001@student.sztu.edu.cn",
  "wechat_openid": "wx_631307_202100000001",
  "qq_number": null,
  "home_address": "宁夏回族自治区大冶县高坪余路a座 841997",
  "current_address": null,
  "postal_code": null,
  "admission_date": "2021-09-01",
  "employment_date": null,
  "graduation_date": "2025-06-30",
  "academic_status": "active",
  "employment_status": "active",
  "permissions": "\"{\\\"read\\\": [\\\"public_announcements\\\", \\\"own_grades\\\", \\\"campus_news\\\", \\\"course_info\\\", \\\"own_sched...",
  "college_id": "C001",
  "major_id": "080901",
  "department_id": null,
  "class_id": "CL2021001",
  "academic_title": null,
  "research_field": null,
  "education_background": null,
  "graduate_school": null,
  "emergency_contact_name": null,
  "emergency_contact_phone": null,
  "emergency_contact_relation": null,
  "bank_account": null,
  "bank_name": null,
  "avatar_url": null,
  "id_photo_url": null,
  "id": 1,
  "created_at": "2025-06-20 15:49:00",
  "updated_at": "2025-06-20 15:49:00",
  "is_deleted": 0,
  "deleted_at": null,
  "status": "active",
  "is_active": 1,
  "notes": null,
  "password_hash": "****",
  "password_salt": "****",
  "password_plain": "****",
  "last_login": "2025-06-23T13:44:03.664982",
  "login_attempts": 0,
  "account_locked": 0
}
,
{
  "person_id": "P2025000002",
  "person_type": "student",
  "student_id": "202100000002",
  "employee_id": null,
  "name": "郭文",
  "name_en": null,
  "gender": "male",
  "birth_date": "2001-07-14",
  "id_card": null,
  "nationality": "中国",
  "ethnicity": "汉族",
  "phone": "187****9075",
  "email": "202100000002@student.sztu.edu.cn",
  "wechat_openid": "wx_947937_202100000002",
  "qq_number": null,
  "home_address": "山东省琴县沈北新黎路G座 858148",
  "current_address": null,
  "postal_code": null,
  "admission_date": "2021-09-01",
  "employment_date": null,
  "graduation_date": "2025-06-30",
  "academic_status": "active",
  "employment_status": "active",
  "permissions": "\"{\\\"read\\\": [\\\"own_grades\\\", \\\"exam_schedule\\\", \\\"library_catalog\\\", \\\"own_schedule\\\"], \\\"write\\\": [...",
  "college_id": "C001",
  "major_id": "080901",
  "department_id": null,
  "class_id": "CL2021001",
  "academic_title": null,
  "research_field": null,
  "education_background": null,
  "graduate_school": null,
  "emergency_contact_name": null,
  "emergency_contact_phone": null,
  "emergency_contact_relation": null,
  "bank_account": null,
  "bank_name": null,
  "avatar_url": null,
  "id_photo_url": null,
  "id": 2,
  "created_at": "2025-06-20 15:49:00",
  "updated_at": "2025-06-20 15:49:00",
  "is_deleted": 0,
  "deleted_at": null,
  "status": "active",
  "is_active": 1,
  "notes": null,
  "password_hash": "****",
  "password_salt": "****",
  "password_plain": "****",
  "last_login": "2025-06-21T09:17:20.008944",
  "login_attempts": 0,
  "account_locked": 0
}
```


### colleges 表
数据量: 13 条记录

```json
{
  "college_id": "VARCHAR(10)",  // 必填
  "college_name": "VARCHAR(50)",  // 必填
  "college_code": "VARCHAR(10)",  // 必填
  "phone": "VARCHAR(20)",  // 电话
  "email": "VARCHAR(100)",  // 邮箱
  "website": "VARCHAR(200)",
  "office_location": "VARCHAR(100)",
  "main_building": "VARCHAR(20)",
  "dean_id": "VARCHAR(10)",
  "vice_dean_id": "VARCHAR(10)",
  "secretary_id": "VARCHAR(10)",
  "total_teachers": "INTEGER",
  "total_students": "INTEGER",
  "total_majors": "INTEGER",
  "description": "TEXT",
  "mission": "TEXT",
  "id": "INTEGER",  // 自增ID, 主键, 必填
  "created_at": "DATETIME",  // 创建时间, 必填, 默认值:CURRENT_TIMESTAMP
  "updated_at": "DATETIME",  // 更新时间, 必填, 默认值:CURRENT_TIMESTAMP
  "is_deleted": "BOOLEAN",  // 删除标记, 必填
  "deleted_at": "DATETIME",  // 删除时间
  "status": "VARCHAR(20)",  // 状态, 必填
  "is_active": "BOOLEAN",  // 激活状态, 必填
  "notes": "TEXT"  // 备注
}
```

**外键关系:**
- secretary_id → persons.employee_id
- vice_dean_id → persons.employee_id
- dean_id → persons.employee_id

**样本数据:**
```json
{
  "college_id": "C001",
  "college_name": "计算机学院",
  "college_code": "CS",
  "phone": "138****6452",
  "email": "cs@sztu.edu.cn",
  "website": null,
  "office_location": null,
  "main_building": "C1",
  "dean_id": null,
  "vice_dean_id": null,
  "secretary_id": null,
  "total_teachers": 0,
  "total_students": 0,
  "total_majors": 0,
  "description": "计算机学院致力于培养高素质的专业人才",
  "mission": null,
  "id": 1,
  "created_at": "2025-06-20 15:48:55",
  "updated_at": "2025-06-20 15:48:55",
  "is_deleted": 0,
  "deleted_at": null,
  "status": "active",
  "is_active": 1,
  "notes": null
}
,
{
  "college_id": "C002",
  "college_name": "数学与统计学院",
  "college_code": "MATH",
  "phone": "184****3853",
  "email": "math@sztu.edu.cn",
  "website": null,
  "office_location": null,
  "main_building": "C2",
  "dean_id": null,
  "vice_dean_id": null,
  "secretary_id": null,
  "total_teachers": 0,
  "total_students": 0,
  "total_majors": 0,
  "description": "数学与统计学院致力于培养高素质的专业人才",
  "mission": null,
  "id": 2,
  "created_at": "2025-06-20 15:48:55",
  "updated_at": "2025-06-20 15:48:55",
  "is_deleted": 0,
  "deleted_at": null,
  "status": "active",
  "is_active": 1,
  "notes": null
}
```


### majors 表
数据量: 78 条记录

```json
{
  "major_id": "VARCHAR(10)",  // 必填
  "major_name": "VARCHAR(50)",  // 必填
  "major_code": "VARCHAR(20)",  // 必填
  "college_id": "VARCHAR(10)",  // 必填
  "duration_years": "INTEGER",
  "degree_type": "VARCHAR(20)",
  "director_id": "VARCHAR(10)",
  "total_teachers": "INTEGER",
  "total_students": "INTEGER",
  "total_classes": "INTEGER",
  "total_courses": "INTEGER",
  "enrollment_quota": "INTEGER",
  "tuition_fee": "NUMERIC(10, 2)",
  "description": "TEXT",
  "career_prospects": "TEXT",
  "core_courses": "JSON",
  "accreditation": "VARCHAR(100)",
  "ranking": "VARCHAR(50)",
  "id": "INTEGER",  // 自增ID, 主键, 必填
  "created_at": "DATETIME",  // 创建时间, 必填, 默认值:CURRENT_TIMESTAMP
  "updated_at": "DATETIME",  // 更新时间, 必填, 默认值:CURRENT_TIMESTAMP
  "is_deleted": "BOOLEAN",  // 删除标记, 必填
  "deleted_at": "DATETIME",  // 删除时间
  "status": "VARCHAR(20)",  // 状态, 必填
  "is_active": "BOOLEAN",  // 激活状态, 必填
  "notes": "TEXT"  // 备注
}
```

**外键关系:**
- director_id → persons.employee_id
- college_id → colleges.college_id

**样本数据:**
```json
{
  "major_id": "080901",
  "major_name": "计算机科学与技术",
  "major_code": "080901",
  "college_id": "C001",
  "duration_years": 4,
  "degree_type": "本科",
  "director_id": null,
  "total_teachers": 0,
  "total_students": 0,
  "total_classes": 0,
  "total_courses": 0,
  "enrollment_quota": 160,
  "tuition_fee": 6407,
  "description": "计算机科学与技术专业培养方案",
  "career_prospects": null,
  "core_courses": "[]",
  "accreditation": null,
  "ranking": null,
  "id": 1,
  "created_at": "2025-06-20 15:48:55",
  "updated_at": "2025-06-20 15:48:55",
  "is_deleted": 0,
  "deleted_at": null,
  "status": "active",
  "is_active": 1,
  "notes": null
}
,
{
  "major_id": "080902",
  "major_name": "软件工程",
  "major_code": "080902",
  "college_id": "C001",
  "duration_years": 4,
  "degree_type": "本科",
  "director_id": null,
  "total_teachers": 0,
  "total_students": 0,
  "total_classes": 0,
  "total_courses": 0,
  "enrollment_quota": 130,
  "tuition_fee": 6994,
  "description": "软件工程专业培养方案",
  "career_prospects": null,
  "core_courses": "[]",
  "accreditation": null,
  "ranking": null,
  "id": 2,
  "created_at": "2025-06-20 15:48:55",
  "updated_at": "2025-06-20 15:48:55",
  "is_deleted": 0,
  "deleted_at": null,
  "status": "active",
  "is_active": 1,
  "notes": null
}
```


### departments 表
数据量: 0 条记录

```json
{
  "department_id": "VARCHAR(10)",  // 必填
  "department_name": "VARCHAR(50)",  // 必填
  "department_type": "VARCHAR(20)",  // 必填
  "college_id": "VARCHAR(10)",
  "parent_department_id": "VARCHAR(10)",
  "level": "INTEGER",
  "phone": "VARCHAR(20)",  // 电话
  "email": "VARCHAR(100)",  // 邮箱
  "office_location": "VARCHAR(100)",
  "head_id": "VARCHAR(10)",
  "deputy_head_id": "VARCHAR(10)",
  "total_staff": "INTEGER",
  "description": "TEXT",
  "responsibilities": "JSON",
  "id": "INTEGER",  // 自增ID, 主键, 必填
  "created_at": "DATETIME",  // 创建时间, 必填, 默认值:CURRENT_TIMESTAMP
  "updated_at": "DATETIME",  // 更新时间, 必填, 默认值:CURRENT_TIMESTAMP
  "is_deleted": "BOOLEAN",  // 删除标记, 必填
  "deleted_at": "DATETIME",  // 删除时间
  "status": "VARCHAR(20)",  // 状态, 必填
  "is_active": "BOOLEAN",  // 激活状态, 必填
  "notes": "TEXT"  // 备注
}
```

**外键关系:**
- deputy_head_id → persons.employee_id
- head_id → persons.employee_id
- parent_department_id → departments.department_id
- college_id → colleges.college_id


### classes 表
数据量: 1,248 条记录

```json
{
  "class_id": "VARCHAR(20)",  // 必填
  "class_name": "VARCHAR(50)",  // 必填
  "class_code": "VARCHAR(20)",  // 必填
  "grade": "INTEGER",  // 必填
  "semester_enrolled": "VARCHAR(20)",  // 必填
  "major_id": "VARCHAR(10)",  // 必填
  "college_id": "VARCHAR(10)",  // 必填
  "class_advisor_id": "VARCHAR(10)",
  "counselor_id": "VARCHAR(10)",
  "total_students": "INTEGER",
  "male_count": "INTEGER",
  "female_count": "INTEGER",
  "graduation_date": "DATE",
  "classroom_location": "VARCHAR(50)",
  "class_motto": "TEXT",
  "class_description": "TEXT",
  "id": "INTEGER",  // 自增ID, 主键, 必填
  "created_at": "DATETIME",  // 创建时间, 必填, 默认值:CURRENT_TIMESTAMP
  "updated_at": "DATETIME",  // 更新时间, 必填, 默认值:CURRENT_TIMESTAMP
  "is_deleted": "BOOLEAN",  // 删除标记, 必填
  "deleted_at": "DATETIME",  // 删除时间
  "status": "VARCHAR(20)",  // 状态, 必填
  "is_active": "BOOLEAN",  // 激活状态, 必填
  "notes": "TEXT"  // 备注
}
```

**外键关系:**
- counselor_id → persons.employee_id
- class_advisor_id → persons.employee_id
- college_id → colleges.college_id
- major_id → majors.major_id

**样本数据:**
```json
{
  "class_id": "CL2021001",
  "class_name": "计算机科学与技术2021级1班",
  "class_code": "080901-2021-1",
  "grade": 2021,
  "semester_enrolled": "2021-2022-1",
  "major_id": "080901",
  "college_id": "C001",
  "class_advisor_id": null,
  "counselor_id": null,
  "total_students": 50,
  "male_count": 0,
  "female_count": 0,
  "graduation_date": "2025-06-30",
  "classroom_location": null,
  "class_motto": null,
  "class_description": null,
  "id": 1,
  "created_at": "2025-06-20 15:48:55",
  "updated_at": "2025-06-20 15:48:55",
  "is_deleted": 0,
  "deleted_at": null,
  "status": "active",
  "is_active": 1,
  "notes": null
}
,
{
  "class_id": "CL2021002",
  "class_name": "计算机科学与技术2021级2班",
  "class_code": "080901-2021-2",
  "grade": 2021,
  "semester_enrolled": "2021-2022-1",
  "major_id": "080901",
  "college_id": "C001",
  "class_advisor_id": null,
  "counselor_id": null,
  "total_students": 50,
  "male_count": 0,
  "female_count": 0,
  "graduation_date": "2025-06-30",
  "classroom_location": null,
  "class_motto": null,
  "class_description": null,
  "id": 2,
  "created_at": "2025-06-20 15:48:55",
  "updated_at": "2025-06-20 15:48:55",
  "is_deleted": 0,
  "deleted_at": null,
  "status": "active",
  "is_active": 1,
  "notes": null
}
```


### locations 表
数据量: 3,300 条记录

```json
{
  "location_id": "VARCHAR(20)",  // 必填
  "location_name": "VARCHAR(50)",  // 必填
  "location_type": "VARCHAR(12)",  // 必填
  "building_code": "VARCHAR(10)",  // 必填
  "building_name": "VARCHAR(50)",  // 必填
  "floor": "INTEGER",
  "room_number": "VARCHAR(20)",
  "capacity": "INTEGER",
  "area": "NUMERIC(8, 2)",
  "facilities": "JSON",
  "equipment_list": "JSON",
  "is_available": "BOOLEAN",
  "usage_restrictions": "TEXT",
  "booking_required": "BOOLEAN",
  "manager_id": "VARCHAR(10)",
  "contact_phone": "VARCHAR(20)",
  "last_maintenance": "DATE",
  "next_maintenance": "DATE",
  "maintenance_notes": "TEXT",
  "id": "INTEGER",  // 自增ID, 主键, 必填
  "created_at": "DATETIME",  // 创建时间, 必填, 默认值:CURRENT_TIMESTAMP
  "updated_at": "DATETIME",  // 更新时间, 必填, 默认值:CURRENT_TIMESTAMP
  "is_deleted": "BOOLEAN",  // 删除标记, 必填
  "deleted_at": "DATETIME",  // 删除时间
  "status": "VARCHAR(20)",  // 状态, 必填
  "is_active": "BOOLEAN",  // 激活状态, 必填
  "notes": "TEXT"  // 备注
}
```

**外键关系:**
- manager_id → persons.employee_id

**样本数据:**
```json
{
  "location_id": "LOCC1F1R01",
  "location_name": "计算机学院1号楼1楼1室",
  "location_type": "classroom",
  "building_code": "C1",
  "building_name": "计算机学院1号楼",
  "floor": 1,
  "room_number": "101",
  "capacity": 80,
  "area": 81,
  "facilities": "[]",
  "equipment_list": "[]",
  "is_available": 1,
  "usage_restrictions": null,
  "booking_required": 0,
  "manager_id": null,
  "contact_phone": null,
  "last_maintenance": null,
  "next_maintenance": null,
  "maintenance_notes": null,
  "id": 1,
  "created_at": "2025-06-20 15:49:04",
  "updated_at": "2025-06-20 15:49:04",
  "is_deleted": 0,
  "deleted_at": null,
  "status": "active",
  "is_active": 1,
  "notes": null
}
,
{
  "location_id": "LOCC1F1R02",
  "location_name": "计算机学院1号楼1楼2室",
  "location_type": "classroom",
  "building_code": "C1",
  "building_name": "计算机学院1号楼",
  "floor": 1,
  "room_number": "102",
  "capacity": 46,
  "area": 80,
  "facilities": "[]",
  "equipment_list": "[]",
  "is_available": 1,
  "usage_restrictions": null,
  "booking_required": 0,
  "manager_id": null,
  "contact_phone": null,
  "last_maintenance": null,
  "next_maintenance": null,
  "maintenance_notes": null,
  "id": 2,
  "created_at": "2025-06-20 15:49:04",
  "updated_at": "2025-06-20 15:49:04",
  "is_deleted": 0,
  "deleted_at": null,
  "status": "active",
  "is_active": 1,
  "notes": null
}
```


### courses 表
数据量: 3,120 条记录

```json
{
  "course_id": "VARCHAR(20)",  // 必填
  "course_name": "VARCHAR(100)",  // 必填
  "course_name_en": "VARCHAR(200)",
  "course_code": "VARCHAR(20)",  // 必填
  "course_type": "VARCHAR(10)",  // 必填
  "credit_hours": "NUMERIC(3, 1)",  // 必填
  "total_hours": "INTEGER",  // 必填
  "theory_hours": "INTEGER",
  "practice_hours": "INTEGER",
  "experiment_hours": "INTEGER",
  "major_id": "VARCHAR(10)",  // 必填
  "college_id": "VARCHAR(10)",  // 必填
  "prerequisite_courses": "JSON",
  "assessment_method": "VARCHAR(50)",
  "exam_form": "VARCHAR(12)",
  "description": "TEXT",
  "objectives": "TEXT",
  "syllabus": "TEXT",
  "textbook": "VARCHAR(200)",
  "references": "JSON",
  "difficulty_level": "INTEGER",
  "workload_level": "INTEGER",
  "is_active": "BOOLEAN",  // 激活状态
  "approval_status": "VARCHAR(20)",
  "id": "INTEGER",  // 自增ID, 主键, 必填
  "created_at": "DATETIME",  // 创建时间, 必填, 默认值:CURRENT_TIMESTAMP
  "updated_at": "DATETIME",  // 更新时间, 必填, 默认值:CURRENT_TIMESTAMP
  "is_deleted": "BOOLEAN",  // 删除标记, 必填
  "deleted_at": "DATETIME",  // 删除时间
  "status": "VARCHAR(20)",  // 状态, 必填
  "notes": "TEXT"  // 备注
}
```

**外键关系:**
- college_id → colleges.college_id
- major_id → majors.major_id

**样本数据:**
```json
{
  "course_id": "C080901001",
  "course_name": "计算机科学与技术专业课程1",
  "course_name_en": null,
  "course_code": "080901-1",
  "course_type": "practice",
  "credit_hours": 2.5,
  "total_hours": 40,
  "theory_hours": 0,
  "practice_hours": 0,
  "experiment_hours": 0,
  "major_id": "080901",
  "college_id": "C001",
  "prerequisite_courses": "[]",
  "assessment_method": null,
  "exam_form": "closed_book",
  "description": "计算机科学与技术专业的重要课程",
  "objectives": null,
  "syllabus": null,
  "textbook": null,
  "references": "[]",
  "difficulty_level": 4,
  "workload_level": 3,
  "is_active": 1,
  "approval_status": "approved",
  "id": 1,
  "created_at": "2025-06-20 15:50:35",
  "updated_at": "2025-06-20 15:50:35",
  "is_deleted": 0,
  "deleted_at": null,
  "status": "active",
  "notes": null
}
,
{
  "course_id": "C080901002",
  "course_name": "计算机科学与技术专业课程2",
  "course_name_en": null,
  "course_code": "080901-2",
  "course_type": "practice",
  "credit_hours": 2.5,
  "total_hours": 22,
  "theory_hours": 0,
  "practice_hours": 0,
  "experiment_hours": 0,
  "major_id": "080901",
  "college_id": "C001",
  "prerequisite_courses": "[]",
  "assessment_method": null,
  "exam_form": "closed_book",
  "description": "计算机科学与技术专业的重要课程",
  "objectives": null,
  "syllabus": null,
  "textbook": null,
  "references": "[]",
  "difficulty_level": 1,
  "workload_level": 3,
  "is_active": 1,
  "approval_status": "approved",
  "id": 2,
  "created_at": "2025-06-20 15:50:35",
  "updated_at": "2025-06-20 15:50:35",
  "is_deleted": 0,
  "deleted_at": null,
  "status": "active",
  "notes": null
}
```


### exams 表
数据量: 13+ 条记录

```json
{
  "exam_id": "TEXT",  // 考试ID, 主键, 必填
  "course_instance_id": "TEXT",  // 课程实例ID
  "course_id": "TEXT",  // 课程ID
  "exam_type": "TEXT",  // 考试类型 (final, midterm, quiz)
  "exam_name": "TEXT",  // 考试名称
  "exam_date": "TEXT",  // 考试日期
  "exam_time": "TEXT",  // 考试时间
  "duration": "INTEGER",  // 考试时长(分钟)
  "location": "TEXT",  // 考试地点
  "exam_status": "TEXT",  // 考试状态 (scheduled, ongoing, completed)
  "total_score": "REAL",  // 总分
  "weight": "REAL",  // 权重
  "instructions": "TEXT",  // 考试说明
  "created_at": "TEXT",  // 创建时间
  "updated_at": "TEXT",  // 更新时间
  "is_deleted": "INTEGER"  // 删除标记, 默认值:0
}
```

**外键关系:**
- course_instance_id → course_instances.instance_id
- course_id → courses.course_id

**样本数据:**
```json
{
  "exam_id": "EXAM_20241225_001",
  "course_instance_id": "CI2025000001",
  "course_id": "C080901001",
  "exam_type": "final",
  "exam_name": "计算机科学与技术专业课程1期末考试",
  "exam_date": "2025-01-14",
  "exam_time": "8:30-10:30",
  "duration": 120,
  "location": "教学楼A101",
  "exam_status": "scheduled",
  "total_score": 100.0,
  "weight": 0.6,
  "instructions": "请携带学生证和文具，禁止使用电子设备",
  "created_at": "2024-12-25T04:07:28.309000",
  "updated_at": "2024-12-25T04:07:28.309000",
  "is_deleted": 0
}
```


### assets 表
数据量: 33,277 条记录

```json
{
  "asset_id": "VARCHAR(20)",  // 必填
  "asset_name": "VARCHAR(100)",  // 必填
  "asset_model": "VARCHAR(50)",
  "asset_brand": "VARCHAR(50)",
  "category": "VARCHAR(30)",  // 必填
  "subcategory": "VARCHAR(50)",
  "asset_type": "VARCHAR(50)",  // 必填
  "location_id": "VARCHAR(20)",
  "building_code": "VARCHAR(10)",
  "room_number": "VARCHAR(20)",
  "purchase_price": "NUMERIC(12, 2)",
  "current_value": "NUMERIC(12, 2)",
  "depreciation_rate": "NUMERIC(5, 2)",
  "purchase_date": "DATE",
  "supplier": "VARCHAR(100)",
  "purchase_contract": "VARCHAR(50)",
  "warranty_period": "INTEGER",
  "warranty_end_date": "DATE",
  "asset_status": "VARCHAR(11)",
  "user_id": "VARCHAR(20)",
  "manager_id": "VARCHAR(10)",
  "specifications": "JSON",
  "configuration": "JSON",
  "last_maintenance": "DATE",
  "next_maintenance": "DATE",
  "maintenance_cycle": "INTEGER",
  "maintenance_cost": "NUMERIC(10, 2)",
  "maintenance_notes": "TEXT",
  "security_level": "VARCHAR(20)",
  "access_restrictions": "JSON",
  "ip_address": "VARCHAR(50)",
  "mac_address": "VARCHAR(20)",
  "network_info": "JSON",
  "temperature_range": "VARCHAR(20)",
  "humidity_range": "VARCHAR(20)",
  "power_requirements": "VARCHAR(50)",
  "disposal_date": "DATE",
  "disposal_method": "VARCHAR(50)",
  "disposal_value": "NUMERIC(10, 2)",
  "photos": "JSON",
  "documents": "JSON",
  "id": "INTEGER",  // 自增ID, 主键, 必填
  "created_at": "DATETIME",  // 创建时间, 必填, 默认值:CURRENT_TIMESTAMP
  "updated_at": "DATETIME",  // 更新时间, 必填, 默认值:CURRENT_TIMESTAMP
  "is_deleted": "BOOLEAN",  // 删除标记, 必填
  "deleted_at": "DATETIME",  // 删除时间
  "status": "VARCHAR(20)",  // 状态, 必填
  "is_active": "BOOLEAN",  // 激活状态, 必填
  "notes": "TEXT"  // 备注
}
```

**外键关系:**
- manager_id → persons.employee_id
- user_id → persons.person_id
- location_id → locations.location_id

**样本数据:**
```json
{
  "asset_id": "AST2025000001",
  "asset_name": "投影仪",
  "asset_model": null,
  "asset_brand": null,
  "category": "teaching_equipment",
  "subcategory": null,
  "asset_type": "projection",
  "location_id": "LOCC1F1R01",
  "building_code": "C1",
  "room_number": "101",
  "purchase_price": 21751,
  "current_value": null,
  "depreciation_rate": 0,
  "purchase_date": "2025-03-07",
  "supplier": "华为技术",
  "purchase_contract": null,
  "warranty_period": null,
  "warranty_end_date": null,
  "asset_status": "in_use",
  "user_id": null,
  "manager_id": null,
  "specifications": "{}",
  "configuration": "{}",
  "last_maintenance": null,
  "next_maintenance": null,
  "maintenance_cycle": null,
  "maintenance_cost": 0,
  "maintenance_notes": null,
  "security_level": "normal",
  "access_restrictions": "[]",
  "ip_address": null,
  "mac_address": null,
  "network_info": "{}",
  "temperature_range": null,
  "humidity_range": null,
  "power_requirements": null,
  "disposal_date": null,
  "disposal_method": null,
  "disposal_value": null,
  "photos": "[]",
  "documents": "[]",
  "id": 1,
  "created_at": "2025-06-20 15:49:04",
  "updated_at": "2025-06-20 15:49:04",
  "is_deleted": 0,
  "deleted_at": null,
  "status": "active",
  "is_active": 1,
  "notes": null
}
,
{
  "asset_id": "AST2025000002",
  "asset_name": "监控摄像头",
  "asset_model": null,
  "asset_brand": null,
  "category": "infrastructure",
  "subcategory": null,
  "asset_type": "security",
  "location_id": "LOCC1F1R01",
  "building_code": "C1",
  "room_number": "101",
  "purchase_price": 6094,
  "current_value": null,
  "depreciation_rate": 0,
  "purchase_date": "2022-05-23",
  "supplier": "戴尔科技",
  "purchase_contract": null,
  "warranty_period": null,
  "warranty_end_date": null,
  "asset_status": "idle",
  "user_id": null,
  "manager_id": null,
  "specifications": "{}",
  "configuration": "{}",
  "last_maintenance": null,
  "next_maintenance": null,
  "maintenance_cycle": null,
  "maintenance_cost": 0,
  "maintenance_notes": null,
  "security_level": "normal",
  "access_restrictions": "[]",
  "ip_address": null,
  "mac_address": null,
  "network_info": "{}",
  "temperature_range": null,
  "humidity_range": null,
  "power_requirements": null,
  "disposal_date": null,
  "disposal_method": null,
  "disposal_value": null,
  "photos": "[]",
  "documents": "[]",
  "id": 2,
  "created_at": "2025-06-20 15:49:04",
  "updated_at": "2025-06-20 15:49:04",
  "is_deleted": 0,
  "deleted_at": null,
  "status": "active",
  "is_active": 1,
  "notes": null
}
```


### books 表
数据量: 50,000 条记录

```json
{
  "book_id": "VARCHAR(20)",  // 必填
  "isbn": "VARCHAR(20)",
  "title": "VARCHAR(200)",  // 必填
  "title_en": "VARCHAR(300)",
  "subtitle": "VARCHAR(200)",
  "author": "VARCHAR(100)",
  "translator": "VARCHAR(100)",
  "editor": "VARCHAR(100)",
  "publisher": "VARCHAR(100)",
  "publication_date": "DATE",
  "edition": "VARCHAR(20)",
  "print_count": "INTEGER",
  "category": "VARCHAR(50)",  // 必填
  "subcategory": "VARCHAR(50)",
  "classification_number": "VARCHAR(20)",
  "subject_keywords": "JSON",
  "pages": "INTEGER",
  "binding": "VARCHAR(20)",
  "format_size": "VARCHAR(20)",
  "price": "NUMERIC(8, 2)",
  "language": "VARCHAR(20)",
  "origin_country": "VARCHAR(30)",
  "abstract": "TEXT",
  "table_of_contents": "TEXT",
  "keywords": "JSON",
  "total_copies": "INTEGER",
  "available_copies": "INTEGER",
  "borrowed_copies": "INTEGER",
  "reserved_copies": "INTEGER",
  "damaged_copies": "INTEGER",
  "location_code": "VARCHAR(20)",
  "shelf_number": "VARCHAR(20)",
  "floor": "INTEGER",
  "reading_room": "VARCHAR(50)",
  "borrowable": "BOOLEAN",
  "loan_period_days": "INTEGER",
  "renewable_times": "INTEGER",
  "reservation_allowed": "BOOLEAN",
  "borrow_count": "INTEGER",
  "reservation_count": "INTEGER",
  "popularity_score": "NUMERIC(5, 2)",
  "book_status": "VARCHAR(20)",
  "acquisition_date": "DATE",
  "last_inventory_date": "DATE",
  "has_ebook": "BOOLEAN",
  "ebook_url": "VARCHAR(300)",
  "has_audiobook": "BOOLEAN",
  "audiobook_url": "VARCHAR(300)",
  "rating": "NUMERIC(3, 2)",
  "review_count": "INTEGER",
  "id": "INTEGER",  // 自增ID, 主键, 必填
  "created_at": "DATETIME",  // 创建时间, 必填, 默认值:CURRENT_TIMESTAMP
  "updated_at": "DATETIME",  // 更新时间, 必填, 默认值:CURRENT_TIMESTAMP
  "is_deleted": "BOOLEAN",  // 删除标记, 必填
  "deleted_at": "DATETIME",  // 删除时间
  "status": "VARCHAR(20)",  // 状态, 必填
  "is_active": "BOOLEAN",  // 激活状态, 必填
  "notes": "TEXT"  // 备注
}
```

**样本数据:**
```json
{
  "book_id": "BK2025000001",
  "isbn": "978-1-07-275647-7",
  "title": "一直商品注册",
  "title_en": null,
  "subtitle": null,
  "author": "张文",
  "translator": null,
  "editor": null,
  "publisher": "人民邮电出版社",
  "publication_date": "2020-08-27",
  "edition": null,
  "print_count": null,
  "category": "计算机",
  "subcategory": null,
  "classification_number": null,
  "subject_keywords": "[]",
  "pages": 669,
  "binding": null,
  "format_size": null,
  "price": 133,
  "language": "中文",
  "origin_country": null,
  "abstract": null,
  "table_of_contents": null,
  "keywords": "[]",
  "total_copies": 10,
  "available_copies": 2,
  "borrowed_copies": 0,
  "reserved_copies": 0,
  "damaged_copies": 0,
  "location_code": "L1-68",
  "shelf_number": null,
  "floor": null,
  "reading_room": null,
  "borrowable": 1,
  "loan_period_days": 30,
  "renewable_times": 2,
  "reservation_allowed": 1,
  "borrow_count": 0,
  "reservation_count": 0,
  "popularity_score": 0,
  "book_status": "available",
  "acquisition_date": "2019-01-16",
  "last_inventory_date": null,
  "has_ebook": 0,
  "ebook_url": null,
  "has_audiobook": 0,
  "audiobook_url": null,
  "rating": null,
  "review_count": 0,
  "id": 1,
  "created_at": "2025-06-20 16:03:01",
  "updated_at": "2025-06-20 16:03:01",
  "is_deleted": 0,
  "deleted_at": null,
  "status": "active",
  "is_active": 1,
  "notes": null
}
,
{
  "book_id": "BK2025000002",
  "isbn": "978-1-77697-118-3",
  "title": "电子操作公司",
  "title_en": null,
  "subtitle": null,
  "author": "唐秀兰",
  "translator": null,
  "editor": null,
  "publisher": "北京大学出版社",
  "publication_date": "2005-09-18",
  "edition": null,
  "print_count": null,
  "category": "数学",
  "subcategory": null,
  "classification_number": null,
  "subject_keywords": "[]",
  "pages": 272,
  "binding": null,
  "format_size": null,
  "price": 163,
  "language": "中文",
  "origin_country": null,
  "abstract": null,
  "table_of_contents": null,
  "keywords": "[]",
  "total_copies": 8,
  "available_copies": 1,
  "borrowed_copies": 0,
  "reserved_copies": 0,
  "damaged_copies": 0,
  "location_code": "L1-34",
  "shelf_number": null,
  "floor": null,
  "reading_room": null,
  "borrowable": 1,
  "loan_period_days": 30,
  "renewable_times": 2,
  "reservation_allowed": 1,
  "borrow_count": 0,
  "reservation_count": 0,
  "popularity_score": 0,
  "book_status": "available",
  "acquisition_date": "2024-06-17",
  "last_inventory_date": null,
  "has_ebook": 0,
  "ebook_url": null,
  "has_audiobook": 0,
  "audiobook_url": null,
  "rating": null,
  "review_count": 0,
  "id": 2,
  "created_at": "2025-06-20 16:03:01",
  "updated_at": "2025-06-20 16:03:01",
  "is_deleted": 0,
  "deleted_at": null,
  "status": "active",
  "is_active": 1,
  "notes": null
}
```


## 关系表

### enrollments 表
数据量: 406,807 条记录

```json
{
  "enrollment_id": "VARCHAR(20)",  // 主键
  "student_id": "VARCHAR(12)",  // 学生ID, 必填
  "course_instance_id": "VARCHAR(20)",  // 必填
  "enrollment_type": "VARCHAR(20)",  // 默认值:'regular'
  "enrollment_status": "VARCHAR(20)",  // 默认值:'enrolled'
  "enrollment_date": "DATETIME",  // 必填
  "drop_date": "DATETIME",
  "credit_hours": "DECIMAL(4,2)",
  "is_mandatory": "BOOLEAN",  // 默认值:0
  "grade_weight_config": "JSON",
  "attendance_requirement": "DECIMAL(5,2)",  // 默认值:80.0
  "approved_by": "VARCHAR(10)",
  "approved_at": "DATETIME",
  "rejection_reason": "TEXT",
  "id": "INTEGER",  // 自增ID, 必填
  "created_at": "DATETIME",  // 创建时间, 必填, 默认值:CURRENT_TIMESTAMP
  "updated_at": "DATETIME",  // 更新时间, 必填, 默认值:CURRENT_TIMESTAMP
  "is_deleted": "BOOLEAN",  // 删除标记, 必填, 默认值:0
  "deleted_at": "DATETIME",  // 删除时间
  "status": "VARCHAR(20)",  // 状态, 必填, 默认值:'active'
  "is_active": "BOOLEAN",  // 激活状态, 必填, 默认值:1
  "notes": "TEXT"  // 备注
}
```

**外键关系:**
- approved_by → persons.employee_id
- course_instance_id → course_instances.instance_id
- student_id → persons.student_id

**样本数据:**
```json
{
  "enrollment_id": "EN202500000001",
  "student_id": "202100000001",
  "course_instance_id": "CI2024202511193",
  "enrollment_type": "regular",
  "enrollment_status": "completed",
  "enrollment_date": "2025-06-20 15:55:46",
  "drop_date": null,
  "credit_hours": 3,
  "is_mandatory": 1,
  "grade_weight_config": null,
  "attendance_requirement": 80,
  "approved_by": null,
  "approved_at": null,
  "rejection_reason": null,
  "id": 1000001,
  "created_at": "2025-06-20 15:55:46",
  "updated_at": "2025-06-20 15:55:46",
  "is_deleted": 0,
  "deleted_at": null,
  "status": "active",
  "is_active": 1,
  "notes": null
}
,
{
  "enrollment_id": "EN202500000002",
  "student_id": "202100000001",
  "course_instance_id": "CI2023202422708",
  "enrollment_type": "regular",
  "enrollment_status": "completed",
  "enrollment_date": "2025-06-20 15:55:46",
  "drop_date": null,
  "credit_hours": 4,
  "is_mandatory": 0,
  "grade_weight_config": null,
  "attendance_requirement": 80,
  "approved_by": null,
  "approved_at": null,
  "rejection_reason": null,
  "id": 1000002,
  "created_at": "2025-06-20 15:55:46",
  "updated_at": "2025-06-20 15:55:46",
  "is_deleted": 0,
  "deleted_at": null,
  "status": "active",
  "is_active": 1,
  "notes": null
}
```


### course_instances 表
数据量: 9,360 条记录

```json
{
  "instance_id": "VARCHAR(20)",  // 必填
  "course_id": "VARCHAR(20)",  // 必填
  "teacher_id": "VARCHAR(10)",  // 必填
  "assistant_teacher_id": "VARCHAR(10)",
  "semester": "VARCHAR(20)",  // 必填
  "academic_year": "VARCHAR(10)",  // 必填
  "schedule_info": "JSON",
  "class_locations": "JSON",
  "max_students": "INTEGER",
  "current_students": "INTEGER",
  "min_students": "INTEGER",
  "target_grades": "JSON",
  "target_majors": "JSON",
  "instance_status": "VARCHAR(20)",
  "registration_start": "DATETIME",
  "registration_end": "DATETIME",
  "class_start_date": "DATE",
  "class_end_date": "DATE",
  "total_weeks": "INTEGER",
  "weekly_hours": "INTEGER",
  "exam_date": "DATETIME",
  "exam_location": "VARCHAR(50)",
  "makeup_exam_date": "DATETIME",
  "avg_score": "NUMERIC(5, 2)",
  "pass_rate": "NUMERIC(5, 2)",
  "excellent_rate": "NUMERIC(5, 2)",
  "teacher_rating": "NUMERIC(3, 2)",
  "course_rating": "NUMERIC(3, 2)",
  "id": "INTEGER",  // 自增ID, 主键, 必填
  "created_at": "DATETIME",  // 创建时间, 必填, 默认值:CURRENT_TIMESTAMP
  "updated_at": "DATETIME",  // 更新时间, 必填, 默认值:CURRENT_TIMESTAMP
  "is_deleted": "BOOLEAN",  // 删除标记, 必填
  "deleted_at": "DATETIME",  // 删除时间
  "status": "VARCHAR(20)",  // 状态, 必填
  "is_active": "BOOLEAN",  // 激活状态, 必填
  "notes": "TEXT"  // 备注
}
```

**外键关系:**
- assistant_teacher_id → persons.employee_id
- teacher_id → persons.employee_id
- course_id → courses.course_id

**样本数据:**
```json
{
  "instance_id": "CI202320241001",
  "course_id": "C080901001",
  "teacher_id": "2025001029",
  "assistant_teacher_id": null,
  "semester": "2023-2024-1",
  "academic_year": "2023-2024",
  "schedule_info": "[]",
  "class_locations": "[]",
  "max_students": 43,
  "current_students": 0,
  "min_students": 10,
  "target_grades": "[]",
  "target_majors": "[]",
  "instance_status": "open",
  "registration_start": null,
  "registration_end": null,
  "class_start_date": "2023-09-01",
  "class_end_date": "2024-01-15",
  "total_weeks": 16,
  "weekly_hours": 2,
  "exam_date": null,
  "exam_location": null,
  "makeup_exam_date": null,
  "avg_score": null,
  "pass_rate": null,
  "excellent_rate": null,
  "teacher_rating": null,
  "course_rating": null,
  "id": 1,
  "created_at": "2025-06-20 15:50:35",
  "updated_at": "2025-06-20 15:50:35",
  "is_deleted": 0,
  "deleted_at": null,
  "status": "active",
  "is_active": 1,
  "notes": null
}
,
{
  "instance_id": "CI202320242001",
  "course_id": "C080901001",
  "teacher_id": "2025001022",
  "assistant_teacher_id": null,
  "semester": "2023-2024-2",
  "academic_year": "2023-2024",
  "schedule_info": "[]",
  "class_locations": "[]",
  "max_students": 69,
  "current_students": 0,
  "min_students": 10,
  "target_grades": "[]",
  "target_majors": "[]",
  "instance_status": "planning",
  "registration_start": null,
  "registration_end": null,
  "class_start_date": "2024-02-15",
  "class_end_date": "2024-07-15",
  "total_weeks": 16,
  "weekly_hours": 2,
  "exam_date": null,
  "exam_location": null,
  "makeup_exam_date": null,
  "avg_score": null,
  "pass_rate": null,
  "excellent_rate": null,
  "teacher_rating": null,
  "course_rating": null,
  "id": 2,
  "created_at": "2025-06-20 15:50:35",
  "updated_at": "2025-06-20 15:50:35",
  "is_deleted": 0,
  "deleted_at": null,
  "status": "active",
  "is_active": 1,
  "notes": null
}
```


### class_schedules 表
数据量: 0 条记录

```json
{
  "schedule_id": "VARCHAR(20)",  // 主键
  "course_instance_id": "VARCHAR(20)",  // 必填
  "day_of_week": "INTEGER",  // 必填
  "start_time": "TIME",  // 必填
  "end_time": "TIME",  // 必填
  "classroom": "VARCHAR(50)",
  "building": "VARCHAR(50)",
  "week_range": "VARCHAR(20)",
  "teacher_id": "VARCHAR(10)",
  "class_type": "VARCHAR(20)",  // 默认值:'lecture'
  "id": "INTEGER",  // 自增ID, 必填
  "created_at": "DATETIME",  // 创建时间, 必填, 默认值:CURRENT_TIMESTAMP
  "updated_at": "DATETIME",  // 更新时间, 必填, 默认值:CURRENT_TIMESTAMP
  "is_deleted": "BOOLEAN",  // 删除标记, 必填, 默认值:0
  "deleted_at": "DATETIME",  // 删除时间
  "status": "VARCHAR(20)",  // 状态, 必填, 默认值:'active'
  "is_active": "BOOLEAN",  // 激活状态, 必填, 默认值:1
  "notes": "TEXT"  // 备注
}
```

**外键关系:**
- teacher_id → persons.employee_id
- course_instance_id → course_instances.instance_id


### borrow_records 表
数据量: 4,427 条记录

```json
{
  "record_id": "VARCHAR(20)",  // 必填
  "book_id": "VARCHAR(20)",  // 必填
  "borrower_id": "VARCHAR(20)",  // 必填
  "librarian_id": "VARCHAR(10)",
  "borrow_date": "DATETIME",  // 必填
  "due_date": "DATETIME",  // 必填
  "return_date": "DATETIME",
  "renewal_count": "INTEGER",
  "last_renewal_date": "DATETIME",
  "max_renewals": "INTEGER",
  "record_status": "VARCHAR(20)",
  "is_overdue": "BOOLEAN",
  "overdue_days": "INTEGER",
  "overdue_fine": "NUMERIC(8, 2)",
  "damage_fee": "NUMERIC(8, 2)",
  "lost_fee": "NUMERIC(8, 2)",
  "total_fee": "NUMERIC(8, 2)",
  "condition_on_borrow": "VARCHAR(20)",
  "condition_on_return": "VARCHAR(20)",
  "damage_description": "TEXT",
  "borrow_location": "VARCHAR(50)",
  "return_location": "VARCHAR(50)",
  "reservation_date": "DATETIME",
  "pickup_deadline": "DATETIME",
  "borrower_rating": "INTEGER",
  "borrower_review": "TEXT",
  "id": "INTEGER",  // 自增ID, 主键, 必填
  "created_at": "DATETIME",  // 创建时间, 必填, 默认值:CURRENT_TIMESTAMP
  "updated_at": "DATETIME",  // 更新时间, 必填, 默认值:CURRENT_TIMESTAMP
  "is_deleted": "BOOLEAN",  // 删除标记, 必填
  "deleted_at": "DATETIME",  // 删除时间
  "status": "VARCHAR(20)",  // 状态, 必填
  "is_active": "BOOLEAN",  // 激活状态, 必填
  "notes": "TEXT"  // 备注
}
```

**外键关系:**
- librarian_id → persons.employee_id
- borrower_id → persons.person_id
- book_id → books.book_id

**样本数据:**
```json
{
  "record_id": "BR202500000001",
  "book_id": "BK2025019017",
  "borrower_id": "P2025053912",
  "librarian_id": null,
  "borrow_date": "2025-05-10 00:00:00.000000",
  "due_date": "2025-06-09 00:00:00.000000",
  "return_date": null,
  "renewal_count": 0,
  "last_renewal_date": null,
  "max_renewals": 2,
  "record_status": "borrowed",
  "is_overdue": 0,
  "overdue_days": 0,
  "overdue_fine": 0,
  "damage_fee": 0,
  "lost_fee": 0,
  "total_fee": 0,
  "condition_on_borrow": "good",
  "condition_on_return": null,
  "damage_description": null,
  "borrow_location": null,
  "return_location": null,
  "reservation_date": null,
  "pickup_deadline": null,
  "borrower_rating": null,
  "borrower_review": null,
  "id": 1,
  "created_at": "2025-06-20 16:03:05",
  "updated_at": "2025-06-20 16:03:05",
  "is_deleted": 0,
  "deleted_at": null,
  "status": "active",
  "is_active": 1,
  "notes": null
}
,
{
  "record_id": "BR202500000002",
  "book_id": "BK2025030962",
  "borrower_id": "P2025053912",
  "librarian_id": null,
  "borrow_date": "2024-11-04 00:00:00.000000",
  "due_date": "2024-12-04 00:00:00.000000",
  "return_date": null,
  "renewal_count": 0,
  "last_renewal_date": null,
  "max_renewals": 2,
  "record_status": "borrowed",
  "is_overdue": 0,
  "overdue_days": 0,
  "overdue_fine": 0,
  "damage_fee": 0,
  "lost_fee": 0,
  "total_fee": 0,
  "condition_on_borrow": "good",
  "condition_on_return": null,
  "damage_description": null,
  "borrow_location": null,
  "return_location": null,
  "reservation_date": null,
  "pickup_deadline": null,
  "borrower_rating": null,
  "borrower_review": null,
  "id": 2,
  "created_at": "2025-06-20 16:03:05",
  "updated_at": "2025-06-20 16:03:05",
  "is_deleted": 0,
  "deleted_at": null,
  "status": "active",
  "is_active": 1,
  "notes": null
}
```


### transactions 表
数据量: 17,134,200 条记录

```json
{
  "transaction_id": "VARCHAR(30)",  // 必填
  "person_id": "VARCHAR(20)",  // 人员ID, 必填
  "campus_card_id": "VARCHAR(20)",
  "transaction_type": "VARCHAR(11)",  // 必填
  "payment_method": "VARCHAR(11)",  // 必填
  "amount": "NUMERIC(10, 2)",  // 必填
  "balance_before": "NUMERIC(10, 2)",
  "balance_after": "NUMERIC(10, 2)",
  "transaction_time": "DATETIME",  // 必填
  "process_time": "DATETIME",
  "location_id": "VARCHAR(20)",
  "merchant_name": "VARCHAR(100)",
  "terminal_id": "VARCHAR(20)",
  "transaction_status": "VARCHAR(20)",
  "description": "VARCHAR(200)",
  "category": "VARCHAR(50)",
  "subcategory": "VARCHAR(50)",
  "order_id": "VARCHAR(30)",
  "external_transaction_id": "VARCHAR(50)",
  "fee_amount": "NUMERIC(8, 2)",
  "actual_amount": "NUMERIC(10, 2)",
  "counterparty_id": "VARCHAR(20)",
  "counterparty_name": "VARCHAR(50)",
  "refund_amount": "NUMERIC(10, 2)",
  "refund_reason": "VARCHAR(200)",
  "refund_date": "DATETIME",
  "risk_level": "VARCHAR(20)",
  "is_suspicious": "BOOLEAN",
  "verification_required": "BOOLEAN",
  "device_info": "JSON",
  "ip_address": "VARCHAR(50)",
  "user_agent": "VARCHAR(200)",
  "id": "INTEGER",  // 自增ID, 主键, 必填
  "created_at": "DATETIME",  // 创建时间, 必填, 默认值:CURRENT_TIMESTAMP
  "updated_at": "DATETIME",  // 更新时间, 必填, 默认值:CURRENT_TIMESTAMP
  "is_deleted": "BOOLEAN",  // 删除标记, 必填
  "deleted_at": "DATETIME",  // 删除时间
  "status": "VARCHAR(20)",  // 状态, 必填
  "is_active": "BOOLEAN",  // 激活状态, 必填
  "notes": "TEXT"  // 备注
}
```

**外键关系:**
- location_id → locations.location_id
- campus_card_id → campus_cards.card_id
- person_id → persons.person_id

**样本数据:**
```json
{
  "transaction_id": "TXN20250000000001",
  "person_id": "P2025000001",
  "campus_card_id": "CC2025000001",
  "transaction_type": "recharge",
  "payment_method": "alipay",
  "amount": 146,
  "balance_before": null,
  "balance_after": null,
  "transaction_time": "2025-06-03 00:03:05.911210",
  "process_time": null,
  "location_id": null,
  "merchant_name": null,
  "terminal_id": null,
  "transaction_status": "success",
  "description": "超市购物",
  "category": "其他",
  "subcategory": null,
  "order_id": null,
  "external_transaction_id": null,
  "fee_amount": 0,
  "actual_amount": null,
  "counterparty_id": null,
  "counterparty_name": null,
  "refund_amount": 0,
  "refund_reason": null,
  "refund_date": null,
  "risk_level": "low",
  "is_suspicious": 0,
  "verification_required": 0,
  "device_info": "{}",
  "ip_address": null,
  "user_agent": null,
  "id": 1,
  "created_at": "2025-06-20 16:04:23",
  "updated_at": "2025-06-20 16:04:23",
  "is_deleted": 0,
  "deleted_at": null,
  "status": "active",
  "is_active": 1,
  "notes": null
}
,
{
  "transaction_id": "TXN20250000000002",
  "person_id": "P2025000001",
  "campus_card_id": "CC2025000001",
  "transaction_type": "recharge",
  "payment_method": "wechat",
  "amount": 176,
  "balance_before": null,
  "balance_after": null,
  "transaction_time": "2025-06-03 00:03:05.911210",
  "process_time": null,
  "location_id": null,
  "merchant_name": null,
  "terminal_id": null,
  "transaction_status": "success",
  "description": "图书馆",
  "category": "购物",
  "subcategory": null,
  "order_id": null,
  "external_transaction_id": null,
  "fee_amount": 0,
  "actual_amount": null,
  "counterparty_id": null,
  "counterparty_name": null,
  "refund_amount": 0,
  "refund_reason": null,
  "refund_date": null,
  "risk_level": "low",
  "is_suspicious": 0,
  "verification_required": 0,
  "device_info": "{}",
  "ip_address": null,
  "user_agent": null,
  "id": 2,
  "created_at": "2025-06-20 16:04:23",
  "updated_at": "2025-06-20 16:04:23",
  "is_deleted": 0,
  "deleted_at": null,
  "status": "active",
  "is_active": 1,
  "notes": null
}
```


### room_occupations 表
数据量: 0 条记录

```json
{
  "occupation_id": "VARCHAR(20)",  // 必填
  "location_id": "VARCHAR(20)",  // 必填
  "course_instance_id": "VARCHAR(20)",
  "event_id": "VARCHAR(20)",
  "start_time": "DATETIME",  // 必填
  "end_time": "DATETIME",  // 必填
  "weekday": "INTEGER",
  "time_slot": "INTEGER",
  "is_recurring": "BOOLEAN",
  "recurring_pattern": "VARCHAR(20)",
  "recurring_weeks": "VARCHAR(50)",
  "occupant_type": "VARCHAR(20)",  // 必填
  "occupant_id": "VARCHAR(20)",
  "occupant_name": "VARCHAR(50)",
  "occupation_status": "VARCHAR(20)",
  "approval_required": "BOOLEAN",
  "approved_by": "VARCHAR(10)",
  "approved_at": "DATETIME",
  "actual_attendees": "INTEGER",
  "equipment_needed": "JSON",
  "special_requirements": "TEXT",
  "id": "INTEGER",  // 自增ID, 主键, 必填
  "created_at": "DATETIME",  // 创建时间, 必填, 默认值:CURRENT_TIMESTAMP
  "updated_at": "DATETIME",  // 更新时间, 必填, 默认值:CURRENT_TIMESTAMP
  "is_deleted": "BOOLEAN",  // 删除标记, 必填
  "deleted_at": "DATETIME",  // 删除时间
  "status": "VARCHAR(20)",  // 状态, 必填
  "is_active": "BOOLEAN",  // 激活状态, 必填
  "notes": "TEXT"  // 备注
}
```

**外键关系:**
- approved_by → persons.employee_id
- course_instance_id → course_instances.instance_id
- location_id → locations.location_id


## 成绩相关表

### grades 表
数据量: 406,807 条记录

```json
{
  "grade_id": "VARCHAR(20)",  // 必填
  "student_id": "VARCHAR(12)",  // 学生ID, 必填
  "course_instance_id": "VARCHAR(20)",  // 必填
  "usual_score": "NUMERIC(5, 2)",
  "midterm_score": "NUMERIC(5, 2)",
  "final_score": "NUMERIC(5, 2)",
  "lab_score": "NUMERIC(5, 2)",
  "homework_score": "NUMERIC(5, 2)",
  "total_score": "NUMERIC(5, 2)",
  "grade_point": "NUMERIC(3, 2)",
  "grade_level": "VARCHAR(2)",
  "score_weights": "JSON",
  "exam_type": "VARCHAR(20)",
  "exam_date": "DATETIME",
  "submit_date": "DATETIME",
  "grade_status": "VARCHAR(20)",
  "is_passed": "BOOLEAN",
  "is_retake_required": "BOOLEAN",
  "teacher_comment": "TEXT",
  "grade_notes": "TEXT",
  "reviewed_by": "VARCHAR(10)",
  "reviewed_at": "DATETIME",
  "id": "INTEGER",  // 自增ID, 主键, 必填
  "created_at": "DATETIME",  // 创建时间, 必填, 默认值:CURRENT_TIMESTAMP
  "updated_at": "DATETIME",  // 更新时间, 必填, 默认值:CURRENT_TIMESTAMP
  "is_deleted": "BOOLEAN",  // 删除标记, 必填
  "deleted_at": "DATETIME",  // 删除时间
  "status": "VARCHAR(20)",  // 状态, 必填
  "is_active": "BOOLEAN",  // 激活状态, 必填
  "notes": "TEXT"  // 备注
}
```

**外键关系:**
- reviewed_by → persons.employee_id
- course_instance_id → course_instances.instance_id
- student_id → persons.student_id

**样本数据:**
```json
{
  "grade_id": "GR202500000001",
  "student_id": "202100000001",
  "course_instance_id": "CI2024202511193",
  "usual_score": null,
  "midterm_score": 71,
  "final_score": 94,
  "lab_score": null,
  "homework_score": 80,
  "total_score": 87.9,
  "grade_point": 3,
  "grade_level": "B",
  "score_weights": "\"{\\\"usual\\\": 20, \\\"midterm\\\": 30, \\\"final\\\": 50, \\\"lab\\\": 0, \\\"homework\\\": 0}\"",
  "exam_type": "normal",
  "exam_date": null,
  "submit_date": null,
  "grade_status": "confirmed",
  "is_passed": null,
  "is_retake_required": 0,
  "teacher_comment": null,
  "grade_notes": null,
  "reviewed_by": null,
  "reviewed_at": null,
  "id": 1,
  "created_at": "2025-06-20 15:55:46",
  "updated_at": "2025-06-20 15:55:46",
  "is_deleted": 0,
  "deleted_at": null,
  "status": "active",
  "is_active": 1,
  "notes": null
}
,
{
  "grade_id": "GR202500000002",
  "student_id": "202100000001",
  "course_instance_id": "CI2023202422708",
  "usual_score": null,
  "midterm_score": 63,
  "final_score": 86,
  "lab_score": null,
  "homework_score": 80,
  "total_score": 81.7,
  "grade_point": 3,
  "grade_level": "B",
  "score_weights": "\"{\\\"usual\\\": 20, \\\"midterm\\\": 30, \\\"final\\\": 50, \\\"lab\\\": 0, \\\"homework\\\": 0}\"",
  "exam_type": "normal",
  "exam_date": null,
  "submit_date": null,
  "grade_status": "confirmed",
  "is_passed": null,
  "is_retake_required": 0,
  "teacher_comment": null,
  "grade_notes": null,
  "reviewed_by": null,
  "reviewed_at": null,
  "id": 2,
  "created_at": "2025-06-20 15:55:46",
  "updated_at": "2025-06-20 15:55:46",
  "is_deleted": 0,
  "deleted_at": null,
  "status": "active",
  "is_active": 1,
  "notes": null
}
```


### grade_statistics 表
数据量: 0 条记录

```json
{
  "stat_id": "VARCHAR(20)",  // 必填
  "course_instance_id": "VARCHAR(20)",  // 必填
  "stat_date": "DATE",  // 必填
  "total_students": "INTEGER",
  "submitted_count": "INTEGER",
  "max_score": "NUMERIC(5, 2)",
  "min_score": "NUMERIC(5, 2)",
  "avg_score": "NUMERIC(5, 2)",
  "median_score": "NUMERIC(5, 2)",
  "std_deviation": "NUMERIC(5, 2)",
  "grade_a_count": "INTEGER",
  "grade_b_count": "INTEGER",
  "grade_c_count": "INTEGER",
  "grade_d_count": "INTEGER",
  "grade_f_count": "INTEGER",
  "pass_rate": "NUMERIC(5, 2)",
  "excellent_rate": "NUMERIC(5, 2)",
  "good_rate": "NUMERIC(5, 2)",
  "score_distribution": "JSON",
  "id": "INTEGER",  // 自增ID, 主键, 必填
  "created_at": "DATETIME",  // 创建时间, 必填, 默认值:CURRENT_TIMESTAMP
  "updated_at": "DATETIME",  // 更新时间, 必填, 默认值:CURRENT_TIMESTAMP
  "is_deleted": "BOOLEAN",  // 删除标记, 必填
  "deleted_at": "DATETIME",  // 删除时间
  "status": "VARCHAR(20)",  // 状态, 必填
  "is_active": "BOOLEAN",  // 激活状态, 必填
  "notes": "TEXT"  // 备注
}
```

**外键关系:**
- course_instance_id → course_instances.instance_id


## 信息发布表

### announcements 表
数据量: 3 条记录

```json
{
  "id": "INTEGER",  // 自增ID, 主键
  "announcement_id": "VARCHAR(20)",  // 必填
  "title": "VARCHAR(200)",  // 必填
  "content": "TEXT",  // 必填
  "content_html": "TEXT",
  "summary": "VARCHAR(500)",
  "publisher_id": "VARCHAR(20)",  // 必填
  "publisher_name": "VARCHAR(50)",  // 必填
  "department": "VARCHAR(50)",  // 必填
  "category": "VARCHAR(30)",  // 默认值:'general'
  "priority": "VARCHAR(10)",  // 默认值:'normal'
  "status": "VARCHAR(20)",  // 状态, 默认值:'published'
  "is_urgent": "BOOLEAN",  // 默认值:FALSE
  "is_pinned": "BOOLEAN",  // 默认值:FALSE
  "publish_time": "DATETIME",  // 必填
  "effective_date": "DATETIME",
  "expire_date": "DATETIME",
  "target_audience": "VARCHAR(50)",  // 默认值:'all'
  "target_colleges": "JSON",
  "target_majors": "JSON",
  "target_grades": "JSON",
  "view_count": "INTEGER",  // 默认值:0
  "like_count": "INTEGER",  // 默认值:0
  "comment_count": "INTEGER",  // 默认值:0
  "attachments": "JSON",
  "cover_image_url": "VARCHAR(200)",
  "reviewed_by": "VARCHAR(20)",
  "review_time": "DATETIME",
  "review_status": "VARCHAR(20)",  // 默认值:'approved'
  "created_at": "DATETIME",  // 创建时间, 默认值:CURRENT_TIMESTAMP
  "updated_at": "DATETIME",  // 更新时间, 默认值:CURRENT_TIMESTAMP
  "is_deleted": "BOOLEAN",  // 删除标记, 默认值:FALSE
  "deleted_at": "DATETIME",  // 删除时间
  "notes": "TEXT"  // 备注
}
```

**外键关系:**
- publisher_id → persons.person_id

**样本数据:**
```json
{
  "id": 1,
  "announcement_id": "ANN2025001",
  "title": "关于2024年寒假放假安排的通知",
  "content": "各位同学：根据学校校历安排，现将2024年寒假放假时间安排通知如下：学生放假时间：2024年1月15日（星期一），开学时间：2024年2月26日（星期一）。请同学们合理安排假期时间，注意人身安全。",
  "content_html": null,
  "summary": null,
  "publisher_id": "P2025063441",
  "publisher_name": "何平",
  "department": "教务处",
  "category": "education",
  "priority": "high",
  "status": "published",
  "is_urgent": 0,
  "is_pinned": 1,
  "publish_time": "2025-06-03 22:59:55.149634",
  "effective_date": null,
  "expire_date": null,
  "target_audience": "all",
  "target_colleges": null,
  "target_majors": null,
  "target_grades": null,
  "view_count": 476,
  "like_count": 0,
  "comment_count": 0,
  "attachments": null,
  "cover_image_url": null,
  "reviewed_by": null,
  "review_time": null,
  "review_status": "approved",
  "created_at": "2025-06-23 14:59:55",
  "updated_at": "2025-06-23 14:59:55",
  "is_deleted": 0,
  "deleted_at": null,
  "notes": null
}
,
{
  "id": 2,
  "announcement_id": "ANN2025002",
  "title": "深圳技术大学第十二届运动会开幕式通知",
  "content": "为推动学校体育事业发展，展示师生良好精神风貌，学校定于2024年3月15日举办第十二届运动会。请各学院积极组织师生参与。",
  "content_html": null,
  "summary": null,
  "publisher_id": "P2025063442",
  "publisher_name": "梁国强",
  "department": "教务处",
  "category": "sports",
  "priority": "normal",
  "status": "published",
  "is_urgent": 0,
  "is_pinned": 1,
  "publish_time": "2025-06-18 22:59:55.149634",
  "effective_date": null,
  "expire_date": null,
  "target_audience": "all",
  "target_colleges": null,
  "target_majors": null,
  "target_grades": null,
  "view_count": 469,
  "like_count": 0,
  "comment_count": 0,
  "attachments": null,
  "cover_image_url": null,
  "reviewed_by": null,
  "review_time": null,
  "review_status": "approved",
  "created_at": "2025-06-23 14:59:55",
  "updated_at": "2025-06-23 14:59:55",
  "is_deleted": 0,
  "deleted_at": null,
  "notes": null
}
```


### events 表
数据量: 0 条记录

```json
{
  "id": "INTEGER",  // 自增ID, 主键
  "event_id": "VARCHAR(20)",  // 必填
  "title": "VARCHAR(200)",  // 必填
  "description": "TEXT",  // 必填
  "short_description": "VARCHAR(500)",
  "event_type": "VARCHAR(30)",  // 默认值:'general'
  "category": "VARCHAR(50)",
  "organizer_id": "VARCHAR(20)",  // 必填
  "organizer_name": "VARCHAR(100)",  // 必填
  "co_organizers": "JSON",
  "start_time": "DATETIME",  // 必填
  "end_time": "DATETIME",  // 必填
  "registration_start": "DATETIME",
  "registration_end": "DATETIME",
  "duration_hours": "INTEGER",
  "location_id": "VARCHAR(20)",
  "location_name": "VARCHAR(100)",
  "venue_details": "VARCHAR(200)",
  "address": "VARCHAR(200)",
  "capacity": "INTEGER",
  "registration_required": "BOOLEAN",  // 默认值:FALSE
  "max_participants": "INTEGER",
  "current_participants": "INTEGER",  // 默认值:0
  "registration_fee": "DECIMAL(8,2)",  // 默认值:0.00
  "requirements": "TEXT",
  "status": "VARCHAR(20)",  // 状态, 默认值:'planned'
  "is_public": "BOOLEAN",  // 默认值:TRUE
  "approval_status": "VARCHAR(20)",  // 默认值:'approved'
  "target_audience": "VARCHAR(50)",  // 默认值:'all'
  "target_colleges": "JSON",
  "target_majors": "JSON",
  "target_grades": "JSON",
  "eligibility_criteria": "TEXT",
  "poster_url": "VARCHAR(200)",
  "images": "JSON",
  "video_url": "VARCHAR(200)",
  "contact_person": "VARCHAR(50)",
  "contact_phone": "VARCHAR(20)",
  "contact_email": "VARCHAR(100)",
  "view_count": "INTEGER",  // 默认值:0
  "interest_count": "INTEGER",  // 默认值:0
  "created_at": "DATETIME",  // 创建时间, 默认值:CURRENT_TIMESTAMP
  "updated_at": "DATETIME",  // 更新时间, 默认值:CURRENT_TIMESTAMP
  "is_deleted": "BOOLEAN",  // 删除标记, 默认值:FALSE
  "deleted_at": "DATETIME",  // 删除时间
  "notes": "TEXT"  // 备注
}
```

**外键关系:**
- location_id → locations.location_id
- organizer_id → persons.person_id


### event_registrations 表
数据量: 0 条记录

```json
{
  "id": "INTEGER",  // 自增ID, 主键
  "registration_id": "VARCHAR(20)",  // 必填
  "event_id": "VARCHAR(20)",  // 必填
  "participant_id": "VARCHAR(20)",  // 必填
  "participant_name": "VARCHAR(50)",  // 必填
  "registration_time": "DATETIME",  // 默认值:CURRENT_TIMESTAMP
  "registration_method": "VARCHAR(20)",  // 默认值:'online'
  "registration_status": "VARCHAR(20)",  // 默认值:'registered'
  "attendance_status": "VARCHAR(20)",  // 默认值:'pending'
  "check_in_time": "DATETIME",
  "check_out_time": "DATETIME",
  "fee_paid": "DECIMAL(8,2)",  // 默认值:0.00
  "payment_status": "VARCHAR(20)",  // 默认值:'pending'
  "payment_method": "VARCHAR(20)",
  "payment_time": "DATETIME",
  "contact_phone": "VARCHAR(20)",
  "contact_email": "VARCHAR(100)",
  "special_requirements": "TEXT",
  "emergency_contact": "VARCHAR(100)",
  "rating": "INTEGER",
  "feedback": "TEXT",
  "feedback_time": "DATETIME",
  "created_at": "DATETIME",  // 创建时间, 默认值:CURRENT_TIMESTAMP
  "updated_at": "DATETIME",  // 更新时间, 默认值:CURRENT_TIMESTAMP
  "is_deleted": "BOOLEAN",  // 删除标记, 默认值:FALSE
  "notes": "TEXT"  // 备注
}
```

**外键关系:**
- participant_id → persons.person_id
- event_id → events.event_id


## 科研相关表

### research_projects 表
数据量: 1,768 条记录

```json
{
  "project_id": "VARCHAR(20)",  // 必填
  "project_name": "VARCHAR(200)",  // 必填
  "project_name_en": "VARCHAR(300)",
  "project_type": "VARCHAR(13)",  // 必填
  "project_level": "VARCHAR(10)",  // 必填
  "project_category": "VARCHAR(50)",
  "principal_investigator_id": "VARCHAR(10)",  // 必填
  "co_investigators": "JSON",
  "college_id": "VARCHAR(10)",  // 必填
  "department_id": "VARCHAR(10)",
  "project_abstract": "TEXT",
  "objectives": "TEXT",
  "methodology": "TEXT",
  "innovation_points": "TEXT",
  "expected_outcomes": "TEXT",
  "start_date": "DATE",  // 必填
  "end_date": "DATE",  // 必填
  "duration_months": "INTEGER",
  "total_funding": "NUMERIC(12, 2)",
  "allocated_funding": "NUMERIC(12, 2)",
  "spent_funding": "NUMERIC(12, 2)",
  "funding_source": "VARCHAR(100)",
  "project_status": "VARCHAR(20)",
  "approval_date": "DATE",
  "completion_date": "DATE",
  "keywords": "JSON",
  "research_fields": "JSON",
  "disciplines": "JSON",
  "papers_published": "INTEGER",
  "patents_applied": "INTEGER",
  "awards_received": "JSON",
  "peer_review_score": "NUMERIC(3, 2)",
  "progress_reports": "JSON",
  "contract_number": "VARCHAR(50)",
  "administrative_department": "VARCHAR(50)",
  "contact_person": "VARCHAR(50)",
  "contact_phone": "VARCHAR(20)",
  "id": "INTEGER",  // 自增ID, 主键, 必填
  "created_at": "DATETIME",  // 创建时间, 必填, 默认值:CURRENT_TIMESTAMP
  "updated_at": "DATETIME",  // 更新时间, 必填, 默认值:CURRENT_TIMESTAMP
  "is_deleted": "BOOLEAN",  // 删除标记, 必填
  "deleted_at": "DATETIME",  // 删除时间
  "status": "VARCHAR(20)",  // 状态, 必填
  "notes": "TEXT"  // 备注
}
```

**外键关系:**
- department_id → departments.department_id
- college_id → colleges.college_id
- principal_investigator_id → persons.employee_id

**样本数据:**
```json
{
  "project_id": "RP20250001",
  "project_name": "计算机科学领域研究项目",
  "project_name_en": null,
  "project_type": "horizontal",
  "project_level": "university",
  "project_category": null,
  "principal_investigator_id": "2025001001",
  "co_investigators": "[]",
  "college_id": "C001",
  "department_id": null,
  "project_abstract": null,
  "objectives": null,
  "methodology": null,
  "innovation_points": null,
  "expected_outcomes": null,
  "start_date": "2023-08-12",
  "end_date": "2025-01-30",
  "duration_months": null,
  "total_funding": 359098,
  "allocated_funding": 0,
  "spent_funding": 0,
  "funding_source": "企业合作",
  "project_status": "completed",
  "approval_date": null,
  "completion_date": null,
  "keywords": "[]",
  "research_fields": "[]",
  "disciplines": "[]",
  "papers_published": 0,
  "patents_applied": 0,
  "awards_received": "[]",
  "peer_review_score": null,
  "progress_reports": "[]",
  "contract_number": null,
  "administrative_department": null,
  "contact_person": null,
  "contact_phone": null,
  "id": 1,
  "created_at": "2025-06-20 16:27:15",
  "updated_at": "2025-06-20 16:27:15",
  "is_deleted": 0,
  "deleted_at": null,
  "status": "active",
  "notes": null
}
,
{
  "project_id": "RP20250002",
  "project_name": "计算机科学领域研究项目",
  "project_name_en": null,
  "project_type": "internal",
  "project_level": "national",
  "project_category": null,
  "principal_investigator_id": "2025001001",
  "co_investigators": "[]",
  "college_id": "C001",
  "department_id": null,
  "project_abstract": null,
  "objectives": null,
  "methodology": null,
  "innovation_points": null,
  "expected_outcomes": null,
  "start_date": "2022-09-25",
  "end_date": "2024-12-23",
  "duration_months": null,
  "total_funding": 243780,
  "allocated_funding": 0,
  "spent_funding": 0,
  "funding_source": "企业合作",
  "project_status": "completed",
  "approval_date": null,
  "completion_date": null,
  "keywords": "[]",
  "research_fields": "[]",
  "disciplines": "[]",
  "papers_published": 0,
  "patents_applied": 0,
  "awards_received": "[]",
  "peer_review_score": null,
  "progress_reports": "[]",
  "contract_number": null,
  "administrative_department": null,
  "contact_person": null,
  "contact_phone": null,
  "id": 2,
  "created_at": "2025-06-20 16:27:15",
  "updated_at": "2025-06-20 16:27:15",
  "is_deleted": 0,
  "deleted_at": null,
  "status": "active",
  "notes": null
}
```


### research_applications 表
数据量: 0 条记录

```json
{
  "application_id": "VARCHAR(20)",  // 必填
  "applicant_id": "VARCHAR(10)",  // 必填
  "project_id": "VARCHAR(20)",
  "application_type": "VARCHAR(20)",  // 必填
  "funding_agency": "VARCHAR(100)",
  "program_name": "VARCHAR(100)",
  "application_title": "VARCHAR(200)",  // 必填
  "application_abstract": "TEXT",
  "research_proposal": "TEXT",
  "budget_plan": "JSON",
  "requested_amount": "NUMERIC(12, 2)",
  "submission_date": "DATE",  // 必填
  "deadline_date": "DATE",
  "review_start_date": "DATE",
  "decision_date": "DATE",
  "application_status": "VARCHAR(20)",
  "review_stage": "VARCHAR(20)",
  "reviewers": "JSON",
  "review_scores": "JSON",
  "review_comments": "TEXT",
  "final_score": "NUMERIC(5, 2)",
  "approval_amount": "NUMERIC(12, 2)",
  "approval_conditions": "TEXT",
  "rejection_reason": "TEXT",
  "supporting_documents": "JSON",
  "cv_attachments": "JSON",
  "id": "INTEGER",  // 自增ID, 主键, 必填
  "created_at": "DATETIME",  // 创建时间, 必填, 默认值:CURRENT_TIMESTAMP
  "updated_at": "DATETIME",  // 更新时间, 必填, 默认值:CURRENT_TIMESTAMP
  "is_deleted": "BOOLEAN",  // 删除标记, 必填
  "deleted_at": "DATETIME",  // 删除时间
  "status": "VARCHAR(20)",  // 状态, 必填
  "is_active": "BOOLEAN",  // 激活状态, 必填
  "notes": "TEXT"  // 备注
}
```

**外键关系:**
- project_id → research_projects.project_id
- applicant_id → persons.employee_id


### paper_library 表
数据量: 5,283 条记录

```json
{
  "paper_id": "VARCHAR(20)",  // 必填
  "title": "VARCHAR(300)",  // 必填
  "title_en": "VARCHAR(500)",
  "first_author_id": "VARCHAR(10)",  // 必填
  "corresponding_author_id": "VARCHAR(10)",
  "all_authors": "JSON",
  "author_affiliations": "JSON",
  "paper_type": "VARCHAR(10)",  // 必填
  "research_field": "VARCHAR(100)",
  "subject_classification": "VARCHAR(100)",
  "journal_name": "VARCHAR(200)",
  "journal_level": "VARCHAR(4)",
  "conference_name": "VARCHAR(200)",
  "publisher": "VARCHAR(100)",
  "publication_date": "DATE",
  "volume": "VARCHAR(20)",
  "issue": "VARCHAR(20)",
  "pages": "VARCHAR(20)",
  "doi": "VARCHAR(100)",
  "issn": "VARCHAR(20)",
  "isbn": "VARCHAR(20)",
  "project_id": "VARCHAR(20)",
  "funding_info": "JSON",
  "abstract": "TEXT",
  "keywords": "JSON",
  "methodology": "TEXT",
  "conclusions": "TEXT",
  "impact_factor": "NUMERIC(6, 3)",
  "citation_count": "INTEGER",
  "download_count": "INTEGER",
  "h_index": "INTEGER",
  "publication_status": "VARCHAR(20)",
  "submission_date": "DATE",
  "acceptance_date": "DATE",
  "is_open_access": "BOOLEAN",
  "access_url": "VARCHAR(300)",
  "pdf_url": "VARCHAR(300)",
  "peer_review_score": "NUMERIC(3, 2)",
  "academic_impact": "VARCHAR(20)",
  "copyright_holder": "VARCHAR(100)",
  "license_type": "VARCHAR(50)",
  "id": "INTEGER",  // 自增ID, 主键, 必填
  "created_at": "DATETIME",  // 创建时间, 必填, 默认值:CURRENT_TIMESTAMP
  "updated_at": "DATETIME",  // 更新时间, 必填, 默认值:CURRENT_TIMESTAMP
  "is_deleted": "BOOLEAN",  // 删除标记, 必填
  "deleted_at": "DATETIME",  // 删除时间
  "status": "VARCHAR(20)",  // 状态, 必填
  "is_active": "BOOLEAN",  // 激活状态, 必填
  "notes": "TEXT"  // 备注
}
```

**外键关系:**
- project_id → research_projects.project_id
- corresponding_author_id → persons.employee_id
- first_author_id → persons.employee_id

**样本数据:**
```json
{
  "paper_id": "PP2025000001",
  "title": "计算机科学相关研究论文",
  "title_en": null,
  "first_author_id": "2025001001",
  "corresponding_author_id": null,
  "all_authors": "[]",
  "author_affiliations": "[]",
  "paper_type": "journal",
  "research_field": null,
  "subject_classification": null,
  "journal_name": "计算机学报",
  "journal_level": "核心",
  "conference_name": null,
  "publisher": null,
  "publication_date": "2024-01-16",
  "volume": null,
  "issue": null,
  "pages": null,
  "doi": null,
  "issn": null,
  "isbn": null,
  "project_id": "RP20250001",
  "funding_info": "[]",
  "abstract": null,
  "keywords": "[]",
  "methodology": null,
  "conclusions": null,
  "impact_factor": null,
  "citation_count": 8,
  "download_count": 0,
  "h_index": null,
  "publication_status": "under_review",
  "submission_date": null,
  "acceptance_date": null,
  "is_open_access": 0,
  "access_url": null,
  "pdf_url": null,
  "peer_review_score": null,
  "academic_impact": null,
  "copyright_holder": null,
  "license_type": null,
  "id": 1,
  "created_at": "2025-06-20 16:27:15",
  "updated_at": "2025-06-20 16:27:15",
  "is_deleted": 0,
  "deleted_at": null,
  "status": "active",
  "is_active": 1,
  "notes": null
}
,
{
  "paper_id": "PP2025000002",
  "title": "计算机科学相关研究论文",
  "title_en": null,
  "first_author_id": "2025001001",
  "corresponding_author_id": null,
  "all_authors": "[]",
  "author_affiliations": "[]",
  "paper_type": "conference",
  "research_field": null,
  "subject_classification": null,
  "journal_name": "软件学报",
  "journal_level": "CSCD",
  "conference_name": null,
  "publisher": null,
  "publication_date": "2024-09-28",
  "volume": null,
  "issue": null,
  "pages": null,
  "doi": null,
  "issn": null,
  "isbn": null,
  "project_id": "RP20250001",
  "funding_info": "[]",
  "abstract": null,
  "keywords": "[]",
  "methodology": null,
  "conclusions": null,
  "impact_factor": null,
  "citation_count": 4,
  "download_count": 0,
  "h_index": null,
  "publication_status": "published",
  "submission_date": null,
  "acceptance_date": null,
  "is_open_access": 0,
  "access_url": null,
  "pdf_url": null,
  "peer_review_score": null,
  "academic_impact": null,
  "copyright_holder": null,
  "license_type": null,
  "id": 2,
  "created_at": "2025-06-20 16:27:15",
  "updated_at": "2025-06-20 16:27:15",
  "is_deleted": 0,
  "deleted_at": null,
  "status": "active",
  "is_active": 1,
  "notes": null
}
```


## 系统管理表

### campus_cards 表
数据量: 63,460 条记录

```json
{
  "card_id": "VARCHAR(20)",  // 必填
  "physical_card_number": "VARCHAR(20)",
  "holder_id": "VARCHAR(20)",  // 必填
  "card_status": "VARCHAR(20)",
  "is_active": "BOOLEAN",  // 激活状态
  "issue_date": "DATE",  // 必填
  "expire_date": "DATE",
  "balance": "NUMERIC(10, 2)",
  "credit_limit": "NUMERIC(10, 2)",
  "available_balance": "NUMERIC(10, 2)",
  "frozen_amount": "NUMERIC(10, 2)",
  "pin_hash": "VARCHAR(128)",
  "pin_attempts": "INTEGER",
  "is_pin_locked": "BOOLEAN",
  "last_pin_change": "DATETIME",
  "daily_limit": "NUMERIC(8, 2)",
  "daily_spent": "NUMERIC(8, 2)",
  "last_spent_date": "DATE",
  "recharge_limit": "NUMERIC(8, 2)",
  "monthly_recharge_limit": "NUMERIC(10, 2)",
  "monthly_recharged": "NUMERIC(10, 2)",
  "total_recharge": "NUMERIC(12, 2)",
  "total_consumption": "NUMERIC(12, 2)",
  "transaction_count": "INTEGER",
  "card_type": "VARCHAR(20)",
  "chip_id": "VARCHAR(50)",
  "last_used_date": "DATETIME",
  "last_used_location": "VARCHAR(50)",
  "is_reported_lost": "BOOLEAN",
  "lost_report_date": "DATETIME",
  "replacement_card_id": "VARCHAR(20)",
  "id": "INTEGER",  // 自增ID, 主键, 必填
  "created_at": "DATETIME",  // 创建时间, 必填, 默认值:CURRENT_TIMESTAMP
  "updated_at": "DATETIME",  // 更新时间, 必填, 默认值:CURRENT_TIMESTAMP
  "is_deleted": "BOOLEAN",  // 删除标记, 必填
  "deleted_at": "DATETIME",  // 删除时间
  "status": "VARCHAR(20)",  // 状态, 必填
  "notes": "TEXT"  // 备注
}
```

**外键关系:**
- holder_id → persons.person_id

**样本数据:**
```json
{
  "card_id": "CC2025000001",
  "physical_card_number": null,
  "holder_id": "P2025000001",
  "card_status": "suspended",
  "is_active": 1,
  "issue_date": "2025-06-21",
  "expire_date": null,
  "balance": 36,
  "credit_limit": 0,
  "available_balance": 0,
  "frozen_amount": 0,
  "pin_hash": null,
  "pin_attempts": 0,
  "is_pin_locked": 0,
  "last_pin_change": null,
  "daily_limit": 997,
  "daily_spent": 0,
  "last_spent_date": null,
  "recharge_limit": 5000,
  "monthly_recharge_limit": 10000,
  "monthly_recharged": 0,
  "total_recharge": 5546,
  "total_consumption": 5688,
  "transaction_count": 0,
  "card_type": "standard",
  "chip_id": null,
  "last_used_date": null,
  "last_used_location": null,
  "is_reported_lost": 0,
  "lost_report_date": null,
  "replacement_card_id": null,
  "id": 1,
  "created_at": "2025-06-20 16:04:21",
  "updated_at": "2025-06-20 16:04:21",
  "is_deleted": 0,
  "deleted_at": null,
  "status": "active",
  "notes": null
}
,
{
  "card_id": "CC2025000002",
  "physical_card_number": null,
  "holder_id": "P2025000002",
  "card_status": "suspended",
  "is_active": 1,
  "issue_date": "2025-06-21",
  "expire_date": null,
  "balance": 632,
  "credit_limit": 0,
  "available_balance": 0,
  "frozen_amount": 0,
  "pin_hash": null,
  "pin_attempts": 0,
  "is_pin_locked": 0,
  "last_pin_change": null,
  "daily_limit": 409,
  "daily_spent": 0,
  "last_spent_date": null,
  "recharge_limit": 5000,
  "monthly_recharge_limit": 10000,
  "monthly_recharged": 0,
  "total_recharge": 6392,
  "total_consumption": 2819,
  "transaction_count": 0,
  "card_type": "standard",
  "chip_id": null,
  "last_used_date": null,
  "last_used_location": null,
  "is_reported_lost": 0,
  "lost_report_date": null,
  "replacement_card_id": null,
  "id": 2,
  "created_at": "2025-06-20 16:04:21",
  "updated_at": "2025-06-20 16:04:21",
  "is_deleted": 0,
  "deleted_at": null,
  "status": "active",
  "notes": null
}
```


### network_permissions 表
数据量: 126,920 条记录

```json
{
  "permission_id": "VARCHAR(20)",  // 必填
  "person_id": "VARCHAR(20)",  // 人员ID, 必填
  "network_type": "VARCHAR(17)",  // 必填
  "username": "VARCHAR(50)",  // 必填
  "password_hash": "VARCHAR(128)",
  "max_devices": "INTEGER",
  "current_devices": "INTEGER",
  "monthly_quota_mb": "INTEGER",
  "used_quota_mb": "INTEGER",
  "daily_quota_mb": "INTEGER",
  "daily_used_mb": "INTEGER",
  "access_start_time": "VARCHAR(8)",
  "access_end_time": "VARCHAR(8)",
  "weekend_access": "BOOLEAN",
  "allowed_ip_ranges": "JSON",
  "blocked_websites": "JSON",
  "allowed_applications": "JSON",
  "provider": "VARCHAR(20)",  // 必填
  "package_type": "VARCHAR(20)",
  "monthly_fee": "NUMERIC(8, 2)",
  "permission_status": "VARCHAR(20)",
  "activation_date": "DATE",
  "expiration_date": "DATE",
  "last_login_time": "DATETIME",
  "total_online_hours": "INTEGER",
  "login_count": "INTEGER",
  "id": "INTEGER",  // 自增ID, 主键, 必填
  "created_at": "DATETIME",  // 创建时间, 必填, 默认值:CURRENT_TIMESTAMP
  "updated_at": "DATETIME",  // 更新时间, 必填, 默认值:CURRENT_TIMESTAMP
  "is_deleted": "BOOLEAN",  // 删除标记, 必填
  "deleted_at": "DATETIME",  // 删除时间
  "status": "VARCHAR(20)",  // 状态, 必填
  "is_active": "BOOLEAN",  // 激活状态, 必填
  "notes": "TEXT"  // 备注
}
```

**外键关系:**
- person_id → persons.person_id

**样本数据:**
```json
{
  "permission_id": "NP2025000001CAMP",
  "person_id": "P2025000001",
  "network_type": "campus_wifi",
  "username": "202100000001",
  "password_hash": null,
  "max_devices": 3,
  "current_devices": 0,
  "monthly_quota_mb": 50000,
  "used_quota_mb": 6432,
  "daily_quota_mb": 2000,
  "daily_used_mb": 0,
  "access_start_time": "00:00:00",
  "access_end_time": "23:59:59",
  "weekend_access": 1,
  "allowed_ip_ranges": "[]",
  "blocked_websites": "[]",
  "allowed_applications": "[]",
  "provider": "中国联通",
  "package_type": "basic",
  "monthly_fee": 0,
  "permission_status": "active",
  "activation_date": null,
  "expiration_date": null,
  "last_login_time": null,
  "total_online_hours": 0,
  "login_count": 0,
  "id": 1,
  "created_at": "2025-06-20 16:27:15",
  "updated_at": "2025-06-20 16:27:15",
  "is_deleted": 0,
  "deleted_at": null,
  "status": "active",
  "is_active": 1,
  "notes": null
}
,
{
  "permission_id": "NP2025000001DORM",
  "person_id": "P2025000001",
  "network_type": "dormitory_network",
  "username": "202100000001",
  "password_hash": null,
  "max_devices": 3,
  "current_devices": 1,
  "monthly_quota_mb": 50000,
  "used_quota_mb": 18978,
  "daily_quota_mb": 2000,
  "daily_used_mb": 0,
  "access_start_time": "00:00:00",
  "access_end_time": "23:59:59",
  "weekend_access": 1,
  "allowed_ip_ranges": "[]",
  "blocked_websites": "[]",
  "allowed_applications": "[]",
  "provider": "中国联通",
  "package_type": "basic",
  "monthly_fee": 0,
  "permission_status": "active",
  "activation_date": null,
  "expiration_date": null,
  "last_login_time": null,
  "total_online_hours": 0,
  "login_count": 0,
  "id": 2,
  "created_at": "2025-06-20 16:27:15",
  "updated_at": "2025-06-20 16:27:15",
  "is_deleted": 0,
  "deleted_at": null,
  "status": "active",
  "is_active": 1,
  "notes": null
}
```


### system_access 表
数据量: 126,920 条记录

```json
{
  "access_id": "VARCHAR(20)",  // 必填
  "person_id": "VARCHAR(20)",  // 人员ID, 必填
  "system_code": "VARCHAR(3)",  // 必填
  "system_name": "VARCHAR(50)",  // 必填
  "system_username": "VARCHAR(50)",  // 必填
  "password_hash": "VARCHAR(128)",
  "access_level": "VARCHAR(20)",
  "role_permissions": "JSON",
  "platform_configs": "JSON",
  "max_concurrent_sessions": "INTEGER",
  "current_sessions": "INTEGER",
  "access_start_date": "DATE",
  "access_end_date": "DATE",
  "daily_access_hours": "INTEGER",
  "access_status": "VARCHAR(20)",
  "is_locked": "BOOLEAN",
  "lock_reason": "VARCHAR(200)",
  "approved_by": "VARCHAR(10)",
  "approval_date": "DATE",
  "approval_notes": "TEXT",
  "last_access_time": "DATETIME",
  "total_access_count": "INTEGER",
  "failed_login_attempts": "INTEGER",
  "two_factor_enabled": "BOOLEAN",
  "ip_restrictions": "JSON",
  "device_binding": "BOOLEAN",
  "id": "INTEGER",  // 自增ID, 主键, 必填
  "created_at": "DATETIME",  // 创建时间, 必填, 默认值:CURRENT_TIMESTAMP
  "updated_at": "DATETIME",  // 更新时间, 必填, 默认值:CURRENT_TIMESTAMP
  "is_deleted": "BOOLEAN",  // 删除标记, 必填
  "deleted_at": "DATETIME",  // 删除时间
  "status": "VARCHAR(20)",  // 状态, 必填
  "is_active": "BOOLEAN",  // 激活状态, 必填
  "notes": "TEXT"  // 备注
}
```

**外键关系:**
- approved_by → persons.employee_id
- person_id → persons.person_id

**样本数据:**
```json
{
  "access_id": "SA2025000001EMS",
  "person_id": "P2025000001",
  "system_code": "EMS",
  "system_name": "教务管理系统",
  "system_username": "202100000001",
  "password_hash": null,
  "access_level": "user",
  "role_permissions": "[]",
  "platform_configs": "{}",
  "max_concurrent_sessions": 1,
  "current_sessions": 0,
  "access_start_date": null,
  "access_end_date": null,
  "daily_access_hours": 24,
  "access_status": "active",
  "is_locked": 0,
  "lock_reason": null,
  "approved_by": null,
  "approval_date": null,
  "approval_notes": null,
  "last_access_time": null,
  "total_access_count": 0,
  "failed_login_attempts": 0,
  "two_factor_enabled": 0,
  "ip_restrictions": "[]",
  "device_binding": 0,
  "id": 1,
  "created_at": "2025-06-20 16:27:20",
  "updated_at": "2025-06-20 16:27:20",
  "is_deleted": 0,
  "deleted_at": null,
  "status": "active",
  "is_active": 1,
  "notes": null
}
,
{
  "access_id": "SA2025000001LMS",
  "person_id": "P2025000001",
  "system_code": "LMS",
  "system_name": "图书馆管理系统",
  "system_username": "202100000001",
  "password_hash": null,
  "access_level": "user",
  "role_permissions": "[]",
  "platform_configs": "{}",
  "max_concurrent_sessions": 1,
  "current_sessions": 0,
  "access_start_date": null,
  "access_end_date": null,
  "daily_access_hours": 24,
  "access_status": "active",
  "is_locked": 0,
  "lock_reason": null,
  "approved_by": null,
  "approval_date": null,
  "approval_notes": null,
  "last_access_time": null,
  "total_access_count": 0,
  "failed_login_attempts": 0,
  "two_factor_enabled": 0,
  "ip_restrictions": "[]",
  "device_binding": 0,
  "id": 2,
  "created_at": "2025-06-20 16:27:20",
  "updated_at": "2025-06-20 16:27:20",
  "is_deleted": 0,
  "deleted_at": null,
  "status": "active",
  "is_active": 1,
  "notes": null
}
```


### platform_configs 表
数据量: 191,400 条记录

```json
{
  "config_id": "VARCHAR(20)",  // 必填
  "person_id": "VARCHAR(20)",  // 人员ID, 必填
  "platform_name": "VARCHAR(50)",  // 必填
  "platform_type": "VARCHAR(20)",  // 必填
  "platform_url": "VARCHAR(200)",
  "auth_method": "VARCHAR(20)",
  "sso_enabled": "BOOLEAN",
  "oauth_config": "JSON",
  "permission_mapping": "JSON",
  "role_mapping": "JSON",
  "session_timeout": "INTEGER",
  "max_idle_time": "INTEGER",
  "remember_me_duration": "INTEGER",
  "force_password_change": "BOOLEAN",
  "password_policy": "JSON",
  "login_retry_limit": "INTEGER",
  "config_status": "VARCHAR(20)",
  "last_sync_time": "DATETIME",
  "id": "INTEGER",  // 自增ID, 主键, 必填
  "created_at": "DATETIME",  // 创建时间, 必填, 默认值:CURRENT_TIMESTAMP
  "updated_at": "DATETIME",  // 更新时间, 必填, 默认值:CURRENT_TIMESTAMP
  "is_deleted": "BOOLEAN",  // 删除标记, 必填
  "deleted_at": "DATETIME",  // 删除时间
  "status": "VARCHAR(20)",  // 状态, 必填
  "is_active": "BOOLEAN",  // 激活状态, 必填
  "notes": "TEXT"  // 备注
}
```

**外键关系:**
- person_id → persons.person_id

**样本数据:**
```json
{
  "config_id": "PC2025000001",
  "person_id": "P2025063441",
  "platform_name": "管理员系统",
  "platform_type": "admin_portal",
  "platform_url": "https://admin.sztu.edu.cn",
  "auth_method": "password",
  "sso_enabled": 0,
  "oauth_config": "{\"enabled\": false, \"reason\": \"Platform uses traditional authentication\"}",
  "permission_mapping": "{\"read\": [\"*\"], \"write\": [\"user_management\", \"system_config\", \"policy_management\", \"all_announcement...",
  "role_mapping": "{\"primary_role\": \"system_administrator\", \"secondary_roles\": [\"user_manager\", \"policy_maker\"], \"role_...",
  "session_timeout": 3022,
  "max_idle_time": 934,
  "remember_me_duration": 2097872,
  "force_password_change": "****",
  "password_policy": "****",
  "login_retry_limit": 5,
  "config_status": "active",
  "last_sync_time": "2025-06-19 14:29:30.754604",
  "id": 1,
  "created_at": "2025-06-21 06:29:30",
  "updated_at": "2025-06-21 06:29:30",
  "is_deleted": 0,
  "deleted_at": null,
  "status": "active",
  "is_active": 1,
  "notes": "何平的管理员系统配置"
}
,
{
  "config_id": "PC2025000002",
  "person_id": "P2025063441",
  "platform_name": "图书馆系统",
  "platform_type": "library_system",
  "platform_url": "https://lib.sztu.edu.cn",
  "auth_method": "sso",
  "sso_enabled": 1,
  "oauth_config": "{\"client_id\": \"sztu_library_system_client\", \"scope\": [\"openid\", \"profile\", \"email\"], \"redirect_uri\":...",
  "permission_mapping": "{\"read\": [\"public_info\"], \"write\": [\"own_profile\"], \"share\": [\"contact_info\"], \"features\": [\"basic_a...",
  "role_mapping": "{\"primary_role\": \"system_administrator\", \"secondary_roles\": [\"user_manager\", \"policy_maker\"], \"role_...",
  "session_timeout": 7030,
  "max_idle_time": 2318,
  "remember_me_duration": 639693,
  "force_password_change": "****",
  "password_policy": "****",
  "login_retry_limit": 7,
  "config_status": "active",
  "last_sync_time": "2025-05-27 14:29:30.754604",
  "id": 2,
  "created_at": "2025-06-21 06:29:30",
  "updated_at": "2025-06-21 06:29:30",
  "is_deleted": 0,
  "deleted_at": null,
  "status": "active",
  "is_active": 1,
  "notes": "何平的图书馆系统配置"
}
```


### user_reading_records 表
数据量: 0 条记录

```json
{
  "id": "INTEGER",  // 自增ID, 主键
  "record_id": "VARCHAR(20)",  // 必填
  "user_id": "VARCHAR(20)",  // 必填
  "content_type": "VARCHAR(20)",  // 必填
  "content_id": "VARCHAR(20)",  // 必填
  "first_read_time": "DATETIME",  // 默认值:CURRENT_TIMESTAMP
  "last_read_time": "DATETIME",  // 默认值:CURRENT_TIMESTAMP
  "read_count": "INTEGER",  // 默认值:1
  "read_duration": "INTEGER",  // 默认值:0
  "is_liked": "BOOLEAN",  // 默认值:FALSE
  "is_bookmarked": "BOOLEAN",  // 默认值:FALSE
  "is_shared": "BOOLEAN",  // 默认值:FALSE
  "created_at": "DATETIME",  // 创建时间, 默认值:CURRENT_TIMESTAMP
  "updated_at": "DATETIME"  // 更新时间, 默认值:CURRENT_TIMESTAMP
}
```

**外键关系:**
- user_id → persons.person_id


### device_registrations 表
数据量: 0 条记录

```json
{
  "registration_id": "VARCHAR(20)",  // 必填
  "person_id": "VARCHAR(20)",  // 人员ID, 必填
  "network_permission_id": "VARCHAR(20)",
  "device_type": "VARCHAR(7)",  // 必填
  "device_name": "VARCHAR(100)",  // 必填
  "device_model": "VARCHAR(50)",
  "mac_address": "VARCHAR(20)",  // 必填
  "ip_address": "VARCHAR(50)",
  "dns_settings": "JSON",
  "registration_status": "VARCHAR(20)",
  "registration_date": "DATETIME",  // 必填
  "last_online_time": "DATETIME",
  "total_online_hours": "INTEGER",
  "data_usage_mb": "INTEGER",
  "id": "INTEGER",  // 自增ID, 主键, 必填
  "created_at": "DATETIME",  // 创建时间, 必填, 默认值:CURRENT_TIMESTAMP
  "updated_at": "DATETIME",  // 更新时间, 必填, 默认值:CURRENT_TIMESTAMP
  "is_deleted": "BOOLEAN",  // 删除标记, 必填
  "deleted_at": "DATETIME",  // 删除时间
  "status": "VARCHAR(20)",  // 状态, 必填
  "is_active": "BOOLEAN",  // 激活状态, 必填
  "notes": "TEXT"  // 备注
}
```

**外键关系:**
- network_permission_id → network_permissions.permission_id
- person_id → persons.person_id


### audit_logs 表
数据量: 0 条记录

```json
{
  "log_id": "VARCHAR(30)",  // 必填
  "person_id": "VARCHAR(20)",  // 人员ID
  "operation_type": "VARCHAR(20)",  // 必填
  "operation_description": "VARCHAR(200)",  // 必填
  "system_code": "VARCHAR(10)",
  "module_name": "VARCHAR(50)",
  "function_name": "VARCHAR(50)",
  "operation_time": "DATETIME",  // 必填
  "ip_address": "VARCHAR(50)",
  "user_agent": "VARCHAR(200)",
  "session_id": "VARCHAR(50)",
  "operation_result": "VARCHAR(20)",
  "error_message": "TEXT",
  "before_data": "JSON",
  "after_data": "JSON",
  "operation_params": "JSON",
  "risk_level": "VARCHAR(20)",
  "is_sensitive": "BOOLEAN",
  "id": "INTEGER",  // 自增ID, 主键, 必填
  "created_at": "DATETIME",  // 创建时间, 必填, 默认值:CURRENT_TIMESTAMP
  "updated_at": "DATETIME",  // 更新时间, 必填, 默认值:CURRENT_TIMESTAMP
  "is_deleted": "BOOLEAN",  // 删除标记, 必填
  "deleted_at": "DATETIME",  // 删除时间
  "status": "VARCHAR(20)",  // 状态, 必填
  "is_active": "BOOLEAN",  // 激活状态, 必填
  "notes": "TEXT"  // 备注
}
```

**外键关系:**
- person_id → persons.person_id


### workflow_instances 表
数据量: 0 条记录

```json
{
  "instance_id": "VARCHAR(20)",  // 必填
  "workflow_name": "VARCHAR(50)",  // 必填
  "workflow_version": "VARCHAR(10)",
  "applicant_id": "VARCHAR(20)",  // 必填
  "application_data": "JSON",  // 必填
  "current_step": "VARCHAR(50)",  // 必填
  "workflow_status": "VARCHAR(20)",
  "start_time": "DATETIME",  // 必填
  "end_time": "DATETIME",
  "approval_history": "JSON",
  "current_approvers": "JSON",
  "final_result": "VARCHAR(20)",
  "result_comments": "TEXT",
  "id": "INTEGER",  // 自增ID, 主键, 必填
  "created_at": "DATETIME",  // 创建时间, 必填, 默认值:CURRENT_TIMESTAMP
  "updated_at": "DATETIME",  // 更新时间, 必填, 默认值:CURRENT_TIMESTAMP
  "is_deleted": "BOOLEAN",  // 删除标记, 必填
  "deleted_at": "DATETIME",  // 删除时间
  "status": "VARCHAR(20)",  // 状态, 必填
  "is_active": "BOOLEAN",  // 激活状态, 必填
  "notes": "TEXT"  // 备注
}
```

**外键关系:**
- applicant_id → persons.person_id

