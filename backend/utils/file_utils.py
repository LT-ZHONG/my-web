"""
文件处理工具函数
"""
import os
import uuid
import aiofiles
from pathlib import Path
from typing import Optional, Tuple, List
from fastapi import UploadFile
from PIL import Image
import mimetypes

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


async def create_thumbnail(image_path: str, thumbnail_path: str, size: Tuple[int, int] = (300, 300)) -> bool:
    """创建缩略图"""
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
        print(f"创建缩略图失败: {e}")
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
    
    # 创建缩略图（仅对图片）
    thumbnail_path = None
    if file_type == "image" and create_thumb:
        thumbnail_filename = f"thumb_{filename}"
        thumbnail_path = os.path.join(upload_path, thumbnail_filename)
        await create_thumbnail(file_path, thumbnail_path)
    
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
    # 移除uploads目录前的路径部分
    relative_path = file_path.replace(settings.UPLOAD_DIR, "").lstrip("/\\")
    return f"/static/uploads/{relative_path.replace(os.sep, '/')}"


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