"""
媒体文件模型
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Enum, ForeignKey, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from database import Base


class MediaType(str, enum.Enum):
    """媒体类型枚举"""
    IMAGE = "image"
    VIDEO = "video"


class MediaStatus(str, enum.Enum):
    """媒体状态枚举"""
    ACTIVE = "active"
    HIDDEN = "hidden"
    DELETED = "deleted"


class MediaCategory(Base):
    """媒体分类模型"""
    __tablename__ = "media_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="分类名称")
    description = Column(Text, comment="分类描述")
    is_paid = Column(Boolean, default=False, comment="是否为付费分类")
    price = Column(Float, default=0.0, comment="价格")
    sort_order = Column(Integer, default=0, comment="排序")
    is_active = Column(Boolean, default=True, comment="是否启用")
    
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关联关系
    media_files = relationship("Media", back_populates="category")
    
    def __repr__(self):
        return f"<MediaCategory(id={self.id}, name='{self.name}', is_paid={self.is_paid})>"


class Media(Base):
    """媒体文件模型"""
    __tablename__ = "media"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 文件信息
    filename = Column(String(255), nullable=False, comment="文件名")
    original_filename = Column(String(255), comment="原始文件名")
    file_path = Column(String(500), nullable=False, comment="文件路径")
    file_url = Column(String(500), comment="文件URL")
    thumbnail_path = Column(String(500), comment="缩略图路径")
    thumbnail_url = Column(String(500), comment="缩略图URL")
    
    # 媒体属性
    media_type = Column(Enum(MediaType), nullable=False, comment="媒体类型")
    mime_type = Column(String(100), comment="MIME类型")
    file_size = Column(Integer, comment="文件大小(字节)")
    width = Column(Integer, comment="宽度")
    height = Column(Integer, comment="高度")
    duration = Column(Float, comment="视频时长(秒)")
    
    # 内容信息
    title = Column(String(200), comment="标题")
    description = Column(Text, comment="描述")
    tags = Column(String(500), comment="标签(逗号分隔)")
    
    # 分类和权限
    category_id = Column(Integer, ForeignKey("media_categories.id"), comment="分类ID")
    is_paid = Column(Boolean, default=False, comment="是否为付费内容")
    price = Column(Float, default=0.0, comment="单独价格")
    is_private = Column(Boolean, default=False, comment="是否为私密内容")
    
    # 状态
    status = Column(Enum(MediaStatus), default=MediaStatus.ACTIVE, comment="状态")
    is_featured = Column(Boolean, default=False, comment="是否为精选")
    
    # 统计信息
    view_count = Column(Integer, default=0, comment="查看次数")
    like_count = Column(Integer, default=0, comment="点赞次数")
    download_count = Column(Integer, default=0, comment="下载次数")
    
    # 关联用户
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="所有者ID")
    
    # 时间戳
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    published_at = Column(DateTime, comment="发布时间")
    
    # 关联关系
    owner = relationship("User", back_populates="media_files")
    category = relationship("MediaCategory", back_populates="media_files")
    purchases = relationship("MediaPurchase", back_populates="media")
    
    def __repr__(self):
        return f"<Media(id={self.id}, filename='{self.filename}', type='{self.media_type}')>"
    
    @property
    def file_size_mb(self) -> float:
        """文件大小(MB)"""
        if self.file_size:
            return round(self.file_size / 1024 / 1024, 2)
        return 0.0
    
    def to_dict(self, include_file_path: bool = False) -> dict:
        """转换为字典"""
        data = {
            "id": self.id,
            "filename": self.filename,
            "original_filename": self.original_filename,
            "file_url": self.file_url,
            "thumbnail_url": self.thumbnail_url,
            "media_type": self.media_type,
            "mime_type": self.mime_type,
            "file_size": self.file_size,
            "file_size_mb": self.file_size_mb,
            "width": self.width,
            "height": self.height,
            "duration": self.duration,
            "title": self.title,
            "description": self.description,
            "tags": self.tags.split(",") if self.tags else [],
            "category_id": self.category_id,
            "is_paid": self.is_paid,
            "price": self.price,
            "is_private": self.is_private,
            "status": self.status,
            "is_featured": self.is_featured,
            "view_count": self.view_count,
            "like_count": self.like_count,
            "download_count": self.download_count,
            "owner_id": self.owner_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "published_at": self.published_at.isoformat() if self.published_at else None
        }
        
        if include_file_path:
            data["file_path"] = self.file_path
            data["thumbnail_path"] = self.thumbnail_path
        
        return data


class MediaPurchase(Base):
    """媒体购买记录"""
    __tablename__ = "media_purchases"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="购买用户ID")
    media_id = Column(Integer, ForeignKey("media.id"), nullable=False, comment="媒体ID")
    price = Column(Float, nullable=False, comment="购买价格")
    
    created_at = Column(DateTime, server_default=func.now(), comment="购买时间")
    
    # 关联关系
    user = relationship("User")
    media = relationship("Media", back_populates="purchases")
    
    def __repr__(self):
        return f"<MediaPurchase(id={self.id}, user_id={self.user_id}, media_id={self.media_id})>"