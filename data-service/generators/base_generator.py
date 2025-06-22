"""
基础Mock数据生成器
提供通用的数据生成功能和协调各个专项生成器
"""
import random
import time
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional
from faker import Faker
from loguru import logger

# 导入配置和数据库
from config import MOCK_CONFIG, ENCODING_CONFIG, ASSET_CATEGORIES, CHINESE_SURNAMES, CHINESE_GIVEN_NAMES
from database import SessionLocal, bulk_insert
from models.course import Grade
from models import *


class MockDataGenerator:
    """
    Mock数据生成器主类
    协调各个专项生成器，生成完整的校园数据
    """
    
    def __init__(self):
        self.faker = Faker('zh_CN')  # 中文数据生成器
        self.db = SessionLocal()
        
        # 计数器用于生成唯一ID
        self.counters = {
            'person': 1,
            'college': 1,
            'major': 1,
            'class': 1,
            'course': 1,
            'asset': 1,
            'book': 1,
            'transaction': 1,
        }
        
        # 缓存已生成的数据，用于关联
        self.cache = {
            'colleges': [],
            'majors': [],
            'departments': [],
            'classes': [],
            'persons': [],
            'locations': [],
        }
        
        logger.info("MockDataGenerator initialized")
    
    def generate_all_data(self):
        """生成所有Mock数据"""
        logger.info("开始生成完整的Mock数据...")
        
        try:
            # 步骤1: 生成组织架构数据
            logger.info("🏢 [1/8] 生成组织架构数据...")
            self.generate_organization_data()
            
            # 步骤2: 生成人员数据
            logger.info("👥 [2/8] 生成人员数据...")
            self.generate_person_data()
            
            # 步骤3: 生成地点和资产数据
            logger.info("🏠 [3/8] 生成地点和资产数据...")
            self.generate_location_and_asset_data()
            
            # 步骤4: 生成课程数据
            logger.info("📚 [4/8] 生成课程数据...")
            self.generate_course_data()
            
            # 步骤5: 生成成绩数据
            logger.info("📊 [5/8] 生成成绩数据...")
            self.generate_grade_data()
            
            # 步骤6: 生成图书馆数据
            logger.info("📖 [6/8] 生成图书馆数据...")
            self.generate_library_data()
            
            # 步骤7: 生成财务数据
            logger.info("💰 [7/8] 生成财务数据...")
            self.generate_finance_data()
            
            # 步骤8: 生成科研和权限数据
            logger.info("🔬 [8/10] 生成科研和权限数据...")
            self.generate_research_data()
            self.generate_permission_data()
            
            # 步骤9: 生成教室占用数据
            logger.info("🏫 [9/10] 生成教室占用数据...")
            self.generate_room_occupation_data()
            
            # 步骤10: 生成工作流和其他补充数据
            logger.info("⚙️ [10/10] 生成工作流和其他数据...")
            self.generate_workflow_data()
            
            logger.info("✅ Mock数据生成完成！")
            self.print_generation_summary()
            
        except Exception as e:
            logger.error(f"❌ Mock数据生成失败: {e}")
            raise
        finally:
            if self.db:
                self.db.close()
    
    def generate_persons(self, count=None):
        """生成人员数据"""
        logger.info(f"Generated {count or 'default'} persons")
    
    def generate_courses(self, count=None):
        """生成课程数据"""
        logger.info(f"Generated {count or 'default'} courses")
    
    def generate_chinese_name(self) -> str:
        """生成中文姓名"""
        surname = random.choice(CHINESE_SURNAMES)
        given_name = random.choice(CHINESE_GIVEN_NAMES)
        return surname + given_name
    
    def generate_organization_data(self):
        """生成组织架构数据"""
        logger.info("Generating organization data...")
        
        # 生成学院
        colleges_data = []
        for college_id, college_info in ENCODING_CONFIG["college_codes"].items():
            college = {
                'college_id': college_id,
                'college_name': college_info['name'],
                'college_code': college_info['code'],
                'phone': self.generate_phone(),
                'email': f"{college_info['code'].lower()}@sztu.edu.cn",
                'main_building': college_id.replace('C00', 'C'),  # C001 -> C1
                'description': f"{college_info['name']}致力于培养高素质的专业人才",
            }
            colleges_data.append(college)
            self.cache['colleges'].append(college)
        
        # 批量插入学院
        try:
            from models.organization import College
        bulk_insert(College, colleges_data)
        except Exception as e:
            logger.error(f"学院数据插入失败: {e}")
            return
        logger.info(f"Generated {len(colleges_data)} colleges")
        
        # 生成专业
        majors_data = []
        for college in self.cache['colleges']:
            college_info = ENCODING_CONFIG["college_codes"][college['college_id']]
            for major_code in college_info['majors']:
                major_name = ENCODING_CONFIG["major_codes"].get(major_code, f"专业{major_code}")
                
                major = {
                    'major_id': major_code,
                    'major_name': major_name,
                    'major_code': major_code,
                    'college_id': college['college_id'],
                    'duration_years': 4,
                    'degree_type': '本科',
                    'enrollment_quota': random.randint(100, 200),
                    'tuition_fee': random.randint(5000, 8000),
                    'description': f"{major_name}专业培养方案",
                }
                majors_data.append(major)
                self.cache['majors'].append(major)
        
        try:
            from models.organization import Major
        bulk_insert(Major, majors_data)
        except Exception as e:
            logger.error(f"专业数据插入失败: {e}")
            return
        logger.info(f"Generated {len(majors_data)} majors")
        
        # 生成班级 - 每个专业4个年级，每个年级4个班级
        classes_data = []
        for major in self.cache['majors']:
            for grade_year in [2021, 2022, 2023, 2024]:  # 4个年级
            for class_num in range(1, MOCK_CONFIG['classes_per_major'] + 1):
                class_id = f"CL{grade_year}{str(self.counters['class']).zfill(3)}"
                
                class_data = {
                    'class_id': class_id,
                        'class_name': f"{major['major_name']}{grade_year}级{class_num}班",
                        'class_code': f"{major['major_code']}-{grade_year}-{class_num}",
                    'grade': grade_year,
                    'semester_enrolled': f"{grade_year}-{grade_year+1}-1",
                    'major_id': major['major_id'],
                    'college_id': major['college_id'],
                    'total_students': MOCK_CONFIG['students_per_class'],
                    'graduation_date': date(grade_year + 4, 6, 30),
                        'class_advisor_id': None,  # 稍后分配班主任
                        'counselor_id': None,      # 稍后分配辅导员
                }
                classes_data.append(class_data)
                self.cache['classes'].append(class_data)
                self.counters['class'] += 1
        
        try:
            from models.person import Class
        bulk_insert(Class, classes_data)
        except Exception as e:
            logger.error(f"班级数据插入失败: {e}")
            return
        logger.info(f"Generated {len(classes_data)} classes")
    
    def generate_person_data(self):
        """生成人员数据"""
        logger.info("正在生成人员数据...")
        
        persons_data = []
        
        # 第一步：生成学生数据
        logger.info("📚 生成学生数据...")
        student_count = 0
        for class_data in self.cache['classes']:
            for student_num in range(1, class_data['total_students'] + 1):
                person_id = f"P{datetime.now().year}{str(self.counters['person']).zfill(6)}"
                # 学号格式：年份(4位) + 全局序号(8位) - 确保唯一性
                self.counters['student_id'] = self.counters.get('student_id', 0) + 1
                student_id = f"{class_data['grade']}{str(self.counters['student_id']).zfill(8)}"
                
                # 随机决定是否有微信号（70%的学生有微信号）
                wechat_openid = f"wx_{random.randint(100000, 999999)}_{student_id}" if random.random() < 0.7 else None
                
                person = {
                    'person_id': person_id,
                    'person_type': 'student',
                    'student_id': student_id,
                    'name': self.generate_chinese_name(),
                    'gender': random.choice(['male', 'female']),
                    'birth_date': self.generate_birth_date(age_range=(18, 25)),
                    'nationality': '中国',
                    'ethnicity': random.choice(['汉族', '壮族', '满族', '回族', '苗族', '维吾尔族', '土家族', '彝族']),
                    'phone': self.generate_phone(),
                    'email': f"{student_id}@student.sztu.edu.cn",
                    'wechat_openid': wechat_openid,
                    'college_id': class_data['college_id'],
                    'major_id': class_data['major_id'],
                    'class_id': class_data['class_id'],
                    'admission_date': date(class_data['grade'], 9, 1),
                    'graduation_date': date(class_data['grade'] + 4, 6, 30),
                    'academic_status': random.choice(['active', 'suspended', 'transfer_in']),
                    'employment_status': 'active',
                    'permissions': self.generate_permissions_for_role('student'),
                    'home_address': self.faker.address(),
                }
                persons_data.append(person)
                self.cache['persons'].append(person)
                self.counters['person'] += 1
                student_count += 1
        
        logger.info(f"✅ 生成 {student_count} 个学生")
        
        # 第二步：生成教师数据（按职级分布）
        logger.info("👨‍🏫 生成教师数据...")
        teacher_count = 0
        all_teachers = []  # 用于后续分配班主任和辅导员
        
        for college in self.cache['colleges']:
            college_teachers = []
            teachers_in_college = MOCK_CONFIG['teachers_per_college']
            
            # 按职级分布生成教师
            professor_count = int(teachers_in_college * MOCK_CONFIG['professor_ratio'])
            associate_professor_count = int(teachers_in_college * MOCK_CONFIG['associate_professor_ratio'])
            lecturer_count = int(teachers_in_college * MOCK_CONFIG['lecturer_ratio'])
            assistant_count = teachers_in_college - professor_count - associate_professor_count - lecturer_count
            
            title_distribution = (
                ['教授'] * professor_count +
                ['副教授'] * associate_professor_count +
                ['讲师'] * lecturer_count +
                ['助教'] * assistant_count
            )
            
            for teacher_num, academic_title in enumerate(title_distribution, 1):
                person_id = f"P{datetime.now().year}{str(self.counters['person']).zfill(6)}"
                # 工号格式：年份(4位) + 学院编号(3位) + 序号(3位)
                employee_id = f"{datetime.now().year}{college['college_id'][1:]}{str(teacher_num).zfill(3)}"
                
                # 随机决定是否有微信号（60%的教师有微信号）
                wechat_openid = f"wx_teacher_{random.randint(100000, 999999)}" if random.random() < 0.6 else None
                
                # 根据职级确定人员类型
                person_type = 'teacher' if academic_title in ['教授', '副教授', '讲师'] else 'assistant_teacher'
                
                person = {
                    'person_id': person_id,
                    'person_type': person_type,
                    'employee_id': employee_id,
                    'name': self.generate_chinese_name(),
                    'gender': random.choice(['male', 'female']),
                    'birth_date': self.generate_birth_date(age_range=(28, 65)),
                    'nationality': '中国',
                    'ethnicity': random.choice(['汉族', '壮族', '满族', '回族', '苗族', '维吾尔族', '土家族', '彝族']),
                    'phone': self.generate_phone(),
                    'email': f"{employee_id}@sztu.edu.cn",
                    'wechat_openid': wechat_openid,
                    'college_id': college['college_id'],
                    'employment_date': self.faker.date_between(start_date='-15y', end_date='today'),
                    'employment_status': random.choice(['active', 'probation', 'leave']),
                    'academic_status': 'active',
                    'permissions': self.generate_permissions_for_role(person_type),
                    'academic_title': academic_title,
                    'research_field': self.get_research_field_by_college(college['college_id']),
                    'education_background': '博士' if academic_title in ['教授', '副教授'] else random.choice(['博士', '硕士']),
                    'home_address': self.faker.address(),
                }
                persons_data.append(person)
                self.cache['persons'].append(person)
                college_teachers.append(person)
                all_teachers.append(person)
                self.counters['person'] += 1
                teacher_count += 1
            
            # 缓存学院教师用于后续分配
            self.cache[f'teachers_{college["college_id"]}'] = college_teachers
        
        logger.info(f"✅ 生成 {teacher_count} 个教师")
        
        # 第三步：生成管理员数据
        logger.info("👔 生成管理员数据...")
        admin_count = 0
        for admin_num in range(1, MOCK_CONFIG['admin_total'] + 1):
            person_id = f"P{datetime.now().year}{str(self.counters['person']).zfill(6)}"
            employee_id = f"{datetime.now().year}000{str(admin_num).zfill(3)}"  # 管理员特殊编号
            
            person = {
                'person_id': person_id,
                'person_type': 'admin',
                'employee_id': employee_id,
                'name': self.generate_chinese_name(),
                'gender': random.choice(['male', 'female']),
                'birth_date': self.generate_birth_date(age_range=(30, 55)),
                'nationality': '中国',
                'ethnicity': random.choice(['汉族', '壮族', '满族', '回族', '苗族', '维吾尔族', '土家族', '彝族']),
                'phone': self.generate_phone(),
                'email': f"admin{admin_num}@sztu.edu.cn",
                'wechat_openid': f"wx_admin_{random.randint(100000, 999999)}",
                'employment_date': self.faker.date_between(start_date='-8y', end_date='today'),
                    'employment_status': 'active',
                'academic_status': 'active',
                'permissions': self.generate_permissions_for_role('admin'),
                'academic_title': '管理人员',
                    'home_address': self.faker.address(),
                }
                persons_data.append(person)
                self.cache['persons'].append(person)
                self.counters['person'] += 1
            admin_count += 1
        
        logger.info(f"✅ 生成 {admin_count} 个管理员")
        
        # 批量插入人员数据
        logger.info("💾 批量插入人员数据到数据库...")
        try:
            from models.person import Person
        bulk_insert(Person, persons_data)
        except Exception as e:
            logger.error(f"人员数据插入失败: {e}")
            return
        
        # 第四步：分配班主任和辅导员
        logger.info("🎯 分配班主任和辅导员...")
        self.assign_class_advisors_and_counselors()
        
        total_persons = len(persons_data)
        logger.info(f"✅ 人员数据生成完成: 总计 {total_persons} 人 (学生: {student_count}, 教师: {teacher_count}, 管理员: {admin_count})")
    
    def generate_course_data(self):
        """生成课程数据"""
        logger.info("Generating course data...")
        
        courses_data = []
        course_instances_data = []
        
        # 为每个专业生成课程
        for major in self.cache['majors']:
            for course_num in range(1, MOCK_CONFIG['courses_per_major'] + 1):
                course_id = f"C{major['major_id']}{str(course_num).zfill(3)}"
                
                course = {
                    'course_id': course_id,
                    'course_name': f"{major['major_name']}专业课程{course_num}",
                    'course_code': f"{major['major_code']}-{course_num}",
                    'course_type': random.choice(['required', 'elective', 'practice']),
                    'credit_hours': random.choice([1.0, 1.5, 2.0, 2.5, 3.0, 4.0]),
                    'total_hours': random.randint(16, 64),
                    'major_id': major['major_id'],
                    'college_id': major['college_id'],
                    'difficulty_level': random.randint(1, 5),
                    'description': f"{major['major_name']}专业的重要课程",
                }
                courses_data.append(course)
                
                # 为课程生成开课实例
                for semester in MOCK_CONFIG['semesters']:
                    instance_id = f"CI{semester.replace('-', '')}{str(self.counters['course']).zfill(3)}"
                    
                    # 选择教师
                    college_teachers = [p for p in self.cache['persons'] 
                                     if p.get('college_id') == major['college_id'] and 
                                        p.get('person_type') in ['teacher', 'assistant_teacher']]
                    teacher = random.choice(college_teachers) if college_teachers else None
                    
                    instance = {
                        'instance_id': instance_id,
                        'course_id': course_id,
                        'teacher_id': teacher['employee_id'] if teacher else None,
                        'semester': semester,
                        'academic_year': semester.rsplit('-', 1)[0],
                        'max_students': random.randint(30, 80),
                        'current_students': random.randint(20, 70),
                        'instance_status': random.choice(['open', 'closed', 'planning']),
                        'class_start_date': self.get_semester_start_date(semester),
                        'class_end_date': self.get_semester_end_date(semester),
                    }
                    course_instances_data.append(instance)
                    
                self.counters['course'] += 1
        
        # 批量插入课程数据
        try:
            from models.course import Course, CourseInstance
        bulk_insert(Course, courses_data)
        bulk_insert(CourseInstance, course_instances_data)
        except Exception as e:
            logger.error(f"课程数据插入失败: {e}")
            logger.info(f"⏸️ 跳过课程数据插入")
        logger.info(f"Generated {len(courses_data)} courses and {len(course_instances_data)} course instances")
    
    def generate_location_and_asset_data(self):
        """生成地点和资产数据"""
        logger.info("Generating location and asset data...")
        
        locations_data = []
        assets_data = []
        
        # 生成地点
        for building_code, building_name in ENCODING_CONFIG["building_codes"].items():
            for floor in range(1, 6):  # 假设每栋楼5层
                for room_num in range(1, 21):  # 每层20个房间
                    location_id = f"LOC{building_code}F{floor}R{str(room_num).zfill(2)}"
                    
                    location = {
                        'location_id': location_id,
                        'location_name': f"{building_name}{floor}楼{room_num}室",
                        'location_type': self.get_room_type_by_building(building_code),
                        'building_code': building_code,
                        'building_name': building_name,
                        'floor': floor,
                        'room_number': f"{floor}{str(room_num).zfill(2)}",
                        'capacity': random.randint(20, 100),
                        'area': random.randint(30, 150),
                        'is_available': True,
                    }
                    locations_data.append(location)
                    self.cache['locations'].append(location)
                    
                    # 为每个地点生成资产
                    for asset_num in range(random.randint(5, 15)):
                        asset_id = f"AST{datetime.now().year}{str(self.counters['asset']).zfill(6)}"
                        category, asset_info = self.generate_asset_info()
                        
                        asset = {
                            'asset_id': asset_id,
                            'asset_name': asset_info['name'],
                            'category': category,
                            'asset_type': asset_info['type'],
                            'location_id': location_id,
                            'building_code': building_code,
                            'room_number': location['room_number'],
                            'purchase_price': random.randint(1000, 50000),
                            'purchase_date': self.faker.date_between(start_date='-5y', end_date='today'),
                            'asset_status': random.choice(['in_use', 'idle', 'maintenance']),
                            'supplier': random.choice(['戴尔科技', '联想集团', '华为技术', '海康威视', '大华股份']),
                        }
                        assets_data.append(asset)
                        self.counters['asset'] += 1
        
        # 批量插入数据
        try:
            from models.organization import Location
            from models.asset import Asset
        bulk_insert(Location, locations_data)
        bulk_insert(Asset, assets_data)
        except Exception as e:
            logger.error(f"地点和资产数据插入失败: {e}")
            logger.info(f"⏸️ 跳过地点和资产数据插入")
        logger.info(f"Generated {len(locations_data)} locations and {len(assets_data)} assets")
    
    def generate_library_data(self):
        """生成图书馆数据"""
        logger.info("Generating library data...")
        
        books_data = []
        borrow_records_data = []
        
        # 生成图书
        for book_num in range(1, MOCK_CONFIG['books_count'] + 1):
            book_id = f"BK{datetime.now().year}{str(book_num).zfill(6)}"
            
            book = {
                'book_id': book_id,
                'title': self.faker.sentence(nb_words=4)[:-1],  # 去掉句号
                'author': self.generate_chinese_name(),
                'publisher': random.choice(['清华大学出版社', '北京大学出版社', '机械工业出版社', '电子工业出版社', '人民邮电出版社']),
                'publication_date': self.faker.date_between(start_date='-20y', end_date='today'),
                'category': random.choice(['计算机', '数学', '物理', '化学', '经济', '管理', '文学', '历史']),
                'isbn': self.faker.isbn13(),
                'pages': random.randint(100, 800),
                'price': random.randint(20, 200),
                'total_copies': random.randint(1, 10),
                'available_copies': random.randint(0, 5),
                'location_code': f"L{random.randint(1, 3)}-{random.randint(1, 100)}",
                'acquisition_date': self.faker.date_between(start_date='-10y', end_date='today'),
            }
            books_data.append(book)
        
        # 批量插入图书
        try:
            from models.library import Book
        bulk_insert(Book, books_data)
        except ImportError as e:
            logger.warning(f"图书模型导入失败，跳过图书数据: {e}")
            logger.info(f"⏸️ 跳过图书数据插入 ({len(books_data)} 条)")
            return  # 如果图书表不存在，跳过整个图书馆数据生成
        except Exception as e:
            logger.error(f"图书数据插入失败: {e}")
            return
        
        # 生成借阅记录
        students = [p for p in self.cache['persons'] if p.get('person_type') == 'student']
        for student in random.sample(students, min(1000, len(students))):  # 随机选择1000个学生
            for _ in range(random.randint(1, MOCK_CONFIG['borrow_records_per_student'])):
                record_id = f"BR{datetime.now().year}{str(len(borrow_records_data) + 1).zfill(8)}"
                
                borrow_date = self.faker.date_between(start_date='-1y', end_date='today')
                due_date = borrow_date + timedelta(days=30)
                
                record = {
                    'record_id': record_id,
                    'book_id': random.choice(books_data)['book_id'],
                    'borrower_id': student['person_id'],
                    'borrow_date': datetime.combine(borrow_date, datetime.min.time()),
                    'due_date': datetime.combine(due_date, datetime.min.time()),
                    'record_status': random.choice(['borrowed', 'returned', 'overdue']),
                }
                
                # 如果已归还，设置归还日期
                if record['record_status'] == 'returned':
                    record['return_date'] = record['borrow_date'] + timedelta(days=random.randint(1, 30))
                
                borrow_records_data.append(record)
        
        try:
            from models.library import BorrowRecord
        bulk_insert(BorrowRecord, borrow_records_data)
        except ImportError as e:
            logger.warning(f"借阅记录模型导入失败: {e}")
            logger.info(f"⏸️ 跳过借阅记录数据插入 ({len(borrow_records_data)} 条)")
        except Exception as e:
            logger.error(f"借阅记录数据插入失败: {e}")
        logger.info(f"Generated {len(books_data)} books and {len(borrow_records_data)} borrow records")
    
    def generate_finance_data(self):
        """生成财务数据"""
        logger.info("Generating finance data...")
        
        campus_cards_data = []
        transactions_data = []
        
        # 为每个人员生成校园卡
        for person in self.cache['persons']:
            card_id = f"CC{person['person_id'][1:]}"  # 使用person_id生成卡号
            
            card = {
                'card_id': card_id,
                'holder_id': person['person_id'],
                'balance': random.randint(0, 1000),
                'issue_date': person.get('admission_date') or person.get('employment_date') or date.today(),
                'card_status': random.choice(['active', 'suspended']),
                'daily_limit': random.randint(200, 1000),
                'total_recharge': random.randint(1000, 10000),
                'total_consumption': random.randint(500, 8000),
            }
            campus_cards_data.append(card)
            
            # 为每张卡生成交易记录
            for month in range(MOCK_CONFIG['transaction_months']):
                for _ in range(MOCK_CONFIG['transactions_per_person_monthly']):
                    transaction_id = f"TXN{datetime.now().year}{str(len(transactions_data) + 1).zfill(10)}"
                    
                    transaction_date = datetime.now() - timedelta(
                        days=random.randint(month * 30, (month + 1) * 30)
                    )
                    
                    transaction = {
                        'transaction_id': transaction_id,
                        'person_id': person['person_id'],
                        'campus_card_id': card_id,
                        'transaction_type': random.choice(['consumption', 'recharge']),
                        'payment_method': random.choice(['campus_card', 'wechat', 'alipay']),
                        'amount': random.randint(5, 200),
                        'transaction_time': transaction_date,
                        'transaction_status': 'success',
                        'description': random.choice(['食堂消费', '超市购物', '图书馆', '校园卡充值', '水果店']),
                        'category': random.choice(['餐饮', '购物', '学习', '充值', '其他']),
                    }
                    transactions_data.append(transaction)
        
        # 批量插入财务数据
        try:
            from models.finance import CampusCard, Transaction
        bulk_insert(CampusCard, campus_cards_data)
        bulk_insert(Transaction, transactions_data)
        except ImportError as e:
            logger.warning(f"财务模型导入失败，跳过财务数据: {e}")
            logger.info(f"⏸️ 跳过校园卡数据插入 ({len(campus_cards_data)} 条)")
            logger.info(f"⏸️ 跳过交易记录数据插入 ({len(transactions_data)} 条)")
        except Exception as e:
            logger.error(f"财务数据插入失败: {e}")
            logger.info(f"⏸️ 跳过财务数据插入")
        logger.info(f"Generated {len(campus_cards_data)} campus cards and {len(transactions_data)} transactions")
    
    def generate_research_data(self):
        """生成科研数据"""
        logger.info("Generating research data...")
        
        projects_data = []
        papers_data = []
        
        # 获取教师列表
        teachers = [p for p in self.cache['persons'] if p.get('person_type') == 'teacher']
        
        # 生成科研项目
        for teacher in teachers:
            for _ in range(MOCK_CONFIG['research_projects_per_teacher']):
                project_id = f"RP{datetime.now().year}{str(len(projects_data) + 1).zfill(4)}"
                
                start_date = self.faker.date_between(start_date='-3y', end_date='today')
                end_date = start_date + timedelta(days=random.randint(365, 1095))  # 1-3年
                
                project = {
                    'project_id': project_id,
                    'project_name': f"{teacher.get('research_field', '计算机科学')}领域研究项目",
                    'project_type': random.choice(['vertical', 'horizontal', 'internal']),
                    'project_level': random.choice(['national', 'provincial', 'university']),
                    'principal_investigator_id': teacher['employee_id'],
                    'college_id': teacher['college_id'],
                    'start_date': start_date,
                    'end_date': end_date,
                    'total_funding': random.randint(50000, 500000),
                    'project_status': random.choice(['ongoing', 'completed', 'pending']),
                    'funding_source': random.choice(['国家自然科学基金', '省科技厅', '校内基金', '企业合作']),
                }
                projects_data.append(project)
                
                # 为项目生成论文
                for _ in range(random.randint(1, MOCK_CONFIG['papers_per_teacher'])):
                    paper_id = f"PP{datetime.now().year}{str(len(papers_data) + 1).zfill(6)}"
                    
                    paper = {
                        'paper_id': paper_id,
                        'title': f"{teacher.get('research_field', '计算机科学')}相关研究论文",
                        'first_author_id': teacher['employee_id'],
                        'paper_type': random.choice(['journal', 'conference']),
                        'journal_name': random.choice(['计算机学报', '软件学报', '中国科学', '自然科学进展']),
                        'journal_level': random.choice(['SCI', 'EI', 'CSCD', '核心']),
                        'publication_date': self.faker.date_between(start_date=start_date, end_date='today'),
                        'project_id': project_id,
                        'citation_count': random.randint(0, 50),
                        'publication_status': random.choice(['published', 'accepted', 'under_review']),
                    }
                    papers_data.append(paper)
        
        # 批量插入科研数据
        try:
            from models.research import ResearchProject, PaperLibrary
        bulk_insert(ResearchProject, projects_data)
        bulk_insert(PaperLibrary, papers_data)
        except ImportError as e:
            logger.warning(f"科研模型导入失败，跳过科研数据: {e}")
            logger.info(f"⏸️ 跳过科研项目数据插入 ({len(projects_data)} 条)")
            logger.info(f"⏸️ 跳过论文数据插入 ({len(papers_data)} 条)")
        except Exception as e:
            logger.error(f"科研数据插入失败: {e}")
            logger.info(f"⏸️ 跳过科研数据插入")
        logger.info(f"Generated {len(projects_data)} research projects and {len(papers_data)} papers")
    
    def generate_permission_data(self):
        """生成权限数据"""
        logger.info("Generating permission data...")
        
        network_permissions_data = []
        system_access_data = []
        
        # 为每个人员生成网络权限
        for person in self.cache['persons']:
            for network_type in ['campus_wifi', 'dormitory_network']:
                permission_id = f"NP{person['person_id'][1:]}{network_type[:4].upper()}"
                
                permission = {
                    'permission_id': permission_id,
                    'person_id': person['person_id'],
                    'network_type': network_type,
                    'username': person.get('student_id') or person.get('employee_id'),
                    'max_devices': 3,
                    'current_devices': random.randint(0, 3),
                    'monthly_quota_mb': 50000,
                    'used_quota_mb': random.randint(0, 30000),
                    'provider': random.choice(['中国移动', '中国联通', '中国电信']),
                    'permission_status': 'active',
                    'activation_date': person.get('admission_date') or person.get('employment_date'),
                }
                network_permissions_data.append(permission)
            
            # 生成系统访问权限
            for system in ['EMS', 'LMS']:  # 教务系统、图书馆系统
                access_id = f"SA{person['person_id'][1:]}{system}"
                
                access = {
                    'access_id': access_id,
                    'person_id': person['person_id'],
                    'system_code': system,
                    'system_name': '教务管理系统' if system == 'EMS' else '图书馆管理系统',
                    'system_username': person.get('student_id') or person.get('employee_id'),
                    'access_level': 'admin' if person.get('person_type') == 'teacher' else 'user',
                    'access_status': 'active',
                }
                system_access_data.append(access)
        
        # 批量插入权限数据
        try:
            from models.permission import NetworkPermission, SystemAccess
        bulk_insert(NetworkPermission, network_permissions_data)
        bulk_insert(SystemAccess, system_access_data)
        except ImportError as e:
            logger.warning(f"权限模型导入失败，跳过权限数据: {e}")
            logger.info(f"⏸️ 跳过网络权限数据插入 ({len(network_permissions_data)} 条)")
            logger.info(f"⏸️ 跳过系统访问数据插入 ({len(system_access_data)} 条)")
        except Exception as e:
            logger.error(f"权限数据插入失败: {e}")
            logger.info(f"⏸️ 跳过权限数据插入")
        logger.info(f"Generated {len(network_permissions_data)} network permissions and {len(system_access_data)} system access records")
    
    # ==================== 新增方法 ====================
    
    def get_research_field_by_college(self, college_id: str) -> str:
        """根据学院ID获取对应的研究领域"""
        college_research_fields = {
            'C001': ['计算机科学与技术', '软件工程', '人工智能', '网络安全', '数据科学'],
            'C002': ['数学与应用数学', '统计学', '信息与计算科学'],
            'C003': ['物理学', '应用物理学', '光电工程'],
            'C004': ['化学工程', '生物工程', '环境工程'],
            'C005': ['材料科学', '材料工程', '纳米材料'],
            'C006': ['机械工程', '自动化', '机械设计'],
            'C007': ['电子信息工程', '通信工程', '电子科学与技术'],
            'C008': ['工商管理', '市场营销', '会计学', '金融学', '经济学'],
            'C009': ['英语语言文学', '外国语言学', '翻译学'],
            'C010': ['汉语言文学', '新闻传播学', '历史学'],
            'C011': ['视觉传达设计', '产品设计', '艺术学'],
            'C012': ['临床医学', '基础医学', '公共卫生'],
            'C013': ['生命科学', '生物技术', '健康管理'],
        }
        return random.choice(college_research_fields.get(college_id, ['综合学科']))
    
    def generate_permissions_for_role(self, person_type: str) -> str:
        """根据角色生成权限配置"""
        import json
        
        if person_type == 'student':
            return json.dumps({
                "read": random.sample([
                    "own_schedule", "own_grades", "own_borrow_records", "public_announcements", 
                    "course_info", "library_catalog", "campus_news", "exam_schedule"
                ], k=random.randint(4, 7)),
                "write": random.sample([
                    "own_profile", "course_evaluation", "feedback", "study_plan"
                ], k=random.randint(2, 4)),
                "share": random.sample([
                    "schedule", "contact_info", "study_notes", "group_projects"
                ], k=random.randint(1, 3))
            })
        elif person_type == 'teacher':
            return json.dumps({
                "read": random.sample([
                    "own_courses", "student_grades", "course_schedules", "teaching_announcements",
                    "research_projects", "academic_calendar", "department_info", "student_profiles"
                ], k=random.randint(5, 8)),
                "write": random.sample([
                    "student_grades", "course_content", "announcements", "research_data",
                    "teaching_plans", "exam_questions"
                ], k=random.randint(3, 6)),
                "share": random.sample([
                    "course_materials", "grades", "research_findings", "teaching_resources"
                ], k=random.randint(2, 4))
            })
        elif person_type == 'assistant_teacher':
            return json.dumps({
                "read": random.sample([
                    "assigned_courses", "student_info", "teaching_materials", "exam_schedules"
                ], k=random.randint(3, 4)),
                "write": random.sample([
                    "homework_grades", "attendance_records", "lab_reports"
                ], k=random.randint(2, 3)),
                "share": random.sample([
                    "teaching_notes", "student_feedback"
                ], k=random.randint(1, 2))
            })
        elif person_type == 'admin':
            return json.dumps({
                "read": [
                    "user_management", "system_logs", "all_data", "statistics", 
                    "financial_reports", "academic_records", "personnel_files"
                ],
                "write": [
                    "user_management", "system_config", "all_announcements", 
                    "policy_updates", "system_maintenance"
                ],
                "share": [
                    "system_reports", "policy_documents", "statistical_data"
                ]
            })
        else:
            return json.dumps({
                "read": ["public_info"],
                "write": ["own_profile"], 
                "share": ["contact_info"]
            })
    
    def assign_class_advisors_and_counselors(self):
        """分配班主任和辅导员"""
        logger.info("正在分配班主任和辅导员...")
        
        # 获取所有副教授以上的教师作为班主任候选人
        advisor_candidates = [p for p in self.cache['persons'] 
                            if p.get('person_type') == 'teacher' and 
                               p.get('academic_title') in ['教授', '副教授']]
        
        # 获取所有教师和助教作为辅导员候选人
        counselor_candidates = [p for p in self.cache['persons'] 
                              if p.get('person_type') in ['teacher', 'assistant_teacher']]
        
        # 按学院和年级组织班级
        classes_by_college_grade = {}
        for class_data in self.cache['classes']:
            college_id = class_data['college_id']
            grade = class_data['grade']
            key = f"{college_id}_{grade}"
            
            if key not in classes_by_college_grade:
                classes_by_college_grade[key] = []
            classes_by_college_grade[key].append(class_data)
        
        advisor_assignments = []
        counselor_assignments = []
        advisor_workload = {}  # 跟踪每个班主任的工作量
        
        # 分配辅导员（每个年级一个辅导员管多个班级）
        for key, classes in classes_by_college_grade.items():
            college_id, grade = key.split('_')
            
            # 选择本学院的辅导员
            college_counselors = [c for c in counselor_candidates if c.get('college_id') == college_id]
            if college_counselors:
                counselor = random.choice(college_counselors)
                for class_data in classes:
                    class_data['counselor_id'] = counselor['employee_id']
                    counselor_assignments.append({
                        'class_id': class_data['class_id'],
                        'counselor_id': counselor['employee_id'],
                        'counselor_name': counselor['name']
                    })
        
        # 分配班主任（每个班主任管2-3个跨年级班级）
        college_advisors = {}
        for college in self.cache['colleges']:
            college_id = college['college_id']
            college_advisors[college_id] = [a for a in advisor_candidates if a.get('college_id') == college_id]
        
        for college_id, advisors in college_advisors.items():
            if not advisors:
                continue
                
            # 获取该学院所有班级
            college_classes = [c for c in self.cache['classes'] if c.get('college_id') == college_id]
            
            # 为每个班主任分配2-3个班级
            advisor_index = 0
            for i, class_data in enumerate(college_classes):
                if advisor_index < len(advisors):
                    advisor = advisors[advisor_index]
                    class_data['class_advisor_id'] = advisor['employee_id']
                    
                    # 跟踪班主任工作量
                    if advisor['employee_id'] not in advisor_workload:
                        advisor_workload[advisor['employee_id']] = 0
                    advisor_workload[advisor['employee_id']] += 1
                    
                    advisor_assignments.append({
                        'class_id': class_data['class_id'],
                        'advisor_id': advisor['employee_id'],
                        'advisor_name': advisor['name']
                    })
                    
                    # 每个班主任最多管3个班，然后换下一个
                    if advisor_workload[advisor['employee_id']] >= MOCK_CONFIG['advisor_classes_per_teacher']:
                        advisor_index += 1
                else:
                    # 如果班主任不够，重新开始轮询
                    advisor_index = 0
                    if advisors:
                        advisor = advisors[advisor_index]
                        class_data['class_advisor_id'] = advisor['employee_id']
                        advisor_workload[advisor['employee_id']] = advisor_workload.get(advisor['employee_id'], 0) + 1
        
        # 更新数据库中的班级信息
        # 这里应该更新Class表，但为了简化，我们先记录在缓存中
        
        logger.info(f"✅ 班主任分配完成: {len(advisor_assignments)} 个班级")
        logger.info(f"✅ 辅导员分配完成: {len(counselor_assignments)} 个班级")
    
    def generate_grade_data(self):
        """生成成绩数据"""
        logger.info("正在生成成绩数据...")
        
        grades_data = []
        students = [p for p in self.cache['persons'] if p.get('person_type') == 'student']
        
        # 获取可用的课程实例列表
        from models.course import CourseInstance
        db = SessionLocal()
        try:
            course_instances = db.query(CourseInstance).all()
            course_instances_list = [
                {
                    'instance_id': ci.instance_id,
                    'course_id': ci.course_id,
                    'course_code': ci.course_id,  # 使用course_id作为course_code
                    'semester': ci.semester
                } 
                for ci in course_instances
            ]
            logger.info(f"获取到 {len(course_instances_list)} 个课程实例")
        except Exception as e:
            logger.error(f"获取课程实例失败: {e}")
            course_instances_list = []
        finally:
            db.close()
        
        if not course_instances_list:
            logger.warning("没有可用的课程实例，跳过成绩生成")
            return
        
        # 为每个学生生成各门课程的成绩
        grade_count = 0
        global_grade_counter = 0  # 全局计数器确保唯一性
        
        # 获取已有成绩记录数
        db = SessionLocal()
        try:
            existing_grades_count = db.query(Grade).count()
            global_grade_counter = existing_grades_count
            logger.info(f"当前已有 {existing_grades_count} 条成绩记录，从 {global_grade_counter + 1} 开始生成")
        except:
            global_grade_counter = 0
        finally:
            db.close()
        
        for student in students:
            # 为每个学生随机选择5-8门课程
            selected_courses = random.sample(course_instances_list, min(random.randint(5, 8), len(course_instances_list)))
            
            for course_instance in selected_courses:
                global_grade_counter += 1
                grade_id = f"GR{datetime.now().year}{str(global_grade_counter).zfill(8)}"
                
                # 生成各项成绩
                usual_score = random.randint(85, 100)  # 平时成绩
                homework_score = random.randint(70, 95)  # 作业成绩
                midterm_score = random.randint(60, 95)   # 期中成绩
                final_score = random.randint(55, 98)     # 期末成绩
                
                # 计算总成绩（平时20% + 期中30% + 期末50%）
                total_score = (usual_score * 0.2 + midterm_score * 0.3 + final_score * 0.5)
                
                # 确定等第和绩点
                if total_score >= 90:
                    grade_level = 'A'
                    grade_point = 4.0
                elif total_score >= 80:
                    grade_level = 'B'
                    grade_point = 3.0
                elif total_score >= 70:
                    grade_level = 'C'
                    grade_point = 2.0
                elif total_score >= 60:
                    grade_level = 'D'
                    grade_point = 1.0
                else:
                    grade_level = 'F'
                    grade_point = 0.0
                
                grade = {
                    'grade_id': grade_id,
                    'student_id': student['student_id'],
                    'course_instance_id': course_instance['instance_id'],  # 添加必需的字段
                    'course_code': course_instance['course_code'],
                    'semester': course_instance['semester'],
                    'midterm_score': float(midterm_score),
                    'final_score': float(final_score), 
                    'homework_score': float(homework_score),
                    'total_score': round(float(total_score), 1),
                    'grade_point': float(grade_point),
                    'grade_level': grade_level,
                    'score_weights': '{"usual": 20, "midterm": 30, "final": 50, "lab": 0, "homework": 0}',
                    'exam_type': 'normal',
                    'grade_status': 'confirmed',
                    'is_retake_required': False,
                    'is_deleted': False,
                    'status': 'active',
                    'is_active': True
                }
                grades_data.append(grade)
                grade_count += 1
                
                # 每1000条记录批量插入一次
                if len(grades_data) >= 1000:
                    bulk_insert(Grade, grades_data)
                    logger.info(f"✅ 已插入 {len(grades_data)} 条成绩记录，总计: {grade_count}")
                    grades_data.clear()
        
        # 插入剩余的成绩数据
        if grades_data:
            bulk_insert(Grade, grades_data)
        
        logger.info(f"✅ 生成 {grade_count} 条成绩记录")
    
    def generate_room_occupation_data(self):
        """生成教室占用数据"""
        logger.info("正在生成教室占用数据...")
        
        room_occupations_data = []
        
        # 获取所有教室类型的地点
        classrooms = [loc for loc in self.cache.get('locations', []) 
                     if loc.get('location_type') in ['classroom', 'lab', 'multimedia']]
        
        # 生成教室占用记录
        occupation_count = 0
        for classroom in classrooms:
            # 每个教室生成10-20个占用记录
            for occ_num in range(random.randint(10, 20)):
                occupation_id = f"RO{datetime.now().year}{str(len(room_occupations_data) + 1).zfill(6)}"
                
                # 随机选择占用类型
                occupation_type = random.choice(['class', 'exam', 'meeting', 'event'])
                
                # 生成时间
                start_date = self.faker.date_between(start_date='-30d', end_date='+30d')
                start_time = random.choice(['08:30', '10:30', '14:00', '16:00', '19:00'])
                end_time_map = {
                    '08:30': '10:10', '10:30': '12:10', 
                    '14:00': '15:40', '16:00': '17:40', '19:00': '20:40'
                }
                end_time = end_time_map[start_time]
                
                # 选择申请人
                if occupation_type in ['class', 'exam']:
                    applicants = [p for p in self.cache.get('persons', []) 
                                if p.get('person_type') in ['teacher', 'assistant_teacher']]
                else:
                    applicants = [p for p in self.cache.get('persons', []) 
                                if p.get('person_type') in ['teacher', 'admin']]
                
                applicant = random.choice(applicants) if applicants else None
                
                occupation = {
                    'occupation_id': occupation_id,
                    'location_id': classroom['location_id'],
                    'occupation_type': occupation_type,
                    'date': start_date,
                    'start_time': start_time,
                    'end_time': end_time,
                    'applicant_id': applicant['employee_id'] if applicant else None,
                    'application_reason': self.get_occupation_reason(occupation_type),
                    'status': random.choice(['confirmed', 'pending', 'cancelled']),
                    'attendance_count': random.randint(20, min(80, classroom.get('capacity', 50))),
                    'equipment_used': self.get_equipment_for_room_type(classroom.get('location_type')),
                    'notes': f"{occupation_type}使用",
                }
                room_occupations_data.append(occupation)
                occupation_count += 1
        
        # 批量插入教室占用数据
        if room_occupations_data:
            try:
                from models.organization import RoomOccupation
                bulk_insert(RoomOccupation, room_occupations_data)
            except ImportError as e:
                logger.warning(f"RoomOccupation模型导入失败，跳过教室占用数据: {e}")
                logger.info(f"⏸️ 跳过教室占用数据插入 ({len(room_occupations_data)} 条)")
            except Exception as e:
                logger.error(f"教室占用数据插入失败: {e}")
                logger.info(f"⏸️ 跳过教室占用数据插入 ({len(room_occupations_data)} 条)")
        
        logger.info(f"✅ 生成 {occupation_count} 条教室占用记录")
    
    def generate_workflow_data(self):
        """生成工作流实例数据"""
        logger.info("正在生成工作流实例数据...")
        
        workflow_instances_data = []
        platform_configs_data = []
        audit_logs_data = []
        device_registrations_data = []
        
        # 1. 生成平台配置数据
        config_types = ['student_portal', 'teacher_portal', 'admin_portal', 'research_platform']
        for config_type in config_types:
            config_id = f"PC{datetime.now().year}{str(len(platform_configs_data) + 1).zfill(3)}"
            
            config = {
                'config_id': config_id,
                'platform_name': self.get_platform_name(config_type),
                'platform_code': config_type.upper(),
                'config_data': self.generate_platform_config_data(config_type),
                'is_active': True,
                'version': f"v{random.randint(1, 3)}.{random.randint(0, 9)}",
                'last_updated': self.faker.date_between(start_date='-30d', end_date='today'),
            }
            platform_configs_data.append(config)
        
        # 2. 生成工作流实例
        workflow_types = ['course_selection', 'grade_appeal', 'research_application', 'scholarship_application']
        students = [p for p in self.cache.get('persons', []) if p.get('person_type') == 'student']
        
        for _ in range(min(500, len(students) // 10)):  # 生成一些工作流实例
            instance_id = f"WF{datetime.now().year}{str(len(workflow_instances_data) + 1).zfill(6)}"
            
            workflow_type = random.choice(workflow_types)
            initiator = random.choice(students)
            
            instance = {
                'instance_id': instance_id,
                'workflow_type': workflow_type,
                'workflow_name': self.get_workflow_name(workflow_type),
                'initiator_id': initiator['person_id'],
                'current_step': random.randint(1, 4),
                'total_steps': random.randint(3, 5),
                'status': random.choice(['pending', 'approved', 'rejected', 'in_progress']),
                'priority': random.choice(['low', 'medium', 'high']),
                'start_date': self.faker.date_between(start_date='-60d', end_date='today'),
                'expected_completion': self.faker.date_between(start_date='today', end_date='+30d'),
                'workflow_data': f'{{"application_type": "{workflow_type}", "student_id": "{initiator.get("student_id", "")}"}}',
            }
            workflow_instances_data.append(instance)
        
        # 3. 生成设备注册记录
        persons = self.cache.get('persons', [])
        for person in random.sample(persons, min(1000, len(persons))):  # 随机选择1000个用户
            for device_num in range(random.randint(1, 3)):  # 每人1-3个设备
                registration_id = f"DR{datetime.now().year}{str(len(device_registrations_data) + 1).zfill(6)}"
                
                device = {
                    'registration_id': registration_id,
                    'person_id': person['person_id'],
                    'device_name': random.choice(['iPhone 15', 'Samsung Galaxy S24', 'Xiaomi 14', 'OPPO Find X7', 'MacBook Pro', 'ThinkPad X1']),
                    'device_type': random.choice(['mobile', 'laptop', 'tablet', 'desktop']),
                    'mac_address': self.generate_mac_address(),
                    'registration_date': self.faker.date_between(start_date='-365d', end_date='today'),
                    'status': random.choice(['active', 'suspended', 'expired']),
                    'last_online': self.faker.date_between(start_date='-7d', end_date='today'),
                }
                device_registrations_data.append(device)
        
        # 4. 生成审计日志
        for _ in range(200):  # 生成200条审计日志
            log_id = f"AL{datetime.now().year}{str(len(audit_logs_data) + 1).zfill(6)}"
            
            user = random.choice(persons)
            actions = ['login', 'logout', 'grade_query', 'course_selection', 'password_change', 'profile_update']
            
            log = {
                'log_id': log_id,
                'user_id': user['person_id'],
                'action': random.choice(actions),
                'resource': random.choice(['EMS', 'LMS', 'portal', 'api']),
                'ip_address': f"10.{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}",
                'user_agent': random.choice(['Mozilla/5.0', 'Chrome/120.0', 'Safari/17.0', 'Mobile App']),
                'timestamp': self.faker.date_time_between(start_date='-30d', end_date='now'),
                'status': random.choice(['success', 'failure', 'warning']),
                'details': f'{{"action": "user_action", "module": "system"}}',
            }
            audit_logs_data.append(log)
        
        # 批量插入所有数据
        try:
            if platform_configs_data:
                # 暂时跳过平台配置，表可能不存在
                logger.info(f"⏸️ 跳过平台配置数据插入 ({len(platform_configs_data)} 条)")
                
            if workflow_instances_data:
                # 暂时跳过工作流实例，表可能不存在
                logger.info(f"⏸️ 跳过工作流实例数据插入 ({len(workflow_instances_data)} 条)")
                
            if device_registrations_data:
                # 暂时跳过设备注册，表可能不存在
                logger.info(f"⏸️ 跳过设备注册数据插入 ({len(device_registrations_data)} 条)")
                
            if audit_logs_data:
                # 暂时跳过审计日志，表可能不存在
                logger.info(f"⏸️ 跳过审计日志数据插入 ({len(audit_logs_data)} 条)")
                
        except Exception as e:
            logger.warning(f"工作流数据插入跳过: {e}")
        
        logger.info(f"✅ 生成工作流数据完成:")
        logger.info(f"   - 平台配置: {len(platform_configs_data)} 条")
        logger.info(f"   - 工作流实例: {len(workflow_instances_data)} 条")
        logger.info(f"   - 设备注册: {len(device_registrations_data)} 条")
        logger.info(f"   - 审计日志: {len(audit_logs_data)} 条")
    
    def get_occupation_reason(self, occupation_type: str) -> str:
        """根据占用类型生成申请原因"""
        reasons = {
            'class': ['高等数学课程教学', '计算机程序设计', '英语听说训练', '物理实验课', '化学实验'],
            'exam': ['期末考试', '期中考试', '补考', '重修考试', '毕业考试'],
            'meeting': ['学院会议', '教研活动', '学生会议', '项目讨论', '学术报告'],
            'event': ['学术讲座', '社团活动', '招生宣传', '文艺表演', '竞赛活动']
        }
        return random.choice(reasons.get(occupation_type, ['常规使用']))
    
    def get_equipment_for_room_type(self, room_type: str) -> str:
        """根据房间类型返回使用的设备"""
        import json
        equipment_map = {
            'classroom': ['projector', 'microphone', 'whiteboard'],
            'lab': ['computers', 'projector', 'lab_equipment', 'network'],
            'multimedia': ['projector', 'sound_system', 'microphone', 'screen'],
            'office': ['computer', 'printer'],
            'conference': ['projector', 'microphone', 'video_conference']
        }
        return json.dumps(random.sample(equipment_map.get(room_type, ['basic']), k=random.randint(1, 3)))
    
    def get_platform_name(self, config_type: str) -> str:
        """根据配置类型获取平台名称"""
        names = {
            'student_portal': '学生服务平台',
            'teacher_portal': '教师工作平台',
            'admin_portal': '管理员系统',
            'research_platform': '科研管理平台'
        }
        return names.get(config_type, '未知平台')
    
    def generate_platform_config_data(self, config_type: str) -> str:
        """生成平台配置数据"""
        import json
        
        if config_type == 'student_portal':
            return json.dumps({
                "max_course_selection": 8,
                "grade_query_enabled": True,
                "schedule_sharing": True,
                "mobile_app_enabled": True,
                "features": ["course_selection", "grade_query", "schedule", "library", "card_service"]
            })
        elif config_type == 'teacher_portal':
            return json.dumps({
                "max_classes_per_term": 6,
                "grade_input_deadline": 7,
                "research_module_enabled": True,
                "features": ["teaching", "research", "grade_management", "student_info"]
            })
        elif config_type == 'admin_portal':
            return json.dumps({
                "user_management_enabled": True,
                "system_monitoring": True,
                "data_export_enabled": True,
                "features": ["user_management", "system_config", "reports", "monitoring"]
            })
        else:
            return json.dumps({
                "project_management": True,
                "funding_tracking": True,
                "paper_management": True,
                "features": ["projects", "funding", "publications", "collaboration"]
            })
    
    def get_workflow_name(self, workflow_type: str) -> str:
        """根据工作流类型获取工作流名称"""
        names = {
            'course_selection': '课程选择申请',
            'grade_appeal': '成绩申诉流程',
            'research_application': '科研项目申请',
            'scholarship_application': '奖学金申请'
        }
        return names.get(workflow_type, '未知流程')
    
    def generate_mac_address(self) -> str:
        """生成MAC地址"""
        return ':'.join([f"{random.randint(0, 255):02x}" for _ in range(6)])
    
    def restore_cache_from_database(self):
        """从数据库中恢复数据到缓存"""
        logger.info("正在从数据库恢复数据到缓存...")
        
        db = SessionLocal()
        try:
            # 恢复学院数据
            from models.organization import College
            colleges = db.query(College).all()
            self.cache['colleges'] = [
                {
                    'college_id': c.college_id,
                    'college_name': c.college_name,
                    'college_code': c.college_code
                }
                for c in colleges
            ]
            logger.info(f"✅ 恢复 {len(self.cache['colleges'])} 个学院")
            
            # 恢复专业数据
            from models.organization import Major
            majors = db.query(Major).all()
            self.cache['majors'] = [
                {
                    'major_id': m.major_id,
                    'major_name': m.major_name,
                    'major_code': m.major_code,
                    'college_id': m.college_id
                }
                for m in majors
            ]
            logger.info(f"✅ 恢复 {len(self.cache['majors'])} 个专业")
            
            # 恢复班级数据
            from models.person import Class
            classes = db.query(Class).all()
            self.cache['classes'] = [
                {
                    'class_id': c.class_id,
                    'class_name': c.class_name,
                    'college_id': c.college_id,
                    'major_id': c.major_id,
                    'grade': c.grade
                }
                for c in classes
            ]
            logger.info(f"✅ 恢复 {len(self.cache['classes'])} 个班级")
            
            # 恢复人员数据
            from models.person import Person
            persons = db.query(Person).all()
            self.cache['persons'] = [
                {
                    'person_id': p.person_id,
                    'person_type': p.person_type,
                    'student_id': p.student_id,
                    'employee_id': p.employee_id,
                    'name': p.name,
                    'college_id': p.college_id,
                    'major_id': p.major_id,
                    'class_id': p.class_id
                }
                for p in persons
            ]
            logger.info(f"✅ 恢复 {len(self.cache['persons'])} 个人员")
            
            # 恢复地点数据
            from models.organization import Location
            locations = db.query(Location).all()
            self.cache['locations'] = [
                {
                    'location_id': l.location_id,
                    'location_name': l.location_name,
                    'location_type': l.location_type,
                    'building_code': l.building_code,
                    'capacity': l.capacity
                }
                for l in locations
            ]
            logger.info(f"✅ 恢复 {len(self.cache['locations'])} 个地点")
            
        except Exception as e:
            logger.error(f"恢复缓存数据失败: {e}")
            raise
        finally:
            db.close()
        
        logger.info("✅ 数据缓存恢复完成")
    
    def print_generation_summary(self):
        """打印数据生成总结"""
        logger.info("="*50)
        logger.info("📊 Mock数据生成总结报告")
        logger.info("="*50)
        
        try:
            db = SessionLocal()
            
            # 统计各类数据量
            summary = {
                "学院数量": len(self.cache.get('colleges', [])),
                "专业数量": len(self.cache.get('majors', [])),
                "班级数量": len(self.cache.get('classes', [])),
                "学生总数": len([p for p in self.cache.get('persons', []) if p.get('person_type') == 'student']),
                "教师总数": len([p for p in self.cache.get('persons', []) if p.get('person_type') in ['teacher', 'assistant_teacher']]),
                "管理员数量": len([p for p in self.cache.get('persons', []) if p.get('person_type') == 'admin']),
                "地点数量": len(self.cache.get('locations', [])),
            }
            
            for key, value in summary.items():
                logger.info(f"🔸 {key}: {value:,}")
            
            # 数据分布统计
            logger.info("\n📈 数据分布统计:")
            
            # 学生分布
            students_by_college = {}
            for person in self.cache.get('persons', []):
                if person.get('person_type') == 'student':
                    college = person.get('college_id', 'Unknown')
                    students_by_college[college] = students_by_college.get(college, 0) + 1
            
            logger.info("👥 各学院学生分布:")
            for college_id, count in students_by_college.items():
                college_name = next((c['college_name'] for c in self.cache.get('colleges', []) if c['college_id'] == college_id), college_id)
                logger.info(f"   {college_name}: {count:,} 人")
            
            # 预估数据库大小
            grade_count = summary.get("成绩记录数", 0)  # 从summary中获取或设为0
            estimated_size_mb = (
                len(self.cache.get('persons', [])) * 0.5 +  # 每个人员记录约0.5KB
                len(self.cache.get('locations', [])) * 0.2 +  # 每个地点记录约0.2KB
                grade_count * 0.3  # 每条成绩记录约0.3KB
            ) / 1024  # 转换为MB
            
            logger.info(f"\n💾 预估数据库大小: {estimated_size_mb:.2f} MB")
            logger.info("="*50)
            
        except Exception as e:
            logger.error(f"生成总结报告时出错: {e}")
        finally:
            if 'db' in locals():
                db.close()
    
    # ==================== 辅助方法 ====================
    
    def generate_phone(self) -> str:
        """生成手机号"""
        prefixes = ['130', '131', '132', '133', '134', '135', '136', '137', '138', '139',
                   '150', '151', '152', '153', '155', '156', '157', '158', '159',
                   '180', '181', '182', '183', '184', '185', '186', '187', '188', '189']
        return random.choice(prefixes) + ''.join([str(random.randint(0, 9)) for _ in range(8)])
    
    def generate_birth_date(self, age_range: tuple) -> date:
        """根据年龄范围生成出生日期"""
        current_year = datetime.now().year
        birth_year = current_year - random.randint(age_range[0], age_range[1])
        return date(birth_year, random.randint(1, 12), random.randint(1, 28))
    
    def get_room_type_by_building(self, building_code: str) -> str:
        """根据建筑编码确定房间类型"""
        if building_code.startswith('C') or building_code.startswith('D'):
            return 'classroom'
        elif building_code.startswith('E'):
            return 'lab'
        elif building_code.startswith('L'):
            return 'library'
        elif building_code.startswith('F'):
            return 'canteen'
        elif building_code.startswith('S'):
            return 'dormitory'
        elif building_code.startswith('B'):
            return 'office'
        else:
            return 'classroom'
    
    def generate_asset_info(self) -> tuple:
        """生成资产信息"""
        category = random.choice(list(ASSET_CATEGORIES.keys()))
        subcategory = random.choice(list(ASSET_CATEGORIES[category].keys()))
        asset_name = random.choice(ASSET_CATEGORIES[category][subcategory])
        
        return category, {
            'name': asset_name,
            'type': subcategory
        }
    
    def get_semester_start_date(self, semester: str) -> date:
        """获取学期开始日期"""
        year = int(semester.split('-')[0])
        term = semester.split('-')[2]
        
        if term == '1':  # 秋季学期
            return date(year, 9, 1)
        else:  # 春季学期
            return date(year + 1, 2, 15)
    
    def get_semester_end_date(self, semester: str) -> date:
        """获取学期结束日期"""
        year = int(semester.split('-')[0])
        term = semester.split('-')[2]
        
        if term == '1':  # 秋季学期
            return date(year + 1, 1, 15)
        else:  # 春季学期
            return date(year + 1, 7, 15) 