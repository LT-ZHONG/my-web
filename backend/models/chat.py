"""
聊天相关模型
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from database import Base


class ChatRoom(Base):
    """聊天室模型"""
    __tablename__ = "chat_rooms"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="聊天室名称")
    description = Column(Text, comment="聊天室描述")
    
    # 房间设置
    is_active = Column(Boolean, default=True, comment="是否激活")
    is_public = Column(Boolean, default=True, comment="是否公开")
    max_users = Column(Integer, default=100, comment="最大用户数")
    
    # 创建者
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False, comment="创建者ID")
    
    # 时间戳
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关联关系
    creator = relationship("User")
    messages = relationship("ChatMessage", back_populates="room", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ChatRoom(id={self.id}, name='{self.name}')>"


class ChatMessage(Base):
    """聊天消息模型"""
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 消息内容
    content = Column(Text, nullable=False, comment="消息内容")
    message_type = Column(String(20), default="text", comment="消息类型: text, image, emoji, system")
    
    # 关联信息
    room_id = Column(Integer, ForeignKey("chat_rooms.id"), nullable=False, comment="聊天室ID")
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="发送者ID")
    
    # 消息状态
    is_deleted = Column(Boolean, default=False, comment="是否已删除")
    is_system = Column(Boolean, default=False, comment="是否为系统消息")
    
    # 时间戳
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关联关系
    room = relationship("ChatRoom", back_populates="messages")
    sender = relationship("User", back_populates="chat_messages")
    
    def __repr__(self):
        return f"<ChatMessage(id={self.id}, room_id={self.room_id}, sender_id={self.sender_id})>"
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "content": self.content,
            "message_type": self.message_type,
            "room_id": self.room_id,
            "sender_id": self.sender_id,
            "is_deleted": self.is_deleted,
            "is_system": self.is_system,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class OnlineUser(Base):
    """在线用户记录"""
    __tablename__ = "online_users"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    room_id = Column(Integer, ForeignKey("chat_rooms.id"), nullable=False, comment="聊天室ID")
    
    # 连接信息
    session_id = Column(String(100), nullable=False, comment="会话ID")
    ip_address = Column(String(45), comment="IP地址")
    user_agent = Column(String(500), comment="用户代理")
    
    # 时间戳
    connected_at = Column(DateTime, server_default=func.now(), comment="连接时间")
    last_seen_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="最后活跃时间")
    
    # 关联关系
    user = relationship("User")
    room = relationship("ChatRoom")
    
    def __repr__(self):
        return f"<OnlineUser(user_id={self.user_id}, room_id={self.room_id})>"