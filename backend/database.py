"""
数据库连接和配置
"""
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
import redis.asyncio as redis
from typing import AsyncGenerator

from config import settings

# SQLite 数据库配置
# 创建数据库目录
import os

db_dir = os.path.dirname(settings.DATABASE_URL.replace("sqlite+aiosqlite:///", ""))
if db_dir and not os.path.exists(db_dir):
    os.makedirs(db_dir, exist_ok=True)

# 同步引擎（用于Alembic迁移）
sync_database_url = settings.DATABASE_URL.replace("sqlite+aiosqlite://", "sqlite://")
sync_engine = create_engine(
    sync_database_url,
    echo=settings.DEBUG
)

# 异步引擎（用于FastAPI应用）
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False
)

# 数据库会话
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# 数据库基类
Base = declarative_base()
metadata = MetaData()


# Redis连接
class RedisDB:
    redis_client = None


redis_db = RedisDB()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_redis():
    """获取Redis连接"""
    return redis_db.redis_client


async def create_all_tables():
    """创建所有数据库表"""
    async with engine.begin() as conn:
        # 导入所有模型以确保它们被注册
        from models.user import User
        from models.media import Media, MediaCategory
        from models.chat import ChatRoom, ChatMessage, OnlineUser
        from models.payment import Order, VIPPlan

        await conn.run_sync(Base.metadata.create_all)


async def connect_to_databases():
    """连接到所有数据库"""
    # 连接Redis
    redis_db.redis_client = redis.from_url(
        settings.REDIS_URL,
        db=settings.REDIS_DB,
        encoding="utf-8",
        decode_responses=True
    )

    print("✅ 已连接到所有数据库")


async def close_database_connections():
    """关闭所有数据库连接"""
    # 关闭Redis连接
    if redis_db.redis_client:
        await redis_db.redis_client.close()

    # 关闭SQLite连接
    await engine.dispose()

    print("✅ 已关闭所有数据库连接")


# 数据库初始化函数
async def init_database():
    """初始化数据库"""
    await connect_to_databases()
    await create_all_tables()


# 数据库健康检查
async def check_database_health():
    """检查数据库连接健康状态"""
    health_status = {
        "sqlite": False,
        "redis": False
    }

    try:
        # 检查SQLite
        async with AsyncSessionLocal() as session:
            await session.execute("SELECT 1")
        health_status["sqlite"] = True
    except Exception as e:
        print(f"SQLite连接失败: {e}")

    try:
        # 检查Redis
        await redis_db.redis_client.ping()
        health_status["redis"] = True
    except Exception as e:
        print(f"Redis连接失败: {e}")

    return health_status
