"""
媒体相关的Pydantic模式
"""
from pydantic import BaseModel, Field, validator
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
    published_at: Optional[datetime]
    
    @validator('tags_list', pre=True)
    def split_tags(cls, v):
        if isinstance(v, str):
            return [tag.strip() for tag in v.split(',') if tag.strip()]
        return v or []
    
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