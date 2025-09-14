#!/usr/bin/env python3
"""
应用程序启动脚本
"""
import uvicorn
from config import settings
from database import init_database


async def startup():
    """启动时初始化"""
    print("🚀 正在启动个人展示网站后端服务...")

    # 初始化数据库
    try:
        await init_database()
        print("✅ 数据库初始化完成")
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        return False

    return True


def main():
    """主函数"""
    print(f"""个人生活展示网站 - 后端服务
        地址: http://{settings.HOST}:{settings.PORT}          
        文档: http://{settings.HOST}:{settings.PORT}/docs    
        环境: {'开发' if settings.DEBUG else '生产'}""")

    # 启动服务器
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info",
        access_log=True
    )


if __name__ == "__main__":
    main()
