"""
文件处理工具函数
"""
import os
import cv2
import uuid
import aiofiles
import mimetypes
from PIL import Image
from pathlib import Path
from fastapi import UploadFile
from typing import Tuple, List

from config import settings
from utils.exceptions import FileUploadError


def generate_filename(original_filename: str) -> str:
    """生成唯一的文件名"""
    file_extension = Path(original_filename).suffix.lower()
    unique_filename = f"{uuid.uuid4().hex}{file_extension}"
    return unique_filename


def get_file_type(content_type: str) -> str:
    """根据MIME类型判断文件类型"""
    if content_type in settings.ALLOWED_IMAGE_TYPES:
        return "image"
    elif content_type in settings.ALLOWED_VIDEO_TYPES:
        return "video"
    else:
        return "unknown"


def validate_file_type(file: UploadFile) -> Tuple[bool, str]:
    """验证文件类型"""
    if not file.content_type:
        return False, "无法识别文件类型"
    
    file_type = get_file_type(file.content_type)
    if file_type == "unknown":
        return False, f"不支持的文件类型: {file.content_type}"
    
    return True, file_type


def validate_file_size(file: UploadFile) -> bool:
    """验证文件大小"""
    if file.size and file.size > settings.MAX_FILE_SIZE:
        return False
    return True


def get_upload_path(file_type: str, user_id: int) -> str:
    """获取上传路径"""
    base_path = Path(settings.UPLOAD_DIR)
    user_path = base_path / file_type / str(user_id)
    user_path.mkdir(parents=True, exist_ok=True)
    return str(user_path)


async def save_uploaded_file(file: UploadFile, file_path: str) -> bool:
    """保存上传的文件"""
    try:
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        return True
    except Exception as e:
        print(f"保存文件失败: {e}")
        return False


async def create_image_thumbnail(image_path: str, thumbnail_path: str, size: Tuple[int, int] = (300, 300)) -> bool:
    """创建图片缩略图"""
    try:
        with Image.open(image_path) as img:
            # 保持纵横比的缩略图
            img.thumbnail(size, Image.Resampling.LANCZOS)
            
            # 如果是RGBA模式的PNG，转换为RGB
            if img.mode in ("RGBA", "P"):
                background = Image.new("RGB", img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
                img = background
            
            img.save(thumbnail_path, "JPEG", quality=85, optimize=True)
        return True
    except Exception as e:
        print(f"创建图片缩略图失败: {e}")
        return False


async def create_video_thumbnail(video_path: str, thumbnail_path: str, size: Tuple[int, int] = (300, 300)) -> bool:
    """创建视频缩略图（提取第一帧）"""
    try:
        # 打开视频文件
        video = cv2.VideoCapture(video_path)
        
        # 读取第一帧
        success, frame = video.read()
        video.release()
        
        if not success or frame is None:
            print(f"无法读取视频帧: {video_path}")
            return False
        
        # 将 OpenCV 的 BGR 格式转换为 RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # 转换为 PIL Image
        img = Image.fromarray(frame_rgb)
        
        # 创建缩略图（保持纵横比）
        img.thumbnail(size, Image.Resampling.LANCZOS)
        
        # 保存为 JPEG
        img.save(thumbnail_path, "JPEG", quality=85, optimize=True)
        
        print(f"视频缩略图创建成功: {thumbnail_path}")
        return True
        
    except Exception as e:
        print(f"创建视频缩略图失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def get_file_info(file_path: str) -> dict:
    """获取文件信息"""
    if not os.path.exists(file_path):
        return {}
    
    stat = os.stat(file_path)
    mime_type, _ = mimetypes.guess_type(file_path)
    
    info = {
        "size": stat.st_size,
        "created_at": stat.st_ctime,
        "modified_at": stat.st_mtime,
        "mime_type": mime_type
    }
    
    # 如果是图片，获取尺寸信息
    if mime_type and mime_type.startswith("image/"):
        try:
            with Image.open(file_path) as img:
                info["width"] = img.width
                info["height"] = img.height
                info["format"] = img.format
        except:
            pass
    
    return info


async def delete_file(file_path: str) -> bool:
    """删除文件"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
        return True
    except Exception as e:
        print(f"删除文件失败: {e}")
        return False


async def process_uploaded_file(
    file: UploadFile,
    user_id: int,
    create_thumb: bool = True
) -> dict:
    """处理上传的文件"""
    # 验证文件类型
    is_valid, file_type_or_error = validate_file_type(file)
    if not is_valid:
        raise FileUploadError(file_type_or_error)
    
    # 验证文件大小
    if not validate_file_size(file):
        raise FileUploadError(f"文件大小超过限制 ({settings.MAX_FILE_SIZE / 1024 / 1024:.1f}MB)")
    
    file_type = file_type_or_error
    
    # 生成文件名和路径
    filename = generate_filename(file.filename)
    upload_path = get_upload_path(file_type, user_id)
    file_path = os.path.join(upload_path, filename)
    
    # 保存文件
    success = await save_uploaded_file(file, file_path)
    if not success:
        raise FileUploadError("文件保存失败")
    
    # 获取文件信息
    file_info = get_file_info(file_path)
    
    # 创建缩略图
    thumbnail_path = None
    if create_thumb:
        thumbnail_filename = f"thumb_{filename}"
        # 视频缩略图统一使用 .jpg 扩展名
        if file_type == "video":
            thumbnail_filename = f"thumb_{Path(filename).stem}.jpg"
        thumbnail_path = os.path.join(upload_path, thumbnail_filename)
        
        if file_type == "image":
            # 为图片创建缩略图
            success = await create_image_thumbnail(file_path, thumbnail_path)
            if not success:
                thumbnail_path = None
        elif file_type == "video":
            # 为视频创建缩略图（提取第一帧）
            success = await create_video_thumbnail(file_path, thumbnail_path)
            if not success:
                thumbnail_path = None
    
    return {
        "filename": filename,
        "original_filename": file.filename,
        "file_path": file_path,
        "thumbnail_path": thumbnail_path,
        "file_type": file_type,
        "file_size": file_info.get("size", 0),
        "mime_type": file_info.get("mime_type", file.content_type),
        "width": file_info.get("width"),
        "height": file_info.get("height")
    }


def get_file_url(file_path: str) -> str:
    """获取文件的URL路径"""
    if not file_path:
        print(f"[get_file_url] 警告: file_path 为空")
        return None
    
    # 移除uploads目录前的路径部分
    relative_path = file_path.replace(settings.UPLOAD_DIR, "").lstrip("/\\")
    url = f"/static/uploads/{relative_path.replace(os.sep, '/')}"
    
    print(f"[get_file_url] 转换:")
    print(f"  file_path: {file_path}")
    print(f"  UPLOAD_DIR: {settings.UPLOAD_DIR}")
    print(f"  relative_path: {relative_path}")
    print(f"  最终URL: {url}")
    
    return url


def clean_empty_directories(directory: str):
    """清理空目录"""
    try:
        for root, dirs, files in os.walk(directory, topdown=False):
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                try:
                    if not os.listdir(dir_path):  # 如果目录为空
                        os.rmdir(dir_path)
                except OSError:
                    pass
    except Exception as e:
        print(f"清理空目录失败: {e}")


async def batch_delete_files(file_paths: List[str]) -> int:
    """批量删除文件"""
    deleted_count = 0
    for file_path in file_paths:
        if await delete_file(file_path):
            deleted_count += 1
    return deleted_count