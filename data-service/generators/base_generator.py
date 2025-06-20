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
        logger.info("Mock data generation completed")
    
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
                'main_building': college_id.replace('C', 'C'),  # C001 -> C1
                'description': f"{college_info['name']}致力于培养高素质的专业人才",
            }
            colleges_data.append(college)
            self.cache['colleges'].append(college)
        
        # 批量插入学院
        bulk_insert(College, colleges_data)
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
        
        bulk_insert(Major, majors_data)
        logger.info(f"Generated {len(majors_data)} majors")
        
        # 生成班级
        classes_data = []
        for major in self.cache['majors']:
            for class_num in range(1, MOCK_CONFIG['classes_per_major'] + 1):
                grade_year = random.choice([2021, 2022, 2023, 2024])
                class_id = f"CL{grade_year}{str(self.counters['class']).zfill(3)}"
                
                class_data = {
                    'class_id': class_id,
                    'class_name': f"{major['major_name']}{class_num}班",
                    'class_code': f"{major['major_code']}-{class_num}",
                    'grade': grade_year,
                    'semester_enrolled': f"{grade_year}-{grade_year+1}-1",
                    'major_id': major['major_id'],
                    'college_id': major['college_id'],
                    'total_students': MOCK_CONFIG['students_per_class'],
                    'graduation_date': date(grade_year + 4, 6, 30),
                }
                classes_data.append(class_data)
                self.cache['classes'].append(class_data)
                self.counters['class'] += 1
        
        bulk_insert(Class, classes_data)
        logger.info(f"Generated {len(classes_data)} classes")
    
    def generate_person_data(self):
        """生成人员数据"""
        logger.info("Generating person data...")
        
        persons_data = []
        
        # 生成学生
        for class_data in self.cache['classes']:
            for student_num in range(1, class_data['total_students'] + 1):
                person_id = f"P{datetime.now().year}{str(self.counters['person']).zfill(6)}"
                student_id = f"{class_data['grade']}{class_data['major_id']}{str(class_data['class_id'][-2:])}{str(student_num).zfill(2)}"
                
                person = {
                    'person_id': person_id,
                    'person_type': 'student',
                    'student_id': student_id,
                    'name': self.generate_chinese_name(),
                    'gender': random.choice(['male', 'female']),
                    'birth_date': self.generate_birth_date(age_range=(18, 25)),
                    'phone': self.generate_phone(),
                    'email': f"{student_id}@student.sztu.edu.cn",
                    'college_id': class_data['college_id'],
                    'major_id': class_data['major_id'],
                    'class_id': class_data['class_id'],
                    'admission_date': date(class_data['grade'], 9, 1),
                    'graduation_date': date(class_data['grade'] + 4, 6, 30),
                    'academic_status': 'active',
                    'home_address': self.faker.address(),
                }
                persons_data.append(person)
                self.cache['persons'].append(person)
                self.counters['person'] += 1
        
        # 生成教师
        for college in self.cache['colleges']:
            for teacher_num in range(1, MOCK_CONFIG['teachers_per_college'] + 1):
                person_id = f"P{datetime.now().year}{str(self.counters['person']).zfill(6)}"
                employee_id = f"{datetime.now().year}{college['college_id'][1:]}{str(teacher_num).zfill(2)}"
                
                person = {
                    'person_id': person_id,
                    'person_type': random.choice(['teacher', 'assistant_teacher']),
                    'employee_id': employee_id,
                    'name': self.generate_chinese_name(),
                    'gender': random.choice(['male', 'female']),
                    'birth_date': self.generate_birth_date(age_range=(25, 60)),
                    'phone': self.generate_phone(),
                    'email': f"{employee_id}@sztu.edu.cn",
                    'college_id': college['college_id'],
                    'employment_date': self.faker.date_between(start_date='-10y', end_date='today'),
                    'employment_status': 'active',
                    'academic_title': random.choice(['教授', '副教授', '讲师', '助教']),
                    'research_field': random.choice(['计算机科学', '数学', '物理学', '化学', '经济学', '管理学']),
                    'education_background': random.choice(['博士', '硕士']),
                    'home_address': self.faker.address(),
                }
                persons_data.append(person)
                self.cache['persons'].append(person)
                self.counters['person'] += 1
        
        # 批量插入人员数据
        bulk_insert(Person, persons_data)
        logger.info(f"Generated {len(persons_data)} persons")
    
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
        bulk_insert(Course, courses_data)
        bulk_insert(CourseInstance, course_instances_data)
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
        bulk_insert(Location, locations_data)
        bulk_insert(Asset, assets_data)
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
        bulk_insert(Book, books_data)
        
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
        
        bulk_insert(BorrowRecord, borrow_records_data)
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
        bulk_insert(CampusCard, campus_cards_data)
        bulk_insert(Transaction, transactions_data)
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
        bulk_insert(ResearchProject, projects_data)
        bulk_insert(PaperLibrary, papers_data)
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
        bulk_insert(NetworkPermission, network_permissions_data)
        bulk_insert(SystemAccess, system_access_data)
        logger.info(f"Generated {len(network_permissions_data)} network permissions and {len(system_access_data)} system access records")
    
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