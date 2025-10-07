"""
支付相关API端点
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import uuid

from database import get_db
from models.user import User
from models.payment import Order, OrderType, OrderStatus, PaymentMethod, CreditTransaction
from schemas.payment import (
    CreditRechargeRequest, CreditRechargeResponse,
    CreditTransactionResponse, CreditTransactionListResponse
)
from utils.auth import get_current_user
from config import Settings

router = APIRouter()
settings = Settings()


@router.post("/credits/recharge", response_model=CreditRechargeResponse)
async def recharge_credits(
    recharge_data: CreditRechargeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    积分充值
    1美元 = 10积分
    """
    # 计算积分数量 (1美元 = 10积分)
    credits = int(recharge_data.amount * 10)
    
    # 生成订单号
    order_no = f"CR{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:8].upper()}"
    
    # 创建充值订单
    order = Order(
        order_no=order_no,
        user_id=current_user.id,
        order_type=OrderType.CREDITS,
        title=f"积分充值 - {credits}积分",
        description=f"充值金额: ${recharge_data.amount} USD = {credits}积分",
        amount=recharge_data.amount,
        discount_amount=0.0,
        final_amount=recharge_data.amount,
        payment_method=recharge_data.payment_method,
        status=OrderStatus.PENDING
    )
    
    db.add(order)
    await db.commit()
    await db.refresh(order)
    
    # 准备支付信息
    payment_info = {}
    if recharge_data.payment_method == PaymentMethod.PAYPAL:
        # PayPal支付链接 (需要在配置中设置)
        paypal_link = getattr(settings, 'PAYPAL_LINK', 'https://PayPal.Me/LTZHONG')
        payment_info = {
            "payment_url": paypal_link,
            "amount": recharge_data.amount,
            "note": f"请在付款备注中填写您的邮箱: {current_user.email}"
        }
    elif recharge_data.payment_method == PaymentMethod.USDT:
        # USDT收款地址 (需要在配置中设置)
        usdt_address = getattr(settings, 'USDT_ADDRESS', '0xF0594E361ad632f29A607C6EfC49fe9ba31de9dD')
        usdt_qr_code = getattr(settings, 'USDT_QR_CODE', 'usdt-qr-code.JPG')
        payment_info = {
            "address": usdt_address,
            "qr_code": usdt_qr_code,
            "amount": recharge_data.amount,
            "note": f"请在付款备注中填写您的邮箱: {current_user.email}",
            "network": "TRC20/ERC20"
        }
    
    return CreditRechargeResponse(
        order_id=order.id,
        order_no=order.order_no,
        amount=recharge_data.amount,
        credits=credits,
        payment_method=recharge_data.payment_method,
        payment_info=payment_info,
        message="订单创建成功，请完成支付。支付成功后，管理员会为您充值积分。"
    )


@router.post("/credits/confirm/{order_id}")
async def confirm_credit_recharge(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    用户确认已完成支付（管理员审核后会充值积分）
    """
    from sqlalchemy import select
    
    # 查询订单
    result = await db.execute(
        select(Order).where(Order.id == order_id, Order.user_id == current_user.id)
    )
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    
    if order.status != OrderStatus.PENDING:
        raise HTTPException(status_code=400, detail="订单状态不正确")
    
    return {
        "message": "已收到您的支付确认，管理员将在审核后为您充值积分",
        "order_no": order.order_no
    }


@router.get("/credits/transactions", response_model=CreditTransactionListResponse)
async def get_credit_transactions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取用户的积分交易记录
    """
    from sqlalchemy import select, func, desc
    
    # 查询总数
    count_query = select(func.count(CreditTransaction.id)).where(
        CreditTransaction.user_id == current_user.id
    )
    result = await db.execute(count_query)
    total = result.scalar()
    
    # 查询记录
    query = select(CreditTransaction).where(
        CreditTransaction.user_id == current_user.id
    ).order_by(desc(CreditTransaction.created_at)).offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    transactions = result.scalars().all()
    
    total_pages = (total + page_size - 1) // page_size
    
    return CreditTransactionListResponse(
        transactions=[CreditTransactionResponse.from_orm(t) for t in transactions],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/credits/balance")
async def get_credit_balance(
    current_user: User = Depends(get_current_user)
):
    """
    获取用户当前积分余额
    """
    return {
        "user_id": current_user.id,
        "username": current_user.username,
        "credits": current_user.credits
    }


# 管理员API - 审核充值订单并充值积分
@router.post("/admin/credits/approve/{order_id}")
async def approve_credit_recharge(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    管理员审核并完成积分充值
    """
    from sqlalchemy import select
    
    # 检查管理员权限
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    # 查询订单
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    
    if order.status != OrderStatus.PENDING:
        raise HTTPException(status_code=400, detail="订单已处理或状态不正确")
    
    if order.order_type != OrderType.CREDITS:
        raise HTTPException(status_code=400, detail="不是积分充值订单")
    
    # 查询用户
    result = await db.execute(select(User).where(User.id == order.user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 计算积分
    credits = int(order.amount * 10)
    
    # 记录充值前的余额
    balance_before = user.credits
    
    # 增加用户积分
    user.credits += credits
    
    # 更新订单状态
    order.status = OrderStatus.PAID
    order.paid_at = datetime.utcnow()
    
    # 创建积分交易记录
    transaction = CreditTransaction(
        user_id=user.id,
        amount=credits,
        balance_before=balance_before,
        balance_after=user.credits,
        transaction_type="recharge",
        description=f"充值积分 - 订单号: {order.order_no}",
        order_id=order.id
    )
    
    db.add(transaction)
    await db.commit()
    
    return {
        "message": "积分充值成功",
        "order_no": order.order_no,
        "user_id": user.id,
        "username": user.username,
        "credits_added": credits,
        "new_balance": user.credits
    }