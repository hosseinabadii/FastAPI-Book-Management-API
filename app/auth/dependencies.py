from typing import Annotated

from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
from pydantic import EmailStr

from app import errors
from app.config import Config
from app.db.main import SessionDep
from app.db.models import Role, User
from app.db.redis_client import token_in_blocklist
from app.users.service import UserService

from .schemas import TokenData
from .utils import decode_token, decode_url_safe_token

user_service = UserService()


class TokenBearer(OAuth2PasswordBearer):
    def __init__(self, token_url=Config.TOKEN_BEARER_URL):
        super().__init__(tokenUrl=token_url)

    async def __call__(self, request: Request) -> TokenData:
        token = await super().__call__(request)
        if token is None:
            raise errors.InvalidToken()
        token_data = decode_token(token)
        if token_data is None:
            raise errors.InvalidToken()
        if await token_in_blocklist(str(token_data.jti)):
            raise errors.InvalidToken()
        self.verify_token_type(token_data.refresh)
        return token_data

    @staticmethod
    def verify_token_type(is_refresh: bool) -> None:
        raise NotImplementedError("Please Override this method in child classes")


class AccessTokenBearer(TokenBearer):
    @staticmethod
    def verify_token_type(is_refresh: bool) -> None:
        if is_refresh:
            raise errors.AccessTokenRequired()


AccessTokenBearerDep = Annotated[TokenData, Depends(AccessTokenBearer())]


class RefreshTokenBearer(TokenBearer):
    @staticmethod
    def verify_token_type(is_refresh: bool) -> None:
        if not is_refresh:
            raise errors.RefreshTokenRequired()


RefreshTokenBearerDep = Annotated[TokenData, Depends(RefreshTokenBearer())]


async def get_current_user(token_data: AccessTokenBearerDep, session: SessionDep) -> User:
    user_email = token_data.user.email
    current_user = await user_service.get_user_by_email(user_email, session)
    if current_user is None:
        raise errors.UserNotFound()
    if not current_user.is_active:
        raise errors.AccountNotActive()
    if not current_user.is_verified:
        raise errors.AccountNotVerified()
    return current_user


CurrentUserDep = Annotated[User, Depends(get_current_user)]


class RoleChecker:
    def __init__(self, allowed_roles: list[str]) -> None:
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: CurrentUserDep) -> None:
        if current_user.role not in self.allowed_roles:
            raise errors.InsufficientPermission()


AdminRoleCheckerDep = Depends(RoleChecker([Role.ADMIN]))
UserRoleCheckerDep = Depends(RoleChecker([Role.ADMIN, Role.USER]))


async def verify_url_safe_token(token: str) -> EmailStr:
    if await token_in_blocklist(f"url_safe_token:{token}"):
        raise errors.InvalidVerificationToken()

    url_safe_token = decode_url_safe_token(token)
    if url_safe_token is None:
        raise errors.InvalidVerificationToken()

    user_email = url_safe_token.get("email")
    if user_email is None:
        raise errors.InvalidVerificationToken

    return user_email


UrlSafeTokenDep = Annotated[EmailStr, Depends(verify_url_safe_token)]
