from fastapi import APIRouter, BackgroundTasks, status

from app.celery_tasks import EmailTaskService
from app.db.main import SessionDep
from app.db.redis_client import add_jti_to_blocklist
from app.errors import AccountNotActive, AccountNotVerified, InvalidCredentials, PasswordsDoNotMatch, UserNotFound
from app.users.schemas import UserCreate
from app.users.service import UserService

from .dependencies import AccessTokenBearerDep, RefreshTokenBearerDep, UrlSafeTokenDep
from .schemas import (
    LoginData,
    LoginResponse,
    LogoutResponse,
    PasswordResetConfirm,
    PasswordResetRequest,
    PasswordResetResponse,
    RefreshTokenResponse,
    SignupResponse,
    VerifyEmailRequest,
    VerifyEmailResponse,
)
from .utils import create_jwt_token, verify_password

auth_router = APIRouter()
user_service = UserService()


@auth_router.post("/signup", response_model=SignupResponse, status_code=status.HTTP_201_CREATED)
async def create_user_Account(user_data: UserCreate, session: SessionDep, bg_tasks: BackgroundTasks):
    new_user = await user_service.create_user(user_data, session)
    email_task_service = EmailTaskService(bg_tasks)
    await email_task_service.send_verification_email(new_user.email)
    return {
        "message": "Account Created! Check your email to verify your account",
        "user": new_user,
    }


@auth_router.post("/login", response_model=LoginResponse)
async def login_users(login_data: LoginData, session: SessionDep):
    email = login_data.email
    password = login_data.password

    user = await user_service.get_user_by_email(email, session)
    if user is None:
        raise InvalidCredentials()

    if not user.is_active:
        raise AccountNotActive()

    if not user.is_verified:
        raise AccountNotVerified()

    is_password_valid = verify_password(password, user.password_hash)
    if not is_password_valid:
        raise InvalidCredentials()

    access_token = create_jwt_token(
        user_data={"email": user.email, "uid": str(user.uid), "role": user.role},
        refresh=False,
    )

    refresh_token = create_jwt_token(
        user_data={"email": user.email, "uid": str(user.uid)},
        refresh=True,
    )

    return {
        "message": "Login successful",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": {"email": user.email, "uid": str(user.uid)},
    }


@auth_router.get("/logout", response_model=LogoutResponse)
async def revoke_token(token_data: AccessTokenBearerDep):
    jti = str(token_data.jti)
    await add_jti_to_blocklist(jti)

    return {"message": "Logged out successfully"}


@auth_router.get("/refresh-token", response_model=RefreshTokenResponse)
async def get_new_access_token(token_data: RefreshTokenBearerDep):
    user = token_data.user
    user_data = {"email": user.email, "uid": str(user.uid)}
    new_access_token = create_jwt_token(user_data=user_data, refresh=False)

    return {"access_token": new_access_token}


@auth_router.post("/verify", response_model=VerifyEmailResponse)
async def send_verification_email(user_data: VerifyEmailRequest, session: SessionDep, bg_tasks: BackgroundTasks):
    user = await user_service.get_user_by_email(email=user_data.email, session=session)
    if user is None:
        raise UserNotFound()

    if user.is_verified:
        return {"message": "Email already verified"}

    email_task_service = EmailTaskService(bg_tasks)
    await email_task_service.send_verification_email(user.email)

    return {"message": "Verification email sent"}


@auth_router.get("/verify/{token}", response_model=VerifyEmailResponse)
async def verify_user_account(token: str, user_email: UrlSafeTokenDep, session: SessionDep):
    await user_service.verify_user_account(user_email, session)
    await add_jti_to_blocklist(f"url_safe_token:{token}")

    return {"message": "Account verified successfully"}


@auth_router.post("/password-reset-request", response_model=PasswordResetResponse)
async def send_password_reset_email(request_data: PasswordResetRequest, session: SessionDep, bg_tasks: BackgroundTasks):
    user = await user_service.get_user_by_email(email=request_data.email, session=session)
    if user is None:
        raise UserNotFound()

    if not user.is_active:
        raise AccountNotActive()

    if not user.is_verified:
        raise AccountNotVerified()

    email_task_service = EmailTaskService(bg_tasks)
    await email_task_service.send_password_reset_email(user.email)

    return {"message": "Please check your email for instructions to reset your password"}


@auth_router.get("/password-reset-confirm/{token}", response_model=PasswordResetResponse)
async def validate_password_reset_token(_: UrlSafeTokenDep):
    return {"message": "Token is valid"}


@auth_router.post("/password-reset-confirm/{token}", response_model=PasswordResetResponse)
async def reset_password(
    token: str, request_data: PasswordResetConfirm, user_email: UrlSafeTokenDep, session: SessionDep
):
    new_password = request_data.new_password
    confirm_password = request_data.confirm_password
    if new_password != confirm_password:
        raise PasswordsDoNotMatch()

    await user_service.reset_user_password(user_email, new_password, session)
    await add_jti_to_blocklist(f"url_safe_token:{token}")

    return {"message": "Password reset successfully"}
