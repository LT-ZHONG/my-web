"""
支付相关API端点（占位符）
"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/plans")
async def get_vip_plans():
    """获取VIP套餐列表"""
    return {"message": "支付API开发中..."}

@router.post("/orders")
async def create_order():
    """创建订单"""
    return {"message": "订单创建API开发中..."}