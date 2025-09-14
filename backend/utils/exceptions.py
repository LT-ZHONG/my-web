"""
自定义异常类
"""
from fastapi import HTTPException
from typing import Optional


class CustomHTTPException(HTTPException):
    """自定义HTTP异常类"""
    
    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: Optional[str] = None,
        headers: Optional[dict] = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.error_code = error_code or f"HTTP_{status_code}"


class AuthenticationError(CustomHTTPException):
    """认证错误"""
    
    def __init__(self, detail: str = "认证失败"):
        super().__init__(
            status_code=401,
            detail=detail,
            error_code="AUTHENTICATION_ERROR"
        )


class AuthorizationError(CustomHTTPException):
    """授权错误"""
    
    def __init__(self, detail: str = "权限不足"):
        super().__init__(
            status_code=403,
            detail=detail,
            error_code="AUTHORIZATION_ERROR"
        )


class ValidationError(CustomHTTPException):
    """验证错误"""
    
    def __init__(self, detail: str = "数据验证失败"):
        super().__init__(
            status_code=422,
            detail=detail,
            error_code="VALIDATION_ERROR"
        )


class ResourceNotFoundError(CustomHTTPException):
    """资源未找到错误"""
    
    def __init__(self, detail: str = "资源未找到"):
        super().__init__(
            status_code=404,
            detail=detail,
            error_code="RESOURCE_NOT_FOUND"
        )


class DuplicateResourceError(CustomHTTPException):
    """资源重复错误"""
    
    def __init__(self, detail: str = "资源已存在"):
        super().__init__(
            status_code=409,
            detail=detail,
            error_code="DUPLICATE_RESOURCE"
        )


class RateLimitError(CustomHTTPException):
    """请求限流错误"""
    
    def __init__(self, detail: str = "请求过于频繁，请稍后再试"):
        super().__init__(
            status_code=429,
            detail=detail,
            error_code="RATE_LIMIT_EXCEEDED"
        )


class PaymentError(CustomHTTPException):
    """支付错误"""
    
    def __init__(self, detail: str = "支付处理失败"):
        super().__init__(
            status_code=402,
            detail=detail,
            error_code="PAYMENT_ERROR"
        )


class FileUploadError(CustomHTTPException):
    """文件上传错误"""
    
    def __init__(self, detail: str = "文件上传失败"):
        super().__init__(
            status_code=413,
            detail=detail,
            error_code="FILE_UPLOAD_ERROR"
        )