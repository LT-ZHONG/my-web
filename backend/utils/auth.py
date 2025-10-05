"""
认证和授权工具函数
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from database import get_db
from models.user import User
from utils.exceptions import AuthenticationError, AuthorizationError

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Bearer认证
security = HTTPBearer()
# 可选的JWT Bearer认证（不强制要求）
optional_security = HTTPBearer(auto_error=False)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    return pwd_context.hash(password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """创建访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """创建刷新令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str, token_type: str = "access") -> Dict[str, Any]:
    """验证令牌"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        # 检查令牌类型
        if payload.get("type") != token_type:
            raise AuthenticationError("无效的令牌类型")
        
        # 检查过期时间
        exp = payload.get("exp")
        if exp is None or datetime.utcfromtimestamp(exp) < datetime.utcnow():
            raise AuthenticationError("令牌已过期")
        
        return payload
    
    except JWTError:
        raise AuthenticationError("无效的令牌")


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """获取当前用户"""
    token = credentials.credentials
    
    try:
        payload = verify_token(token, "access")
        user_id = payload.get("sub")
        if user_id is None:
            raise AuthenticationError("令牌中缺少用户ID")
        
        # 从数据库获取用户信息
        from services.user_service import get_user_by_id
        user = await get_user_by_id(db, int(user_id))
        if user is None:
            raise AuthenticationError("用户不存在")
        
        if not user.is_active:
            raise AuthenticationError("用户已被禁用")
        
        return user
    
    except JWTError:
        raise AuthenticationError("无效的令牌")


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """获取当前活跃用户"""
    if not current_user.is_active:
        raise AuthenticationError("用户已被禁用")
    return current_user


async def get_current_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """获取当前管理员用户"""
    if not current_user.is_admin:
        raise AuthorizationError("需要管理员权限")
    return current_user


async def get_current_vip_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """获取当前VIP用户"""
    if not current_user.is_vip and not current_user.is_admin:
        raise AuthorizationError("需要VIP权限")
    return current_user


def create_tokens_for_user(user: User) -> Dict[str, str]:
    """为用户创建访问令牌和刷新令牌"""
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "role": user.role},
        expires_delta=access_token_expires
    )
    
    refresh_token = create_refresh_token(
        data={"sub": str(user.id)},
        expires_delta=refresh_token_expires
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


def check_permission(user: User, required_role: str) -> bool:
    """检查用户权限"""
    role_hierarchy = {
        "user": 1,
        "vip": 2,
        "admin": 3
    }
    
    user_role_level = role_hierarchy.get(user.role, 0)
    required_role_level = role_hierarchy.get(required_role, 999)
    
    return user_role_level >= required_role_level


async def optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_security),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """可选的当前用户，游客可以浏览内容，但要执行某些操作时需要登录"""
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials, db)
    except:
        return None