"""
统一API响应处理器
消除Controller层中的重复响应格式代码
"""
from datetime import datetime
from typing import Any, Optional, Dict
import json


class APIResponse:
    """统一API响应格式处理器"""
    
    @staticmethod
    def success(
        data: Any = None, 
        message: str = "success",
        code: int = 0
    ) -> Dict[str, Any]:
        """成功响应"""
        return {
            "code": code,
            "message": message,
            "data": data,
            "timestamp": datetime.now().isoformat(),
            "version": "v1.0"
        }
    
    @staticmethod
    def error(
        message: str,
        code: int = 500,
        data: Any = None
    ) -> Dict[str, Any]:
        """错误响应"""
        return {
            "code": code,
            "message": message,
            "data": data,
            "timestamp": datetime.now().isoformat(),
            "version": "v1.0"
        }
    
    @staticmethod
    def paginated(
        items: list,
        total: int,
        page: int = 1,
        size: int = 20,
        message: str = "success"
    ) -> Dict[str, Any]:
        """分页响应"""
        return APIResponse.success(
            data={
                "items": items,
                "pagination": {
                    "page": page,
                    "size": size,
                    "total": total,
                    "pages": (total + size - 1) // size if size > 0 else 0
                }
            },
            message=message
        )
    
    @staticmethod
    def list_response(
        items: list,
        total: Optional[int] = None,
        message: str = "success"
    ) -> Dict[str, Any]:
        """列表响应"""
        return APIResponse.success(
            data={
                "items": items,
                "total": total or len(items)
            },
            message=message
        )
    
    @staticmethod
    def detail_response(
        item: Any,
        message: str = "success"
    ) -> Dict[str, Any]:
        """详情响应"""
        return APIResponse.success(data=item, message=message)


# 常用快捷方法
def success_response(data: Any = None, message: str = "success") -> Dict[str, Any]:
    """快捷成功响应"""
    return APIResponse.success(data, message)


def error_response(code: int, message: str, data: Any = None) -> Dict[str, Any]:
    """快捷错误响应"""
    return APIResponse.error(message, code, data) 