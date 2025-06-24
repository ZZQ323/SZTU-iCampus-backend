"""
统一API响应格式工具类
严格按照API_DESIGN_FIXED.md文档标准实现
"""
from datetime import datetime
from typing import Any, Optional, Dict


class APIResponse:
    """
    统一API响应格式类
    严格按照API文档标准：
    {
        "code": 0,           // 0为成功，其他为错误码
        "message": "success", // 返回消息  
        "data": {},          // 具体数据
        "timestamp": "2024-03-01T12:30:00Z", // ISO 8601格式时间戳
        "version": "v1.0"
    }
    """
    
    @staticmethod
    def success(
        data: Any = None, 
        message: str = "success"
    ) -> Dict[str, Any]:
        """
        成功响应
        
        Args:
            data: 响应数据
            message: 响应消息，默认"success"
        
        Returns:
            标准格式的响应字典
        """
        return {
            "code": 0,
            "message": message,
            "data": data,
            "timestamp": datetime.now().isoformat() + "Z",
            "version": "v1.0"
        }
    
    @staticmethod
    def error(
        code: int,
        message: str,
        data: Any = None
    ) -> Dict[str, Any]:
        """
        错误响应
        
        Args:
            code: 错误码（非0）
            message: 错误消息
            data: 错误详情数据
        
        Returns:
            标准格式的错误响应字典
        """
        return {
            "code": code,
            "message": message, 
            "data": data,
            "timestamp": datetime.now().isoformat() + "Z",
            "version": "v1.0"
        }
    
    @staticmethod
    def client_error(message: str = "Bad Request", data: Any = None) -> Dict[str, Any]:
        """客户端错误 (400)"""
        return APIResponse.error(400, message, data)
    
    @staticmethod
    def unauthorized(message: str = "Unauthorized", data: Any = None) -> Dict[str, Any]:
        """未授权错误 (401)"""
        return APIResponse.error(401, message, data)
    
    @staticmethod
    def forbidden(message: str = "Forbidden", data: Any = None) -> Dict[str, Any]:
        """禁止访问错误 (403)"""
        return APIResponse.error(403, message, data)
    
    @staticmethod
    def not_found(message: str = "Not Found", data: Any = None) -> Dict[str, Any]:
        """资源不存在错误 (404)"""
        return APIResponse.error(404, message, data)
    
    @staticmethod
    def server_error(message: str = "Internal Server Error", data: Any = None) -> Dict[str, Any]:
        """服务器错误 (500)"""
        return APIResponse.error(500, message, data)


# 常用快捷方法
def success_response(data: Any = None, message: str = "success") -> Dict[str, Any]:
    """快捷成功响应"""
    return APIResponse.success(data, message)


def error_response(code: int, message: str, data: Any = None) -> Dict[str, Any]:
    """快捷错误响应"""
    return APIResponse.error(code, message, data) 