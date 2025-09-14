"""
自定义中间件
"""
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import time
import redis.asyncio as redis
from typing import Callable
import asyncio
from collections import defaultdict

from config import settings
from utils.exceptions import RateLimitError


class RateLimitMiddleware(BaseHTTPMiddleware):
    """请求限流中间件"""
    
    def __init__(self, app):
        super().__init__(app)
        self.redis_client = None
        self.memory_store = defaultdict(list)  # 内存存储作为备选
    
    async def get_redis_client(self):
        """获取Redis客户端"""
        if not self.redis_client:
            try:
                self.redis_client = redis.from_url(settings.REDIS_URL)
                await self.redis_client.ping()
            except:
                self.redis_client = None
        return self.redis_client
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 获取客户端IP
        client_ip = request.client.host
        if "x-forwarded-for" in request.headers:
            client_ip = request.headers["x-forwarded-for"].split(",")[0].strip()
        
        # 检查限流
        if await self.is_rate_limited(client_ip):
            return JSONResponse(
                status_code=429,
                content={
                    "success": False,
                    "message": "请求过于频繁，请稍后再试",
                    "error_code": "RATE_LIMIT_EXCEEDED"
                }
            )
        
        # 记录请求
        await self.record_request(client_ip)
        
        response = await call_next(request)
        return response
    
    async def is_rate_limited(self, client_ip: str) -> bool:
        """检查是否达到限流阈值"""
        redis_client = await self.get_redis_client()
        current_time = int(time.time())
        window_start = current_time - settings.RATE_LIMIT_WINDOW
        
        if redis_client:
            # 使用Redis存储
            key = f"rate_limit:{client_ip}"
            try:
                # 清理过期记录
                await redis_client.zremrangebyscore(key, 0, window_start)
                # 获取当前时间窗口内的请求数
                count = await redis_client.zcard(key)
                return count >= settings.RATE_LIMIT_REQUESTS
            except:
                # Redis故障时使用内存存储
                pass
        
        # 使用内存存储
        requests = self.memory_store[client_ip]
        # 清理过期请求
        self.memory_store[client_ip] = [req_time for req_time in requests if req_time > window_start]
        return len(self.memory_store[client_ip]) >= settings.RATE_LIMIT_REQUESTS
    
    async def record_request(self, client_ip: str):
        """记录请求时间"""
        redis_client = await self.get_redis_client()
        current_time = int(time.time())
        
        if redis_client:
            try:
                key = f"rate_limit:{client_ip}"
                await redis_client.zadd(key, {str(current_time): current_time})
                await redis_client.expire(key, settings.RATE_LIMIT_WINDOW)
                return
            except:
                pass
        
        # 使用内存存储
        self.memory_store[client_ip].append(current_time)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """安全响应头中间件"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # 添加安全响应头
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        if not settings.DEBUG:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """请求日志中间件"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # 记录请求信息
        client_ip = request.client.host
        if "x-forwarded-for" in request.headers:
            client_ip = request.headers["x-forwarded-for"].split(",")[0].strip()
        
        response = await call_next(request)
        
        # 计算处理时间
        process_time = time.time() - start_time
        
        # 记录日志
        log_data = {
            "method": request.method,
            "url": str(request.url),
            "client_ip": client_ip,
            "status_code": response.status_code,
            "process_time": round(process_time, 4),
            "user_agent": request.headers.get("user-agent", ""),
            "timestamp": int(time.time())
        }
        
        # 这里可以发送到日志系统或数据库
        print(f"Request: {log_data}")
        
        # 添加处理时间到响应头
        response.headers["X-Process-Time"] = str(process_time)
        
        return response