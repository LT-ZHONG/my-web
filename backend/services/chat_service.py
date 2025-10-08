"""
聊天服务层
"""

import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, and_
from sqlalchemy.orm import selectinload

from models.chat import ChatRoom, ChatMessage
from models.user import User
from schemas.chat import ChatMessageResponse, ChatRoomResponse, WSMessage, WSChatMessage


class ConnectionManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        # 存储活跃连接：{user_id: {room_id: websocket}}
        self.active_connections: Dict[int, Dict[int, any]] = {}
        # 存储房间连接：{room_id: {user_id: websocket}}
        self.room_connections: Dict[int, Dict[int, any]] = {}
        # 存储用户信息：{user_id: user_data}
        self.user_info: Dict[int, dict] = {}
        # 正在输入的用户：{room_id: {user_id: timestamp}}
        self.typing_users: Dict[int, Dict[int, datetime]] = {}
        
    async def connect(self, websocket: any, user_id: int, room_id: int, user_data: dict, accept_connection: bool = True):
        """用户连接到房间
        
        Args:
            websocket: WebSocket连接对象
            user_id: 用户ID
            room_id: 房间ID
            user_data: 用户数据
            accept_connection: 是否接受WebSocket连接（首次连接时为True，加入房间时为False）
        """
        import logging
        logger = logging.getLogger(__name__)
        
        # 只在首次连接时接受WebSocket
        if accept_connection:
            logger.info(f"[ConnectionManager] 接受 WebSocket 连接: user_id={user_id}, room_id={room_id}")
            await websocket.accept()
        else:
            logger.info(f"[ConnectionManager] 用户加入房间（不接受连接）: user_id={user_id}, room_id={room_id}")
        
        # 存储连接
        if user_id not in self.active_connections:
            self.active_connections[user_id] = {}
        self.active_connections[user_id][room_id] = websocket
        
        if room_id not in self.room_connections:
            self.room_connections[room_id] = {}
        self.room_connections[room_id][user_id] = websocket
        
        # 存储用户信息
        self.user_info[user_id] = user_data
        
        logger.info(f"[ConnectionManager] 用户 {user_id} 已连接到房间 {room_id}")
        
        # 通知房间其他用户
        await self.broadcast_to_room(room_id, {
            "type": "user_online",
            "data": {
                "user_id": user_id,
                "username": user_data.get("username"),
                "nickname": user_data.get("nickname"),
                "avatar_url": user_data.get("avatar_url"),
                "connected_at": datetime.now().isoformat()
            }
        }, exclude_user=user_id)
        
    async def disconnect(self, user_id: int, room_id: int):
        """用户断开连接"""
        # 移除连接
        if user_id in self.active_connections:
            if room_id in self.active_connections[user_id]:
                del self.active_connections[user_id][room_id]
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
                
        if room_id in self.room_connections:
            if user_id in self.room_connections[room_id]:
                del self.room_connections[room_id][user_id]
            if not self.room_connections[room_id]:
                del self.room_connections[room_id]
                
        # 移除正在输入状态
        if room_id in self.typing_users:
            if user_id in self.typing_users[room_id]:
                del self.typing_users[room_id][user_id]
                
        print(f"用户 {user_id} 断开房间 {room_id} 连接")
        
        # 通知房间其他用户
        await self.broadcast_to_room(room_id, {
            "type": "user_offline",
            "data": {"user_id": user_id}
        })
        
    async def send_personal_message(self, user_id: int, room_id: int, message: dict):
        """发送个人消息"""
        if user_id in self.active_connections and room_id in self.active_connections[user_id]:
            websocket = self.active_connections[user_id][room_id]
            try:
                await websocket.send_text(json.dumps(message, ensure_ascii=False))
            except Exception as e:
                print(f"发送消息失败: {e}")
                await self.disconnect(user_id, room_id)
                
    async def broadcast_to_room(self, room_id: int, message: dict, exclude_user: Optional[int] = None):
        """向房间广播消息"""
        if room_id not in self.room_connections:
            return
            
        disconnect_users = []
        for user_id, websocket in self.room_connections[room_id].items():
            if exclude_user and user_id == exclude_user:
                continue
                
            try:
                await websocket.send_text(json.dumps(message, ensure_ascii=False))
            except Exception as e:
                print(f"广播消息失败 (用户 {user_id}): {e}")
                disconnect_users.append(user_id)
                
        # 清理断开的连接
        for user_id in disconnect_users:
            await self.disconnect(user_id, room_id)
            
    async def get_room_online_users(self, room_id: int) -> List[dict]:
        """获取房间在线用户"""
        online_users = []
        if room_id in self.room_connections:
            for user_id in self.room_connections[room_id]:
                if user_id in self.user_info:
                    user_data = self.user_info[user_id]
                    online_users.append({
                        "user_id": user_id,
                        "username": user_data.get("username"),
                        "nickname": user_data.get("nickname"),
                        "avatar_url": user_data.get("avatar_url")
                    })
        return online_users
        
    async def set_typing_status(self, user_id: int, room_id: int, is_typing: bool):
        """设置用户输入状态"""
        if room_id not in self.typing_users:
            self.typing_users[room_id] = {}
            
        if is_typing:
            self.typing_users[room_id][user_id] = datetime.now()
            message_type = "user_typing"
        else:
            if user_id in self.typing_users[room_id]:
                del self.typing_users[room_id][user_id]
            message_type = "user_stop_typing"
            
        # 通知房间其他用户
        await self.broadcast_to_room(room_id, {
            "type": message_type,
            "data": {"user_id": user_id}
        }, exclude_user=user_id)
        
    async def cleanup_expired_typing(self):
        """清理过期的输入状态"""
        current_time = datetime.now()
        expired_threshold = timedelta(seconds=10)  # 10秒后自动清除输入状态
        
        for room_id in list(self.typing_users.keys()):
            for user_id in list(self.typing_users[room_id].keys()):
                if current_time - self.typing_users[room_id][user_id] > expired_threshold:
                    await self.set_typing_status(user_id, room_id, False)


class ChatService:
    """聊天服务"""
    
    def __init__(self):
        self.connection_manager = ConnectionManager()
        
    async def get_or_create_private_room(self, session: AsyncSession, user_id: int, admin_id: int) -> ChatRoom:
        """获取或创建用户与管理员的私聊房间"""
        # 查找已存在的私聊房间
        result = await session.execute(
            select(ChatRoom).where(
                ChatRoom.name == f"private_{min(user_id, admin_id)}_{max(user_id, admin_id)}"
            )
        )
        room = result.scalar_one_or_none()
        
        if not room:
            # 创建新的私聊房间
            room = ChatRoom(
                name=f"private_{min(user_id, admin_id)}_{max(user_id, admin_id)}",
                description=f"用户 {user_id} 与管理员 {admin_id} 的私聊",
                is_public=False,  # 私聊房间不公开
                is_active=True,
                max_users=2,  # 只允许两个用户
                created_by=admin_id
            )
            session.add(room)
            await session.commit()
            await session.refresh(room)
            
        return room
        
    async def get_user_private_room(self, session: AsyncSession, user_id: int) -> Optional[ChatRoom]:
        """获取用户的私聊房间（与任何管理员）"""
        # 获取所有管理员
        admin_result = await session.execute(
            select(User).where(User.is_admin == True)
        )
        admins = admin_result.scalars().all()
        
        for admin in admins:
            room_name = f"private_{min(user_id, admin.id)}_{max(user_id, admin.id)}"
            result = await session.execute(
                select(ChatRoom).where(ChatRoom.name == room_name)
            )
            room = result.scalar_one_or_none()
            if room:
                return room
                
        return None
        
    async def get_admin_chat_list(self, session: AsyncSession, admin_id: int) -> List[dict]:
        """获取管理员的聊天列表（所有用户的私聊）"""
        # 获取所有私聊房间
        result = await session.execute(
            select(ChatRoom).where(
                and_(
                    ChatRoom.name.like("private_%"),
                    ChatRoom.created_by == admin_id
                )
            ).order_by(ChatRoom.updated_at.desc())
        )
        rooms = result.scalars().all()
        
        chat_list = []
        for room in rooms:
            # 解析房间名称获取用户ID
            parts = room.name.split("_")
            if len(parts) == 3:
                user_id1, user_id2 = int(parts[1]), int(parts[2])
                other_user_id = user_id1 if user_id1 != admin_id else user_id2
                
                # 获取用户信息
                user_result = await session.execute(
                    select(User).where(User.id == other_user_id)
                )
                user = user_result.scalar_one_or_none()
                
                if user:
                    # 获取最后一条消息
                    last_msg_result = await session.execute(
                        select(ChatMessage)
                        .where(ChatMessage.room_id == room.id)
                        .order_by(ChatMessage.created_at.desc())
                        .limit(1)
                    )
                    last_message = last_msg_result.scalar_one_or_none()
                    
                    chat_list.append({
                        "room_id": room.id,
                        "user_id": user.id,
                        "username": user.username,
                        "nickname": user.nickname or user.full_name,
                        "avatar_url": user.avatar_url,
                        "last_message": last_message.content if last_message else "暂无消息",
                        "last_message_time": last_message.created_at if last_message else room.created_at,
                        "unread_count": 0  # TODO: 实现未读消息计数
                    })
                    
        return chat_list
        
    async def get_chat_rooms(self, session: AsyncSession) -> List[ChatRoomResponse]:
        """获取聊天室列表"""
        result = await session.execute(
            select(ChatRoom)
            .where(ChatRoom.is_active == True)
            .order_by(ChatRoom.created_at.desc())
        )
        rooms = result.scalars().all()
        
        return [ChatRoomResponse.model_validate(room) for room in rooms]
        
    async def get_room_messages(
        self, 
        session: AsyncSession, 
        room_id: int, 
        page: int = 1, 
        page_size: int = 50,
        before_id: Optional[int] = None
    ) -> List[ChatMessageResponse]:
        """获取房间消息历史"""
        query = (
            select(ChatMessage)
            .options(selectinload(ChatMessage.sender))
            .where(
                and_(
                    ChatMessage.room_id == room_id,
                    ChatMessage.is_deleted == False
                )
            )
        )
        
        if before_id:
            query = query.where(ChatMessage.id < before_id)
            
        query = query.order_by(desc(ChatMessage.created_at)).limit(page_size)
        
        result = await session.execute(query)
        messages = result.scalars().all()
        
        # 转换为响应模式并添加发送者信息
        message_responses = []
        for msg in messages:
            msg_data = ChatMessageResponse.model_validate(msg)
            if msg.sender:
                msg_data.sender_username = msg.sender.username
                msg_data.sender_avatar = msg.sender.avatar_url
            message_responses.append(msg_data)
            
        # 按时间正序排列（旧消息在前）
        message_responses.reverse()
        return message_responses
        
    async def save_message(
        self, 
        session: AsyncSession, 
        message_data: WSChatMessage, 
        sender_id: int
    ) -> ChatMessage:
        """保存消息到数据库"""
        message = ChatMessage(
            content=message_data.content,
            message_type=message_data.message_type,
            room_id=message_data.room_id,
            sender_id=sender_id
        )
        
        session.add(message)
        await session.commit()
        await session.refresh(message)
        
        # 加载发送者信息
        await session.refresh(message, ['sender'])
        
        return message
        
    async def handle_websocket_message(
        self, 
        websocket: any, 
        user_id: int, 
        message: WSMessage,
        session: AsyncSession
    ):
        """处理WebSocket消息"""
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            if message.type == "join_room":
                room_id = message.data.get("room_id")
                if room_id:
                    logger.info(f"[ChatService] 处理加入房间消息: user_id={user_id}, room_id={room_id}")
                    user_data = message.data.get("user", {})
                    # 注意：这里不需要接受连接，因为在 websocket_endpoint 中已经接受了
                    # 这里只是更新房间连接状态
                    await self.connection_manager.connect(websocket, user_id, room_id, user_data, accept_connection=False)
                    
                    # 发送在线用户列表
                    online_users = await self.connection_manager.get_room_online_users(room_id)
                    logger.info(f"[ChatService] 房间 {room_id} 当前在线用户: {len(online_users)} 人")
                    await self.connection_manager.send_personal_message(user_id, room_id, {
                        "type": "online_users",
                        "data": {"users": online_users}
                    })
                    
            elif message.type == "leave_room":
                room_id = message.data.get("room_id")
                if room_id:
                    await self.connection_manager.disconnect(user_id, room_id)
                    
            elif message.type == "send_message":
                # 保存消息到数据库
                message_data = WSChatMessage(**message.data)
                saved_message = await self.save_message(session, message_data, user_id)
                
                # 构建响应消息
                response_message = {
                    "type": "new_message",
                    "data": {
                        "id": saved_message.id,
                        "content": saved_message.content,
                        "message_type": saved_message.message_type,
                        "room_id": saved_message.room_id,
                        "sender_id": saved_message.sender_id,
                        "sender_username": saved_message.sender.username if saved_message.sender else None,
                        "sender_avatar": saved_message.sender.avatar_url if saved_message.sender else None,
                        "created_at": saved_message.created_at.isoformat(),
                        "is_system": saved_message.is_system
                    }
                }
                
                # 广播给房间所有用户
                await self.connection_manager.broadcast_to_room(
                    saved_message.room_id, 
                    response_message
                )
                
            elif message.type == "typing":
                room_id = message.data.get("room_id")
                is_typing = message.data.get("is_typing", True)
                if room_id is not None:
                    await self.connection_manager.set_typing_status(user_id, room_id, is_typing)
                    
        except Exception as e:
            # 发送错误消息给客户端
            await websocket.send_text(json.dumps({
                "type": "error",
                "data": {
                    "message": f"处理消息失败: {str(e)}",
                    "code": "PROCESSING_ERROR"
                }
            }, ensure_ascii=False))


# 全局聊天服务实例
chat_service = ChatService()
