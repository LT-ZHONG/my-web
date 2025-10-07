"""
用户模型
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from database import Base


class UserRole(str, enum.Enum):
    """用户角色枚举"""
    USER = "user"
    VIP = "vip"
    ADMIN = "admin"


class UserStatus(str, enum.Enum):
    """用户状态枚举"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    BANNED = "banned"


class User(Base):
    """用户模型"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False, comment="邮箱")
    username = Column(String(50), unique=True, index=True, nullable=False, comment="用户名")
    hashed_password = Column(String(255), nullable=False, comment="密码哈希")
    
    # 基本信息
    full_name = Column(String(100), comment="全名")
    nickname = Column(String(50), comment="昵称")
    avatar_url = Column(String(500), comment="头像URL")
    bio = Column(Text, comment="个人简介")

    # 角色和状态
    role = Column(Enum(UserRole), default=UserRole.USER, comment="用户角色")
    status = Column(Enum(UserStatus), default=UserStatus.ACTIVE, comment="用户状态")
    is_active = Column(Boolean, default=True, comment="是否激活")
    is_verified = Column(Boolean, default=False, comment="是否已验证邮箱")
    
    # VIP相关
    is_vip = Column(Boolean, default=False, comment="是否为VIP")
    vip_expire_at = Column(DateTime, comment="VIP过期时间")
    
    # 管理员标识
    is_admin = Column(Boolean, default=False, comment="是否为管理员")
    
    # 时间戳
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    last_login_at = Column(DateTime, comment="最后登录时间")
    
    # 统计信息
    login_count = Column(Integer, default=0, comment="登录次数")
    media_count = Column(Integer, default=0, comment="媒体文件数量")

    # 积分
    credits = Column(Integer, default=0, comment="用户积分余额")

    # 关联关系
    media_files = relationship("Media", back_populates="owner", cascade="all, delete-orphan")
    chat_messages = relationship("ChatMessage", back_populates="sender")
    orders = relationship("Order", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"
    
    @property
    def is_vip_active(self) -> bool:
        """检查VIP是否有效"""
        if not self.is_vip:
            return False
        if self.vip_expire_at is None:
            return True
        from datetime import datetime
        return self.vip_expire_at > datetime.utcnow()
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "full_name": self.full_name,
            "nickname": self.nickname,
            "avatar_url": self.avatar_url,
            "bio": self.bio,
            "role": self.role,
            "status": self.status,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "is_vip": self.is_vip,
            "vip_expire_at": self.vip_expire_at.isoformat() if self.vip_expire_at else None,
            "is_admin": self.is_admin,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login_at": self.last_login_at.isoformat() if self.last_login_at else None,
            "media_count": self.media_count,
            "credits": self.credits
        }