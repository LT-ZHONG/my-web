"""
支付相关的Pydantic模式
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from models.payment import PaymentMethod, OrderStatus, OrderType


class VIPPlanBase(BaseModel):
    """VIP套餐基础模式"""
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    duration_days: int = Field(..., gt=0)
    features: Optional[List[str]] = None
    sort_order: int = 0


class VIPPlanCreate(VIPPlanBase):
    """VIP套餐创建模式"""
    pass


class VIPPlanUpdate(BaseModel):
    """VIP套餐更新模式"""
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    duration_days: Optional[int] = Field(None, gt=0)
    features: Optional[List[str]] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


class VIPPlanResponse(VIPPlanBase):
    """VIP套餐响应模式"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class OrderBase(BaseModel):
    """订单基础模式"""
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    amount: float = Field(..., gt=0)


class OrderCreate(BaseModel):
    """订单创建模式"""
    order_type: OrderType
    vip_plan_id: Optional[int] = None
    media_id: Optional[int] = None
    category_id: Optional[int] = None
    payment_method: PaymentMethod
    
    @validator('vip_plan_id')
    def validate_vip_plan(cls, v, values):
        if values.get('order_type') == OrderType.VIP and not v:
            raise ValueError('VIP订单必须指定套餐ID')
        return v
    
    @validator('media_id')
    def validate_media(cls, v, values):
        if values.get('order_type') == OrderType.MEDIA and not v:
            raise ValueError('媒体订单必须指定媒体ID')
        return v
    
    @validator('category_id')
    def validate_category(cls, v, values):
        if values.get('order_type') == OrderType.CATEGORY and not v:
            raise ValueError('分类订单必须指定分类ID')
        return v


class OrderResponse(OrderBase):
    """订单响应模式"""
    id: int
    order_no: str
    user_id: int
    order_type: OrderType
    discount_amount: float
    final_amount: float
    payment_method: Optional[PaymentMethod]
    payment_no: Optional[str]
    status: OrderStatus
    vip_plan_id: Optional[int]
    media_id: Optional[int]
    category_id: Optional[int]
    metadata: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    paid_at: Optional[datetime]
    expired_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class OrderListQuery(BaseModel):
    """订单列表查询模式"""
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
    order_type: Optional[OrderType] = None
    status: Optional[OrderStatus] = None
    payment_method: Optional[PaymentMethod] = None
    user_id: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class OrderListResponse(BaseModel):
    """订单列表响应模式"""
    orders: List[OrderResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class PaymentRequest(BaseModel):
    """支付请求模式"""
    order_id: int
    payment_method: PaymentMethod
    return_url: Optional[str] = None
    notify_url: Optional[str] = None


class PaymentResponse(BaseModel):
    """支付响应模式"""
    order_id: int
    payment_url: Optional[str] = None
    payment_params: Optional[Dict[str, Any]] = None
    qr_code: Optional[str] = None
    message: str


class PaymentNotification(BaseModel):
    """支付通知模式"""
    order_no: str
    payment_no: str
    amount: float
    status: str
    timestamp: datetime
    signature: str
    raw_data: Dict[str, Any]


class PaymentStatsResponse(BaseModel):
    """支付统计响应模式"""
    total_orders: int
    total_amount: float
    paid_orders: int
    paid_amount: float
    pending_orders: int
    pending_amount: float
    refunded_orders: int
    refunded_amount: float
    
    # 按类型统计
    vip_orders: int
    vip_amount: float
    media_orders: int
    media_amount: float
    
    # 按支付方式统计
    wechat_orders: int
    wechat_amount: float
    alipay_orders: int
    alipay_amount: float


class RefundRequest(BaseModel):
    """退款请求模式"""
    order_id: int
    reason: str = Field(..., max_length=500)
    amount: Optional[float] = None  # 部分退款金额，不指定则全额退款


class RefundResponse(BaseModel):
    """退款响应模式"""
    order_id: int
    refund_no: str
    amount: float
    status: str
    message: str


class CreditRechargeRequest(BaseModel):
    """积分充值请求模式"""
    amount: float = Field(..., gt=0, description="充值金额(美元)")
    payment_method: PaymentMethod = Field(..., description="支付方式(paypal或usdt)")
    
    @validator('payment_method')
    def validate_payment_method(cls, v):
        if v not in [PaymentMethod.PAYPAL, PaymentMethod.USDT]:
            raise ValueError('积分充值仅支持PayPal或USDT支付')
        return v


class CreditRechargeResponse(BaseModel):
    """积分充值响应模式"""
    order_id: int
    order_no: str
    amount: float
    credits: int  # 对应的积分数量 (amount * 10)
    payment_method: PaymentMethod
    payment_info: Dict[str, Any]  # 支付信息(PayPal链接或USDT地址)
    message: str


class CreditTransactionResponse(BaseModel):
    """积分交易记录响应模式"""
    id: int
    user_id: int
    amount: int
    balance_before: int
    balance_after: int
    transaction_type: str
    description: Optional[str]
    order_id: Optional[int]
    media_id: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True


class CreditTransactionListResponse(BaseModel):
    """积分交易记录列表响应"""
    transactions: List[CreditTransactionResponse]
    total: int
    page: int
    page_size: int
    total_pages: int