from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import Optional, List, Dict
from datetime import datetime

from app.models.role import Role, UserRole


class RoleService:
    """角色服务层"""

    @staticmethod
    async def create_role(session: AsyncSession, data: Dict) -> Role:
        """创建角色"""
        role = Role(
            name=data["name"],
            code=data["code"],
            description=data.get("description"),
            permissions=data.get("permissions", []),
            is_system=data.get("is_system", False),
        )

        session.add(role)
        await session.commit()
        await session.refresh(role)

        return role

    @staticmethod
    async def get_role(session: AsyncSession, role_id: int) -> Optional[Role]:
        """获取角色详情"""
        query = select(Role).where(Role.id == role_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_role_by_code(session: AsyncSession, code: str) -> Optional[Role]:
        """根据编码获取角色"""
        query = select(Role).where(Role.code == code)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def update_role(
        session: AsyncSession, role_id: int, data: Dict
    ) -> Optional[Role]:
        """更新角色"""
        query = select(Role).where(Role.id == role_id)
        result = await session.execute(query)
        role = result.scalar_one_or_none()

        if not role:
            return None

        # 更新字段
        if "name" in data:
            role.name = data["name"]
        if "description" in data:
            role.description = data["description"]
        if "permissions" in data:
            role.permissions = data["permissions"]

        await session.commit()
        await session.refresh(role)

        return role

    @staticmethod
    async def delete_role(session: AsyncSession, role_id: int) -> bool:
        """删除角色"""
        # 检查是否为系统角色
        role = await RoleService.get_role(session, role_id)
        if role and role.is_system:
            return False

        # 删除用户角色关联
        await session.execute(select(UserRole).where(UserRole.role_id == role_id))

        # 删除角色
        result = await session.execute(select(Role).where(Role.id == role_id))
        role = result.scalar_one_or_none()

        if role:
            await session.delete(role)
            await session.commit()
            return True

        return False

    @staticmethod
    async def list_roles(
        session: AsyncSession,
        page: int = 1,
        size: int = 20,
        keyword: Optional[str] = None,
    ) -> Dict:
        """角色列表"""
        query = select(Role)

        # 关键词搜索
        if keyword:
            query = query.where(
                (Role.name.like(f"%{keyword}%")) | (Role.code.like(f"%{keyword}%"))
            )

        # 总数
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await session.execute(count_query)
        total = total_result.scalar() or 0

        # 分页
        query = query.order_by(Role.id.asc()).limit(size).offset((page - 1) * size)
        result = await session.execute(query)
        items = result.scalars().all()

        return {
            "items": [item.to_dict() for item in items],
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size,
        }

    @staticmethod
    async def assign_role_to_user(
        session: AsyncSession, user_id: int, role_id: int
    ) -> UserRole:
        """分配角色给用户"""
        user_role = UserRole(user_id=user_id, role_id=role_id)
        session.add(user_role)
        await session.commit()
        await session.refresh(user_role)

        return user_role

    @staticmethod
    async def remove_role_from_user(
        session: AsyncSession, user_id: int, role_id: int
    ) -> bool:
        """移除用户角色"""
        result = await session.execute(
            select(UserRole).where(
                UserRole.user_id == user_id, UserRole.role_id == role_id
            )
        )
        user_role = result.scalar_one_or_none()

        if user_role:
            await session.delete(user_role)
            await session.commit()
            return True

        return False

    @staticmethod
    async def get_user_roles(session: AsyncSession, user_id: int) -> List[Role]:
        """获取用户的所有角色"""
        result = await session.execute(
            select(Role)
            .join(UserRole, Role.id == UserRole.role_id)
            .where(UserRole.user_id == user_id)
        )
        return result.scalars().all()
