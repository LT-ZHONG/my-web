"""
API v1 主路由
"""
from fastapi import APIRouter
from api.v1 import auth, users, media, chat, payment, admin

api_router = APIRouter()

# 认证相关路由
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])

# 用户相关路由
api_router.include_router(users.router, prefix="/users", tags=["用户"])

# 媒体相关路由
api_router.include_router(media.router, prefix="/media", tags=["媒体"])

# 聊天相关路由
api_router.include_router(chat.router, prefix="/chat", tags=["聊天"])

# 支付相关路由
api_router.include_router(payment.router, prefix="/payment", tags=["支付"])

# 管理员相关路由
api_router.include_router(admin.router, prefix="/admin", tags=["管理员"])