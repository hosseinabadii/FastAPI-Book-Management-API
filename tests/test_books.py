import pytest
from fastapi import status
from httpx import AsyncClient

from app.db.models import Book, User

BOOKS_PREFIX = "/api/v1/books"


@pytest.mark.asyncio
async def test_create_book_success(async_client: AsyncClient, test_user: User, test_user_access_token: str):
    test_user.is_verified = True
    book_data = {
        "title": "New Book",
        "author": "New Author",
        "publisher": "New Publisher",
        "page_count": 300,
        "language": "en",
        "published_date": "2023-01-01",
    }
    headers = {"Authorization": f"Bearer {test_user_access_token}"}
    response = await async_client.post(f"{BOOKS_PREFIX}/", json=book_data, headers=headers)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["title"] == book_data["title"]
    assert response.json()["author"] == book_data["author"]
    assert response.json()["user_uid"] == str(test_user.uid)


@pytest.mark.asyncio
async def test_create_book_unauthorized(async_client: AsyncClient):
    book_data = {
        "title": "New Book",
        "author": "New Author",
        "publisher": "New Publisher",
        "page_count": 300,
        "language": "en",
        "published_date": "2023-01-01",
    }
    response = await async_client.post(f"{BOOKS_PREFIX}/", json=book_data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.headers["WWW-Authenticate"] == "Bearer"
    assert response.json()["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_create_book_invalid_data(async_client: AsyncClient, test_user: User, test_user_access_token: str):
    test_user.is_verified = True
    book_data = {
        "title": "",  # Invalid: empty title
        "author": "New Author",
        "publisher": "New Publisher",
        "page_count": 0,  # Invalid: must be > 0
        "language": "en",
        "published_date": "2035-01-01",  # Invalid: future date
    }
    headers = {"Authorization": f"Bearer {test_user_access_token}"}
    response = await async_client.post(f"{BOOKS_PREFIX}/", json=book_data, headers=headers)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_get_all_books(async_client: AsyncClient, test_book: Book):
    response = await async_client.get(f"{BOOKS_PREFIX}/")

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == test_book.title


@pytest.mark.asyncio
async def test_get_book_detail_success(async_client: AsyncClient, test_book: Book):
    response = await async_client.get(f"{BOOKS_PREFIX}/{test_book.uid}")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["uid"] == str(test_book.uid)
    assert response.json()["title"] == test_book.title
    assert "reviews" in response.json()
    assert "tags" in response.json()


@pytest.mark.asyncio
async def test_get_book_detail_not_found(async_client: AsyncClient):
    non_existent_uid = "123e4567-e89b-12d3-a456-426614174000"
    response = await async_client.get(f"{BOOKS_PREFIX}/{non_existent_uid}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Book not found"
    assert response.json()["error_code"] == "book_not_found"


@pytest.mark.asyncio
async def test_update_book_success(
    async_client: AsyncClient, test_book: Book, test_user: User, test_user_access_token: str
):
    test_user.is_verified = True
    update_data = {"title": "Updated Title", "author": "Updated Author"}

    headers = {"Authorization": f"Bearer {test_user_access_token}"}
    response = await async_client.put(f"{BOOKS_PREFIX}/{test_book.uid}", json=update_data, headers=headers)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["title"] == update_data["title"]
    assert response.json()["author"] == update_data["author"]


@pytest.mark.asyncio
async def test_update_book_unauthorized(async_client: AsyncClient, test_book: Book):
    update_data = {"title": "Updated Title"}
    response = await async_client.put(f"{BOOKS_PREFIX}/{test_book.uid}", json=update_data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.headers["WWW-Authenticate"] == "Bearer"
    assert response.json()["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_update_book_insufficient_permission(
    async_client: AsyncClient, test_book: Book, other_user: User, other_user_access_token: str
):
    other_user.is_verified = True
    update_data = {"title": "Updated Title"}
    headers = {"Authorization": f"Bearer {other_user_access_token}"}
    response = await async_client.put(f"{BOOKS_PREFIX}/{test_book.uid}", json=update_data, headers=headers)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "You do not have enough permissions to perform this action"
    assert response.json()["error_code"] == "insufficient_permissions"


@pytest.mark.asyncio
async def test_update_book_admin_permission(async_client: AsyncClient, test_book: Book, admin_user_access_token: str):
    update_data = {"title": "Admin Updated Title"}
    headers = {"Authorization": f"Bearer {admin_user_access_token}"}
    response = await async_client.put(f"{BOOKS_PREFIX}/{test_book.uid}", json=update_data, headers=headers)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["title"] == update_data["title"]


@pytest.mark.asyncio
async def test_delete_book_success(
    async_client: AsyncClient, test_book: Book, test_user: User, test_user_access_token: str
):
    test_user.is_verified = True
    headers = {"Authorization": f"Bearer {test_user_access_token}"}
    response = await async_client.delete(f"{BOOKS_PREFIX}/{test_book.uid}", headers=headers)

    assert response.status_code == status.HTTP_204_NO_CONTENT

    get_response = await async_client.get(f"{BOOKS_PREFIX}/{test_book.uid}")

    assert get_response.status_code == status.HTTP_404_NOT_FOUND
    assert get_response.json()["detail"] == "Book not found"
    assert get_response.json()["error_code"] == "book_not_found"


@pytest.mark.asyncio
async def test_delete_book_unauthorized(async_client: AsyncClient, test_book: Book):
    response = await async_client.delete(f"{BOOKS_PREFIX}/{test_book.uid}")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.headers["WWW-Authenticate"] == "Bearer"
    assert response.json()["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_delete_book_insufficient_permission(
    async_client: AsyncClient, test_book: Book, other_user: User, other_user_access_token: str
):
    other_user.is_verified = True
    headers = {"Authorization": f"Bearer {other_user_access_token}"}
    response = await async_client.delete(f"{BOOKS_PREFIX}/{test_book.uid}", headers=headers)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "You do not have enough permissions to perform this action"
    assert response.json()["error_code"] == "insufficient_permissions"


@pytest.mark.asyncio
async def test_get_user_books_success(async_client: AsyncClient, test_book: Book, test_user: User):
    response = await async_client.get(f"{BOOKS_PREFIX}/user/{test_user.uid}/")

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == test_book.title


@pytest.mark.asyncio
async def test_get_user_books_empty(async_client: AsyncClient, other_user: User):
    response = await async_client.get(f"{BOOKS_PREFIX}/user/{other_user.uid}/")

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)
    assert len(response.json()) == 0
