"""
媒体相关的Pydantic模式
"""
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, List
from datetime import datetime
from models.media import MediaType, MediaStatus


class MediaCategoryBase(BaseModel):
    """媒体分类基础模式"""
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    is_paid: bool = False
    price: float = Field(0.0, ge=0)
    sort_order: int = 0


class MediaCategoryCreate(MediaCategoryBase):
    """媒体分类创建模式"""
    pass


class MediaCategoryUpdate(BaseModel):
    """媒体分类更新模式"""
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    is_paid: Optional[bool] = None
    price: Optional[float] = Field(None, ge=0)
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


class MediaCategoryResponse(MediaCategoryBase):
    """媒体分类响应模式"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class MediaBase(BaseModel):
    """媒体基础模式"""
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    tags: Optional[str] = None
    category_id: Optional[int] = None
    is_paid: bool = False
    price: float = Field(0.0, ge=0)
    is_private: bool = False
    is_featured: bool = False


class MediaCreate(MediaBase):
    """媒体创建模式"""
    pass


class MediaUpdate(BaseModel):
    """媒体更新模式"""
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    tags: Optional[str] = None
    category_id: Optional[int] = None
    is_paid: Optional[bool] = None
    price: Optional[float] = Field(None, ge=0)
    is_private: Optional[bool] = None
    is_featured: Optional[bool] = None
    status: Optional[MediaStatus] = None


class MediaResponse(MediaBase):
    """媒体响应模式"""
    id: int
    filename: str
    original_filename: Optional[str]
    file_url: Optional[str]
    thumbnail_url: Optional[str]
    media_type: MediaType
    mime_type: Optional[str]
    file_size: Optional[int]
    file_size_mb: float
    width: Optional[int]
    height: Optional[int]
    duration: Optional[float]
    tags_list: List[str] = []
    status: MediaStatus
    view_count: int
    like_count: int
    download_count: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    published_at: Optional[datetime]
    
    @classmethod
    def from_orm_model(cls, media_obj):
        """从ORM模型创建响应对象"""
        # 处理tags_list
        tags_list = []
        if media_obj.tags:
            tags_list = [tag.strip() for tag in media_obj.tags.split(',') if tag.strip()]
        
        print(f"[MediaResponse.from_orm_model] 转换 Media ID: {media_obj.id}")
        print(f"  ORM file_url: {media_obj.file_url}")
        print(f"  ORM thumbnail_url: {media_obj.thumbnail_url}")
        print(f"  ORM file_path: {media_obj.file_path}")
        print(f"  ORM thumbnail_path: {media_obj.thumbnail_path}")
        
        return cls(
            id=media_obj.id,
            filename=media_obj.filename,
            original_filename=media_obj.original_filename,
            file_url=media_obj.file_url,
            thumbnail_url=media_obj.thumbnail_url,
            media_type=media_obj.media_type,
            mime_type=media_obj.mime_type,
            file_size=media_obj.file_size,
            file_size_mb=media_obj.file_size_mb,
            width=media_obj.width,
            height=media_obj.height,
            duration=media_obj.duration,
            title=media_obj.title,
            description=media_obj.description,
            tags=media_obj.tags,
            tags_list=tags_list,
            category_id=media_obj.category_id,
            is_paid=media_obj.is_paid,
            price=media_obj.price,
            is_private=media_obj.is_private,
            is_featured=media_obj.is_featured,
            status=media_obj.status,
            view_count=media_obj.view_count,
            like_count=media_obj.like_count,
            download_count=media_obj.download_count,
            owner_id=media_obj.owner_id,
            created_at=media_obj.created_at,
            updated_at=media_obj.updated_at,
            published_at=media_obj.published_at
        )
    
    class Config:
        from_attributes = True


class MediaUploadResponse(BaseModel):
    """媒体上传响应模式"""
    media: MediaResponse
    message: str


class MediaListQuery(BaseModel):
    """媒体列表查询模式"""
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
    search: Optional[str] = None
    media_type: Optional[MediaType] = None
    category_id: Optional[int] = None
    is_paid: Optional[bool] = None
    is_private: Optional[bool] = None
    is_featured: Optional[bool] = None
    status: Optional[MediaStatus] = None
    owner_id: Optional[int] = None
    tags: Optional[str] = None
    sort_by: Optional[str] = Field("created_at", description="排序字段")
    order: Optional[str] = Field("desc", description="排序方向: asc 或 desc")


class MediaListResponse(BaseModel):
    """媒体列表响应模式"""
    media_list: List[MediaResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class MediaPurchaseResponse(BaseModel):
    """媒体购买响应模式"""
    id: int
    user_id: int
    media_id: int
    price: float
    created_at: datetime
    
    class Config:
        from_attributes = True


class MediaStatsResponse(BaseModel):
    """媒体统计响应模式"""
    total_media: int
    total_images: int
    total_videos: int
    total_size: int
    total_size_mb: float
    paid_media: int
    free_media: int