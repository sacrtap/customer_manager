from typing import Optional, List, Dict, Any
from sqlalchemy import delete, select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.role import Role, UserRole
from app.utils.password import hash_password


class UserService:
    """用户服务层"""

    @staticmethod
    async def list_users(
        session: AsyncSession,
        page: int = 1,
        size: int = 20,
        keyword: Optional[str] = None,
    ) -> Dict[str, Any]:
        """获取用户列表"""
        query = select(User).order_by(desc(User.created_at))

        if keyword:
            query = query.where(
                (User.username.ilike(f"%{keyword}%"))
                | (User.real_name.ilike(f"%{keyword}%"))
                | (User.email.ilike(f"%{keyword}%"))
            )

        total_result = await session.execute(select(func.count()).select_from(User))
        total = total_result.scalar()

        offset = (page - 1) * size
        query = query.limit(size).offset(offset)

        result = await session.execute(query)
        users = result.scalars().all()

        users_with_roles = []
        for user in users:
            user_dict = user.to_dict()
            role_result = await session.execute(
                select(Role)
                .join(UserRole, Role.id == UserRole.role_id)
                .where(UserRole.user_id == user.id)
            )
            roles = role_result.scalars().all()
            user_dict["roles"] = [role.code for role in roles]
            user_dict["role_ids"] = [role.id for role in roles]
            users_with_roles.append(user_dict)

        return {
            "items": users_with_roles,
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size if size > 0 else 0,
        }

    @staticmethod
    async def get_user(session: AsyncSession, user_id: int) -> Optional[User]:
        """获取用户详情"""
        result = await session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_username(
        session: AsyncSession, username: str
    ) -> Optional[User]:
        """根据用户名获取用户"""
        result = await session.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    @staticmethod
    async def create_user(
        session: AsyncSession,
        data: Dict[str, Any],
        role_ids: Optional[List[int]] = None,
    ) -> User:
        """创建用户"""
        password_hash = hash_password(data["password"])

        user = User(
            username=data["username"],
            password_hash=password_hash,
            real_name=data["real_name"],
            email=data.get("email"),
            phone=data.get("phone"),
            status=data.get("status", "active"),
        )

        session.add(user)
        await session.flush()

        if role_ids:
            for role_id in role_ids:
                user_role = UserRole(user_id=user.id, role_id=role_id)
                session.add(user_role)

        await session.flush()
        return user

    @staticmethod
    async def update_user(
        session: AsyncSession,
        user_id: int,
        data: Dict[str, Any],
        role_ids: Optional[List[int]] = None,
    ) -> Optional[User]:
        """更新用户"""
        user = await UserService.get_user(session, user_id)
        if not user:
            return None

        if "real_name" in data:
            user.real_name = data["real_name"]
        if "email" in data:
            user.email = data["email"]
        if "phone" in data:
            user.phone = data["phone"]
        if "status" in data:
            user.status = data["status"]

        if role_ids is not None:
            await session.execute(delete(UserRole).where(UserRole.user_id == user_id))
            for role_id in role_ids:
                user_role = UserRole(user_id=user.id, role_id=role_id)
                session.add(user_role)

        await session.flush()
        return user

    @staticmethod
    async def delete_user(session: AsyncSession, user_id: int) -> bool:
        """删除用户"""
        user = await UserService.get_user(session, user_id)
        if not user:
            return False

        await session.execute(delete(UserRole).where(UserRole.user_id == user_id))
        await session.delete(user)
        await session.flush()
        return True

    @staticmethod
    async def update_password(
        session: AsyncSession, user_id: int, new_password: str
    ) -> bool:
        """更新用户密码"""
        user = await UserService.get_user(session, user_id)
        if not user:
            return False

        user.password_hash = hash_password(new_password)
        await session.flush()
        return True
