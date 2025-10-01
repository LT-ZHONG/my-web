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