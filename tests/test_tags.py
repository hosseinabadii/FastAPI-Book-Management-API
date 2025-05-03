import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Book, BookTag, Tag, User

TAGS_PREFIX = "/api/v1/tags"


@pytest.mark.asyncio
async def test_get_tag_success(async_client: AsyncClient, test_tag: Tag):
    response = await async_client.get(f"{TAGS_PREFIX}/{test_tag.uid}")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["uid"] == str(test_tag.uid)
    assert response.json()["name"] == test_tag.name


@pytest.mark.asyncio
async def test_get_tag_not_found(async_client: AsyncClient):
    non_existent_uid = "123e4567-e89b-12d3-a456-426614174000"
    response = await async_client.get(f"{TAGS_PREFIX}/{non_existent_uid}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Tag not found"
    assert response.json()["error_code"] == "tag_not_found"


@pytest.mark.asyncio
async def test_get_tags_of_book(async_client: AsyncClient, test_book: Book, test_tag: Tag, test_session: AsyncSession):
    book_tag = BookTag(book_uid=test_book.uid, tag_uid=test_tag.uid)
    test_session.add(book_tag)
    await test_session.commit()

    response = await async_client.get(f"{TAGS_PREFIX}/book/{test_book.uid}")

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == test_tag.name


@pytest.mark.asyncio
async def test_add_tags_to_book_success(
    async_client: AsyncClient, test_book: Book, test_user: User, test_user_access_token: str
):
    test_user.is_verified = True
    tag_data = {"tags": [{"name": "New Tag 1"}, {"name": "New Tag 2"}]}

    headers = {"Authorization": f"Bearer {test_user_access_token}"}
    response = await async_client.post(f"{TAGS_PREFIX}/book/{test_book.uid}", json=tag_data, headers=headers)

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)
    assert len(response.json()) == 2
    assert response.json()[0]["name"] in ["New Tag 1", "New Tag 2"]
    assert response.json()[1]["name"] in ["New Tag 1", "New Tag 2"]


@pytest.mark.asyncio
async def test_add_tags_to_book_unauthorized(async_client: AsyncClient, test_book: Book):
    tag_data = {"tags": [{"name": "New Tag 1"}, {"name": "New Tag 2"}]}

    response = await async_client.post(f"{TAGS_PREFIX}/book/{test_book.uid}", json=tag_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.headers["WWW-Authenticate"] == "Bearer"
    assert response.json()["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_add_tags_to_book_insufficient_permission(
    async_client: AsyncClient, test_book: Book, other_user: User, other_user_access_token: str
):
    other_user.is_verified = True
    tag_data = {"tags": [{"name": "New Tag 1"}, {"name": "New Tag 2"}]}

    headers = {"Authorization": f"Bearer {other_user_access_token}"}
    response = await async_client.post(f"{TAGS_PREFIX}/book/{test_book.uid}", json=tag_data, headers=headers)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "You do not have enough permissions to perform this action"
    assert response.json()["error_code"] == "insufficient_permissions"


@pytest.mark.asyncio
async def test_update_tag_of_book_success(
    async_client: AsyncClient,
    test_book: Book,
    test_tag: Tag,
    test_user: User,
    test_user_access_token: str,
    test_session: AsyncSession,
):
    test_user.is_verified = True
    book_tag = BookTag(book_uid=test_book.uid, tag_uid=test_tag.uid)
    test_session.add(book_tag)
    await test_session.commit()

    update_data = {"name": "Updated Tag Name"}
    headers = {"Authorization": f"Bearer {test_user_access_token}"}
    response = await async_client.put(
        f"{TAGS_PREFIX}/book/{test_book.uid}/tag/{test_tag.uid}", json=update_data, headers=headers
    )

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == update_data["name"]


@pytest.mark.asyncio
async def test_update_tag_of_book_unauthorized(
    async_client: AsyncClient, test_book: Book, test_tag: Tag, test_session: AsyncSession
):
    book_tag = BookTag(book_uid=test_book.uid, tag_uid=test_tag.uid)
    test_session.add(book_tag)
    await test_session.commit()

    update_data = {"name": "Updated Tag Name"}
    response = await async_client.put(f"{TAGS_PREFIX}/book/{test_book.uid}/tag/{test_tag.uid}", json=update_data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.headers["WWW-Authenticate"] == "Bearer"
    assert response.json()["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_update_tag_of_book_insufficient_permission(
    async_client: AsyncClient,
    test_book: Book,
    test_tag: Tag,
    other_user: User,
    other_user_access_token: str,
    test_session: AsyncSession,
):
    other_user.is_verified = True
    book_tag = BookTag(book_uid=test_book.uid, tag_uid=test_tag.uid)
    test_session.add(book_tag)
    await test_session.commit()

    update_data = {"name": "Updated Tag Name"}
    headers = {"Authorization": f"Bearer {other_user_access_token}"}
    response = await async_client.put(
        f"{TAGS_PREFIX}/book/{test_book.uid}/tag/{test_tag.uid}", json=update_data, headers=headers
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "You do not have enough permissions to perform this action"
    assert response.json()["error_code"] == "insufficient_permissions"


@pytest.mark.asyncio
async def test_delete_tag_from_book_success(
    async_client: AsyncClient,
    test_book: Book,
    test_tag: Tag,
    test_user: User,
    test_user_access_token: str,
    test_session: AsyncSession,
):
    test_user.is_verified = True
    book_tag = BookTag(book_uid=test_book.uid, tag_uid=test_tag.uid)
    test_session.add(book_tag)
    await test_session.commit()

    headers = {"Authorization": f"Bearer {test_user_access_token}"}
    response = await async_client.delete(f"{TAGS_PREFIX}/book/{test_book.uid}/tag/{test_tag.uid}", headers=headers)

    assert response.status_code == status.HTTP_204_NO_CONTENT

    get_response = await async_client.get(f"{TAGS_PREFIX}/book/{test_book.uid}")

    assert get_response.status_code == status.HTTP_200_OK
    assert isinstance(get_response.json(), list)
    assert len(get_response.json()) == 0


@pytest.mark.asyncio
async def test_delete_tag_from_book_unauthorized(
    async_client: AsyncClient, test_book: Book, test_tag: Tag, test_session: AsyncSession
):
    book_tag = BookTag(book_uid=test_book.uid, tag_uid=test_tag.uid)
    test_session.add(book_tag)
    await test_session.commit()

    response = await async_client.delete(f"{TAGS_PREFIX}/book/{test_book.uid}/tag/{test_tag.uid}")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.headers["WWW-Authenticate"] == "Bearer"
    assert response.json()["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_delete_tag_from_book_insufficient_permission(
    async_client: AsyncClient,
    test_book: Book,
    test_tag: Tag,
    other_user: User,
    other_user_access_token: str,
    test_session: AsyncSession,
):
    other_user.is_verified = True
    book_tag = BookTag(book_uid=test_book.uid, tag_uid=test_tag.uid)
    test_session.add(book_tag)
    await test_session.commit()

    headers = {"Authorization": f"Bearer {other_user_access_token}"}
    response = await async_client.delete(f"{TAGS_PREFIX}/book/{test_book.uid}/tag/{test_tag.uid}", headers=headers)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "You do not have enough permissions to perform this action"
    assert response.json()["error_code"] == "insufficient_permissions"
