"""
管理员相关API端点（占位符）
"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/dashboard")
async def get_admin_dashboard():
    """获取管理员面板数据"""
    return {"message": "管理员API开发中..."}

@router.get("/users")
async def admin_manage_users():
    """管理用户"""
    return {"message": "用户管理API开发中..."}