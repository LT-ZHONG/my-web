"""
聊天相关的Pydantic模式
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ChatRoomBase(BaseModel):
    """聊天室基础模式"""
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    is_public: bool = True
    max_users: int = Field(100, ge=1, le=1000)


class ChatRoomCreate(ChatRoomBase):
    """聊天室创建模式"""
    pass


class ChatRoomUpdate(BaseModel):
    """聊天室更新模式"""
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    is_active: Optional[bool] = None
    is_public: Optional[bool] = None
    max_users: Optional[int] = Field(None, ge=1, le=1000)


class ChatRoomResponse(ChatRoomBase):
    """聊天室响应模式"""
    id: int
    is_active: bool
    created_by: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ChatMessageBase(BaseModel):
    """聊天消息基础模式"""
    content: str = Field(..., max_length=1000)
    message_type: str = Field("text", pattern="^(text|image|emoji|system)$")


class ChatMessageCreate(ChatMessageBase):
    """聊天消息创建模式"""
    room_id: int


class ChatMessageResponse(ChatMessageBase):
    """聊天消息响应模式"""
    id: int
    room_id: int
    sender_id: int
    is_deleted: bool
    is_system: bool
    created_at: datetime
    updated_at: datetime
    
    # 关联数据
    sender_username: Optional[str] = None
    sender_avatar: Optional[str] = None
    
    class Config:
        from_attributes = True


class ChatMessageListQuery(BaseModel):
    """聊天消息列表查询模式"""
    room_id: int
    page: int = Field(1, ge=1)
    page_size: int = Field(50, ge=1, le=100)
    before_id: Optional[int] = None  # 获取指定消息之前的消息
    after_id: Optional[int] = None   # 获取指定消息之后的消息


class ChatMessageListResponse(BaseModel):
    """聊天消息列表响应模式"""
    messages: List[ChatMessageResponse]
    total: int
    page: int
    page_size: int
    has_more: bool


class OnlineUserResponse(BaseModel):
    """在线用户响应模式"""
    user_id: int
    username: str
    nickname: Optional[str]
    avatar_url: Optional[str]
    connected_at: datetime
    last_seen_at: datetime
    
    class Config:
        from_attributes = True


class ChatRoomStatsResponse(BaseModel):
    """聊天室统计响应模式"""
    room_id: int
    total_messages: int
    online_users: int
    total_users: int
    
    class Config:
        from_attributes = True


# WebSocket相关模式
class WSMessage(BaseModel):
    """WebSocket消息模式"""
    type: str  # join, leave, message, typing, etc.
    data: Dict[str, Any]


class WSChatMessage(BaseModel):
    """WebSocket聊天消息模式"""
    content: str
    message_type: str = "text"
    room_id: int


class WSTypingIndicator(BaseModel):
    """WebSocket打字指示器模式"""
    room_id: int
    is_typing: bool


class WSJoinRoom(BaseModel):
    """WebSocket加入房间模式"""
    room_id: int


class WSLeaveRoom(BaseModel):
    """WebSocket离开房间模式"""
    room_id: int


class WSErrorResponse(BaseModel):
    """WebSocket错误响应模式"""
    error: str
    message: str
    code: Optional[str] = None