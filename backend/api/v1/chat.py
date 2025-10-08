"""
聊天相关API端点
"""
import json
from typing import List, Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, Query
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from utils.auth import get_current_user, verify_token
from utils.exceptions import AuthenticationError
from models.user import User
from models.chat import ChatRoom
from schemas.chat import (
    ChatRoomResponse, ChatMessageResponse, ChatMessageListResponse,
    ChatRoomCreate, OnlineUserResponse, WSMessage
)
from services.chat_service import chat_service

router = APIRouter()
security = HTTPBearer()


@router.get("/private-room")
async def get_or_create_private_room(
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取或创建用户的私聊房间"""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"[私聊房间] 用户 {current_user.id} ({current_user.username}) 请求私聊房间")
        
        if current_user.is_admin:
            logger.warning(f"[私聊房间] 管理员 {current_user.id} 尝试访问普通用户私聊接口")
            raise HTTPException(status_code=400, detail="管理员请使用管理员聊天接口")
            
        # 获取任一管理员
        from sqlalchemy import select
        admin_result = await session.execute(
            select(User).where(User.is_admin == True).limit(1)
        )
        admin = admin_result.scalar_one_or_none()
        
        if not admin:
            logger.error("[私聊房间] 系统中没有管理员账户")
            raise HTTPException(status_code=404, detail="没有找到管理员")
        
        logger.info(f"[私聊房间] 找到管理员: {admin.id} ({admin.username})")
            
        # 获取或创建私聊房间
        room = await chat_service.get_or_create_private_room(session, current_user.id, admin.id)
        logger.info(f"[私聊房间] 获取/创建房间成功: room_id={room.id}, room_name={room.name}")
        
        response_data = {
            "room_id": room.id,
            "room_name": room.name,
            "admin_info": {
                "id": admin.id,
                "username": admin.username,
                "nickname": admin.nickname or admin.full_name,
                "avatar_url": admin.avatar_url
            }
        }
        logger.info(f"[私聊房间] 返回响应数据: {response_data}")
        
        return response_data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[私聊房间] 获取私聊房间失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取私聊房间失败: {str(e)}")


@router.get("/admin/chat-list")
async def get_admin_chat_list(
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取管理员的聊天列表"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="只有管理员可以访问此接口")
        
    try:
        chat_list = await chat_service.get_admin_chat_list(session, current_user.id)
        return chat_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取聊天列表失败: {str(e)}")


@router.post("/admin/start-chat/{user_id}")
async def start_chat_with_user(
    user_id: int,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """管理员主动开始与用户的聊天"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="只有管理员可以访问此接口")
        
    try:
        # 检查用户是否存在
        from sqlalchemy import select
        user_result = await session.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
            
        # 获取或创建私聊房间
        room = await chat_service.get_or_create_private_room(session, user_id, current_user.id)
        
        return {
            "room_id": room.id,
            "user_info": {
                "id": user.id,
                "username": user.username,
                "nickname": user.nickname or user.full_name,
                "avatar_url": user.avatar_url
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"开始聊天失败: {str(e)}")


@router.get("/rooms/{room_id}/messages", response_model=List[ChatMessageResponse])
async def get_room_messages(
    room_id: int,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(50, ge=1, le=100, description="每页数量"),
    before_id: Optional[int] = Query(None, description="获取此消息ID之前的消息"),
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取房间消息历史"""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"[历史消息] 用户 {current_user.id} 请求房间 {room_id} 的消息, page={page}, page_size={page_size}, before_id={before_id}")
        messages = await chat_service.get_room_messages(
            session, room_id, page, page_size, before_id
        )
        logger.info(f"[历史消息] 返回 {len(messages)} 条消息")
        return messages
    except Exception as e:
        logger.error(f"[历史消息] 获取消息失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取消息失败: {str(e)}")


@router.get("/rooms/{room_id}/online-users", response_model=List[dict])
async def get_room_online_users(
    room_id: int,
    current_user: User = Depends(get_current_user)
):
    """获取房间在线用户"""
    try:
        online_users = await chat_service.connection_manager.get_room_online_users(room_id)
        return online_users
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取在线用户失败: {str(e)}")


@router.post("/rooms", response_model=ChatRoomResponse)
async def create_chat_room(
    room_data: ChatRoomCreate,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建聊天室（管理员功能）"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="权限不足")
        
    try:
        room = ChatRoom(
            name=room_data.name,
            description=room_data.description,
            is_public=room_data.is_public,
            max_users=room_data.max_users,
            created_by=current_user.id
        )
        session.add(room)
        await session.commit()
        await session.refresh(room)
        
        return ChatRoomResponse.model_validate(room)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建聊天室失败: {str(e)}")


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: Optional[str] = Query(None, description="JWT Token"),
    room_id: int = Query(1, description="房间ID")
):
    """WebSocket聊天端点"""
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"[WebSocket] 收到连接请求, room_id={room_id}, token={'已提供' if token else '未提供'}")
    
    # 验证token
    if not token:
        logger.warning("[WebSocket] 拒绝连接: 缺少token")
        await websocket.close(code=4001, reason="需要认证token")
        return
        
    try:
        logger.info("[WebSocket] 开始验证token...")
        payload = verify_token(token, "access")
        user_id = payload.get("sub")
        if not user_id:
            logger.warning("[WebSocket] token无效: 缺少用户ID")
            await websocket.close(code=4001, reason="无效的token")
            return
            
        user_id = int(user_id)
        logger.info(f"[WebSocket] Token验证成功, user_id={user_id}")
    except (AuthenticationError, ValueError, Exception) as e:
        logger.error(f"[WebSocket] Token验证失败: {str(e)}", exc_info=True)
        await websocket.close(code=4001, reason="token验证失败")
        return
    
    # 获取用户信息
    try:
        async for session in get_db():
            # 获取用户信息
            from sqlalchemy import select
            logger.info(f"[WebSocket] 查询用户信息, user_id={user_id}")
            result = await session.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            
            if not user:
                logger.error(f"[WebSocket] 用户不存在, user_id={user_id}")
                await websocket.close(code=4004, reason="用户不存在")
                return
            
            logger.info(f"[WebSocket] 用户信息: {user.username} (ID: {user.id})")
                
            # 检查房间是否存在
            logger.info(f"[WebSocket] 检查房间是否存在, room_id={room_id}")
            room_result = await session.execute(select(ChatRoom).where(ChatRoom.id == room_id))
            room = room_result.scalar_one_or_none()
            
            if not room:
                logger.error(f"[WebSocket] 聊天室不存在, room_id={room_id}")
                await websocket.close(code=4004, reason="聊天室不存在")
                return
            
            logger.info(f"[WebSocket] 房间信息: {room.name} (ID: {room.id})")
                
            # 接受连接
            user_data = {
                "username": user.username,
                "nickname": user.nickname,
                "avatar_url": user.avatar_url
            }
            
            logger.info(f"[WebSocket] 准备接受连接, user_data={user_data}")
            # 首次连接时接受 WebSocket，传入 accept_connection=True
            await chat_service.connection_manager.connect(websocket, user_id, room_id, user_data, accept_connection=True)
            logger.info(f"[WebSocket] ✅ 连接已建立: user_id={user_id}, room_id={room_id}")
            
            try:
                while True:
                    # 接收消息
                    data = await websocket.receive_text()
                    logger.info(f"[WebSocket] 收到消息: {data}")
                    message_data = json.loads(data)
                    
                    # 验证消息格式
                    try:
                        ws_message = WSMessage(**message_data)
                        logger.info(f"[WebSocket] 处理消息类型: {ws_message.type}")
                        await chat_service.handle_websocket_message(
                            websocket, user_id, ws_message, session
                        )
                    except Exception as e:
                        logger.error(f"[WebSocket] 消息处理失败: {str(e)}", exc_info=True)
                        await websocket.send_text(json.dumps({
                            "type": "error",
                            "data": {
                                "message": f"消息格式错误: {str(e)}",
                                "code": "INVALID_MESSAGE_FORMAT"
                            }
                        }, ensure_ascii=False))
                        
            except WebSocketDisconnect:
                logger.info(f"[WebSocket] 客户端断开连接: user_id={user_id}, room_id={room_id}")
                await chat_service.connection_manager.disconnect(user_id, room_id)
            except Exception as e:
                logger.error(f"[WebSocket] WebSocket错误: {str(e)}", exc_info=True)
                await chat_service.connection_manager.disconnect(user_id, room_id)
                
    except Exception as e:
        logger.error(f"[WebSocket] WebSocket连接错误: {str(e)}", exc_info=True)
        await websocket.close(code=4000, reason="服务器内部错误")