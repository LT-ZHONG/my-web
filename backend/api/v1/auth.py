"""
认证相关API端点
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from schemas.user import (
    UserCreate, UserLogin, UserResponse, TokenResponse, 
    TokenRefresh, PasswordChange
)
from services.user_service import create_user, authenticate_user, update_user_password
from utils.auth import (
    create_tokens_for_user, verify_token, get_current_user,
    get_current_active_user
)
from utils.exceptions import AuthenticationError, ValidationError

router = APIRouter()
security = HTTPBearer()


@router.post("/register", response_model=TokenResponse, summary="用户注册")
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    用户注册
    
    - **email**: 邮箱地址
    - **username**: 用户名（3-50个字符，只能包含字母和数字）
    - **password**: 密码（6-100个字符）
    - **confirm_password**: 确认密码
    - **full_name**: 全名（可选）
    - **nickname**: 昵称（可选）
    - **bio**: 个人简介（可选）
    """
    try:
        # 创建用户
        user = await create_user(db, user_data)
        
        # 生成令牌
        tokens = create_tokens_for_user(user)
        
        return TokenResponse(
            **tokens,
            user=UserResponse.from_orm(user)
        )
    
    except Exception as e:
        if "邮箱已被注册" in str(e) or "用户名已被使用" in str(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="注册失败，请检查输入信息"
        )


@router.post("/login", response_model=TokenResponse, summary="用户登录")
async def login(
    login_data: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """
    用户登录
    
    - **username**: 用户名或邮箱
    - **password**: 密码
    """
    user = await authenticate_user(db, login_data.username, login_data.password)
    
    if not user:
        raise AuthenticationError("用户名或密码错误")
    
    # 生成令牌
    tokens = create_tokens_for_user(user)
    
    return TokenResponse(
        **tokens,
        user=UserResponse.from_orm(user)
    )


@router.post("/refresh", response_model=TokenResponse, summary="刷新令牌")
async def refresh_token(
    refresh_data: TokenRefresh,
    db: AsyncSession = Depends(get_db)
):
    """
    刷新访问令牌
    
    - **refresh_token**: 刷新令牌
    """
    try:
        # 验证刷新令牌
        payload = verify_token(refresh_data.refresh_token, "refresh")
        user_id = payload.get("sub")
        
        if not user_id:
            raise AuthenticationError("无效的刷新令牌")
        
        # 获取用户信息
        from services.user_service import get_user_by_id
        user = await get_user_by_id(db, int(user_id))
        
        if not user or not user.is_active:
            raise AuthenticationError("用户不存在或已被禁用")
        
        # 生成新的令牌
        tokens = create_tokens_for_user(user)
        
        return TokenResponse(
            **tokens,
            user=UserResponse.from_orm(user)
        )
    
    except Exception as e:
        raise AuthenticationError("令牌刷新失败")


@router.post("/change-password", summary="修改密码")
async def change_password(
    password_data: PasswordChange,
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    修改密码
    
    - **old_password**: 当前密码
    - **new_password**: 新密码（6-100个字符）
    - **confirm_password**: 确认新密码
    """
    try:
        success = await update_user_password(
            db, 
            current_user.id, 
            password_data.old_password, 
            password_data.new_password
        )
        
        if success:
            return {"message": "密码修改成功"}
        else:
            raise ValidationError("密码修改失败")
    
    except AuthenticationError:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密码修改失败"
        )


@router.get("/me", response_model=UserResponse, summary="获取当前用户信息")
async def get_current_user_info(
    current_user=Depends(get_current_active_user)
):
    """
    获取当前登录用户的详细信息
    """
    return UserResponse.from_orm(current_user)


@router.post("/logout", summary="用户登出")
async def logout():
    """
    用户登出
    
    注意：由于使用JWT令牌，服务端无状态，实际的登出需要客户端删除存储的令牌
    """
    return {"message": "登出成功"}


@router.post("/verify-token", summary="验证令牌")
async def verify_access_token(
    current_user = Depends(get_current_user)
):
    """
    验证访问令牌是否有效
    """
    return {
        "valid": True,
        "user_id": current_user.id,
        "username": current_user.username,
        "role": current_user.role
    }
