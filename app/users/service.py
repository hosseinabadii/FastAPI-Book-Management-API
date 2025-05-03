from collections.abc import Sequence
from uuid import UUID

from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.auth.utils import hash_password
from app.db.models import Role, User
from app.errors import (
    AccountNotActive,
    AccountNotVerified,
    EmailAlreadyExists,
    InsufficientPermission,
    UsernameAlreadyExists,
    UserNotFound,
)

from .schemas import UserCreate, UserUpdate


class UserService:
    async def _check_permission(self, user_uid: UUID, currenrt_user: User) -> None:
        if user_uid != currenrt_user.uid and currenrt_user.role != Role.ADMIN:
            raise InsufficientPermission()

    async def get_user_by_email(self, email: EmailStr, session: AsyncSession) -> User | None:
        statement = select(User).where(User.email == email)
        result = await session.execute(statement)
        return result.scalar_one_or_none()

    async def get_user_by_username(self, username: str, session: AsyncSession) -> User | None:
        statement = select(User).where(User.username == username)
        result = await session.execute(statement)
        return result.scalar_one_or_none()

    async def create_user(self, user_data: UserCreate, session: AsyncSession) -> User:
        if await self.get_user_by_email(user_data.email, session):
            raise EmailAlreadyExists()

        if await self.get_user_by_username(user_data.username, session):
            raise UsernameAlreadyExists()

        new_user = User(**user_data.model_dump(exclude={"password"}))
        new_user.password_hash = hash_password(user_data.password)
        new_user.role = Role.USER
        session.add(new_user)
        await session.commit()
        return new_user

    async def get_all_users(self, session: AsyncSession) -> Sequence[User]:
        statement = select(User).where(User.role != Role.ADMIN)
        result = await session.execute(statement)
        return result.scalars().all()

    async def get_user_profile(self, username: str, session: AsyncSession) -> User:
        statement = (
            select(User)
            .where(User.username == username)
            .where(User.role != Role.ADMIN)
            .options(joinedload(User.books), joinedload(User.reviews))
        )
        result = await session.execute(statement)
        user = result.unique().scalar_one_or_none()
        if not user:
            raise UserNotFound()
        return user

    async def update_user_profile(
        self, user_uid: UUID, update_data: UserUpdate, current_user: User, session: AsyncSession
    ) -> User:
        await self._check_permission(user_uid, current_user)
        target_user = current_user
        if current_user.role == Role.ADMIN and current_user.uid != user_uid:
            target_user = await session.get(User, user_uid)
            if target_user is None:
                raise UserNotFound()

        update_data_dict = update_data.model_dump(exclude_none=True)

        email = update_data_dict.get("email")
        if email and email != target_user.email and await self.get_user_by_email(email, session):
            raise EmailAlreadyExists()

        username = update_data_dict.get("username")
        if username and username != target_user.username and await self.get_user_by_username(username, session):
            raise UsernameAlreadyExists()

        for key, value in update_data_dict.items():
            setattr(target_user, key, value)
        await session.commit()
        await session.refresh(target_user)
        return target_user

    async def delete_user_profile(self, user_uid: UUID, current_user: User, session: AsyncSession) -> None:
        await self._check_permission(user_uid, current_user)
        target_user = current_user
        if current_user.role == Role.ADMIN and current_user.uid != user_uid:
            target_user = await session.get(User, user_uid)
            if target_user is None:
                raise UserNotFound()
        await session.delete(target_user)
        await session.commit()

    async def verify_user_account(self, user_email: EmailStr, session: AsyncSession) -> None:
        user = await self.get_user_by_email(user_email, session)
        if user is None:
            raise UserNotFound()
        if not user.is_active:
            raise AccountNotActive()
        user.is_verified = True
        await session.commit()

    async def reset_user_password(self, user_email: EmailStr, new_password: str, session: AsyncSession) -> None:
        user = await self.get_user_by_email(user_email, session)
        if user is None:
            raise UserNotFound()
        if not user.is_active:
            raise AccountNotActive()
        if not user.is_verified:
            raise AccountNotVerified()
        user.password_hash = hash_password(new_password)
        await session.commit()
