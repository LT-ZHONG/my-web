"""
支付相关模型
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Enum, ForeignKey, Float, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from database import Base


class PaymentMethod(str, enum.Enum):
    """支付方式枚举"""
    WECHAT = "wechat"
    ALIPAY = "alipay"
    BANK_CARD = "bank_card"


class OrderStatus(str, enum.Enum):
    """订单状态枚举"""
    PENDING = "pending"      # 待支付
    PAID = "paid"            # 已支付
    EXPIRED = "expired"      # 已过期
    CANCELLED = "cancelled"  # 已取消
    REFUNDED = "refunded"    # 已退款


class OrderType(str, enum.Enum):
    """订单类型枚举"""
    VIP = "vip"              # VIP会员
    MEDIA = "media"          # 媒体内容
    CATEGORY = "category"    # 分类内容


class VIPPlan(Base):
    """VIP套餐模型"""
    __tablename__ = "vip_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="套餐名称")
    description = Column(Text, comment="套餐描述")
    
    # 价格和时长
    price = Column(Float, nullable=False, comment="价格")
    duration_days = Column(Integer, nullable=False, comment="有效期天数")
    
    # 套餐特权
    features = Column(JSON, comment="套餐特权列表")
    
    # 状态
    is_active = Column(Boolean, default=True, comment="是否启用")
    sort_order = Column(Integer, default=0, comment="排序")
    
    # 时间戳
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关联关系
    orders = relationship("Order", back_populates="vip_plan")
    
    def __repr__(self):
        return f"<VIPPlan(id={self.id}, name='{self.name}', price={self.price})>"
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "duration_days": self.duration_days,
            "features": self.features or [],
            "is_active": self.is_active,
            "sort_order": self.sort_order,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class Order(Base):
    """订单模型"""
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    order_no = Column(String(32), unique=True, nullable=False, comment="订单号")
    
    # 用户信息
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    
    # 订单信息
    order_type = Column(Enum(OrderType), nullable=False, comment="订单类型")
    title = Column(String(200), nullable=False, comment="订单标题")
    description = Column(Text, comment="订单描述")
    
    # 价格信息
    amount = Column(Float, nullable=False, comment="订单金额")
    discount_amount = Column(Float, default=0.0, comment="优惠金额")
    final_amount = Column(Float, nullable=False, comment="最终金额")
    
    # 支付信息
    payment_method = Column(Enum(PaymentMethod), comment="支付方式")
    payment_no = Column(String(100), comment="第三方支付单号")
    
    # 订单状态
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING, comment="订单状态")
    
    # 关联内容
    vip_plan_id = Column(Integer, ForeignKey("vip_plans.id"), comment="VIP套餐ID")
    media_id = Column(Integer, ForeignKey("media.id"), comment="媒体ID")
    category_id = Column(Integer, ForeignKey("media_categories.id"), comment="分类ID")
    
    # 订单元数据
    # metadata = Column(JSON, comment="订单元数据")
    
    # 时间戳
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    paid_at = Column(DateTime, comment="支付时间")
    expired_at = Column(DateTime, comment="过期时间")
    
    # 关联关系
    user = relationship("User", back_populates="orders")
    vip_plan = relationship("VIPPlan", back_populates="orders")
    media = relationship("Media")
    category = relationship("MediaCategory")
    
    def __repr__(self):
        return f"<Order(id={self.id}, order_no='{self.order_no}', status='{self.status}')>"
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "order_no": self.order_no,
            "user_id": self.user_id,
            "order_type": self.order_type,
            "title": self.title,
            "description": self.description,
            "amount": self.amount,
            "discount_amount": self.discount_amount,
            "final_amount": self.final_amount,
            "payment_method": self.payment_method,
            "payment_no": self.payment_no,
            "status": self.status,
            "vip_plan_id": self.vip_plan_id,
            "media_id": self.media_id,
            "category_id": self.category_id,
            # "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "paid_at": self.paid_at.isoformat() if self.paid_at else None,
            "expired_at": self.expired_at.isoformat() if self.expired_at else None
        }


class PaymentLog(Base):
    """支付日志模型"""
    __tablename__ = "payment_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, comment="订单ID")
    
    # 支付信息
    payment_method = Column(Enum(PaymentMethod), nullable=False, comment="支付方式")
    payment_no = Column(String(100), comment="第三方支付单号")
    amount = Column(Float, nullable=False, comment="支付金额")
    
    # 支付结果
    is_success = Column(Boolean, default=False, comment="是否成功")
    error_code = Column(String(50), comment="错误码")
    error_message = Column(Text, comment="错误信息")
    
    # 第三方响应
    raw_response = Column(JSON, comment="第三方原始响应")
    
    # 时间戳
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    
    # 关联关系
    order = relationship("Order")
    
    def __repr__(self):
        return f"<PaymentLog(id={self.id}, order_id={self.order_id}, is_success={self.is_success})>"