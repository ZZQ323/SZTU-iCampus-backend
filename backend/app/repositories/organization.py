"""
组织架构Repository
处理学院、专业、班级、部门等组织架构数据访问
"""
from typing import Optional, List, Dict, Any
import logging

from .base import BaseRepository
from app.models.organization import College, Major, Class, Department

logger = logging.getLogger(__name__)


class OrganizationRepository(BaseRepository[College]):
    """组织架构Repository"""
    
    def __init__(self):
        super().__init__(College, "colleges")  # 默认处理学院
    
    def _get_primary_key_field(self) -> str:
        return "college_id"
    
    async def find_all_colleges(self) -> List[College]:
        """查询所有学院"""
        try:
            return await self.find_all(order_by="college_code ASC")
        except Exception as e:
            logger.error(f"查询所有学院失败: {e}")
            return []
    
    async def find_majors_by_college(self, college_id: str) -> List[Major]:
        """根据学院ID查询专业列表"""
        try:
            result = await self.client.query_table(
                table_name="majors",
                filters={
                    "college_id": college_id,
                    "is_deleted": False
                },
                order_by="major_code ASC"
            )
            
            records = result.get("data", {}).get("records", [])
            return Major.from_list(records)
            
        except Exception as e:
            logger.error(f"根据学院查询专业失败: {e}")
            return []
    
    async def find_classes_by_major(self, major_id: str) -> List[Class]:
        """根据专业ID查询班级列表"""
        try:
            result = await self.client.query_table(
                table_name="classes",
                filters={
                    "major_id": major_id,
                    "is_deleted": False
                },
                order_by="grade DESC, class_code ASC"
            )
            
            records = result.get("data", {}).get("records", [])
            return Class.from_list(records)
            
        except Exception as e:
            logger.error(f"根据专业查询班级失败: {e}")
            return []
    
    async def find_classes_by_college(self, college_id: str) -> List[Class]:
        """根据学院ID查询班级列表"""
        try:
            result = await self.client.query_table(
                table_name="classes", 
                filters={
                    "college_id": college_id,
                    "is_deleted": False
                },
                order_by="grade DESC, major_id ASC, class_code ASC"
            )
            
            records = result.get("data", {}).get("records", [])
            return Class.from_list(records)
            
        except Exception as e:
            logger.error(f"根据学院查询班级失败: {e}")
            return []
    
    async def find_departments_by_college(self, college_id: str) -> List[Department]:
        """根据学院ID查询部门列表"""
        try:
            result = await self.client.query_table(
                table_name="departments",
                filters={
                    "college_id": college_id,
                    "is_deleted": False
                },
                order_by="level ASC, department_name ASC"
            )
            
            records = result.get("data", {}).get("records", [])
            return Department.from_list(records)
            
        except Exception as e:
            logger.error(f"根据学院查询部门失败: {e}")
            return []
    
    async def get_organization_tree(self) -> List[Dict[str, Any]]:
        """获取完整的组织架构树"""
        try:
            # 查询所有学院
            colleges = await self.find_all_colleges()
            
            tree = []
            for college in colleges:
                college_node = {
                    "id": college.college_id,
                    "name": college.college_name,
                    "code": college.college_code,
                    "type": "college",
                    "children": []
                }
                
                # 查询学院下的专业
                majors = await self.find_majors_by_college(college.college_id)
                for major in majors:
                    major_node = {
                        "id": major.major_id,
                        "name": major.major_name,
                        "code": major.major_code,
                        "type": "major",
                        "children": []
                    }
                    
                    # 查询专业下的班级
                    classes = await self.find_classes_by_major(major.major_id)
                    for class_obj in classes:
                        class_node = {
                            "id": class_obj.class_id,
                            "name": class_obj.class_name,
                            "code": class_obj.class_code,
                            "type": "class",
                            "grade": class_obj.grade,
                            "student_count": class_obj.total_students
                        }
                        major_node["children"].append(class_node)
                    
                    college_node["children"].append(major_node)
                
                tree.append(college_node)
            
            return tree
            
        except Exception as e:
            logger.error(f"获取组织架构树失败: {e}")
            return []
    
    async def get_organization_statistics(self) -> Dict[str, Any]:
        """获取组织架构统计信息"""
        try:
            # 统计各类型数量
            college_count = await self.count({})
            
            major_result = await self.client.query_table(
                table_name="majors",
                filters={"is_deleted": False},
                limit=1
            )
            major_count = major_result.get("data", {}).get("estimated_total", 0)
            
            class_result = await self.client.query_table(
                table_name="classes",
                filters={"is_deleted": False},
                limit=1
            )
            class_count = class_result.get("data", {}).get("estimated_total", 0)
            
            department_result = await self.client.query_table(
                table_name="departments",
                filters={"is_deleted": False},
                limit=1
            )
            department_count = department_result.get("data", {}).get("estimated_total", 0)
            
            return {
                "total_colleges": college_count,
                "total_majors": major_count,
                "total_classes": class_count,
                "total_departments": department_count
            }
            
        except Exception as e:
            logger.error(f"获取组织架构统计失败: {e}")
            return {
                "total_colleges": 0,
                "total_majors": 0,
                "total_classes": 0,
                "total_departments": 0
            }
    
    async def search_organizations(
        self,
        keyword: str,
        org_type: Optional[str] = None,
        college_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """搜索组织架构"""
        try:
            results = []
            
            # 根据类型搜索不同的表
            if not org_type or org_type == "college":
                colleges = await self._search_colleges(keyword)
                results.extend([{"type": "college", "data": c} for c in colleges])
            
            if not org_type or org_type == "major":
                majors = await self._search_majors(keyword, college_id)
                results.extend([{"type": "major", "data": m} for m in majors])
            
            if not org_type or org_type == "class":
                classes = await self._search_classes(keyword, college_id)
                results.extend([{"type": "class", "data": c} for c in classes])
            
            return results
            
        except Exception as e:
            logger.error(f"搜索组织架构失败: {e}")
            return []
    
    async def _search_colleges(self, keyword: str) -> List[College]:
        """搜索学院"""
        try:
            filters = {
                "$or": [
                    {"college_name": {"$regex": keyword, "$options": "i"}},
                    {"college_code": {"$regex": keyword, "$options": "i"}}
                ]
            }
            
            result = await self.client.query_table(
                table_name="colleges",
                filters=filters,
                limit=50
            )
            
            records = result.get("data", {}).get("records", [])
            return College.from_list(records)
            
        except Exception as e:
            logger.error(f"搜索学院失败: {e}")
            return []
    
    async def _search_majors(self, keyword: str, college_id: Optional[str] = None) -> List[Major]:
        """搜索专业"""
        try:
            filters = {
                "$or": [
                    {"major_name": {"$regex": keyword, "$options": "i"}},
                    {"major_code": {"$regex": keyword, "$options": "i"}}
                ]
            }
            
            if college_id:
                filters["college_id"] = college_id
            
            result = await self.client.query_table(
                table_name="majors",
                filters=filters,
                limit=50
            )
            
            records = result.get("data", {}).get("records", [])
            return Major.from_list(records)
            
        except Exception as e:
            logger.error(f"搜索专业失败: {e}")
            return []
    
    async def _search_classes(self, keyword: str, college_id: Optional[str] = None) -> List[Class]:
        """搜索班级"""
        try:
            filters = {
                "$or": [
                    {"class_name": {"$regex": keyword, "$options": "i"}},
                    {"class_code": {"$regex": keyword, "$options": "i"}}
                ]
            }
            
            if college_id:
                filters["college_id"] = college_id
            
            result = await self.client.query_table(
                table_name="classes",
                filters=filters,
                limit=50
            )
            
            records = result.get("data", {}).get("records", [])
            return Class.from_list(records)
            
        except Exception as e:
            logger.error(f"搜索班级失败: {e}")
            return [] 