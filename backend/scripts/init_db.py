#!/usr/bin/env python3
"""
数据库初始化脚本
"""
import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import init_database
from services.user_service import create_user
from schemas.user import UserCreate
from models.user import UserRole
from database import AsyncSessionLocal


async def create_admin_user():
    """创建管理员用户"""
    async with AsyncSessionLocal() as db:
        try:
            admin_data = UserCreate(
                email="admin@example.com",
                username="admin",
                password="admin123456",
                confirm_password="admin123456",
                full_name="系统管理员",
                nickname="Admin"
            )

            admin_user = await create_user(db, admin_data)
            admin_user.role = UserRole.ADMIN
            admin_user.is_admin = True
            admin_user.is_verified = True

            await db.commit()
            print(f"✅ 管理员用户创建成功: {admin_user.username} ({admin_user.email})")

        except Exception as e:
            print(f"⚠️  管理员用户创建失败: {e}")


async def create_sample_data():
    """创建示例数据"""
    from models.media import MediaCategory
    from models.payment import VIPPlan

    async with AsyncSessionLocal() as db:
        try:
            # 创建媒体分类
            categories = [
                MediaCategory(
                    name="生活随拍",
                    description="日常生活的美好瞬间",
                    is_paid=False,
                    sort_order=1
                ),
                MediaCategory(
                    name="旅行足迹",
                    description="世界各地的旅行记录",
                    is_paid=False,
                    sort_order=2
                ),
                MediaCategory(
                    name="VIP专享",
                    description="VIP会员专享内容",
                    is_paid=True,
                    price=9.9,
                    sort_order=3
                )
            ]

            for category in categories:
                db.add(category)

            # 创建VIP套餐
            vip_plans = [
                VIPPlan(
                    name="月度会员",
                    description="享受一个月的VIP特权",
                    price=19.9,
                    duration_days=30,
                    features=["查看VIP专享内容", "无限下载", "专属客服"],
                    sort_order=1
                ),
                VIPPlan(
                    name="季度会员",
                    description="享受三个月的VIP特权，更优惠",
                    price=49.9,
                    duration_days=90,
                    features=["查看VIP专享内容", "无限下载", "专属客服", "优先更新"],
                    sort_order=2
                ),
                VIPPlan(
                    name="年度会员",
                    description="享受一年的VIP特权，最划算",
                    price=149.9,
                    duration_days=365,
                    features=["查看VIP专享内容", "无限下载", "专属客服", "优先更新", "年度纪念品"],
                    sort_order=3
                )
            ]

            for plan in vip_plans:
                db.add(plan)

            print("✅ 私聊系统已配置完成（私聊房间将在用户开始聊天时自动创建）")

            await db.commit()
            print("✅ 示例数据创建成功")

        except Exception as e:
            print(f"⚠️  示例数据创建失败: {e}")


async def main():
    """主函数"""
    print("🔧 开始初始化数据库...")

    try:
        # 初始化数据库
        await init_database()
        print("✅ 数据库连接和表创建完成")

        # 创建管理员用户
        await create_admin_user()

        # 创建示例数据
        await create_sample_data()

        print("\n🎉 数据库初始化完成！")
        print("\n📋 默认管理员账户:")
        print("   用户名: admin")
        print("   邮箱: admin@example.com")
        print("   密码: admin123456")
        print("\n⚠️  请及时修改默认密码！")

    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
