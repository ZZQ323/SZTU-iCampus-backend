# SZTU-iCampus 数据模型与API设计

## 编号系统设计

### 1. 学院编码 (College Code)
```
C001 - 计算机学院 (CS)
C002 - 数学与统计学院 (MATH)  
C003 - 物理与光电工程学院 (PHY)
C004 - 化学与生物工程学院 (CBE)
C005 - 材料科学与工程学院 (MSE)
C006 - 机械设计制造及其自动化学院 (ME)
C007 - 电子与信息工程学院 (EIE)
C008 - 经济管理学院 (EM)
C009 - 外国语学院 (FL)
C010 - 人文社会科学学院 (HSS)
C011 - 艺术设计学院 (AD)
C012 - 医学院 (MED)
C013 - 生命健康学院 (LH)
```

### 2. 专业编码系统 (Major Code)
基于国标专业代码+学院特色编码：

#### 基础学科类
```
080100 - 数学与应用数学
080200 - 信息与计算科学  
080300 - 统计学
070100 - 物理学
070200 - 应用物理学
070300 - 化学
070400 - 应用化学
071000 - 生物科学
071001 - 生物技术
```

#### 理工类
```
080901 - 计算机科学与技术
080902 - 软件工程
080903 - 网络工程
080904 - 信息安全
080905 - 物联网工程
080906 - 数字媒体技术
081001 - 电子信息工程
081002 - 通信工程
081003 - 电子科学与技术
082801 - 机械工程
082802 - 机械设计制造及其自动化
082803 - 材料成型及控制工程
```

#### 经济管理类
```
120100 - 工商管理
120200 - 市场营销
120300 - 会计学
120400 - 财务管理
120500 - 国际经济与贸易
120600 - 金融学
120700 - 经济学
```

#### 语言文化类
```
050101 - 英语
050102 - 日语
050103 - 德语
050201 - 汉语言文学
050301 - 新闻学
050302 - 传播学
130400 - 视觉传达设计
130500 - 产品设计
```

### 3. 学生学号编码规则
格式：`年份(4位) + 专业编码(4位) + 班级号(2位) + 学生序号(2位)`

示例：
```
202408090101 - 2024年软件工程专业1班第1号学生
202408090102 - 2024年软件工程专业1班第2号学生
202408090201 - 2024年软件工程专业2班第1号学生
202412010301 - 2024年工商管理专业3班第1号学生
```

### 4. 教职工工号编码
格式：`入职年份(4位) + 专业编号(4位) + 序号(2位)`

示例：
```
202408900101 - 2024年入职软件工程专业第1号教师
202408900102 - 2024年入职软件工程专业第2号教师  
202412010001 - 2024年入职工商管理专业第1号教师
202200010001 - 2022年入职数学专业第1号教师
```

### 5. 建筑与教室编码
```
建筑编码：
C1-C5 - 教学楼群C区（计算机、理工类）
D1-D3 - 教学楼群D区（经管、人文类）  
E0-E3 - 实验楼群E区（实验室、研究中心）
B0-B2 - 办公楼群B区（行政办公）
L1-L3 - 图书馆区域
F1-F5 - 食堂区域
S1-S10 - 宿舍楼群

教室编码：建筑编码 + 楼层(1位) + 房间号(2位)
示例：C1-101, C1-302, D2-201, E1-105
```

## 参数范围说明

### 枚举值定义

#### 人员类型 (person_type)
```
student - 学生
teacher - 教师  
assistant_teacher - 助教
counselor - 辅导员
class_advisor - 班主任
department_head - 部门主管
dean - 院长
major_director - 专业主任
admin - 系统管理员
security - 保卫人员
librarian - 图书管理员
```

#### 性别 (gender)
```
male - 男
female - 女
other - 其他
```

#### 学籍状态 (academic_status)
```
active - 在读
suspended - 休学
graduated - 已毕业
dropout - 退学
transfer_in - 转入
transfer_out - 转出
```

#### 就职状态 (employment_status)
```
active - 在职
probation - 试用期
leave - 请假
retired - 退休
resigned - 离职
transfer - 调动
```

#### 课程类型 (course_type)
```
required - 必修课
elective - 选修课
practice - 实践课
experiment - 实验课
thesis - 毕业设计
internship - 实习
```

#### 考试形式 (exam_form)
```
closed_book - 闭卷考试
open_book - 开卷考试
online - 在线考试
oral - 口试
presentation - 答辩
project - 项目作业
```

#### 成绩等第 (grade_level)
```
A - 优秀 (90-100分)
B - 良好 (80-89分)  
C - 中等 (70-79分)
D - 及格 (60-69分)
E - 不及格 (0-59分)
F - 缺考
P - 通过 (Pass，用于实践课)
NP - 不通过 (Not Pass)
```

#### 资产状态 (asset_status)
```
in_use - 使用中
maintenance - 维修中
idle - 闲置
scrapped - 已报废
lost - 丢失
```

#### 教室类型 (room_type)
```
classroom - 普通教室
lab - 实验室
computer_lab - 机房
language_lab - 语音室
multimedia - 多媒体教室
lecture_hall - 阶梯教室
office - 办公室
conference - 会议室
library - 图书馆
canteen - 食堂
dormitory - 宿舍
gym - 体育馆
```

## 核心实体关系分析

### 1. 人员实体 (Person)
```json
{
  "person_id": "P2024001",           // 统一人员ID，格式：P+年份+序号
  "person_type": "student",         // 枚举：见上述人员类型
  "student_id": "202408090101",     // 学号（学生专用），格式见编码规则
  "employee_id": "T2024C01001",     // 工号（教职工专用），格式见编码规则
  "name": "张三",                   // 真实姓名，长度1-50字符
  "gender": "male",                 // 枚举：male/female/other
  "id_card": "440***199901010001",  // 身份证（脱敏），显示前3位和后4位
  "phone": "138****1234",           // 联系电话（脱敏），显示前3位和后4位
  "email": "zhangsan@sztu.edu.cn",  // 邮箱，必须@sztu.edu.cn结尾
  "wechat_openid": "ox1234567890",  // 微信OpenID，28位字符串
  
  // 时间属性（ISO 8601格式）
  "admission_date": "2024-09-01",   // 入学时间（学生），格式YYYY-MM-DD
  "employment_date": "2020-08-01",  // 入职时间（教职工）
  "graduation_date": "2028-06-30",  // 预计毕业时间
  
  // 状态属性
  "academic_status": "active",      // 枚举：见上述学籍状态
  "employment_status": "active",    // 枚举：见上述就职状态
  
  // 权限属性（数组，可多选）
  "permissions": {
    "read": ["own_data", "public_announcements"],   // 可读权限列表
    "write": ["own_profile"],                       // 可写权限列表
    "share": ["schedule", "contacts"]               // 可分享权限列表
  },
  
  // 关联属性（外键）
  "college_id": "C001",             // 所属学院，关联colleges表
  "major_id": "M001",               // 所属专业，关联majors表
  "department_id": "D001",          // 所属部门，关联departments表
  "class_id": "CL2024001",          // 所属班级，关联classes表
  
  "notes": "备注信息",               // 文本，最大1000字符
  "created_at": "2024-01-01T10:00:00Z",    // 创建时间，ISO 8601格式
  "updated_at": "2024-01-01T10:00:00Z"     // 更新时间，ISO 8601格式
}
```

### 2. 班级实体 (Class)
```json
{
  "class_id": "CL2024001",          // 班级ID，格式：CL+年份+序号
  "class_name": "软工2024-1班",      // 班级名称
  "class_code": "SE2024-01",        // 班级代码
  "grade": 2024,                    // 年级，4位数字
  "semester_enrolled": "2024-2025-1", // 入学学期
  
  // 关联信息
  "major_id": "M001",               // 所属专业
  "college_id": "C001",             // 所属学院
  
  // 人员配置
  "class_advisor_id": "T2023C01005", // 班主任（教师）
  "counselor_id": "T2023D01002",      // 辅导员
  
  // 班级统计
  "total_students": 35,             // 总学生数，1-50
  "male_count": 20,                 // 男生人数
  "female_count": 15,               // 女生人数
  
  // 班级状态
  "status": "active",               // active/graduated/disbanded
  "graduation_date": "2028-06-30",  // 预计毕业时间
  
  "notes": "班级备注信息",
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": "2024-01-01T10:00:00Z"
}
```

### 3. 场所占用实体 (Room_Occupation)
```json
{
  "occupation_id": "RO2024001",     // 占用记录ID
  "location_id": "L001",            // 场所ID，关联locations表
  "occupation_type": "class",       // 占用类型：class/exam/meeting/maintenance/event
  
  // 时间信息
  "date": "2024-03-15",            // 占用日期，YYYY-MM-DD
  "start_time": "08:30",           // 开始时间，HH:MM
  "end_time": "10:10",             // 结束时间，HH:MM
  "duration_minutes": 100,          // 持续时长（分钟），1-480
  
  // 关联信息
  "course_instance_id": "CI2024001", // 课程实例（如果是上课）
  "exam_id": "E2024001",             // 考试ID（如果是考试）
  "event_id": "EV2024001",           // 活动ID（如果是活动）
  
  // 申请信息
  "applicant_id": "T2024C01001",     // 申请人ID
  "application_reason": "高等数学A课程教学", // 申请原因
  "approved_by": "T2023C01001",      // 审批人ID
  "approval_time": "2024-03-10T14:30:00Z", // 审批时间
  
  // 状态信息
  "status": "confirmed",            // pending/confirmed/cancelled/completed
  "attendance_count": 58,           // 实际出席人数，0-教室容量
  
  // 设备使用
  "equipment_used": ["projector", "microphone"], // 使用的设备列表
  "equipment_status": "normal",     // normal/malfunction/missing
  
  "notes": "使用备注",
  "created_at": "2024-03-10T14:30:00Z",
  "updated_at": "2024-03-15T10:10:00Z"
}
```

### 4. 组织架构实体

#### 学院 (College)
```json
{
  "college_id": "C001",             // 学院ID，格式：C+3位数字
  "college_code": "CS",             // 学院代码，2-5个字符
  "college_name": "计算机学院",      // 学院全称，最大50字符
  "college_name_en": "School of Computer Science", // 英文名称
  "dean_id": "T2020001",            // 院长人员ID，关联persons表
  "vice_dean_ids": ["T2021001", "T2021002"], // 副院长列表
  
  // 物理位置
  "building_codes": ["C1", "C2"],   // 主要办公教学楼列表
  "main_office_location": "C1-301", // 院办公室位置
  
  // 联系信息
  "contact_phone": "0755-12345678", // 联系电话，格式：区号-电话号码
  "contact_email": "cs@sztu.edu.cn", // 联系邮箱
  "website": "https://cs.sztu.edu.cn", // 学院网站
  
  // 历史信息
  "established_date": "2016-01-01", // 成立日期
  "history": "学院发展历程简介",     // 历史沿革，最大2000字符
  
  // 统计信息
  "faculty_count": 120,             // 教职工数量，1-500
  "student_count": 2800,            // 学生总数，1-10000
  "major_count": 8,                 // 专业数量，1-20
  
  "status": "active"                // active/merged/closed
}
```

#### 专业 (Major)  
```json
{
  "major_id": "M001",               // 专业ID，格式：M+3位数字
  "major_code": "080902",           // 国标专业代码，6位数字
  "major_name": "软件工程",          // 专业名称
  "major_name_en": "Software Engineering", // 英文名称
  "college_id": "C001",             // 所属学院
  "major_director_id": "T2021001",  // 专业主任
  
  // 学位信息
  "degree_type": "bachelor",        // bachelor/master/doctor
  "degree_name": "工学学士",         // 学位名称
  "duration_years": 4,              // 学制年限，1-8年
  "total_credits": 160,             // 总学分要求，60-300
  
  // 课程要求
  "required_credits": 120,          // 必修课学分，30-200
  "elective_credits": 25,           // 选修课学分，10-100
  "practice_credits": 15,           // 实践课学分，5-50
  
  // 招生信息
  "enrollment_quota": 120,          // 年度招生计划，10-300
  "current_students": 480,          // 在校学生数
  
  // 专业特色
  "features": ["软件开发", "系统架构", "项目管理"], // 专业特色列表
  "career_prospects": "软件开发工程师、系统架构师等", // 就业前景
  
  "status": "active",               // active/suspended/closed
  "accreditation": "工程教育认证",   // 专业认证情况
  "ranking": "省级一流专业",         // 专业排名/等级
  
  "established_date": "2016-09-01",
  "last_review_date": "2023-06-30" // 最近评估时间
}
```

#### 部门 (Department)
```json
{
  "department_id": "D001",          // 部门ID，格式：D+3位数字
  "department_name": "教务处",       // 部门名称
  "department_type": "administrative", // administrative/academic/service
  "level": 1,                       // 部门级别，1-5（1为最高级）
  
  // 人员配置
  "head_id": "T2019001",            // 部门主管
  "deputy_head_ids": ["T2020001"],  // 副主管列表
  "staff_count": 15,                // 部门人员数量
  
  // 组织结构
  "parent_department_id": null,     // 上级部门，null表示顶级部门
  "sub_departments": ["D001001", "D001002"], // 下级部门列表
  
  // 办公位置
  "building_code": "B1",            // 办公楼编码
  "floor": 1,                       // 楼层，1-20
  "room_numbers": ["101", "102"],   // 办公室房间号列表
  
  // 职能描述
  "functions": ["学籍管理", "课程安排", "考试组织"], // 主要职能
  "responsibilities": "负责全校教学管理工作", // 职责描述
  
  // 服务信息
  "service_hours": "08:30-17:30",   // 服务时间
  "contact_phone": "0755-26731000", // 联系电话
  "service_phone": "0755-26731001", // 服务热线
  
  "budget_annual": 2000000.00,      // 年度预算，单位：元
  "established_date": "2016-01-01"
}
```

### 5. 场所实体 (Location)
```json
{
  "location_id": "L001",
  "building_code": "C1",             // C1-C5, D1-D3, E0-E3, B0-B2
  "building_name": "计算机学院1号楼",
  "room_number": "101",
  "room_type": "classroom",          // classroom/office/lab/library/canteen
  "capacity": 60,
  "facilities": ["projector", "whiteboard", "air_conditioner"],
  "college_id": "C001",              // 主要使用学院
  "status": "active"                 // active/maintenance/closed
}
```

### 6. 课程体系

#### 课程 (Course)
```json
{
  "course_id": "MATH001",           // 课程ID，英文+数字
  "course_code": "080901001",       // 课程代码，与专业相关
  "course_name": "高等数学A",        // 课程名称
  "course_name_en": "Advanced Mathematics A", // 英文名称
  
  // 课程属性
  "course_type": "required",        // required/elective/practice/experiment
  "course_category": "基础课",       // 基础课/专业课/通识课/实践课
  "credits": 4,                     // 学分，0.5-10，步长0.5
  "total_hours": 64,                // 总学时，16-200
  "theory_hours": 56,               // 理论学时，0-200
  "practice_hours": 8,              // 实践学时，0-100
  "experiment_hours": 0,            // 实验学时，0-100
  
  // 开课信息
  "college_id": "C002",             // 开课学院
  "department_id": "D002",          // 开课部门
  "major_ids": ["M001", "M002"],    // 适用专业列表
  "semester_offered": [1, 2],       // 开课学期，1-8
  
  // 课程要求
  "prerequisites": ["MATH_FOUNDATION"], // 先修课程列表
  "corequisites": [],               // 同修课程列表
  "difficulty_level": 3,            // 难度等级，1-5
  "workload_level": 4,              // 工作量等级，1-5
  
  // 教学信息
  "teaching_methods": ["lecture", "practice", "discussion"], // 教学方法
  "assessment_methods": ["exam", "homework", "project"],     // 考核方式
  "textbooks": [                    // 教材信息
    {
      "title": "高等数学(第七版)",
      "author": "同济大学数学系",
      "publisher": "高等教育出版社",
      "isbn": "9787040396638",
      "is_required": true
    }
  ],
  
  // 课程描述
  "description": "高等数学基础课程，涵盖微积分基本理论", // 课程简介
  "objectives": ["掌握微积分基本概念", "培养逻辑思维能力"], // 教学目标
  "learning_outcomes": ["能够进行函数极限计算"], // 学习成果
  
  "status": "active",               // active/suspended/obsolete
  "approval_date": "2023-06-01",    // 课程审批日期
  "last_update": "2024-01-01"       // 最近更新日期
}
```

#### 开课实例 (Course_Instance)
```json
{
  "instance_id": "CI2024001",       // 开课实例ID，格式：CI+年份+序号
  "course_id": "MATH001",           // 关联课程
  "semester": "2024-2025-1",        // 开课学期
  "academic_year": "2024-2025",     // 学年
  "term": 1,                        // 学期，1-2
  
  // 教学人员
  "teacher_id": "T2022001",         // 主讲教师
  "assistant_ids": ["T2023001"],    // 助教列表
  "substitute_teacher_id": null,    // 代课教师
  
  // 学生信息
  "class_ids": ["CL2024001"],       // 上课班级列表
  "max_students": 60,               // 最大容量，10-300
  "enrolled_students": 58,          // 已选课人数
  "waitlist_count": 5,              // 候补人数
  
  // 时间安排
  "schedule": [
    {
      "weekday": 1,                 // 星期，1-7（周一到周日）
      "start_slot": 1,              // 开始节次，1-5
      "end_slot": 2,                // 结束节次，1-5
      "start_time": "08:30",        // 开始时间，HH:MM
      "end_time": "10:10",          // 结束时间，HH:MM
      "location_id": "L001",        // 上课地点
      "weeks": "1-16",              // 上课周次
      "week_type": "all"            // all/odd/even
    }
  ],
  
  // 考试安排
  "exam": {
    "exam_id": "E2024001",          // 考试ID
    "exam_type": "final",           // midterm/final/makeup
    "exam_date": "2024-01-15",      // 考试日期
    "start_time": "14:30",          // 开始时间
    "end_time": "16:30",            // 结束时间
    "duration_minutes": 120,        // 考试时长，30-300分钟
    "location_id": "L002",          // 考试地点
    "exam_form": "closed_book",     // 考试形式
    "total_score": 100,             // 总分，50-150
    "pass_score": 60                // 及格分，30-90
  },
  
  // 成绩组成
  "grade_composition": {
    "attendance": 10,               // 出勤占比，0-30%
    "homework": 20,                 // 作业占比，0-50%
    "midterm": 30,                  // 期中占比，0-50%
    "final": 40                     // 期末占比，30-100%
  },
  
  // 课程状态
  "status": "ongoing",              // planning/ongoing/completed/cancelled
  "enrollment_status": "open",      // open/closed/full
  
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": "2024-01-01T10:00:00Z"
}
```

### 7. 成绩体系

#### 成绩记录 (Grade)
```json
{
  "grade_id": "G2024001",           // 成绩记录ID，格式：G+年份+序号
  "student_id": "202408090101",     // 学生学号
  "instance_id": "CI2024001",       // 开课实例ID
  "semester": "2024-2025-1",        // 学期
  "academic_year": "2024-2025",     // 学年
  
  // 成绩详情
  "scores": {
    "attendance": 95,               // 出勤成绩，0-100
    "homework": 88,                 // 作业成绩，0-100
    "quiz": 90,                     // 小测验成绩，0-100
    "midterm": 92,                  // 期中成绩，0-100
    "final": 89,                    // 期末成绩，0-100
    "project": 94,                  // 项目成绩，0-100
    "total": 90                     // 总成绩，0-100
  },
  
  // 等第评定
  "grade_point": 4.0,               // 绩点，0.0-5.0
  "grade_level": "A",               // 等第：A/B/C/D/E/F
  "pass_status": "pass",            // pass/fail/retake/exempt
  "rank_in_class": 5,               // 班级排名，1-班级人数
  "rank_in_major": 15,              // 专业排名，1-专业人数
  
  // 考试信息
  "exam_times": 1,                  // 考试次数，1-3
  "exam_type": "normal",            // normal/makeup/retake
  "exam_seat": "A001",              // 考场座位号
  "exam_room": "C1-101",            // 考场教室
  
  // 学术诚信
  "integrity_status": "normal",     // normal/warning/violation
  "plagiarism_check": "passed",     // passed/failed/not_checked
  
  // 审核信息
  "teacher_id": "T2022001",         // 任课教师
  "graded_by": "T2022001",          // 阅卷教师
  "reviewed_by": "T2023001",        // 复核教师
  "grade_date": "2024-01-20",       // 成绩录入日期
  "publish_date": "2024-01-25",     // 成绩公布日期
  
  // 修改记录
  "is_modified": false,             // 是否有修改
  "modification_reason": "",        // 修改原因
  "modification_date": null,        // 修改日期
  "approved_by": null,              // 修改审批人
  
  "notes": "表现优秀",               // 备注，最大500字符
  "created_at": "2024-01-20T15:30:00Z",
  "updated_at": "2024-01-25T10:00:00Z"
}
```

#### 成绩统计 (Grade_Statistics)
```json
{
  "stat_id": "GS2024001",           // 统计ID
  "type": "class",                  // class/major/college/course
  "target_id": "CL2024001",         // 目标ID（班级/专业/学院/课程）
  "semester": "2024-2025-1",        // 统计学期
  
  // 基础统计
  "total_students": 58,             // 参与统计学生数
  "passed_students": 55,            // 及格学生数
  "failed_students": 3,             // 不及格学生数
  "pass_rate": 94.83,               // 及格率，百分比
  
  // 分数统计
  "average_score": 87.5,            // 平均分，0-100
  "highest_score": 98,              // 最高分，0-100
  "lowest_score": 45,               // 最低分，0-100
  "median_score": 88,               // 中位数，0-100
  "standard_deviation": 12.3,       // 标准差
  
  // 等第分布
  "grade_distribution": {
    "A": 15,                        // A等人数
    "B": 25,                        // B等人数
    "C": 15,                        // C等人数
    "D": 2,                         // D等人数
    "E": 1,                         // E等人数
    "F": 0                          // F等人数
  },
  
  // 分数段分布
  "score_distribution": {
    "90-100": 20,                   // 90-100分人数
    "80-89": 25,                    // 80-89分人数
    "70-79": 10,                    // 70-79分人数
    "60-69": 2,                     // 60-69分人数
    "0-59": 1                       // 0-59分人数
  },
  
  "generated_at": "2024-01-26T10:00:00Z"
}
```

### 8. 资产管理

#### 资产登记 (Asset)
```json
{
  "asset_id": "A2024001",           // 资产ID，格式：A+年份+序号
  "asset_code": "SZTU-C1-001",      // 资产编号，学校-建筑-序号
  "barcode": "8901234567890",       // 条形码，13位数字
  "rfid_tag": "E00401006C8E2040",   // RFID标签，24位十六进制
  
  // 基础信息
  "asset_name": "投影仪",            // 资产名称
  "asset_type": "hardware",         // hardware/software/furniture/vehicle
  "category": "teaching_equipment",  // 资产类别
  "subcategory": "projection",      // 子类别
  
  // 品牌型号
  "brand": "SONY",                  // 品牌
  "model": "VPL-EW295",             // 型号
  "specification": "WXGA 3300流明", // 规格说明
  "serial_number": "SN123456789",   // 出厂序列号
  
  // 财务信息
  "purchase_date": "2024-01-01",    // 采购日期
  "purchase_price": 5999.00,        // 采购价格，单位：元
  "current_value": 4500.00,         // 当前价值，单位：元
  "depreciation_rate": 20.0,        // 年折旧率，百分比
  "depreciation_method": "straight_line", // 折旧方法
  
  // 供应商信息
  "supplier": "索尼（中国）有限公司",  // 供应商
  "supplier_contact": "0755-12345678", // 供应商联系方式
  "purchase_contract": "CONT2024001",  // 采购合同号
  
  // 位置信息
  "location_id": "L001",            // 当前位置
  "building_code": "C1",            // 所在建筑
  "room_number": "101",             // 房间号
  "storage_location": "讲台左侧",     // 具体位置描述
  
  // 责任信息
  "responsible_person_id": "T2022001", // 责任人
  "department_id": "D001",          // 所属部门
  "user_department_id": "C001",     // 使用部门
  
  // 状态信息
  "status": "in_use",               // in_use/maintenance/idle/scrapped/lost
  "condition": "good",              // excellent/good/fair/poor/broken
  "last_inspection_date": "2024-03-01", // 最近检查日期
  "next_inspection_date": "2024-09-01", // 下次检查日期
  
  // 保修信息
  "warranty_start_date": "2024-01-01",  // 保修开始日期
  "warranty_end_date": "2027-01-01",    // 保修结束日期
  "warranty_provider": "厂家保修",       // 保修方
  "warranty_terms": "三年免费维修",       // 保修条款
  
  // 使用信息
  "usage_frequency": "daily",       // daily/weekly/monthly/occasional
  "total_usage_hours": 1250,        // 总使用小时数
  "last_maintenance_date": "2024-02-15", // 最近维护日期
  "maintenance_interval": 180,      // 维护间隔（天）
  
  // 安全信息
  "is_sensitive": false,            // 是否涉密设备
  "security_level": "public",       // public/internal/confidential/secret
  "access_control": "none",         // none/key/card/biometric
  
  "notes": "教学专用设备，使用状况良好",
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": "2024-03-01T15:30:00Z"
}
```

### 9. 图书馆系统

#### 图书 (Book)
```json
{
  "book_id": "B001",                // 图书ID，格式：B+序号
  "isbn": "9787111547952",          // ISBN号，13位数字
  "isbn10": "7111547951",           // ISBN10（可选）
  "call_number": "TP301.6/C722",    // 索书号
  "barcode": "SZ240001",            // 条形码
  
  // 基础信息
  "title": "算法导论",               // 书名
  "subtitle": "第三版",              // 副标题
  "title_en": "Introduction to Algorithms", // 英文书名
  "authors": ["Thomas H. Cormen", "Charles E. Leiserson"], // 作者列表
  "translators": ["潘金贵", "顾铁成"], // 译者列表（如果是译作）
  "editors": ["机械工业出版社编辑部"], // 编辑列表
  
  // 出版信息
  "publisher": "机械工业出版社",       // 出版社
  "publish_date": "2023-01-01",      // 出版日期
  "edition": "第三版",                // 版次
  "print_number": 5,                 // 印次，1-50
  "pages": 1312,                     // 页数，1-5000
  "language": "zh-CN",               // 语言代码
  
  // 分类信息
  "category": "计算机科学",            // 主分类
  "subcategory": "算法与数据结构",     // 子分类
  "clc_number": "TP301.6",           // 中图分类号
  "subject_headings": ["算法", "数据结构", "计算机科学"], // 主题词
  
  // 物理属性
  "format": "hardcover",             // hardcover/paperback/ebook
  "dimensions": "26cm×19cm",          // 尺寸
  "weight": 1.8,                     // 重量（公斤）
  "binding": "精装",                  // 装帧方式
  
  // 采购信息
  "price": 128.00,                   // 定价，单位：元
  "purchase_price": 102.40,          // 采购价，单位：元
  "purchase_date": "2023-03-15",     // 采购日期
  "supplier": "机械工业出版社",        // 供应商
  
  // 馆藏信息
  "location_code": "TP301",          // 排架位置
  "floor": 3,                        // 楼层，1-10
  "shelf_number": "A-15-3",          // 书架号
  "total_copies": 10,                // 总册数，1-100
  "available_copies": 7,             // 可借册数，0-总册数
  "borrowed_copies": 2,              // 已借册数
  "processing_copies": 1,            // 加工中册数
  "damaged_copies": 0,               // 损坏册数
  "lost_copies": 0,                  // 丢失册数
  
  // 使用统计
  "borrow_count": 156,               // 借阅次数
  "reserve_count": 12,               // 预约次数
  "popularity_score": 8.5,           // 热门程度，1.0-10.0
  "last_borrowed_date": "2024-03-01", // 最近借阅日期
  
  // 内容信息
  "abstract": "本书全面介绍了算法设计与分析的基本理论...", // 摘要，最大2000字符
  "keywords": ["算法", "复杂度分析", "动态规划"], // 关键词
  "target_audience": "undergraduate",  // undergraduate/graduate/professional
  "difficulty_level": 4,              // 难度等级，1-5
  
  // 数字资源
  "has_ebook": true,                  // 是否有电子版
  "ebook_url": "https://lib.sztu.edu.cn/ebook/123", // 电子书链接
  "has_audiobook": false,             // 是否有有声书
  
  "status": "available",              // available/processing/withdrawn
  "created_at": "2023-03-15T10:00:00Z",
  "updated_at": "2024-03-01T15:30:00Z"
}
```

#### 借阅记录 (Borrow_Record)
```json
{
  "record_id": "BR2024001",          // 借阅记录ID，格式：BR+年份+序号
  "student_id": "202408090101",      // 借阅者学号
  "book_id": "B001",                 // 图书ID
  "copy_id": "B001-001",             // 具体册次ID
  
  // 借阅信息
  "borrow_date": "2024-03-01",       // 借阅日期
  "due_date": "2024-06-01",          // 应还日期
  "return_date": null,               // 实际归还日期，null表示未归还
  "borrow_duration": 92,             // 借阅期限（天），1-365
  
  // 续借信息
  "renew_times": 0,                  // 续借次数，0-3
  "max_renew_times": 2,              // 最大续借次数
  "can_renew": true,                 // 是否可续借
  "last_renew_date": null,           // 最近续借日期
  
  // 逾期信息
  "is_overdue": false,               // 是否逾期
  "overdue_days": 0,                 // 逾期天数，0-1000
  "fine_per_day": 0.50,              // 每日罚金，单位：元
  "fine_amount": 0.00,               // 罚金总额，单位：元
  "fine_paid": false,                // 罚金是否已缴
  "fine_waived": false,              // 罚金是否已免除
  
  // 操作信息
  "borrow_method": "self_service",   // self_service/librarian/online
  "borrow_location": "L1-自助借还机", // 借阅地点
  "return_method": null,             // 归还方式
  "return_location": null,           // 归还地点
  "processed_by": "SYS001",          // 处理员工ID
  
  // 状态信息
  "status": "borrowed",              // borrowed/returned/overdue/lost/damaged
  "condition_borrowed": "good",      // 借出时状态
  "condition_returned": null,        // 归还时状态
  "damage_description": "",          // 损坏描述
  "damage_compensation": 0.00,       // 损坏赔偿，单位：元
  
  // 通知记录
  "reminder_sent": 1,                // 已发送提醒次数，0-10
  "last_reminder_date": "2024-05-25", // 最近提醒日期
  "notification_method": "email",    // email/sms/wechat/app
  
  "notes": "正常借阅",
  "created_at": "2024-03-01T14:30:00Z",
  "updated_at": "2024-05-25T09:00:00Z"
}
```

### 10. 财务系统

#### 消费流水 (Transaction)
```json
{
  "transaction_id": "T2024001",      // 交易ID，格式：T+年份+序号
  "person_id": "P2024001",           // 人员ID
  "card_number": "202408090101",     // 校园卡号（一般与学号相同）
  
  // 交易基本信息
  "transaction_type": "consumption", // consumption/recharge/refund/transfer/subsidy
  "amount": -12.50,                 // 交易金额，负数表示消费，正数表示收入
  "balance_before": 300.00,          // 交易前余额
  "balance_after": 287.50,           // 交易后余额
  
  // 商户信息
  "merchant": "学生食堂一楼",         // 商户名称
  "merchant_id": "M001",             // 商户ID
  "terminal_id": "T001",             // 终端ID
  "location_id": "L050",             // 交易地点
  
  // 时间信息
  "transaction_time": "2024-03-01T12:30:00Z", // 交易时间
  "business_date": "2024-03-01",     // 营业日期
  "batch_number": "20240301001",     // 批次号
  
  // 支付信息
  "payment_method": "campus_card",   // campus_card/wechat/alipay/cash/bank_card
  "payment_channel": "offline",      // offline/online/mobile
  "external_transaction_id": null,   // 外部交易号（第三方支付）
  
  // 商品信息（消费类交易）
  "items": [
    {
      "item_name": "宫保鸡丁",        // 商品名称
      "quantity": 1,                 // 数量
      "unit_price": 8.00,            // 单价
      "subtotal": 8.00               // 小计
    },
    {
      "item_name": "米饭",
      "quantity": 1,
      "unit_price": 2.00,
      "subtotal": 2.00
    },
    {
      "item_name": "西红柿鸡蛋汤",
      "quantity": 1,
      "unit_price": 2.50,
      "subtotal": 2.50
    }
  ],
  
  // 优惠信息
  "discount_amount": 0.00,           // 优惠金额
  "discount_type": "none",           // none/student/staff/activity
  "coupon_used": null,               // 使用的优惠券
  
  // 状态信息
  "status": "completed",             // pending/completed/cancelled/failed
  "is_refunded": false,              // 是否已退款
  "refund_amount": 0.00,             // 退款金额
  "refund_date": null,               // 退款日期
  
  // 结算信息
  "settlement_date": "2024-03-01",   // 结算日期
  "commission_rate": 0.02,           // 手续费率
  "commission_amount": 0.25,         // 手续费金额
  
  "description": "午餐消费",          // 交易描述
  "notes": "",                       // 备注
  "created_at": "2024-03-01T12:30:00Z",
  "updated_at": "2024-03-01T12:30:00Z"
}
```

#### 校园卡信息 (Campus_Card)
```json
{
  "card_id": "CC2024001",            // 卡片ID
  "card_number": "202408090101",     // 卡号
  "person_id": "P2024001",           // 持卡人ID
  
  // 卡片状态
  "status": "active",                // active/frozen/lost/cancelled/expired
  "card_type": "student",            // student/staff/visitor/temporary
  "issue_date": "2024-09-01",        // 发卡日期
  "expire_date": "2028-07-31",       // 到期日期
  "last_active_date": "2024-03-01",  // 最近使用日期
  
  // 余额信息
  "balance": 287.50,                 // 当前余额，单位：元
  "frozen_balance": 0.00,            // 冻结余额
  "daily_limit": 200.00,             // 日消费限额
  "single_limit": 50.00,             // 单笔消费限额
  "overdraft_limit": 0.00,           // 透支限额
  
  // 功能权限
  "dining_enabled": true,            // 餐饮消费权限
  "shopping_enabled": true,          // 商店消费权限
  "library_enabled": true,           // 图书馆权限
  "access_enabled": true,            // 门禁权限
  "attendance_enabled": true,        // 考勤权限
  
  // 安全设置
  "pin_required": false,             // 是否需要密码
  "pin_hash": null,                  // 密码哈希
  "failed_attempts": 0,              // 失败尝试次数，0-10
  "locked_until": null,              // 锁定到期时间
  
  // 统计信息
  "total_recharge": 2000.00,         // 总充值金额
  "total_consumption": 1712.50,      // 总消费金额
  "transaction_count": 156,          // 交易次数
  "last_recharge_date": "2024-02-28", // 最近充值日期
  "last_consumption_date": "2024-03-01", // 最近消费日期
  
  // 补助信息
  "subsidy_balance": 0.00,           // 补助余额
  "monthly_subsidy": 200.00,         // 月度补助金额
  "subsidy_last_issued": "2024-03-01", // 最近补助发放日期
  
  "notes": "正常使用",
  "created_at": "2024-09-01T10:00:00Z",
  "updated_at": "2024-03-01T12:30:00Z"
}
```

## API数据模板设计

### 1. 统一响应格式（不变）
```json
{
  "status": 0,
  "msg": "success",
  "data": {},
  "timestamp": 1640995200000,
  "version": "v1.0"
}
```

### 2. 用户认证响应

#### 微信小程序登录认证
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

#### 微信号绑定机制说明

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

**API接口**：
- `POST /auth/wechat/login` - 微信登录
- `POST /auth/wechat/bind` - 绑定微信号
- `POST /auth/wechat/unbind` - 解绑微信号
- `GET /auth/wechat/status` - 查询绑定状态

### 3. 课表查询响应
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

### 4. 成绩查询响应
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

### 5. 图书馆服务响应
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

### 6. 校园卡消费响应
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

### 7. 权限控制矩阵

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

## 数据库表结构建议

### 核心表
1. `persons` - 人员基础表
2. `colleges` - 学院表
3. `majors` - 专业表
4. `departments` - 部门表
5. `classes` - 班级表（新增）
6. `locations` - 场所表
7. `room_occupations` - 场所占用表（新增）
8. `courses` - 课程表
9. `course_instances` - 开课实例表
10. `grades` - 成绩表
11. `grade_statistics` - 成绩统计表（新增）
12. `assets` - 资产表
13. `books` - 图书表
14. `borrow_records` - 借阅记录表
15. `transactions` - 消费流水表
16. `campus_cards` - 校园卡信息表（新增）

这样的设计能够支持复杂的查询需求，如：
- 某学院某专业某学年的学生成绩统计分析
- 某教学楼某时间段的教室使用情况
- 某时间段的消费流水分析和财务报表
- 跨学院的课程安排冲突检测和排课优化
- 图书馆借阅行为分析和图书采购建议 

## 新增实体设计

### 11. 科研项目系统

#### 科研项目 (Research_Project)
```json
{
  "project_id": "RP2024001",         // 项目ID，格式：RP+年份+序号
  "project_code": "NSFC-2024-001",  // 项目编号（外部）
  "project_name": "基于深度学习的智能校园系统研究", // 项目名称
  "project_name_en": "Intelligent Campus System Research Based on Deep Learning",
  
  // 项目分类
  "project_type": "vertical",        // vertical/horizontal/internal/international
  "project_level": "national",       // national/provincial/municipal/university/department
  "funding_source": "国家自然科学基金", // 资助来源
  "funding_agency": "国家自然科学基金委员会", // 资助机构
  
  // 项目负责人和团队
  "principal_investigator_id": "202408900101", // 项目负责人（教师工号）
  "co_investigators": ["202408900102", "202408900103"], // 主要参与者
  "student_participants": ["202408090101", "202408090102"], // 参与学生
  
  // 项目周期
  "start_date": "2024-01-01",        // 开始日期
  "end_date": "2026-12-31",          // 结束日期
  "duration_months": 36,             // 项目周期（月）
  
  // 经费信息
  "total_funding": 500000.00,        // 总经费，单位：元
  "university_funding": 50000.00,    // 学校配套资金
  "used_funding": 120000.00,         // 已使用经费
  "remaining_funding": 380000.00,    // 剩余经费
  
  // 项目状态
  "status": "ongoing",               // applying/approved/ongoing/suspended/completed/terminated
  "progress": 35.5,                  // 进度百分比，0-100
  "milestone_achieved": 2,           // 已完成里程碑数量
  "total_milestones": 6,             // 总里程碑数量
  
  // 成果信息
  "expected_papers": 5,              // 预期论文数量
  "published_papers": 2,             // 已发表论文数量
  "expected_patents": 2,             // 预期专利数量
  "applied_patents": 1,              // 已申请专利数量
  
  // 项目描述
  "abstract": "本项目旨在构建基于深度学习的智能校园系统...", // 项目摘要
  "keywords": ["深度学习", "智能校园", "物联网"], // 关键词
  "research_field": "计算机科学与技术",   // 研究领域
  "application_domain": "教育信息化",    // 应用领域
  
  // 管理信息
  "college_id": "C001",              // 所属学院
  "department_id": "D001",           // 所属部门
  "lab_id": "LAB001",                // 所属实验室
  "contract_signed": true,           // 合同是否签署
  "contract_date": "2023-12-15",     // 合同签署日期
  
  "notes": "项目进展顺利",
  "created_at": "2023-11-01T10:00:00Z",
  "updated_at": "2024-03-01T15:30:00Z"
}
```

#### 科研项目申请 (Research_Application)
```json
{
  "application_id": "RA2024001",     // 申请ID，格式：RA+年份+序号
  "applicant_id": "202408900101",    // 申请人工号
  "application_type": "new_project", // new_project/extension/modification/termination
  
  // 申请项目信息
  "project_title": "基于深度学习的智能校园系统研究",
  "funding_program": "国家自然科学基金", // 申请的资助计划
  "funding_category": "面上项目",      // 资助类别
  "requested_amount": 500000.00,     // 申请金额
  "project_duration": 36,            // 申请项目周期（月）
  
  // 申请团队
  "team_members": [
    {
      "person_id": "202408900102",
      "role": "co_investigator",      // principal/co_investigator/participant
      "contribution_rate": 30.0       // 贡献率百分比
    }
  ],
  
  // 申请状态
  "status": "under_review",          // draft/submitted/under_review/approved/rejected/withdrawn
  "submission_date": "2023-10-15",   // 提交日期
  "review_deadline": "2023-12-15",   // 评审截止日期
  "result_date": "2023-12-20",       // 结果公布日期
  
  // 评审信息
  "reviewers": ["202200010001", "202100020001"], // 评审专家
  "review_score": 85.5,              // 评审分数，0-100
  "review_comments": "项目具有较好的创新性和应用前景", // 评审意见
  "revision_required": false,        // 是否需要修改
  
  // 申请材料
  "documents": [
    {
      "doc_type": "application_form", // 文档类型
      "doc_name": "项目申请书.pdf",
      "upload_date": "2023-10-10",
      "file_size": 2048576,           // 文件大小（字节）
      "checksum": "md5hash123456"     // 文件校验码
    }
  ],
  
  "notes": "首次申请",
  "created_at": "2023-10-01T10:00:00Z",
  "updated_at": "2023-12-20T16:00:00Z"
}
```

#### 学校论文库 (Paper_Library)
```json
{
  "paper_id": "PL2024001",           // 论文ID，格式：PL+年份+序号
  "title": "基于深度学习的校园智能推荐系统", // 论文标题
  "title_en": "Campus Intelligent Recommendation System Based on Deep Learning",
  
  // 作者信息
  "authors": [
    {
      "person_id": "202408900101",    // 作者人员ID
      "author_name": "张三",          // 作者姓名
      "author_order": 1,             // 作者顺序
      "is_corresponding": true,      // 是否通讯作者
      "affiliation": "深圳技术大学计算机学院" // 所属单位
    }
  ],
  
  // 发表信息
  "journal_name": "计算机研究与发展",    // 期刊名称
  "journal_name_en": "Journal of Computer Research and Development",
  "issn": "1000-1239",               // 期刊ISSN
  "volume": "61",                    // 卷
  "issue": "3",                      // 期
  "pages": "156-168",                // 页码
  "publish_date": "2024-03-15",      // 发表日期
  "doi": "10.7544/issn1000-1239.20240315", // DOI
  
  // 论文分类
  "research_field": "计算机科学与技术", // 研究领域
  "subject_category": "人工智能",      // 学科分类
  "keywords": ["深度学习", "推荐系统", "校园应用"], // 关键词
  "clc_number": "TP391.3",           // 中图分类号
  
  // 质量评价
  "journal_level": "CSCD",           // SCI/EI/CSCD/核心/普通
  "impact_factor": 2.85,             // 影响因子
  "citation_count": 12,              // 被引用次数
  "download_count": 156,             // 下载次数
  
  // 内容信息
  "abstract": "本文提出了一种基于深度学习的校园智能推荐系统...", // 摘要
  "abstract_en": "This paper proposes a campus intelligent recommendation system...",
  "funding_info": "国家自然科学基金(62003001)", // 基金资助信息
  
  // 文件信息
  "pdf_url": "https://lib.sztu.edu.cn/papers/PL2024001.pdf", // PDF链接
  "file_size": 5242880,              // 文件大小（字节）
  "page_count": 13,                  // 页数
  
  // 项目关联
  "related_project_id": "RP2024001", // 关联科研项目
  "thesis_type": "journal",          // journal/conference/patent/thesis/report
  
  // 状态信息
  "status": "published",             // draft/submitted/accepted/published/withdrawn
  "submission_date": "2023-11-01",   // 投稿日期
  "acceptance_date": "2024-01-15",   // 录用日期
  "online_date": "2024-02-01",       // 在线发表日期
  
  "notes": "高质量期刊论文",
  "created_at": "2024-02-01T10:00:00Z",
  "updated_at": "2024-03-15T09:00:00Z"
}
```

### 12. 扩展资产管理

#### 资产类型扩展定义
```json
{
  "asset_categories": {
    "teaching_equipment": {
      "projection": ["投影仪", "激光投影仪", "短焦投影仪", "互动投影仪"],
      "display": ["液晶显示屏", "LED显示屏", "触控一体机", "电子白板", "拼接屏"],
      "audio": ["音响设备", "话筒", "扩音器", "调音台", "无线麦克风"],
      "computer": ["台式电脑", "笔记本电脑", "平板电脑", "一体机电脑"],
      "network": ["交换机", "路由器", "无线AP", "网线", "光纤设备"]
    },
    "lab_equipment": {
      "computing": ["服务器", "工作站", "GPU服务器", "A100芯片", "H100芯片", "计算节点"],
      "storage": ["存储服务器", "磁盘阵列", "NAS设备", "SSD硬盘", "机械硬盘"],
      "instruments": ["示波器", "万用表", "信号发生器", "频谱分析仪", "逻辑分析仪"],
      "specialized": ["3D打印机", "激光切割机", "PCB制板机", "焊接设备"]
    },
    "office_equipment": {
      "furniture": ["办公桌", "办公椅", "会议桌", "文件柜", "书架", "沙发"],
      "appliances": ["空调", "饮水机", "复印机", "打印机", "扫描仪", "碎纸机"],
      "communication": ["座机电话", "对讲机", "视频会议设备", "摄像头"]
    },
    "infrastructure": {
      "lighting": ["LED灯管", "应急灯", "路灯", "景观灯", "投光灯"],
      "hvac": ["中央空调", "新风系统", "排风扇", "空气净化器"],
      "security": ["监控摄像头", "门禁设备", "报警器", "消防设备"],
      "landscape": ["草坪修剪机", "洒水设备", "园艺工具", "花盆"]
    },
    "facility_equipment": {
      "cleaning": ["扫地车", "洗地机", "吸尘器", "垃圾桶", "清洁工具"],
      "transport": ["通勤车", "电动车", "自行车", "搬运车"],
      "sports": ["篮球架", "乒乓球台", "健身器材", "体育用品"],
      "catering": ["餐桌", "餐椅", "厨房设备", "餐具", "冰箱"]
    },
    "dormitory_equipment": {
      "furniture": ["宿舍床", "书桌", "衣柜", "椅子"],
      "appliances": ["热水器", "洗衣机", "空调", "风扇"],
      "facilities": ["窗帘", "百叶窗", "晾衣架", "鞋柜"]
    }
  }
}
```

### 13. 网络权限与登录管理

#### 网络使用权限 (Network_Permission)
```json
{
  "permission_id": "NP2024001",      // 权限ID，格式：NP+年份+序号
  "person_id": "P2024001",           // 人员ID
  "network_type": "campus_wifi",     // campus_wifi/dormitory_network/lab_network
  
  // 设备限制
  "max_devices": 3,                  // 最大同时在线设备数，1-10
  "current_devices": 2,              // 当前在线设备数
  "registered_devices": [            // 已注册设备列表
    {
      "device_id": "DEV001",
      "device_name": "iPhone 15",
      "mac_address": "00:11:22:33:44:55",
      "device_type": "mobile",       // mobile/laptop/desktop/tablet
      "register_date": "2024-01-15",
      "last_online": "2024-03-01T10:30:00Z",
      "status": "active"             // active/suspended/expired
    }
  ],
  
  // 流量限制
  "daily_traffic_limit": 2048,       // 日流量限制，单位：MB
  "monthly_traffic_limit": 51200,    // 月流量限制，单位：MB
  "used_traffic_today": 256,         // 今日已用流量，单位：MB
  "used_traffic_month": 8192,        // 本月已用流量，单位：MB
  
  // 时间限制
  "time_restrictions": {
    "weekday_start": "06:00",        // 工作日开始时间
    "weekday_end": "23:00",          // 工作日结束时间
    "weekend_start": "08:00",        // 周末开始时间
    "weekend_end": "23:00",          // 周末结束时间
    "daily_duration_limit": 720      // 日使用时长限制，单位：分钟
  },
  
  // 网络供应商（宿舍网）
  "dormitory_network": {
    "provider": "中国移动",           // 中国移动/中国联通/中国电信
    "package_type": "unlimited",     // unlimited/limited/pay_per_use
    "monthly_fee": 29.00,            // 月费，单位：元
    "bandwidth": 100,                // 带宽，单位：Mbps
    "contract_end_date": "2025-06-30" // 合约到期日期
  },
  
  // 访问控制
  "access_control": {
    "blocked_websites": ["游戏网站", "视频网站"], // 封禁网站类别
    "allowed_ports": [80, 443, 22, 21], // 允许的端口
    "vpn_allowed": false,            // 是否允许VPN
    "p2p_allowed": false             // 是否允许P2P
  },
  
  "status": "active",                // active/suspended/expired/banned
  "expiry_date": "2025-07-31",       // 权限到期日期
  "violation_count": 0,              // 违规次数，0-10
  "last_violation_date": null,       // 最近违规日期
  
  "created_at": "2024-01-15T10:00:00Z",
  "updated_at": "2024-03-01T15:30:00Z"
}
```

#### 系统登录权限 (System_Access)
```json
{
  "access_id": "SA2024001",          // 访问权限ID，格式：SA+年份+序号
  "person_id": "P2024001",           // 人员ID
  "system_name": "教务管理系统",       // 系统名称
  "system_code": "EMS",              // 系统代码
  "system_url": "https://ems.sztu.edu.cn", // 系统URL
  
  // 权限级别
  "access_level": "student",         // admin/teacher/student/staff/guest
  "role": "undergraduate",           // 具体角色
  "permissions": [                   // 具体权限列表
    "view_schedule",                 // 查看课表
    "view_grades",                   // 查看成绩
    "course_selection",              // 选课
    "scholarship_application",       // 奖学金申请
    "thesis_submission"              // 论文提交
  ],
  
  // 访问限制
  "ip_restrictions": {
    "allowed_networks": ["10.0.0.0/8", "192.168.0.0/16"], // 允许的网络段
    "campus_only": true,             // 是否仅限校园网访问
    "vpn_access": false              // 是否支持VPN访问
  },
  
  // 登录策略
  "login_policy": {
    "max_concurrent_sessions": 3,    // 最大并发会话数
    "session_timeout": 7200,         // 会话超时时间，单位：秒
    "password_policy": "strong",     // weak/medium/strong
    "two_factor_required": false,    // 是否需要双因子认证
    "failed_attempts_limit": 5       // 失败尝试次数限制
  },
  
  // 使用统计
  "usage_stats": {
    "total_logins": 156,             // 总登录次数
    "last_login": "2024-03-01T10:30:00Z", // 最近登录时间
    "failed_attempts": 0,            // 失败尝试次数
    "average_session_duration": 1800, // 平均会话时长，单位：秒
    "most_used_features": ["view_schedule", "view_grades"] // 最常用功能
  },
  
  // 审计信息
  "audit_log": [
    {
      "timestamp": "2024-03-01T10:30:00Z",
      "action": "login",             // login/logout/access_denied/password_change
      "ip_address": "10.1.1.100",
      "user_agent": "Mozilla/5.0...",
      "result": "success"            // success/failure
    }
  ],
  
  "status": "active",                // active/suspended/expired/locked
  "grant_date": "2024-01-15",        // 授权日期
  "expiry_date": "2025-07-31",       // 权限到期日期
  "granted_by": "202200010001",      // 授权人
  
  "notes": "正常使用权限",
  "created_at": "2024-01-15T10:00:00Z",
  "updated_at": "2024-03-01T15:30:00Z"
}
```

#### 平台权限配置 (Platform_Config)
```json
{
  "config_id": "PC2024001",          // 配置ID
  "platform_name": "科研管理平台",     // 平台名称
  "platform_code": "RMS",            // 平台代码
  "base_url": "https://research.sztu.edu.cn",
  
  // 角色权限映射
  "role_permissions": {
    "teacher": {
      "可见功能": ["项目申请", "项目管理", "经费查询", "成果管理", "学术评价"],
      "操作权限": ["create_project", "edit_project", "submit_report", "upload_paper"],
      "数据范围": "own_projects"      // own_projects/department_projects/college_projects/all_projects
    },
    "department_head": {
      "可见功能": ["项目审批", "部门统计", "资源分配", "绩效评估"],
      "操作权限": ["approve_project", "assign_funding", "view_department_stats"],
      "数据范围": "department_projects"
    },
    "student": {
      "可见功能": ["课题申请", "毕业设计", "竞赛管理", "奖学金申请"],
      "操作权限": ["apply_topic", "submit_thesis", "apply_scholarship"],
      "数据范围": "own_data"
    }
  },
  
  // 菜单配置
  "menu_structure": {
    "teacher": [
      {
        "menu_name": "项目管理",
        "sub_menus": ["在研项目", "项目申请", "项目结题", "经费管理"]
      },
      {
        "menu_name": "成果管理", 
        "sub_menus": ["论文管理", "专利管理", "获奖情况", "学术兼职"]
      }
    ],
    "student": [
      {
        "menu_name": "学业管理",
        "sub_menus": ["课表查询", "成绩查询", "选课系统", "评教系统"]
      },
      {
        "menu_name": "申请服务",
        "sub_menus": ["奖学金申请", "助学金申请", "课题申请", "实习申请"]
      }
    ]
  },
  
  // 工作流配置
  "workflow_config": {
    "项目申请": {
      "审批流程": ["申请人提交", "学院审核", "科研处审批", "财务确认"],
      "审批时限": [7, 14, 21, 3],     // 各环节审批时限（天）
      "自动通过条件": "amount < 10000" // 自动通过条件
    },
    "奖学金申请": {
      "审批流程": ["学生申请", "班级评议", "学院审核", "学校审批"],
      "审批时限": [3, 7, 14, 21],
      "评分标准": {"学习成绩": 0.6, "综合表现": 0.4}
    }
  },
  
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": "2024-03-01T15:30:00Z"
}
```

### 14. 更新的数据库表结构

#### 新增核心表
```
17. research_projects - 科研项目表
18. research_applications - 科研项目申请表  
19. paper_library - 学校论文库表
20. network_permissions - 网络使用权限表
21. system_access - 系统登录权限表
22. platform_configs - 平台权限配置表
23. audit_logs - 审计日志表
24. device_registrations - 设备注册表
25. workflow_instances - 工作流实例表
```

#### 修改的表结构
```sql
-- persons表中的employee_id字段修改
ALTER TABLE persons MODIFY COLUMN employee_id VARCHAR(12) COMMENT '工号：年份(4位)+专业编号(4位)+序号(2位)';

-- assets表中增加更详细的分类
ALTER TABLE assets ADD COLUMN subcategory VARCHAR(50) COMMENT '资产子类别';
ALTER TABLE assets ADD COLUMN location_type VARCHAR(20) COMMENT '位置类型：classroom/lab/office/dormitory/outdoor';
```

这样的扩展设计能够支持：
- 完整的科研项目全生命周期管理
- 真实的校园网络使用场景和限制
- 基于角色的细粒度权限控制系统
- 多平台统一身份认证和授权
- 详细的资产分类和定位管理
- 完整的审计追踪和合规性要求 