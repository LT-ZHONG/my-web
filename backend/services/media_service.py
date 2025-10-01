"""
媒体管理服务
"""

from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, or_, desc, asc, select, func
from fastapi import UploadFile, HTTPException
from datetime import datetime

from models.media import Media, MediaCategory, MediaPurchase, MediaType, MediaStatus
from models.user import User
from schemas.media import (
    MediaCreate, MediaUpdate, MediaListQuery, MediaCategoryCreate, 
    MediaCategoryUpdate, MediaResponse, MediaListResponse, MediaStatsResponse
)
from utils.file_utils import process_uploaded_file, get_file_url, delete_file
from utils.exceptions import FileUploadError


class MediaService:
    """媒体管理服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def upload_media(
        self, 
        file: UploadFile, 
        user_id: int, 
        media_data: Optional[MediaCreate] = None
    ) -> Media:
        """上传媒体文件"""
        try:
            # 处理文件上传
            file_info = await process_uploaded_file(file, user_id)
            
            # 打印文件信息
            print(f"[MediaService.upload_media] 文件处理结果:")
            print(f"  filename: {file_info['filename']}")
            print(f"  file_path: {file_info['file_path']}")
            print(f"  thumbnail_path: {file_info.get('thumbnail_path')}")
            print(f"  file_type: {file_info['file_type']}")
            
            # 创建媒体记录
            file_url = get_file_url(file_info["file_path"])
            thumbnail_url = get_file_url(file_info["thumbnail_path"]) if file_info.get("thumbnail_path") else None
            
            print(f"[MediaService.upload_media] URL生成结果:")
            print(f"  file_url: {file_url}")
            print(f"  thumbnail_url: {thumbnail_url}")
            
            media = Media(
                filename=file_info["filename"],
                original_filename=file_info["original_filename"],
                file_path=file_info["file_path"],
                file_url=file_url,
                thumbnail_path=file_info.get("thumbnail_path"),
                thumbnail_url=thumbnail_url,
                media_type=MediaType.IMAGE if file_info["file_type"] == "image" else MediaType.VIDEO,
                mime_type=file_info["mime_type"],
                file_size=file_info["file_size"],
                width=file_info.get("width"),
                height=file_info.get("height"),
                owner_id=user_id,
                published_at=datetime.utcnow()
            )
            
            # 设置媒体属性
            if media_data:
                media.title = media_data.title
                media.description = media_data.description
                media.tags = media_data.tags
                media.category_id = media_data.category_id
                media.is_paid = media_data.is_paid
                media.price = media_data.price
                media.is_private = media_data.is_private
                media.is_featured = media_data.is_featured
            
            self.db.add(media)
            await self.db.commit()
            await self.db.refresh(media)
            
            # 更新用户媒体计数
            await self._update_user_media_count(user_id)
            
            return media
            
        except FileUploadError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")
    
    async def get_media_list(
        self, 
        query: MediaListQuery,
        current_user_id: Optional[int] = None,
        is_admin: bool = False
    ) -> MediaListResponse:
        """获取媒体列表"""
        filters = []
        
        print(f"[MediaService.get_media_list] 用户ID: {current_user_id}, 是否管理员: {is_admin}")
        
        # 基础过滤条件
        if not is_admin:
            # 非管理员只能看到状态为active的媒体
            filters.append(Media.status == MediaStatus.ACTIVE)
            print(f"[MediaService.get_media_list] 添加过滤: status == ACTIVE")
            
            # 如果不是所有者，不能看到私密内容
            if query.owner_id != current_user_id:
                filters.append(Media.is_private == False)
                print(f"[MediaService.get_media_list] 添加过滤: is_private == False")
        
        # 搜索条件
        if query.search:
            search_term = f"%{query.search}%"
            filters.append(
                or_(
                    Media.title.ilike(search_term),
                    Media.description.ilike(search_term),
                    Media.tags.ilike(search_term),
                    Media.original_filename.ilike(search_term)
                )
            )
        
        # 过滤条件
        if query.media_type:
            filters.append(Media.media_type == query.media_type)
        if query.category_id:
            filters.append(Media.category_id == query.category_id)
        if query.is_paid is not None:
            filters.append(Media.is_paid == query.is_paid)
        if query.is_private is not None:
            filters.append(Media.is_private == query.is_private)
        if query.is_featured is not None:
            filters.append(Media.is_featured == query.is_featured)
        if query.status:
            filters.append(Media.status == query.status)
        if query.owner_id:
            filters.append(Media.owner_id == query.owner_id)
        if query.tags:
            filters.append(Media.tags.ilike(f"%{query.tags}%"))
        
        # 构建查询
        stmt = select(Media).filter(and_(*filters))
        
        # 计算总数
        count_stmt = select(func.count(Media.id)).filter(and_(*filters))
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar()
        
        print(f"[MediaService.get_media_list] 符合条件的总数: {total}")
        
        # 动态排序
        sort_field = query.sort_by or "created_at"
        sort_order = query.order or "desc"
        
        # 映射排序字段
        sort_column_map = {
            "created_at": Media.created_at,
            "views": Media.view_count,
            "likes": Media.like_count,
            "title": Media.title,
            "updated_at": Media.updated_at,
            "file_size": Media.file_size
        }
        
        # 获取排序列
        sort_column = sort_column_map.get(sort_field, Media.created_at)
        
        # 应用排序方向
        if sort_order.lower() == "asc":
            order_by_clause = asc(sort_column)
        else:
            order_by_clause = desc(sort_column)
        
        # 分页和排序
        stmt = (
            stmt
            .order_by(desc(Media.is_featured), order_by_clause)
            .offset((query.page - 1) * query.page_size)
            .limit(query.page_size)
        )
        
        result = await self.db.execute(stmt)
        media_list = result.scalars().all()
        
        print(f"[MediaService.get_media_list] 查询到 {len(media_list)} 条数据")
        for media in media_list:
            print(f"  - Media ID: {media.id}, 标题: {media.title}, 状态: {media.status}, 私密: {media.is_private}")
        
        # 转换为响应对象
        from schemas.media import MediaResponse
        media_responses = [MediaResponse.from_orm_model(media) for media in media_list]
        
        # 打印转换后的响应数据
        print(f"[MediaService.get_media_list] 转换为响应对象后:")
        for media_resp in media_responses:
            print(f"  - ID: {media_resp.id}, 标题: {media_resp.title}")
            print(f"    file_url: {media_resp.file_url}")
            print(f"    thumbnail_url: {media_resp.thumbnail_url}")
            print(f"    media_type: {media_resp.media_type}")
        
        # 计算总页数
        total_pages = (total + query.page_size - 1) // query.page_size
        
        return MediaListResponse(
            media_list=media_responses,
            total=total,
            page=query.page,
            page_size=query.page_size,
            total_pages=total_pages
        )
    
    async def get_media_by_id(self, media_id: int, current_user_id: Optional[int] = None, is_admin: bool = False) -> Optional[Media]:
        """根据ID获取媒体"""
        stmt = select(Media).filter(Media.id == media_id)
        result = await self.db.execute(stmt)
        media = result.scalar_one_or_none()
        
        if not media:
            return None
        
        # 权限检查
        if not is_admin:
            # 检查状态
            if media.status != MediaStatus.ACTIVE:
                return None
            
            # 检查私密内容权限
            if media.is_private and media.owner_id != current_user_id:
                return None
        
        # 增加查看次数
        if current_user_id != media.owner_id:  # 不对所有者计数
            media.view_count += 1
            await self.db.commit()
        
        return media
    
    async def update_media(self, media_id: int, update_data: MediaUpdate, user_id: int, is_admin: bool = False) -> Optional[Media]:
        """更新媒体信息"""
        stmt = select(Media).filter(Media.id == media_id)
        result = await self.db.execute(stmt)
        media = result.scalar_one_or_none()
        
        if not media:
            return None
        
        # 权限检查：只有所有者或管理员可以修改
        if not is_admin and media.owner_id != user_id:
            raise HTTPException(status_code=403, detail="无权限修改该媒体")
        
        # 更新字段
        for field, value in update_data.dict(exclude_unset=True).items():
            setattr(media, field, value)
        
        media.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(media)
        
        return media
    
    async def delete_media(self, media_id: int, user_id: int, is_admin: bool = False) -> bool:
        """删除媒体"""
        stmt = select(Media).filter(Media.id == media_id)
        result = await self.db.execute(stmt)
        media = result.scalar_one_or_none()
        
        if not media:
            return False
        
        # 权限检查
        if not is_admin and media.owner_id != user_id:
            raise HTTPException(status_code=403, detail="无权限删除该媒体")
        
        try:
            # 删除文件
            if media.file_path:
                await delete_file(media.file_path)
            if media.thumbnail_path:
                await delete_file(media.thumbnail_path)
            
            # 删除数据库记录
            await self.db.delete(media)
            await self.db.commit()
            
            # 更新用户媒体计数
            await self._update_user_media_count(media.owner_id)
            
            return True
            
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(status_code=500, detail=f"删除媒体失败: {str(e)}")
    
    async def toggle_like(self, media_id: int, user_id: int) -> Tuple[bool, int]:
        """切换点赞状态"""
        stmt = select(Media).filter(Media.id == media_id)
        result = await self.db.execute(stmt)
        media = result.scalar_one_or_none()
        
        if not media:
            raise HTTPException(status_code=404, detail="媒体不存在")
        
        # 这里简化处理，实际应该有单独的点赞表
        # 暂时只更新点赞数，不跟踪具体用户
        media.like_count += 1
        await self.db.commit()
        
        return True, media.like_count
    
    async def get_media_stats(self, user_id: Optional[int] = None) -> MediaStatsResponse:
        """获取媒体统计信息"""
        stmt = select(Media)
        
        if user_id:
            stmt = stmt.filter(Media.owner_id == user_id)
        
        result = await self.db.execute(stmt)
        media_list = result.scalars().all()
        
        total_media = len(media_list)
        total_images = len([m for m in media_list if m.media_type == MediaType.IMAGE])
        total_videos = len([m for m in media_list if m.media_type == MediaType.VIDEO])
        total_size = sum(m.file_size or 0 for m in media_list)
        total_size_mb = round(total_size / 1024 / 1024, 2)
        paid_media = len([m for m in media_list if m.is_paid])
        free_media = total_media - paid_media
        
        return MediaStatsResponse(
            total_media=total_media,
            total_images=total_images,
            total_videos=total_videos,
            total_size=total_size,
            total_size_mb=total_size_mb,
            paid_media=paid_media,
            free_media=free_media
        )
    
    async def _update_user_media_count(self, user_id: int):
        """更新用户媒体计数"""
        count_stmt = select(func.count(Media.id)).filter(
            Media.owner_id == user_id,
            Media.status == MediaStatus.ACTIVE
        )
        count_result = await self.db.execute(count_stmt)
        count = count_result.scalar()
        
        user_stmt = select(User).filter(User.id == user_id)
        user_result = await self.db.execute(user_stmt)
        user = user_result.scalar_one_or_none()
        if user:
            user.media_count = count
            await self.db.commit()


class MediaCategoryService:
    """媒体分类服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_category(self, category_data: MediaCategoryCreate) -> MediaCategory:
        """创建媒体分类"""
        category = MediaCategory(**category_data.dict())
        self.db.add(category)
        await self.db.commit()
        await self.db.refresh(category)
        return category
    
    async def get_categories(self, active_only: bool = True) -> List[MediaCategory]:
        """获取分类列表"""
        stmt = select(MediaCategory)
        
        if active_only:
            stmt = stmt.filter(MediaCategory.is_active == True)
        
        stmt = stmt.order_by(MediaCategory.sort_order, MediaCategory.name)
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def get_category_by_id(self, category_id: int) -> Optional[MediaCategory]:
        """根据ID获取分类"""
        stmt = select(MediaCategory).filter(MediaCategory.id == category_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def update_category(self, category_id: int, update_data: MediaCategoryUpdate) -> Optional[MediaCategory]:
        """更新分类"""
        stmt = select(MediaCategory).filter(MediaCategory.id == category_id)
        result = await self.db.execute(stmt)
        category = result.scalar_one_or_none()
        
        if not category:
            return None
        
        for field, value in update_data.dict(exclude_unset=True).items():
            setattr(category, field, value)
        
        category.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(category)
        
        return category
    
    async def delete_category(self, category_id: int) -> bool:
        """删除分类"""
        stmt = select(MediaCategory).filter(MediaCategory.id == category_id)
        result = await self.db.execute(stmt)
        category = result.scalar_one_or_none()
        
        if not category:
            return False
        
        # 检查是否有媒体使用该分类
        count_stmt = select(func.count(Media.id)).filter(Media.category_id == category_id)
        count_result = await self.db.execute(count_stmt)
        media_count = count_result.scalar()
        if media_count > 0:
            raise HTTPException(status_code=400, detail="该分类下还有媒体文件，无法删除")
        
        await self.db.delete(category)
        await self.db.commit()
        return True
