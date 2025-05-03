import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.utils import create_jwt_token, decode_token
from app.db.models import User
from app.db.redis_client import reset_redis_mock, token_in_blocklist

AUTH_PREFIX = "/api/v1/auth"


@pytest.mark.asyncio
async def test_signup_success(async_client: AsyncClient, mock_email_service):
    user_data = {
        "email": "newuser@example.com",
        "username": "newuser",
        "password": "newpassword123",
        "first_name": "New",
        "last_name": "User",
    }
    response = await async_client.post(f"{AUTH_PREFIX}/signup", json=user_data)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["message"] == "Account Created! Check your email to verify your account"
    assert response.json()["user"]["email"] == user_data["email"]
    assert response.json()["user"]["username"] == user_data["username"]


@pytest.mark.asyncio
async def test_signup_email_exists(async_client: AsyncClient, test_user: User):
    user_data = {
        "email": test_user.email,
        "username": "differentuser",
        "password": "newpassword123",
        "first_name": "New",
        "last_name": "User",
    }
    response = await async_client.post(f"{AUTH_PREFIX}/signup", json=user_data)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "User with email already exists"
    assert response.json()["error_code"] == "email_exists"


@pytest.mark.asyncio
async def test_signup_username_exists(async_client: AsyncClient, test_user: User):
    user_data = {
        "email": "different@example.com",
        "username": test_user.username,
        "password": "newpassword123",
        "first_name": "New",
        "last_name": "User",
    }
    response = await async_client.post(f"{AUTH_PREFIX}/signup", json=user_data)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "User with username already exists"
    assert response.json()["error_code"] == "username_exists"


@pytest.mark.asyncio
async def test_login_success(async_client: AsyncClient, test_user: User, test_session: AsyncSession):
    test_user.is_verified = True
    await test_session.commit()

    login_data = {"email": test_user.email, "password": "testpassword123"}
    response = await async_client.post(f"{AUTH_PREFIX}/login", json=login_data)

    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()
    assert response.json()["user"]["email"] == test_user.email


@pytest.mark.asyncio
async def test_login_invalid_credentials(async_client: AsyncClient):
    login_data = {"email": "nonexistent@example.com", "password": "wrongpassword"}
    response = await async_client.post(f"{AUTH_PREFIX}/login", json=login_data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.headers["WWW-Authenticate"] == "Bearer"
    assert response.json()["detail"] == "Invalid email or password"
    assert response.json()["error_code"] == "invalid_email_or_password"


@pytest.mark.asyncio
async def test_login_unverified_account(async_client: AsyncClient, test_user: User):
    login_data = {"email": test_user.email, "password": "testpassword123"}
    response = await async_client.post(f"{AUTH_PREFIX}/login", json=login_data)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "Account not verified"
    assert response.json()["error_code"] == "account_not_verified"


@pytest.mark.asyncio
async def test_logout_success(async_client: AsyncClient, test_user: User):
    access_token = create_jwt_token(
        user_data={"email": test_user.email, "uid": str(test_user.uid), "role": test_user.role}, refresh=False
    )

    headers = {"Authorization": f"Bearer {access_token}"}
    response = await async_client.get(f"{AUTH_PREFIX}/logout", headers=headers)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Logged out successfully"

    token_data = decode_token(access_token)
    assert token_data is not None
    assert await token_in_blocklist(str(token_data.jti))

    reset_redis_mock()


@pytest.mark.asyncio
async def test_logout_without_access_token(async_client: AsyncClient):
    response = await async_client.get(f"{AUTH_PREFIX}/logout")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.headers["WWW-Authenticate"] == "Bearer"
    assert response.json()["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_logout_with_invalid_access_token(async_client: AsyncClient, test_user: User):
    refresh_token = create_jwt_token(
        user_data={"email": test_user.email, "uid": str(test_user.uid), "role": test_user.role}, refresh=True
    )

    headers = {"Authorization": f"Bearer {refresh_token}"}
    response = await async_client.get(f"{AUTH_PREFIX}/logout", headers=headers)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.headers["WWW-Authenticate"] == "Bearer"
    assert response.json()["detail"] == "Please provide a valid access token"
    assert response.json()["error_code"] == "access_token_required"


@pytest.mark.asyncio
async def test_refresh_token_success(async_client: AsyncClient, test_user: User):
    refresh_token = create_jwt_token(user_data={"email": test_user.email, "uid": str(test_user.uid)}, refresh=True)

    headers = {"Authorization": f"Bearer {refresh_token}"}
    response = await async_client.get(f"{AUTH_PREFIX}/refresh-token", headers=headers)

    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()


@pytest.mark.asyncio
async def test_send_verification_email(async_client: AsyncClient, test_user: User, mock_email_service):
    data = {"email": test_user.email}
    response = await async_client.post(f"{AUTH_PREFIX}/verify", json=data)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Verification email sent"


@pytest.mark.asyncio
async def test_verify_account(
    async_client: AsyncClient, test_user: User, test_session: AsyncSession, url_safe_token: str
):
    response = await async_client.get(f"{AUTH_PREFIX}/verify/{url_safe_token}")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Account verified successfully"

    await test_session.refresh(test_user)
    assert test_user.is_verified is True

    reset_redis_mock()


@pytest.mark.asyncio
async def test_password_reset_request(
    async_client: AsyncClient, test_user: User, test_session: AsyncSession, mock_email_service
):
    test_user.is_verified = True
    await test_session.commit()

    data = {"email": test_user.email}
    response = await async_client.post(f"{AUTH_PREFIX}/password-reset-request", json=data)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Please check your email for instructions to reset your password"


@pytest.mark.asyncio
async def test_password_reset_confirm_get_success(async_client: AsyncClient, test_user: User, url_safe_token: str):
    response = await async_client.get(f"{AUTH_PREFIX}/password-reset-confirm/{url_safe_token}")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Token is valid"


@pytest.mark.asyncio
async def test_password_reset_confirm_post_success(
    async_client: AsyncClient, test_user: User, test_session: AsyncSession, url_safe_token: str
):
    test_user.is_verified = True
    await test_session.commit()

    data = {"new_password": "newpassword123", "confirm_password": "newpassword123"}
    response = await async_client.post(f"{AUTH_PREFIX}/password-reset-confirm/{url_safe_token}", json=data)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Password reset successfully"
    assert await token_in_blocklist(f"url_safe_token:{url_safe_token}")

    reset_redis_mock()


@pytest.mark.asyncio
async def test_password_reset_confirm_post_mismatch(async_client: AsyncClient, url_safe_token: str):
    data = {"new_password": "newpassword123", "confirm_password": "differentpassword"}
    response = await async_client.post(f"{AUTH_PREFIX}/password-reset-confirm/{url_safe_token}", json=data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Passwords do not match"
    assert response.json()["error_code"] == "passwords_do_not_match"

    reset_redis_mock()
