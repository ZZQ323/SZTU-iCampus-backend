"""
SZTU-iCampus 数据服务配置文件
包含数据库连接、Mock数据生成、API服务等配置
"""
import os
from typing import Dict, Any
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置类"""
    
    # 基础配置
    APP_NAME: str = "SZTU-iCampus Data Service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # 服务配置
    HOST: str = "0.0.0.0"
    PORT: int = 8001
    WORKERS: int = 4
    
    # 数据库配置 (修改为SQLite便于快速测试)
    DATABASE_URL: str = "sqlite:///./sztu_campus.db"
    DATABASE_ECHO: bool = False  # 是否打印SQL语句
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 30
    
    # Redis配置
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # API配置
    API_PREFIX: str = "/api/v1"
    API_KEY: str = "sztu-data-service-key-2024"
    CORS_ORIGINS: list = ["*"]
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/data-service.log"
    
    class Config:
        env_file = ".env"


# 全局设置实例
settings = Settings()

# 数据库配置
DATABASE_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "sztu_campus",
    "username": "postgres",
    "password": "password",
    "echo": settings.DATABASE_ECHO,
    "pool_size": settings.DATABASE_POOL_SIZE,
    "max_overflow": settings.DATABASE_MAX_OVERFLOW,
}

# Mock数据生成配置
MOCK_CONFIG = {
    # 组织架构数据量
    "colleges": 13,                    # 学院数量
    "majors_per_college": 6,           # 每学院专业数
    "departments": 25,                 # 部门数量
    "classes_per_major": 4,            # 每专业班级数
    
    # 人员数据量
    "students_per_class": 35,          # 每班学生数
    "teachers_per_college": 50,        # 每学院教师数
    "staff_per_department": 8,         # 每部门行政人员数
    
    # 课程数据量
    "courses_per_major": 40,           # 每专业课程数
    "course_instances_per_semester": 200, # 每学期开课实例数
    "semesters": ["2023-2024-1", "2023-2024-2", "2024-2025-1"], # 生成的学期
    
    # 科研数据量
    "research_projects_per_teacher": 2,  # 每教师科研项目数
    "papers_per_teacher": 5,            # 每教师论文数
    
    # 资产数据量
    "assets_per_location": 15,          # 每地点资产数
    "locations_per_building": 20,       # 每建筑地点数
    
    # 图书馆数据量
    "books_count": 50000,               # 图书总数
    "borrow_records_per_student": 8,    # 每学生借阅记录数
    
    # 财务数据量
    "transactions_per_person_monthly": 45, # 每人每月交易数
    "transaction_months": 6,            # 生成交易记录的月数
    
    # 权限数据量
    "network_devices_per_person": 2,    # 每人网络设备数
    "system_access_per_person": 3,      # 每人系统访问权限数
}

# 编号规则配置
ENCODING_CONFIG = {
    # 学院编码映射
    "college_codes": {
        "C001": {"name": "计算机学院", "code": "CS", "majors": ["080901", "080902", "080903", "080904", "080905", "080906"]},
        "C002": {"name": "数学与统计学院", "code": "MATH", "majors": ["080100", "080200", "080300"]},
        "C003": {"name": "物理与光电工程学院", "code": "PHY", "majors": ["070100", "070200"]},
        "C004": {"name": "化学与生物工程学院", "code": "CBE", "majors": ["070300", "070400", "071000", "071001"]},
        "C005": {"name": "材料科学与工程学院", "code": "MSE", "majors": ["082801", "082802", "082803"]},
        "C006": {"name": "机械设计制造及其自动化学院", "code": "ME", "majors": ["082801", "082802", "082803"]},
        "C007": {"name": "电子与信息工程学院", "code": "EIE", "majors": ["081001", "081002", "081003"]},
        "C008": {"name": "经济管理学院", "code": "EM", "majors": ["120100", "120200", "120300", "120400", "120500", "120600", "120700"]},
        "C009": {"name": "外国语学院", "code": "FL", "majors": ["050101", "050102", "050103"]},
        "C010": {"name": "人文社会科学学院", "code": "HSS", "majors": ["050201", "050301", "050302"]},
        "C011": {"name": "艺术设计学院", "code": "AD", "majors": ["130400", "130500"]},
        "C012": {"name": "医学院", "code": "MED", "majors": ["100201", "100301"]},
        "C013": {"name": "生命健康学院", "code": "LH", "majors": ["100401", "100501"]},
    },
    
    # 专业编码映射
    "major_codes": {
        "080100": "数学与应用数学", "080200": "信息与计算科学", "080300": "统计学",
        "070100": "物理学", "070200": "应用物理学", "070300": "化学", "070400": "应用化学",
        "071000": "生物科学", "071001": "生物技术",
        "080901": "计算机科学与技术", "080902": "软件工程", "080903": "网络工程", 
        "080904": "信息安全", "080905": "物联网工程", "080906": "数字媒体技术",
        "081001": "电子信息工程", "081002": "通信工程", "081003": "电子科学与技术",
        "082801": "机械工程", "082802": "机械设计制造及其自动化", "082803": "材料成型及控制工程",
        "120100": "工商管理", "120200": "市场营销", "120300": "会计学", "120400": "财务管理",
        "120500": "国际经济与贸易", "120600": "金融学", "120700": "经济学",
        "050101": "英语", "050102": "日语", "050103": "德语",
        "050201": "汉语言文学", "050301": "新闻学", "050302": "传播学",
        "130400": "视觉传达设计", "130500": "产品设计",
        "100201": "临床医学", "100301": "口腔医学", "100401": "预防医学", "100501": "中医学",
    },
    
    # 建筑编码配置
    "building_codes": {
        "C1": "计算机学院1号楼", "C2": "计算机学院2号楼", "C3": "理工学院1号楼", 
        "C4": "理工学院2号楼", "C5": "理工学院3号楼",
        "D1": "经管学院教学楼", "D2": "人文学院教学楼", "D3": "外语学院教学楼",
        "E0": "中央实验楼", "E1": "计算机实验楼", "E2": "物理实验楼", "E3": "化学实验楼",
        "B0": "行政办公楼", "B1": "学院办公楼", "B2": "后勤服务楼",
        "L1": "图书馆主楼", "L2": "图书馆东楼", "L3": "图书馆西楼",
        "F1": "学生食堂一楼", "F2": "学生食堂二楼", "F3": "教工食堂", "F4": "风味餐厅", "F5": "咖啡厅",
        "S1": "学生宿舍1栋", "S2": "学生宿舍2栋", "S3": "学生宿舍3栋", "S4": "学生宿舍4栋",
        "S5": "学生宿舍5栋", "S6": "学生宿舍6栋", "S7": "学生宿舍7栋", "S8": "学生宿舍8栋",
        "S9": "研究生宿舍1栋", "S10": "研究生宿舍2栋",
    }
}

# 资产分类配置
ASSET_CATEGORIES = {
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

# 时间配置
TIME_CONFIG = {
    # 学期配置
    "current_semester": "2024-2025-1",
    "current_academic_year": "2024-2025",
    
    # 上课时间段
    "time_slots": {
        1: {"name": "第1-2节", "start": "08:30", "end": "10:10"},
        2: {"name": "第3-4节", "start": "10:30", "end": "12:10"},
        3: {"name": "第5-6节", "start": "14:00", "end": "15:40"},
        4: {"name": "第7-8节", "start": "16:00", "end": "17:40"},
        5: {"name": "第9-10节", "start": "19:00", "end": "20:40"},
    },
    
    # 学期时间配置
    "semester_dates": {
        "2023-2024-1": {"start": "2023-09-01", "end": "2024-01-31"},
        "2023-2024-2": {"start": "2024-02-01", "end": "2024-07-31"},
        "2024-2025-1": {"start": "2024-09-01", "end": "2025-01-31"},
        "2024-2025-2": {"start": "2025-02-01", "end": "2025-07-31"},
    }
}

# 网络供应商配置
NETWORK_PROVIDERS = ["中国移动", "中国联通", "中国电信"]

# 常用中文姓名库（用于Mock数据生成）
CHINESE_SURNAMES = [
    "王", "李", "张", "刘", "陈", "杨", "黄", "赵", "周", "吴",
    "徐", "孙", "胡", "朱", "高", "林", "何", "郭", "马", "罗",
    "梁", "宋", "郑", "谢", "韩", "唐", "冯", "于", "董", "萧"
]

CHINESE_GIVEN_NAMES = [
    "伟", "芳", "娜", "秀英", "敏", "静", "丽", "强", "磊", "军",
    "洋", "勇", "艳", "杰", "娟", "涛", "明", "超", "秀兰", "霞",
    "平", "刚", "桂英", "建华", "文", "华", "金凤", "素梅", "建国", "国强"
] 