"""
人员Repository
处理人员相关的数据访问逻辑
"""
from typing import Optional, List, Dict, Any
import hashlib
import logging

from .base import BaseRepository
from app.models.person import Person, Student, Teacher, Admin

logger = logging.getLogger(__name__)


class PersonRepository(BaseRepository[Person]):
    """人员Repository"""
    
    def __init__(self):
        super().__init__(Person, "persons")
    
    def _get_primary_key_field(self) -> str:
        return "person_id"
    
    async def find_by_student_id(self, student_id: str) -> Optional[Student]:
        """根据学生ID查询学生"""
        try:
            result = await self.find_one_by_filters({
                "student_id": student_id,
                "person_type": "student"
            })
            
            if result:
                # 转换为Student实例
                return Student.from_dict(result.to_dict())
            return None
            
        except Exception as e:
            logger.error(f"根据学生ID查询失败: {e}")
            return None
    
    async def find_by_employee_id(self, employee_id: str) -> Optional[Person]:
        """根据员工ID查询教师或管理员"""
        try:
            result = await self.find_one_by_filters({
                "employee_id": employee_id,
                "person_type": {"$in": ["teacher", "admin", "staff"]}
            })
            
            if result:
                # 根据类型返回对应的子类实例
                if result.person_type == "teacher":
                    return Teacher.from_dict(result.to_dict())
                elif result.person_type == "admin":
                    return Admin.from_dict(result.to_dict())
                else:
                    return result
            return None
            
        except Exception as e:
            logger.error(f"根据员工ID查询失败: {e}")
            return None
    
    async def find_by_wechat_openid(self, openid: str) -> Optional[Person]:
        """根据微信OpenID查询用户"""
        try:
            return await self.find_one_by_filters({
                "wechat_openid": openid
            })
        except Exception as e:
            logger.error(f"根据微信OpenID查询失败: {e}")
            return None
    
    async def authenticate(self, username: str, password: str) -> Optional[Person]:
        """用户认证"""
        try:
            # 先尝试学生ID登录
            person = await self.find_by_student_id(username)
            
            # 如果不是学生，尝试员工ID登录
            if not person:
                person = await self.find_by_employee_id(username)
            
            # 如果还是没找到，尝试person_id登录
            if not person:
                person = await self.find_by_id(username)
            
            if not person:
                return None
            
            # 验证密码
            if self._verify_password(password, person.password_hash, person.password_salt):
                # 更新最后登录时间
                await self._update_last_login(person.person_id)
                return person
            
            return None
            
        except Exception as e:
            logger.error(f"用户认证失败: {e}")
            return None
    
    async def find_students_by_class(self, class_id: str) -> List[Student]:
        """根据班级ID查询学生列表"""
        try:
            results = await self.find_by_filters({
                "class_id": class_id,
                "person_type": "student"
            })
            
            # 转换为Student实例
            return [Student.from_dict(person.to_dict()) for person in results]
            
        except Exception as e:
            logger.error(f"根据班级查询学生失败: {e}")
            return []
    
    async def find_teachers_by_college(self, college_id: str) -> List[Teacher]:
        """根据学院ID查询教师列表"""
        try:
            results = await self.find_by_filters({
                "college_id": college_id,
                "person_type": "teacher"
            })
            
            # 转换为Teacher实例
            return [Teacher.from_dict(person.to_dict()) for person in results]
            
        except Exception as e:
            logger.error(f"根据学院查询教师失败: {e}")
            return []
    
    async def search_persons(
        self,
        keyword: str,
        person_type: Optional[str] = None,
        college_id: Optional[str] = None,
        limit: int = 50
    ) -> List[Person]:
        """搜索人员"""
        try:
            filters = {}
            
            # 添加类型过滤
            if person_type:
                filters["person_type"] = person_type
            
            # 添加学院过滤
            if college_id:
                filters["college_id"] = college_id
            
            # 模糊搜索（这里简化处理，实际应该支持模糊查询）
            if keyword:
                # 先尝试精确匹配各种ID
                exact_filters = [
                    {**filters, "person_id": keyword},
                    {**filters, "student_id": keyword},
                    {**filters, "employee_id": keyword},
                    {**filters, "name": keyword}
                ]
                
                for filter_set in exact_filters:
                    results = await self.find_by_filters(filter_set, limit=limit)
                    if results:
                        return results
            
            return []
            
        except Exception as e:
            logger.error(f"搜索人员失败: {e}")
            return []
    
    async def get_person_statistics(self, college_id: Optional[str] = None) -> Dict[str, Any]:
        """获取人员统计信息"""
        try:
            base_filters = {}
            if college_id:
                base_filters["college_id"] = college_id
            
            # 分别统计不同类型的人员数量
            total_students = await self.count({**base_filters, "person_type": "student"})
            total_teachers = await self.count({**base_filters, "person_type": "teacher"})
            total_admins = await self.count({**base_filters, "person_type": "admin"})
            
            return {
                "total_students": total_students,
                "total_teachers": total_teachers,
                "total_admins": total_admins,
                "total_persons": total_students + total_teachers + total_admins
            }
            
        except Exception as e:
            logger.error(f"获取人员统计失败: {e}")
            return {
                "total_students": 0,
                "total_teachers": 0,
                "total_admins": 0,
                "total_persons": 0
            }
    
    def _verify_password(self, password: str, password_hash: str, password_salt: str) -> bool:
        """验证密码"""
        if not password_hash or not password_salt:
            return False
        
        # 使用相同的算法验证密码
        computed_hash = hashlib.sha256((password + password_salt).encode()).hexdigest()
        return computed_hash == password_hash
    
    async def _update_last_login(self, person_id: str):
        """更新最后登录时间"""
        try:
            # 这里应该调用更新接口，但目前的HTTP客户端可能不支持更新
            # 所以先记录日志
            logger.info(f"用户 {person_id} 登录成功")
        except Exception as e:
            logger.error(f"更新最后登录时间失败: {e}")
    
    async def check_permissions(self, person_id: str, required_permissions: List[str]) -> bool:
        """检查用户权限"""
        try:
            person = await self.find_by_id(person_id)
            if not person:
                return False
            
            user_permissions = person.get_permissions()
            
            # 检查用户是否具有所需权限
            for permission in required_permissions:
                if permission not in user_permissions.get("read", []) and \
                   permission not in user_permissions.get("write", []) and \
                   permission not in user_permissions.get("admin", []):
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"检查用户权限失败: {e}")
            return False 