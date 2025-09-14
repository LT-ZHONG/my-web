"""
用户服务层
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload
from typing import Optional, List, Tuple
from datetime import datetime, timedelta

from models.user import User, UserRole, UserStatus
from schemas.user import UserCreate, UserUpdate, UserAdminUpdate, UserListQuery
from utils.auth import get_password_hash, verify_password
from utils.exceptions import (
    DuplicateResourceError, 
    ResourceNotFoundError, 
    AuthenticationError,
    ValidationError
)


async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    """根据ID获取用户"""
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """根据邮箱获取用户"""
    result = await db.execute(
        select(User).where(User.email == email)
    )
    return result.scalar_one_or_none()


async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    """根据用户名获取用户"""
    result = await db.execute(
        select(User).where(User.username == username)
    )
    return result.scalar_one_or_none()


async def get_user_by_username_or_email(db: AsyncSession, identifier: str) -> Optional[User]:
    """根据用户名或邮箱获取用户"""
    result = await db.execute(
        select(User).where(
            or_(User.username == identifier, User.email == identifier)
        )
    )
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
    """创建新用户"""
    # 检查邮箱是否已存在
    existing_user = await get_user_by_email(db, user_data.email)
    if existing_user:
        raise DuplicateResourceError("邮箱已被注册")
    
    # 检查用户名是否已存在
    existing_user = await get_user_by_username(db, user_data.username)
    if existing_user:
        raise DuplicateResourceError("用户名已被使用")
    
    # 创建用户
    hashed_password = get_password_hash(user_data.password)
    
    user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        nickname=user_data.nickname,
        bio=user_data.bio,
        role=UserRole.USER,
        status=UserStatus.ACTIVE,
        is_active=True
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    return user


async def authenticate_user(db: AsyncSession, identifier: str, password: str) -> Optional[User]:
    """用户认证"""
    user = await get_user_by_username_or_email(db, identifier)
    
    if not user:
        return None
    
    if not verify_password(password, user.hashed_password):
        return None
    
    if not user.is_active or user.status != UserStatus.ACTIVE:
        return None
    
    # 更新登录信息
    user.last_login_at = datetime.utcnow()
    user.login_count += 1
    await db.commit()
    
    return user


async def update_user(db: AsyncSession, user_id: int, user_data: UserUpdate) -> User:
    """更新用户信息"""
    user = await get_user_by_id(db, user_id)
    if not user:
        raise ResourceNotFoundError("用户不存在")
    
    # 更新字段
    for field, value in user_data.dict(exclude_unset=True).items():
        setattr(user, field, value)
    
    await db.commit()
    await db.refresh(user)
    
    return user


async def update_user_password(db: AsyncSession, user_id: int, old_password: str, new_password: str) -> bool:
    """更新用户密码"""
    user = await get_user_by_id(db, user_id)
    if not user:
        raise ResourceNotFoundError("用户不存在")
    
    # 验证旧密码
    if not verify_password(old_password, user.hashed_password):
        raise AuthenticationError("当前密码错误")
    
    # 更新密码
    user.hashed_password = get_password_hash(new_password)
    await db.commit()
    
    return True


async def admin_update_user(db: AsyncSession, user_id: int, admin_data: UserAdminUpdate) -> User:
    """管理员更新用户信息"""
    user = await get_user_by_id(db, user_id)
    if not user:
        raise ResourceNotFoundError("用户不存在")
    
    # 更新字段
    for field, value in admin_data.dict(exclude_unset=True).items():
        setattr(user, field, value)
    
    await db.commit()
    await db.refresh(user)
    
    return user


async def delete_user(db: AsyncSession, user_id: int) -> bool:
    """删除用户"""
    user = await get_user_by_id(db, user_id)
    if not user:
        raise ResourceNotFoundError("用户不存在")
    
    # 软删除：设置为不活跃状态
    user.is_active = False
    user.status = UserStatus.INACTIVE
    await db.commit()
    
    return True


async def get_users_list(
    db: AsyncSession, 
    query: UserListQuery
) -> Tuple[List[User], int]:
    """获取用户列表"""
    # 构建查询条件
    conditions = []
    
    if query.search:
        search_term = f"%{query.search}%"
        conditions.append(
            or_(
                User.username.ilike(search_term),
                User.email.ilike(search_term),
                User.full_name.ilike(search_term),
                User.nickname.ilike(search_term)
            )
        )
    
    if query.role:
        conditions.append(User.role == query.role)
    
    if query.status:
        conditions.append(User.status == query.status)
    
    if query.is_vip is not None:
        conditions.append(User.is_vip == query.is_vip)
    
    # 计算总数
    count_stmt = select(func.count(User.id))
    if conditions:
        count_stmt = count_stmt.where(and_(*conditions))
    
    total_result = await db.execute(count_stmt)
    total = total_result.scalar()
    
    # 获取用户列表
    stmt = select(User)
    if conditions:
        stmt = stmt.where(and_(*conditions))
    
    stmt = stmt.order_by(User.created_at.desc())
    stmt = stmt.offset((query.page - 1) * query.page_size)
    stmt = stmt.limit(query.page_size)
    
    result = await db.execute(stmt)
    users = result.scalars().all()
    
    return list(users), total


async def get_user_stats(db: AsyncSession) -> dict:
    """获取用户统计信息"""
    # 总用户数
    total_users = await db.execute(select(func.count(User.id)))
    total_users = total_users.scalar()
    
    # 活跃用户数
    active_users = await db.execute(
        select(func.count(User.id)).where(User.is_active == True)
    )
    active_users = active_users.scalar()
    
    # VIP用户数
    vip_users = await db.execute(
        select(func.count(User.id)).where(User.is_vip == True)
    )
    vip_users = vip_users.scalar()
    
    # 管理员数
    admin_users = await db.execute(
        select(func.count(User.id)).where(User.is_admin == True)
    )
    admin_users = admin_users.scalar()
    
    # 今日新用户
    today = datetime.now().date()
    today_users = await db.execute(
        select(func.count(User.id)).where(
            func.date(User.created_at) == today
        )
    )
    today_users = today_users.scalar()
    
    # 本月新用户
    this_month = datetime.now().replace(day=1).date()
    month_users = await db.execute(
        select(func.count(User.id)).where(
            User.created_at >= this_month
        )
    )
    month_users = month_users.scalar()
    
    return {
        "total_users": total_users,
        "active_users": active_users,
        "vip_users": vip_users,
        "admin_users": admin_users,
        "today_users": today_users,
        "month_users": month_users
    }


async def update_user_vip_status(
    db: AsyncSession, 
    user_id: int, 
    is_vip: bool, 
    expire_at: Optional[datetime] = None
) -> User:
    """更新用户VIP状态"""
    user = await get_user_by_id(db, user_id)
    if not user:
        raise ResourceNotFoundError("用户不存在")
    
    user.is_vip = is_vip
    user.vip_expire_at = expire_at
    
    await db.commit()
    await db.refresh(user)
    
    return user


async def check_vip_expiration(db: AsyncSession) -> int:
    """检查并处理VIP过期用户"""
    now = datetime.utcnow()
    
    # 查找过期的VIP用户
    expired_users = await db.execute(
        select(User).where(
            and_(
                User.is_vip == True,
                User.vip_expire_at < now
            )
        )
    )
    expired_users = expired_users.scalars().all()
    
    # 更新过期用户状态
    count = 0
    for user in expired_users:
        user.is_vip = False
        count += 1
    
    if count > 0:
        await db.commit()
    
    return count