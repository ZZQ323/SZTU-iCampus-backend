"""
基础数据模型
提供所有业务模型的共同功能和约定
"""
from datetime import datetime
from typing import Any, Dict, Optional, ClassVar
from pydantic import BaseModel as PydanticBaseModel, Field


class BaseModel(PydanticBaseModel):
    """
    基础数据模型
    所有业务模型的基类，提供通用字段和方法
    """
    
    # 基础字段（所有表都有的字段）
    id: Optional[int] = Field(None, description="自增ID，主键")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")
    is_deleted: bool = Field(False, description="删除标记")
    deleted_at: Optional[datetime] = Field(None, description="删除时间")
    status: str = Field("active", description="状态")
    is_active: bool = Field(True, description="激活状态")
    notes: Optional[str] = Field(None, description="备注")
    
    # 类配置
    class Config:
        # 允许从字典创建实例时忽略额外字段
        extra = "ignore"
        # 允许字段别名
        allow_population_by_field_name = True
        # 使用枚举值而不是枚举名称
        use_enum_values = True
        # 日期时间序列化格式
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BaseModel":
        """
        从字典创建模型实例
        自动处理字段映射和类型转换
        """
        if not data:
            return None
            
        # 处理常见字段映射
        if "timestamp" in data:
            data.setdefault("created_at", data["timestamp"])
        
        # 移除None值和空字符串
        cleaned_data = {
            k: v for k, v in data.items() 
            if v is not None and v != ""
        }
        
        try:
            return cls(**cleaned_data)
        except Exception as e:
            # 如果创建失败，返回None而不是抛出异常
            return None
    
    @classmethod
    def from_list(cls, data_list: list) -> list:
        """从字典列表创建模型实例列表"""
        if not data_list:
            return []
        
        return [
            instance for instance in [
                cls.from_dict(item) for item in data_list
            ] if instance is not None
        ]
    
    def to_dict(self, exclude_none: bool = True) -> Dict[str, Any]:
        """
        转换为字典，排除property属性避免FastAPI序列化错误
        """
        # 使用Pydantic的dict方法，但排除计算属性
        data = self.dict(exclude_unset=False, exclude_defaults=False)
        
        # 移除可能导致序列化问题的property属性
        property_keys = []
        for key in dir(self.__class__):
            attr = getattr(self.__class__, key, None)
            if isinstance(attr, property):
                property_keys.append(key)
        
        # 从数据中移除property属性
        for key in property_keys:
            data.pop(key, None)
        
        if exclude_none:
            data = {k: v for k, v in data.items() if v is not None}
        
        return data
    
    def update_from_dict(self, data: Dict[str, Any]) -> "BaseModel":
        """
        从字典更新模型实例
        """
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
        return self
    
    @property
    def primary_key(self) -> Any:
        """获取主键值，子类可重写"""
        return self.id
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"{self.__class__.__name__}(id={self.primary_key})"
    
    def __repr__(self) -> str:
        """调试表示"""
        return f"{self.__class__.__name__}({self.primary_key})" 