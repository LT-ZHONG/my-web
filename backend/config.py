"""
应用程序配置管理
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List
import os
from functools import lru_cache


class Settings(BaseSettings):
    """应用程序配置类"""
    
    # 基础配置
    APP_NAME: str = "个人生活展示网站"
    DEBUG: bool = Field(default=True, env="DEBUG")
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    
    # 安全配置
    SECRET_KEY: str = Field(default="your-secret-key-here", env="SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS")
    ALGORITHM: str = "HS256"
    
    # CORS配置
    ALLOWED_HOSTS: List[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"],
        env="ALLOWED_HOSTS"
    )
    
    # 数据库配置
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./data/myweb.db",
        env="DATABASE_URL"
    )
    
    # Redis配置（用于缓存和会话）
    REDIS_URL: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    REDIS_DB: int = Field(default=0, env="REDIS_DB")
    
    # 文件上传配置
    UPLOAD_DIR: str = Field(default="static/uploads", env="UPLOAD_DIR")
    MAX_FILE_SIZE: int = Field(default=50 * 1024 * 1024, env="MAX_FILE_SIZE")  # 50MB
    ALLOWED_IMAGE_TYPES: List[str] = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    ALLOWED_VIDEO_TYPES: List[str] = ["video/mp4", "video/avi", "video/mov", "video/wmv"]
    
    # 邮件配置
    SMTP_HOST: str = Field(default="smtp.gmail.com", env="SMTP_HOST")
    SMTP_PORT: int = Field(default=587, env="SMTP_PORT")
    SMTP_USER: str = Field(default="", env="SMTP_USER")
    SMTP_PASSWORD: str = Field(default="", env="SMTP_PASSWORD")
    
    # 支付配置
    # 微信支付
    WECHAT_PAY_APP_ID: str = Field(default="", env="WECHAT_PAY_APP_ID")
    WECHAT_PAY_MCH_ID: str = Field(default="", env="WECHAT_PAY_MCH_ID")
    WECHAT_PAY_API_KEY: str = Field(default="", env="WECHAT_PAY_API_KEY")
    
    # 支付宝
    ALIPAY_APP_ID: str = Field(default="", env="ALIPAY_APP_ID")
    ALIPAY_PRIVATE_KEY: str = Field(default="", env="ALIPAY_PRIVATE_KEY")
    ALIPAY_PUBLIC_KEY: str = Field(default="", env="ALIPAY_PUBLIC_KEY")
    
    # 限流配置
    RATE_LIMIT_REQUESTS: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    RATE_LIMIT_WINDOW: int = Field(default=60, env="RATE_LIMIT_WINDOW")  # 秒
    
    # WebSocket配置
    WS_MESSAGE_MAX_SIZE: int = Field(default=1024, env="WS_MESSAGE_MAX_SIZE")  # bytes
    WS_PING_INTERVAL: int = Field(default=20, env="WS_PING_INTERVAL")  # 秒
    WS_PING_TIMEOUT: int = Field(default=20, env="WS_PING_TIMEOUT")  # 秒
    
    # 日志配置
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FILE: str = Field(default="logs/app.log", env="LOG_FILE")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """获取应用程序配置实例（单例模式）"""
    return Settings()


# 全局配置实例
settings = get_settings()

# 创建必要的目录
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs("logs", exist_ok=True)
os.makedirs("data", exist_ok=True)
