from fastapi import HTTPException, status


class AuthException(HTTPException):
    """认证相关异常的基类"""

    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class InvalidSessionException(AuthException):
    """无效会话异常"""

    def __init__(self):
        super().__init__("Invalid or expired session")


class UnauthorizedException(AuthException):
    """未授权异常"""

    def __init__(self):
        super().__init__("Unauthorized access")


class ExternalAuthException(HTTPException):
    """外部认证异常"""

    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )