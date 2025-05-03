import pytest
from fastapi import status
from httpx import AsyncClient

from app.db.models import User

USERS_PREFIX = "/api/v1/users"


@pytest.mark.asyncio
async def test_get_current_user_success(async_client: AsyncClient, test_user: User, test_user_access_token: str):
    test_user.is_verified = True
    headers = {"Authorization": f"Bearer {test_user_access_token}"}
    response = await async_client.get(f"{USERS_PREFIX}/me", headers=headers)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["uid"] == str(test_user.uid)
    assert response.json()["username"] == test_user.username
    assert response.json()["email"] == test_user.email


@pytest.mark.asyncio
async def test_get_current_user_unauthorized(async_client: AsyncClient):
    response = await async_client.get(f"{USERS_PREFIX}/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.headers["WWW-Authenticate"] == "Bearer"
    assert response.json()["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_get_all_users_success(
    async_client: AsyncClient, test_user: User, other_user: User, admin_user_access_token: str
):
    headers = {"Authorization": f"Bearer {admin_user_access_token}"}
    response = await async_client.get(f"{USERS_PREFIX}/", headers=headers)

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)
    assert len(response.json()) == 2  # Not include admin user


@pytest.mark.asyncio
async def test_get_all_users_unauthorized(async_client: AsyncClient):
    response = await async_client.get(f"{USERS_PREFIX}/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.headers["WWW-Authenticate"] == "Bearer"
    assert response.json()["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_get_all_users_non_admin(async_client: AsyncClient, test_user: User, test_user_access_token: str):
    test_user.is_verified = True
    headers = {"Authorization": f"Bearer {test_user_access_token}"}
    response = await async_client.get(f"{USERS_PREFIX}/", headers=headers)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "You do not have enough permissions to perform this action"
    assert response.json()["error_code"] == "insufficient_permissions"


@pytest.mark.asyncio
async def test_get_user_profile_success(async_client: AsyncClient, test_user: User):
    response = await async_client.get(f"{USERS_PREFIX}/user-profile/{test_user.username}")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["uid"] == str(test_user.uid)
    assert response.json()["username"] == test_user.username
    assert response.json()["email"] == test_user.email
    assert "books" in response.json()
    assert "reviews" in response.json()


@pytest.mark.asyncio
async def test_get_user_profile_not_found(async_client: AsyncClient):
    response = await async_client.get(f"{USERS_PREFIX}/user-profile/nonexistentuser")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "User not found"
    assert response.json()["error_code"] == "user_not_found"


@pytest.mark.asyncio
async def test_update_user_profile_success(async_client: AsyncClient, test_user: User, test_user_access_token: str):
    test_user.is_verified = True
    update_data = {
        "username": "updatedusername",
        "email": "updated@example.com",
        "first_name": "Updated",
        "last_name": "User",
    }

    headers = {"Authorization": f"Bearer {test_user_access_token}"}
    response = await async_client.put(f"{USERS_PREFIX}/user-profile/{test_user.uid}", json=update_data, headers=headers)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["username"] == update_data["username"]
    assert response.json()["email"] == update_data["email"]
    assert response.json()["first_name"] == update_data["first_name"]
    assert response.json()["last_name"] == update_data["last_name"]


@pytest.mark.asyncio
async def test_update_user_profile_unauthorized(async_client: AsyncClient, test_user: User):
    update_data = {"username": "updatedusername", "email": "updated@example.com"}

    response = await async_client.put(f"{USERS_PREFIX}/user-profile/{test_user.uid}", json=update_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.headers["WWW-Authenticate"] == "Bearer"
    assert response.json()["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_update_user_profile_insufficient_permission(
    async_client: AsyncClient, test_user: User, other_user: User, other_user_access_token: str
):
    other_user.is_verified = True
    update_data = {"username": "updatedusername", "email": "updated@example.com"}

    headers = {"Authorization": f"Bearer {other_user_access_token}"}
    response = await async_client.put(f"{USERS_PREFIX}/user-profile/{test_user.uid}", json=update_data, headers=headers)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "You do not have enough permissions to perform this action"
    assert response.json()["error_code"] == "insufficient_permissions"


@pytest.mark.asyncio
async def test_update_user_profile_admin_permission(
    async_client: AsyncClient, test_user: User, admin_user_access_token: str
):
    update_data = {"username": "adminupdated", "email": "adminupdated@example.com"}

    headers = {"Authorization": f"Bearer {admin_user_access_token}"}
    response = await async_client.put(f"{USERS_PREFIX}/user-profile/{test_user.uid}", json=update_data, headers=headers)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["username"] == update_data["username"]
    assert response.json()["email"] == update_data["email"]


@pytest.mark.asyncio
async def test_update_user_profile_invalid_data(
    async_client: AsyncClient, test_user: User, test_user_access_token: str
):
    test_user.is_verified = True
    update_data = {
        "username": "a",  # Invalid: too short
        "email": "invalid-email",  # Invalid: not a valid email
        "first_name": "a" * 26,  # Invalid: too long
        "last_name": "a" * 26,  # Invalid: too long
    }

    headers = {"Authorization": f"Bearer {test_user_access_token}"}
    response = await async_client.put(f"{USERS_PREFIX}/user-profile/{test_user.uid}", json=update_data, headers=headers)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_delete_user_profile_success(async_client: AsyncClient, test_user: User, test_user_access_token: str):
    test_user.is_verified = True
    headers = {"Authorization": f"Bearer {test_user_access_token}"}
    response = await async_client.delete(f"{USERS_PREFIX}/user-profile/{test_user.uid}", headers=headers)

    assert response.status_code == status.HTTP_204_NO_CONTENT

    get_response = await async_client.get(f"{USERS_PREFIX}/user-profile/{test_user.username}")

    assert get_response.status_code == status.HTTP_404_NOT_FOUND
    assert get_response.json()["detail"] == "User not found"
    assert get_response.json()["error_code"] == "user_not_found"


@pytest.mark.asyncio
async def test_delete_user_profile_unauthorized(async_client: AsyncClient, test_user: User):
    response = await async_client.delete(f"{USERS_PREFIX}/user-profile/{test_user.uid}")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.headers["WWW-Authenticate"] == "Bearer"
    assert response.json()["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_delete_user_profile_insufficient_permission(
    async_client: AsyncClient, test_user: User, other_user: User, other_user_access_token: str
):
    other_user.is_verified = True
    headers = {"Authorization": f"Bearer {other_user_access_token}"}
    response = await async_client.delete(f"{USERS_PREFIX}/user-profile/{test_user.uid}", headers=headers)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "You do not have enough permissions to perform this action"
    assert response.json()["error_code"] == "insufficient_permissions"


@pytest.mark.asyncio
async def test_delete_user_profile_admin_permission(
    async_client: AsyncClient, test_user: User, admin_user_access_token: str
):
    headers = {"Authorization": f"Bearer {admin_user_access_token}"}
    response = await async_client.delete(f"{USERS_PREFIX}/user-profile/{test_user.uid}", headers=headers)

    assert response.status_code == status.HTTP_204_NO_CONTENT

    get_response = await async_client.get(f"{USERS_PREFIX}/user-profile/{test_user.username}")

    assert get_response.status_code == status.HTTP_404_NOT_FOUND
    assert get_response.json()["detail"] == "User not found"
    assert get_response.json()["error_code"] == "user_not_found"
