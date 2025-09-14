"""
用户相关API端点
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from database import get_db
from schemas.user import (
    UserResponse, UserUpdate, UserListQuery, UserListResponse
)
from services.user_service import (
    get_user_by_id, update_user, get_users_list
)
import os
from utils.auth import get_current_active_user, get_current_admin_user
from utils.exceptions import ResourceNotFoundError

router = APIRouter()


# 上传头像接口
@router.post("/avatar", summary="上传用户头像", response_model=UserResponse)
async def upload_avatar(
        file: UploadFile = File(...),
        current_user=Depends(get_current_active_user),
        db: AsyncSession = Depends(get_db)
):
    """
    上传头像图片，保存到 static/uploads 目录，并更新用户 avatar_url 字段
    """
    # 检查文件类型
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="只能上传图片文件")

    # 检查文件大小（最大2MB）
    contents = await file.read()
    if len(contents) > 2 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="图片大小不能超过2MB")

    # 保存文件
    upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    ext = os.path.splitext(file.filename)[-1] or ".jpg"
    filename = f"avatar_{current_user.id}{ext}"
    file_path = os.path.join(upload_dir, filename)
    with open(file_path, "wb") as f:
        f.write(contents)

    # 构造头像URL（假设静态文件通过 /static/uploads/ 访问）
    avatar_url = f"/static/uploads/{filename}"

    # 更新数据库
    update_data = UserUpdate(avatar_url=avatar_url)
    updated_user = await update_user(db, current_user.id, update_data)

    return UserResponse.from_orm(updated_user)


@router.get("/me", response_model=UserResponse, summary="获取当前用户信息")
async def get_my_profile(
        current_user=Depends(get_current_active_user)
):
    """
    获取当前登录用户的详细信息
    """
    return UserResponse.from_orm(current_user)


@router.put("/me", response_model=UserResponse, summary="更新当前用户信息")
async def update_my_profile(
        user_data: UserUpdate,
        current_user=Depends(get_current_active_user),
        db: AsyncSession = Depends(get_db)
):
    """
    更新当前用户的个人信息
    
    - **full_name**: 全名
    - **nickname**: 昵称
    - **bio**: 个人简介
    - **avatar_url**: 头像URL
    """
    try:
        updated_user = await update_user(db, current_user.id, user_data)
        return UserResponse.from_orm(updated_user)

    except ResourceNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="更新用户信息失败"
        )


@router.get("/{user_id}", response_model=UserResponse, summary="获取指定用户信息")
async def get_user_profile(
        user_id: int,
        db: AsyncSession = Depends(get_db),
        current_user=Depends(get_current_active_user)
):
    """
    获取指定用户的公开信息
    """
    user = await get_user_by_id(db, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    # 只返回公开信息
    return UserResponse.from_orm(user)


@router.get("/", response_model=UserListResponse, summary="获取用户列表")
async def get_users_list_api(
        page: int = Query(1, ge=1, description="页码"),
        page_size: int = Query(20, ge=1, le=100, description="每页数量"),
        search: Optional[str] = Query(None, description="搜索关键词"),
        role: Optional[str] = Query(None, description="用户角色"),
        status: Optional[str] = Query(None, description="用户状态"),
        is_vip: Optional[bool] = Query(None, description="是否为VIP"),
        db: AsyncSession = Depends(get_db),
        current_user=Depends(get_current_admin_user)  # 需要管理员权限
):
    """
    获取用户列表（管理员功能）
    
    支持分页和筛选：
    - **page**: 页码（从1开始）
    - **page_size**: 每页数量（1-100）
    - **search**: 搜索用户名、邮箱、姓名或昵称
    - **role**: 按角色筛选（user/vip/admin）
    - **status**: 按状态筛选（active/inactive/banned）
    - **is_vip**: 按VIP状态筛选
    """
    try:
        query = UserListQuery(
            page=page,
            page_size=page_size,
            search=search,
            role=role,
            status=status,
            is_vip=is_vip
        )

        users, total = await get_users_list(db, query)

        total_pages = (total + page_size - 1) // page_size

        return UserListResponse(
            users=[UserResponse.from_orm(user) for user in users],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="获取用户列表失败"
        )


@router.get("/stats/overview", summary="获取用户统计信息")
async def get_user_stats(
        db: AsyncSession = Depends(get_db),
        current_user=Depends(get_current_admin_user)
):
    """
    获取用户统计信息（管理员功能）
    
    返回：
    - 总用户数
    - 活跃用户数
    - VIP用户数
    - 管理员数
    - 今日新用户
    - 本月新用户
    """
    from services.user_service import get_user_stats

    try:
        stats = await get_user_stats(db)
        return {
            "success": True,
            "data": stats
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取统计信息失败"
        )
