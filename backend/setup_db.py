#!/usr/bin/env python3
"""
数据库初始化脚本
用于快速设置SZTU-iCampus项目的测试数据
"""

import sys
import os
from sqlalchemy.orm import Session
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, engine, Base
from app.models.user import User
from app.models.announcement import Announcement
from app.models.schedule import Schedule
from app.models.notice import Notice
from app.models.event import Event
from app.models.grade import Grade

def init_database():
    """初始化数据库和测试数据"""
    print("正在创建数据库表...")
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    print("✓ 数据库表创建完成")
    
    # 创建数据库会话
    db = SessionLocal()
    
    try:
        # 检查是否已有数据
        existing_users = db.query(User).count()
        existing_announcements = db.query(Announcement).count()
        existing_schedules = db.query(Schedule).count()
        existing_notices = db.query(Notice).count()
        existing_events = db.query(Event).count()
        existing_grades = db.query(Grade).count()
        
        if existing_users > 0 or existing_announcements > 0 or existing_schedules > 0 or existing_notices > 0 or existing_events > 0 or existing_grades > 0:
            print(f"发现已有数据：{existing_users} 个用户，{existing_announcements} 个公告，{existing_schedules} 个课程，{existing_notices} 个通知，{existing_events} 个活动，{existing_grades} 个成绩")
            choice = input("是否清空现有数据并重新初始化？(y/N): ")
            if choice.lower() == 'y':
                print("正在清空现有数据...")
                db.query(Grade).delete()
                db.query(Event).delete()
                db.query(Notice).delete()
                db.query(Schedule).delete()
                db.query(Announcement).delete()
                db.query(User).delete()
                db.commit()
                print("✓ 现有数据已清空")
            else:
                print("保持现有数据，退出初始化")
                return
        
        # 创建测试用户
        print("正在创建测试用户...")
        test_users = [
            {
                "openid": "test_admin",
                "student_id": "admin",
                "name": "管理员"
            },
            {
                "openid": "test_student_001",
                "student_id": "2024001001",
                "name": "张三"
            },
            {
                "openid": "test_student_002",
                "student_id": "2024001002",
                "name": "李四"
            }
        ]
        
        for user_data in test_users:
            user = User(**user_data)
            db.add(user)
        
        # 创建测试公告
        print("正在创建测试公告...")
        test_announcements = [
            {
                "title": "关于2024年春季学期开学安排的通知",
                "content": """各位同学：

根据学校安排，2024年春季学期将于2月26日正式开学。请同学们做好返校准备，具体安排如下：

1. 返校时间：2月24日-25日
2. 健康检查：返校前需完成健康申报
3. 宿舍安排：保持原宿舍分配
4. 开学典礼：2月26日上午9:00在体育馆举行

注意事项：
- 返校途中注意安全，做好个人防护
- 携带必要的学习和生活用品
- 如有特殊情况请及时联系辅导员

祝大家新学期学习进步！

深圳技术大学教务处
2024年2月1日""",
                "department": "教务处"
            },
            {
                "title": "图书馆开放时间调整通知",
                "content": """亲爱的读者：

为了更好地服务广大师生，图书馆开放时间调整如下：

周一至周五：8:00-22:00
周六至周日：9:00-21:00
法定节假日：9:00-17:00

新增服务：
- 24小时自习室开放（需刷卡进入）
- 新增电子阅览区域
- 延长借阅时间至30天

请广大师生合理安排学习时间，遵守图书馆相关规定。

图书馆
2024年2月5日""",
                "department": "图书馆"
            },
            {
                "title": "校园网络维护通知",
                "content": """各位师生：

为提升校园网络服务质量，信息中心将于本周六（3月2日）凌晨2:00-6:00进行网络设备维护升级。

维护内容：
- 核心交换机升级
- 网络安全设备更新
- 服务器系统优化

影响范围：
- 校园网将暂时中断4小时
- 宿舍网络同时受影响
- 教学楼WiFi暂时不可用

建议：
- 提前下载需要的资料
- 合理安排网络使用时间
- 如有紧急情况请联系值班人员

联系电话：0755-12345678

信息中心
2024年2月28日""",
                "department": "信息中心"
            },
            {
                "title": "2024年春季学期课程选课通知",
                "content": """各位同学：

2024年春季学期选课工作即将开始，现将有关事项通知如下：

选课时间：
- 第一轮：3月1日 9:00 - 3月3日 17:00
- 第二轮：3月5日 9:00 - 3月7日 17:00
- 补选时间：3月10日 9:00 - 3月12日 17:00

选课说明：
1. 登录教务系统进行选课
2. 每人最多选择25学分课程
3. 优先保证必修课选课
4. 选修课采用抽签方式

注意事项：
- 请按时完成选课，逾期不予补选
- 如有课程冲突，系统会自动提醒
- 选课结果请及时核对

教务处
2024年2月20日""",
                "department": "教务处"
            },
            {
                "title": "学生宿舍安全检查通知",
                "content": """各位同学：

为确保宿舍安全，学生处将组织宿舍安全检查活动。

检查时间：3月15日-3月17日
检查内容：
- 违规电器使用情况
- 宿舍卫生状况
- 消防安全设施
- 门窗安全状况

检查标准：
1. 不得使用大功率电器
2. 保持宿舍整洁卫生
3. 不得私拉电线
4. 消防通道保持畅通

请各位同学积极配合检查工作，营造安全和谐的住宿环境。

学生处
2024年3月10日""",
                "department": "学生处"
            }
        ]
        
        for announcement_data in test_announcements:
            announcement = Announcement(**announcement_data)
            db.add(announcement)
        
        # 创建测试课表
        print("正在创建测试课表...")
        test_schedules = [
            # 周一课程
            {
                "course_name": "高等数学",
                "teacher": "王教授",
                "classroom": "A101",
                "week_day": 1,
                "start_time": "08:30",
                "end_time": "10:10",
                "weeks": "1-16周",
                "course_type": "必修",
                "credits": "4",
                "student_id": "2024001",
                "semester": "2024春"
            },
            {
                "course_name": "大学英语",
                "teacher": "李老师",
                "classroom": "B205",
                "week_day": 1,
                "start_time": "10:30",
                "end_time": "12:10",
                "weeks": "1-16周",
                "course_type": "必修",
                "credits": "3",
                "student_id": "2024001",
                "semester": "2024春"
            },
            # 周二课程
            {
                "course_name": "数据结构",
                "teacher": "张教授",
                "classroom": "C301",
                "week_day": 2,
                "start_time": "08:30",
                "end_time": "10:10",
                "weeks": "1-16周",
                "course_type": "必修",
                "credits": "4",
                "student_id": "2024001",
                "semester": "2024春"
            },
            {
                "course_name": "计算机网络",
                "teacher": "赵博士",
                "classroom": "D401",
                "week_day": 2,
                "start_time": "14:00",
                "end_time": "15:40",
                "weeks": "1-16周",
                "course_type": "必修",
                "credits": "3",
                "student_id": "2024001",
                "semester": "2024春"
            },
            # 周三课程
            {
                "course_name": "操作系统",
                "teacher": "刘教授",
                "classroom": "E102",
                "week_day": 3,
                "start_time": "08:30",
                "end_time": "10:10",
                "weeks": "1-16周",
                "course_type": "必修",
                "credits": "3",
                "student_id": "2024001",
                "semester": "2024春"
            },
            {
                "course_name": "软件工程",
                "teacher": "陈老师",
                "classroom": "F203",
                "week_day": 3,
                "start_time": "14:00",
                "end_time": "15:40",
                "weeks": "1-16周",
                "course_type": "必修",
                "credits": "3",
                "student_id": "2024001",
                "semester": "2024春"
            },
            # 周四课程
            {
                "course_name": "数据库原理",
                "teacher": "周教授",
                "classroom": "G304",
                "week_day": 4,
                "start_time": "10:30",
                "end_time": "12:10",
                "weeks": "1-16周",
                "course_type": "必修",
                "credits": "3",
                "student_id": "2024001",
                "semester": "2024春"
            },
            # 周五课程
            {
                "course_name": "算法设计",
                "teacher": "吴博士",
                "classroom": "H201",
                "week_day": 5,
                "start_time": "08:30",
                "end_time": "10:10",
                "weeks": "1-16周",
                "course_type": "选修",
                "credits": "2",
                "student_id": "2024001",
                "semester": "2024春"
            },
            {
                "course_name": "人工智能导论",
                "teacher": "郑教授",
                "classroom": "I305",
                "week_day": 5,
                "start_time": "14:00",
                "end_time": "15:40",
                "weeks": "1-16周",
                "course_type": "选修",
                "credits": "2",
                "student_id": "2024001",
                "semester": "2024春"
            }
        ]
        
        for schedule_data in test_schedules:
            schedule = Schedule(**schedule_data)
            db.add(schedule)
        
        # 创建测试通知
        print("正在创建测试通知...")
        test_notices = [
            {
                "title": "【紧急通知】期末考试时间调整",
                "content": "各位同学注意：\n\n由于教学安排调整，部分课程的期末考试时间有所变更：\n\n1. 高等数学：原定1月15日改为1月18日\n2. 线性代数：原定1月16日改为1月19日\n3. 概率论：原定1月17日改为1月20日\n\n请各位同学及时关注考试安排，合理安排复习时间。如有疑问，请联系教务处。",
                "department": "教务处",
                "notice_type": "URGENT",
                "priority": "HIGH",
                "target_audience": "全体学生",
                "effective_date": datetime(2024, 1, 10, 9, 0),
                "expire_date": datetime(2024, 1, 25, 18, 0)
            },
            {
                "title": "关于图书馆寒假开放时间的通知",
                "content": "各位师生：\n\n图书馆寒假期间开放时间安排如下：\n\n1月20日-2月28日：\n- 周一至周五：9:00-17:00\n- 周六：9:00-12:00\n- 周日：闭馆\n\n春节期间（2月10日-2月17日）闭馆。\n\n请各位读者合理安排时间，注意开放时间变更。",
                "department": "图书馆",
                "notice_type": "NORMAL",
                "priority": "MEDIUM",
                "target_audience": "全体师生",
                "effective_date": datetime(2024, 1, 15, 10, 0),
                "expire_date": datetime(2024, 3, 1, 18, 0)
            },
            {
                "title": "网络系统维护通知",
                "content": "各位用户：\n\n为提升网络服务质量，信息中心将于本周六晚进行系统维护：\n\n维护时间：1月13日 22:00 - 1月14日 6:00\n影响范围：校园网、教务系统、图书馆系统\n\n维护期间上述系统将暂停服务，请各位用户提前做好相关准备。维护完成后系统将自动恢复正常。\n\n如有紧急情况，请联系信息中心值班电话：0755-12345678",
                "department": "信息中心",
                "notice_type": "NORMAL",
                "priority": "HIGH",
                "target_audience": "全体师生",
                "effective_date": datetime(2024, 1, 11, 14, 0),
                "expire_date": datetime(2024, 1, 15, 8, 0)
            },
            {
                "title": "学生证补办流程说明",
                "content": "各位同学：\n\n学生证补办流程如下：\n\n1. 填写《学生证补办申请表》\n2. 提供身份证复印件1份\n3. 提供近期免冠照片2张（1寸）\n4. 缴纳工本费20元\n5. 等待3-5个工作日制作完成\n\n办理地点：行政楼一楼学生事务中心\n办理时间：周一至周五 9:00-12:00, 14:00-17:00\n\n请遗失学生证的同学尽快办理补办手续。",
                "department": "学生事务中心",
                "notice_type": "INFO",
                "priority": "LOW",
                "target_audience": "在校学生",
                "effective_date": datetime(2024, 1, 8, 9, 0),
                "expire_date": datetime(2024, 6, 30, 18, 0)
            },
            {
                "title": "食堂就餐优惠活动",
                "content": "各位师生：\n\n为提升用餐体验，食堂推出优惠活动：\n\n活动时间：1月10日-1月31日\n活动内容：\n1. 午餐时段（11:30-13:30）消费满15元减2元\n2. 晚餐时段（17:30-19:30）消费满20元减3元\n3. 使用校园卡支付享额外9.5折优惠\n\n优惠可叠加使用，欢迎大家到食堂用餐！",
                "department": "后勤服务中心",
                "notice_type": "INFO",
                "priority": "LOW",
                "target_audience": "全体师生",
                "effective_date": datetime(2024, 1, 10, 8, 0),
                "expire_date": datetime(2024, 2, 1, 20, 0)
            }
        ]
        
        for notice_data in test_notices:
            notice = Notice(**notice_data)
            db.add(notice)
        
        # 创建测试活动
        print("正在创建测试活动...")
        test_events = [
            {
                "title": "2024年春季学术论坛",
                "description": "本次学术论坛将邀请国内外知名学者分享最新研究成果，主题涵盖人工智能、大数据、物联网等前沿技术领域。欢迎全校师生踊跃参加，共同探讨学术前沿。",
                "organizer": "学术委员会",
                "event_type": "ACADEMIC",
                "status": "UPCOMING",
                "location": "学术报告厅（主楼A座201）",
                "start_time": datetime(2024, 3, 15, 14, 0),
                "end_time": datetime(2024, 3, 15, 17, 0),
                "registration_deadline": datetime(2024, 3, 10, 18, 0),
                "max_participants": 200,
                "current_participants": 45,
                "contact_info": "学术委员会 联系电话：0755-12345678",
                "requirements": "建议提前了解相关技术背景，携带笔记本电脑"
            },
            {
                "title": "校园文化艺术节",
                "description": "一年一度的校园文化艺术节即将拉开帷幕！活动包括歌唱比赛、舞蹈表演、书法展览、摄影作品展等。展现青春风采，丰富校园文化生活。",
                "organizer": "学生会",
                "event_type": "CULTURAL",
                "status": "UPCOMING",
                "location": "校园文化广场",
                "start_time": datetime(2024, 4, 20, 18, 30),
                "end_time": datetime(2024, 4, 20, 21, 0),
                "registration_deadline": datetime(2024, 4, 15, 12, 0),
                "max_participants": 500,
                "current_participants": 126,
                "contact_info": "学生会文艺部 微信群：SZTU艺术节2024",
                "requirements": "参赛选手需提前报名，观众免费入场"
            },
            {
                "title": "春季篮球联赛决赛",
                "description": "经过激烈的小组赛和淘汰赛，春季篮球联赛即将迎来决赛！计算机学院 VS 电子工程学院，精彩对决不容错过。为你喜爱的队伍加油呐喊！",
                "organizer": "体育部",
                "event_type": "SPORTS",
                "status": "UPCOMING",
                "location": "体育馆篮球场",
                "start_time": datetime(2024, 5, 8, 19, 0),
                "end_time": datetime(2024, 5, 8, 21, 0),
                "registration_deadline": None,
                "max_participants": 800,
                "current_participants": 234,
                "contact_info": "体育部 QQ群：567890123",
                "requirements": "观众免费入场，请提前30分钟到场"
            },
            {
                "title": "程序设计竞赛初赛",
                "description": "深圳技术大学第五届程序设计竞赛初赛即将举行。比赛采用ACM-ICPC赛制，题目涵盖算法设计、数据结构等内容。优胜者将代表学校参加省级比赛。",
                "organizer": "计算机学院",
                "event_type": "COMPETITION",
                "status": "UPCOMING",
                "location": "计算机实验楼机房",
                "start_time": datetime(2024, 3, 25, 9, 0),
                "end_time": datetime(2024, 3, 25, 14, 0),
                "registration_deadline": datetime(2024, 3, 20, 23, 59),
                "max_participants": 120,
                "current_participants": 87,
                "contact_info": "计算机学院竞赛组 邮箱：contest@sztu.edu.cn",
                "requirements": "需要具备C++或Java编程基础，自带键盘（可选）"
            },
            {
                "title": "社团招新宣传周",
                "description": "新学期开始，各大社团开启招新模式！音乐社、摄影社、创业社、机器人社等50+社团等你加入。现场体验社团活动，找到志同道合的小伙伴。",
                "organizer": "社团联合会",
                "event_type": "SOCIAL",
                "status": "ONGOING",
                "location": "学生活动中心广场",
                "start_time": datetime(2024, 2, 26, 10, 0),
                "end_time": datetime(2024, 3, 1, 18, 0),
                "registration_deadline": None,
                "max_participants": 1000,
                "current_participants": 456,
                "contact_info": "社团联合会 微信公众号：SZTU社团",
                "requirements": "持学生证免费参加，可现场报名心仪社团"
            },
            {
                "title": "毕业设计答辩会",
                "description": "2024届本科生毕业设计答辩会，展示四年学习成果。答辩涵盖工程设计、科学研究、创新项目等多个类别。欢迎师弟师妹观摩学习。",
                "organizer": "教务处",
                "event_type": "ACADEMIC",
                "status": "COMPLETED",
                "location": "各学院会议室",
                "start_time": datetime(2024, 1, 8, 8, 30),
                "end_time": datetime(2024, 1, 12, 18, 0),
                "registration_deadline": datetime(2024, 1, 5, 17, 0),
                "max_participants": 300,
                "current_participants": 298,
                "contact_info": "教务处 电话：0755-87654321",
                "requirements": "答辩学生需提前准备PPT，观摩学生需提前预约"
            }
        ]
        
        for event_data in test_events:
            event = Event(**event_data)
            db.add(event)
        
        # 创建测试成绩
        print("正在创建测试成绩...")
        
        # 计算GPA和等级的辅助函数
        def calculate_gpa(score):
            if score >= 97: return 4.0, "A+"
            elif score >= 93: return 4.0, "A"
            elif score >= 90: return 3.7, "A-"
            elif score >= 87: return 3.3, "B+"
            elif score >= 83: return 3.0, "B"
            elif score >= 80: return 2.7, "B-"
            elif score >= 77: return 2.3, "C+"
            elif score >= 73: return 2.0, "C"
            elif score >= 70: return 1.7, "C-"
            elif score >= 67: return 1.3, "D+"
            elif score >= 65: return 1.0, "D"
            else: return 0.0, "F"
        
        test_grades = [
            # 2023-2024学年第一学期
            {
                "student_id": "2024001",
                "student_name": "张三",
                "course_code": "MATH001",
                "course_name": "高等数学A(一)",
                "course_type": "必修",
                "credits": 4.0,
                "semester": "2023-2024-1",
                "academic_year": "2023-2024",
                "teacher_name": "王教授",
                "regular_score": 85.0,
                "midterm_score": 88.0,
                "final_score": 92.0,
                "total_score": 89.0,
                "grade_level": "B+",
                "gpa_points": 3.3,
                "status": "PASS",
                "class_rank": 12,
                "class_total": 45,
                "exam_date": datetime(2023, 12, 25, 9, 0),
                "publish_date": datetime(2024, 1, 5, 14, 30)
            },
            {
                "student_id": "2024001",
                "student_name": "张三",
                "course_code": "PHYS001",
                "course_name": "大学物理A(一)",
                "course_type": "必修",
                "credits": 3.0,
                "semester": "2023-2024-1",
                "academic_year": "2023-2024",
                "teacher_name": "李教授",
                "regular_score": 92.0,
                "midterm_score": 90.0,
                "final_score": 95.0,
                "total_score": 93.0,
                "grade_level": "A",
                "gpa_points": 4.0,
                "status": "PASS",
                "class_rank": 3,
                "class_total": 38,
                "exam_date": datetime(2023, 12, 28, 14, 0),
                "publish_date": datetime(2024, 1, 6, 16, 20)
            },
            {
                "student_id": "2024001",
                "student_name": "张三",
                "course_code": "PROG001",
                "course_name": "程序设计基础(C语言)",
                "course_type": "必修",
                "credits": 3.5,
                "semester": "2023-2024-1",
                "academic_year": "2023-2024",
                "teacher_name": "陈老师",
                "regular_score": 88.0,
                "midterm_score": 85.0,
                "final_score": 90.0,
                "total_score": 88.0,
                "grade_level": "B+",
                "gpa_points": 3.3,
                "status": "PASS",
                "class_rank": 8,
                "class_total": 42,
                "exam_date": datetime(2024, 1, 3, 10, 0),
                "publish_date": datetime(2024, 1, 8, 9, 15)
            },
            {
                "student_id": "2024001",
                "student_name": "张三",
                "course_code": "ENG001",
                "course_name": "大学英语(一)",
                "course_type": "必修",
                "credits": 2.0,
                "semester": "2023-2024-1",
                "academic_year": "2023-2024",
                "teacher_name": "刘老师",
                "regular_score": 82.0,
                "midterm_score": 78.0,
                "final_score": 84.0,
                "total_score": 81.0,
                "grade_level": "B-",
                "gpa_points": 2.7,
                "status": "PASS",
                "class_rank": 18,
                "class_total": 35,
                "exam_date": datetime(2023, 12, 30, 15, 0),
                "publish_date": datetime(2024, 1, 7, 11, 45)
            },
            {
                "student_id": "2024001",
                "student_name": "张三",
                "course_code": "PE001",
                "course_name": "体育(一)",
                "course_type": "必修",
                "credits": 1.0,
                "semester": "2023-2024-1",
                "academic_year": "2023-2024",
                "teacher_name": "赵教练",
                "regular_score": 90.0,
                "midterm_score": None,
                "final_score": 88.0,
                "total_score": 89.0,
                "grade_level": "B+",
                "gpa_points": 3.3,
                "status": "PASS",
                "class_rank": 15,
                "class_total": 50,
                "exam_date": datetime(2023, 12, 20, 10, 0),
                "publish_date": datetime(2024, 1, 4, 13, 20)
            },
            # 2023-2024学年第二学期
            {
                "student_id": "2024001",
                "student_name": "张三",
                "course_code": "MATH002",
                "course_name": "高等数学A(二)",
                "course_type": "必修",
                "credits": 4.0,
                "semester": "2023-2024-2",
                "academic_year": "2023-2024",
                "teacher_name": "王教授",
                "regular_score": 90.0,
                "midterm_score": 92.0,
                "final_score": 94.0,
                "total_score": 92.5,
                "grade_level": "A-",
                "gpa_points": 3.7,
                "status": "PASS",
                "class_rank": 5,
                "class_total": 45,
                "exam_date": datetime(2024, 6, 25, 9, 0),
                "publish_date": datetime(2024, 7, 5, 14, 30)
            },
            {
                "student_id": "2024001",
                "student_name": "张三",
                "course_code": "PROG002",
                "course_name": "数据结构与算法",
                "course_type": "必修",
                "credits": 3.5,
                "semester": "2023-2024-2",
                "academic_year": "2023-2024",
                "teacher_name": "张教授",
                "regular_score": 95.0,
                "midterm_score": 96.0,
                "final_score": 98.0,
                "total_score": 97.0,
                "grade_level": "A+",
                "gpa_points": 4.0,
                "status": "PASS",
                "class_rank": 1,
                "class_total": 40,
                "exam_date": datetime(2024, 6, 28, 14, 0),
                "publish_date": datetime(2024, 7, 6, 16, 20)
            },
            {
                "student_id": "2024001",
                "student_name": "张三",
                "course_name": "线性代数",
                "course_code": "MATH003",
                "course_type": "必修",
                "credits": 3.0,
                "semester": "2023-2024-2",
                "academic_year": "2023-2024",
                "teacher_name": "周教授",
                "regular_score": 87.0,
                "midterm_score": 85.0,
                "final_score": 91.0,
                "total_score": 88.5,
                "grade_level": "B+",
                "gpa_points": 3.3,
                "status": "PASS",
                "class_rank": 7,
                "class_total": 43,
                "exam_date": datetime(2024, 7, 2, 10, 0),
                "publish_date": datetime(2024, 7, 8, 9, 15)
            }
        ]
        
        for grade_data in test_grades:
            grade = Grade(**grade_data)
            db.add(grade)
        
        # 提交所有更改
        db.commit()
        print("✓ 测试数据创建完成")
        
        # 显示统计信息
        user_count = db.query(User).count()
        announcement_count = db.query(Announcement).count()
        schedule_count = db.query(Schedule).count()
        notice_count = db.query(Notice).count()
        event_count = db.query(Event).count()
        grade_count = db.query(Grade).count()
        
        print(f"\n数据库初始化完成！")
        print(f"✓ 创建用户: {user_count} 个")
        print(f"✓ 创建公告: {announcement_count} 个")
        print(f"✓ 创建课程: {schedule_count} 个")
        print(f"✓ 创建通知: {notice_count} 个")
        print(f"✓ 创建活动: {event_count} 个")
        print(f"✓ 创建成绩: {grade_count} 个")
        print(f"\n现在可以启动后端服务：python run.py")
        print(f"API文档地址：http://localhost:8000/docs")
        print(f"公告接口：http://localhost:8000/api/announcements")
        print(f"课表接口：http://localhost:8000/api/schedule")
        print(f"通知接口：http://localhost:8000/api/notices")
        print(f"活动接口：http://localhost:8000/api/events")
        print(f"成绩接口：http://localhost:8000/api/grades")
        
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("=== SZTU-iCampus 数据库初始化工具 ===\n")
    init_database() 