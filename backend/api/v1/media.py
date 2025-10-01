"""
媒体相关API端点
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
import os

from database import get_db
from models.user import User
from models.media import MediaType, MediaStatus
from schemas.media import (
    MediaResponse, MediaCreate, MediaUpdate, MediaListQuery, MediaListResponse,
    MediaUploadResponse, MediaStatsResponse, MediaCategoryResponse, 
    MediaCategoryCreate, MediaCategoryUpdate
)
from services.media_service import MediaService, MediaCategoryService
from utils.auth import get_current_user, get_current_admin_user

router = APIRouter()


@router.get("/", response_model=MediaListResponse)
async def get_media_list(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    media_type: Optional[MediaType] = Query(None, description="媒体类型"),
    category_id: Optional[int] = Query(None, description="分类ID"),
    is_paid: Optional[bool] = Query(None, description="是否付费"),
    is_private: Optional[bool] = Query(None, description="是否私密"),
    is_featured: Optional[bool] = Query(None, description="是否精选"),
    status: Optional[MediaStatus] = Query(None, description="状态"),
    owner_id: Optional[int] = Query(None, description="所有者ID"),
    tags: Optional[str] = Query(None, description="标签"),
    sort_by: Optional[str] = Query("created_at", description="排序字段"),
    order: Optional[str] = Query("desc", description="排序方向"),
    current_user: Optional[User] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取媒体列表"""
    print(f"[获取媒体列表] 用户: {current_user.username if current_user else '游客'}, 页码: {page}, 页大小: {page_size}")
    print(f"[获取媒体列表] 筛选条件 - 类型: {media_type}, 付费: {is_paid}, 私密: {is_private}")
    
    query = MediaListQuery(
        page=page,
        page_size=page_size,
        search=search,
        media_type=media_type,
        category_id=category_id,
        is_paid=is_paid,
        is_private=is_private,
        is_featured=is_featured,
        status=status,
        owner_id=owner_id,
        tags=tags,
        sort_by=sort_by,
        order=order
    )
    
    service = MediaService(db)
    result = await service.get_media_list(
        query,
        current_user_id=current_user.id if current_user else None,
        is_admin=current_user.is_admin if current_user else False
    )
    
    print(f"[获取媒体列表] 返回结果 - 总数: {result.total}, 当前页数据: {len(result.media_list)}")
    if result.media_list:
        for media in result.media_list:
            print(f"  - ID: {media.id}, 标题: {media.title}, 状态: {media.status}")
    
    return result


@router.post("/upload", response_model=MediaUploadResponse)
async def upload_media(
    file: UploadFile = File(..., description="上传的文件"),
    title: Optional[str] = Form(None, description="标题"),
    description: Optional[str] = Form(None, description="描述"),
    tags: Optional[str] = Form(None, description="标签"),
    category_id: Optional[int] = Form(None, description="分类ID"),
    is_paid: bool = Form(False, description="是否付费"),
    price: float = Form(0.0, description="价格"),
    is_private: bool = Form(False, description="是否私密"),
    is_featured: bool = Form(False, description="是否精选"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """上传媒体文件"""
    print(f"[上传媒体] 用户ID: {current_user.id}, 文件名: {file.filename}")
    print(f"[上传媒体] 标题: {title}, 付费: {is_paid}, 价格: {price}")
    
    media_data = MediaCreate(
        title=title,
        description=description,
        tags=tags,
        category_id=category_id,
        is_paid=is_paid,
        price=price,
        is_private=is_private,
        is_featured=is_featured
    )
    
    service = MediaService(db)
    media = await service.upload_media(file, current_user.id, media_data)
    
    print(f"[上传媒体] 创建成功 - ID: {media.id}, 状态: {media.status}")
    
    from schemas.media import MediaResponse
    media_response = MediaResponse.from_orm_model(media)
    
    result = MediaUploadResponse(
        media=media_response,
        message="文件上传成功"
    )
    
    print(f"[上传媒体] 返回响应 - Media ID: {media_response.id}, Status: {media_response.status}")
    
    return result


@router.get("/{media_id}", response_model=MediaResponse)
async def get_media_detail(
    media_id: int,
    current_user: Optional[User] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取媒体详情"""
    service = MediaService(db)
    media = await service.get_media_by_id(
        media_id,
        current_user_id=current_user.id if current_user else None,
        is_admin=current_user.is_admin if current_user else False
    )
    
    if not media:
        raise HTTPException(status_code=404, detail="媒体不存在")
    
    from schemas.media import MediaResponse
    return MediaResponse.from_orm_model(media)


@router.put("/{media_id}", response_model=MediaResponse)
async def update_media(
    media_id: int,
    update_data: MediaUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """更新媒体信息"""
    service = MediaService(db)
    media = await service.update_media(
        media_id, 
        update_data, 
        current_user.id, 
        is_admin=current_user.is_admin
    )
    
    if not media:
        raise HTTPException(status_code=404, detail="媒体不存在")
    
    from schemas.media import MediaResponse
    return MediaResponse.from_orm_model(media)


@router.delete("/{media_id}")
async def delete_media(
    media_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """删除媒体"""
    service = MediaService(db)
    success = await service.delete_media(
        media_id, 
        current_user.id, 
        is_admin=current_user.is_admin
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="媒体不存在")
    
    return {"message": "媒体删除成功"}


@router.post("/{media_id}/like")
async def toggle_like(
    media_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """切换点赞状态"""
    service = MediaService(db)
    is_liked, like_count = await service.toggle_like(media_id, current_user.id)
    
    return {
        "message": "操作成功",
        "is_liked": is_liked,
        "like_count": like_count
    }


@router.get("/{media_id}/download")
async def download_media(
    media_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """下载媒体文件"""
    service = MediaService(db)
    media = await service.get_media_by_id(
        media_id,
        current_user_id=current_user.id,
        is_admin=current_user.is_admin
    )
    
    if not media:
        raise HTTPException(status_code=404, detail="媒体不存在")
    
    # 检查付费内容权限
    if media.is_paid and media.owner_id != current_user.id:
        # 这里应该检查用户是否已购买，简化处理
        if not current_user.is_vip:
            raise HTTPException(status_code=403, detail="需要购买该内容或开通VIP")
    
    # 增加下载计数
    media.download_count += 1
    db.commit()
    
    if not os.path.exists(media.file_path):
        raise HTTPException(status_code=404, detail="文件不存在")
    
    return FileResponse(
        path=media.file_path,
        filename=media.original_filename or media.filename,
        media_type=media.mime_type
    )


@router.get("/stats/overview", response_model=MediaStatsResponse)
async def get_media_stats(
    owner_id: Optional[int] = Query(None, description="所有者ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取媒体统计信息"""
    # 如果指定了owner_id且不是管理员，只能查看自己的统计
    if owner_id and not current_user.is_admin and owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权限查看该用户统计")
    
    # 如果没有指定owner_id，普通用户只能查看自己的
    if not owner_id and not current_user.is_admin:
        owner_id = current_user.id
    
    service = MediaService(db)
    return await service.get_media_stats(owner_id)


# 媒体分类相关API
@router.get("/categories/", response_model=List[MediaCategoryResponse])
async def get_categories(
    active_only: bool = Query(True, description="只获取启用的分类"),
    db: AsyncSession = Depends(get_db)
):
    """获取分类列表"""
    service = MediaCategoryService(db)
    return await service.get_categories(active_only)


@router.post("/categories/", response_model=MediaCategoryResponse)
async def create_category(
    category_data: MediaCategoryCreate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """创建分类（管理员）"""
    service = MediaCategoryService(db)
    return await service.create_category(category_data)


@router.get("/categories/{category_id}", response_model=MediaCategoryResponse)
async def get_category(
    category_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取分类详情"""
    service = MediaCategoryService(db)
    category = await service.get_category_by_id(category_id)
    
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    
    return category


@router.put("/categories/{category_id}", response_model=MediaCategoryResponse)
async def update_category(
    category_id: int,
    update_data: MediaCategoryUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """更新分类（管理员）"""
    service = MediaCategoryService(db)
    category = await service.update_category(category_id, update_data)
    
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    
    return category


@router.delete("/categories/{category_id}")
async def delete_category(
    category_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """删除分类（管理员）"""
    service = MediaCategoryService(db)
    success = await service.delete_category(category_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="分类不存在")
    
    return {"message": "分类删除成功"}
