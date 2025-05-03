import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession  # noqa: F401

from app.db.models import Book, Review, User

REVIEWS_PREFIX = "/api/v1/reviews"


@pytest.mark.asyncio
async def test_get_all_reviews(async_client: AsyncClient, test_review: Review):
    response = await async_client.get(f"{REVIEWS_PREFIX}/")

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)
    assert len(response.json()) == 1
    assert response.json()[0]["rating"] == test_review.rating
    assert response.json()[0]["review_text"] == test_review.review_text


@pytest.mark.asyncio
async def test_get_review_success(async_client: AsyncClient, test_review: Review):
    response = await async_client.get(f"{REVIEWS_PREFIX}/{test_review.uid}")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["uid"] == str(test_review.uid)
    assert response.json()["rating"] == test_review.rating
    assert response.json()["review_text"] == test_review.review_text


@pytest.mark.asyncio
async def test_get_review_not_found(async_client: AsyncClient):
    non_existent_uid = "123e4567-e89b-12d3-a456-426614174000"
    response = await async_client.get(f"{REVIEWS_PREFIX}/{non_existent_uid}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Review not found"
    assert response.json()["error_code"] == "review_not_found"


@pytest.mark.asyncio
async def test_add_review_to_book_success(
    async_client: AsyncClient, test_book: Book, test_user: User, test_user_access_token: str
):
    test_user.is_verified = True
    review_data = {"rating": 5, "review_text": "Excellent book!"}

    headers = {"Authorization": f"Bearer {test_user_access_token}"}
    response = await async_client.post(f"{REVIEWS_PREFIX}/book/{test_book.uid}", json=review_data, headers=headers)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["rating"] == review_data["rating"]
    assert response.json()["review_text"] == review_data["review_text"]
    assert response.json()["user_uid"] == str(test_user.uid)
    assert response.json()["book_uid"] == str(test_book.uid)


@pytest.mark.asyncio
async def test_add_review_to_book_unauthorized(async_client: AsyncClient, test_book: Book):
    review_data = {"rating": 5, "review_text": "Excellent book!"}

    response = await async_client.post(f"{REVIEWS_PREFIX}/book/{test_book.uid}", json=review_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.headers["WWW-Authenticate"] == "Bearer"
    assert response.json()["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_add_review_to_book_invalid_data(
    async_client: AsyncClient, test_book: Book, test_user: User, test_user_access_token: str
):
    test_user.is_verified = True
    review_data = {
        "rating": 6,  # Invalid: rating must be <= 5
        "review_text": "",  # Invalid: empty review text
    }

    headers = {"Authorization": f"Bearer {test_user_access_token}"}
    response = await async_client.post(f"{REVIEWS_PREFIX}/book/{test_book.uid}", json=review_data, headers=headers)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_update_review_success(
    async_client: AsyncClient, test_review: Review, test_user: User, test_user_access_token: str
):
    test_user.is_verified = True
    update_data = {"rating": 3, "review_text": "Updated review text"}

    headers = {"Authorization": f"Bearer {test_user_access_token}"}
    response = await async_client.put(f"{REVIEWS_PREFIX}/{test_review.uid}", json=update_data, headers=headers)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["rating"] == update_data["rating"]
    assert response.json()["review_text"] == update_data["review_text"]


@pytest.mark.asyncio
async def test_update_review_unauthorized(async_client: AsyncClient, test_review: Review):
    update_data = {"rating": 3, "review_text": "Updated review text"}
    response = await async_client.put(f"{REVIEWS_PREFIX}/{test_review.uid}", json=update_data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.headers["WWW-Authenticate"] == "Bearer"
    assert response.json()["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_update_review_insufficient_permission(
    async_client: AsyncClient, test_review: Review, other_user: User, other_user_access_token: str
):
    other_user.is_verified = True
    update_data = {"rating": 3, "review_text": "Updated review text"}
    headers = {"Authorization": f"Bearer {other_user_access_token}"}
    response = await async_client.put(f"{REVIEWS_PREFIX}/{test_review.uid}", json=update_data, headers=headers)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "You do not have enough permissions to perform this action"
    assert response.json()["error_code"] == "insufficient_permissions"


@pytest.mark.asyncio
async def test_update_review_admin_permission(
    async_client: AsyncClient, test_review: Review, admin_user_access_token: str
):
    update_data = {"rating": 3, "review_text": "Admin updated review"}
    headers = {"Authorization": f"Bearer {admin_user_access_token}"}
    response = await async_client.put(f"{REVIEWS_PREFIX}/{test_review.uid}", json=update_data, headers=headers)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["rating"] == update_data["rating"]
    assert response.json()["review_text"] == update_data["review_text"]


@pytest.mark.asyncio
async def test_delete_review_success(
    async_client: AsyncClient, test_review: Review, test_user: User, test_user_access_token: str
):
    test_user.is_verified = True
    headers = {"Authorization": f"Bearer {test_user_access_token}"}
    response = await async_client.delete(f"{REVIEWS_PREFIX}/{test_review.uid}", headers=headers)

    assert response.status_code == status.HTTP_204_NO_CONTENT

    get_response = await async_client.get(f"{REVIEWS_PREFIX}/{test_review.uid}")

    assert get_response.status_code == status.HTTP_404_NOT_FOUND
    assert get_response.json()["detail"] == "Review not found"
    assert get_response.json()["error_code"] == "review_not_found"


@pytest.mark.asyncio
async def test_delete_review_unauthorized(async_client: AsyncClient, test_review: Review):
    response = await async_client.delete(f"{REVIEWS_PREFIX}/{test_review.uid}")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.headers["WWW-Authenticate"] == "Bearer"
    assert response.json()["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_delete_review_insufficient_permission(
    async_client: AsyncClient, test_review: Review, other_user: User, other_user_access_token: str
):
    other_user.is_verified = True
    headers = {"Authorization": f"Bearer {other_user_access_token}"}
    response = await async_client.delete(f"{REVIEWS_PREFIX}/{test_review.uid}", headers=headers)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "You do not have enough permissions to perform this action"
    assert response.json()["error_code"] == "insufficient_permissions"
