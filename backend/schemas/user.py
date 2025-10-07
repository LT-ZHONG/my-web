"""
用户相关的Pydantic模式
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime
from models.user import UserRole, UserStatus


class UserBase(BaseModel):
    """用户基础模式"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = Field(None, max_length=100)
    nickname: Optional[str] = Field(None, max_length=50)
    bio: Optional[str] = None
    phone: Optional[str] = None


class UserCreate(UserBase):
    """用户创建模式"""
    password: str = Field(..., min_length=6, max_length=100)
    confirm_password: str
    
    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('密码确认不匹配')
        return v
    
    @validator('username')
    def username_alphanumeric(cls, v):
        if not v.isalnum():
            raise ValueError('用户名只能包含字母和数字')
        return v


class UserUpdate(BaseModel):
    """用户更新模式"""
    full_name: Optional[str] = Field(None, max_length=100)
    nickname: Optional[str] = Field(None, max_length=50)
    bio: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None


class UserResponse(UserBase):
    """用户响应模式"""
    id: int
    avatar_url: Optional[str]
    role: UserRole
    status: UserStatus
    is_active: bool
    is_verified: bool
    is_vip: bool
    vip_expire_at: Optional[datetime]
    is_admin: bool
    created_at: datetime
    last_login_at: Optional[datetime]
    media_count: int
    credits: int
    
    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """用户登录模式"""
    username: str  # 可以是用户名或邮箱
    password: str


class UserRegister(UserCreate):
    """用户注册模式"""
    pass


class PasswordChange(BaseModel):
    """密码修改模式"""
    old_password: str
    new_password: str = Field(..., min_length=6, max_length=100)
    confirm_password: str
    
    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('新密码确认不匹配')
        return v


class TokenResponse(BaseModel):
    """令牌响应模式"""
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    user: UserResponse


class TokenRefresh(BaseModel):
    """令牌刷新模式"""
    refresh_token: str


# 管理员相关模式
class UserAdminUpdate(BaseModel):
    """管理员用户更新模式"""
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    is_vip: Optional[bool] = None
    vip_expire_at: Optional[datetime] = None


class UserListQuery(BaseModel):
    """用户列表查询模式"""
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
    search: Optional[str] = None
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None
    is_vip: Optional[bool] = None


class UserListResponse(BaseModel):
    """用户列表响应模式"""
    users: List[UserResponse]
    total: int
    page: int
    page_size: int
    total_pages: int