from uuid import UUID

from fastapi import APIRouter, status

from app.auth.dependencies import AdminRoleCheckerDep, CurrentUserDep
from app.db.main import SessionDep

from .schemas import UserBooks, UserPublic, UserUpdate
from .service import UserService

user_router = APIRouter()
user_service = UserService()


@user_router.get("/me", response_model=UserPublic)
async def get_current_user(user: CurrentUserDep):
    return user


@user_router.get("/", response_model=list[UserPublic], dependencies=[AdminRoleCheckerDep])
async def get_all_users(session: SessionDep):
    return await user_service.get_all_users(session)


@user_router.get("/user-profile/{username}", response_model=UserBooks)
async def get_user_profile(username: str, session: SessionDep):
    return await user_service.get_user_profile(username, session)


@user_router.put("/user-profile/{user_uid}", response_model=UserPublic)
async def update_user_profile(
    user_uid: UUID, update_data: UserUpdate, current_user: CurrentUserDep, session: SessionDep
):
    return await user_service.update_user_profile(user_uid, update_data, current_user, session)


@user_router.delete("/user-profile/{user_uid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_profile(user_uid: UUID, current_user: CurrentUserDep, session: SessionDep):
    return await user_service.delete_user_profile(user_uid, current_user, session)
