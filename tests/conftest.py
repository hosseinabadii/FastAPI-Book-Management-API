from collections.abc import AsyncGenerator
from datetime import date

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import StaticPool
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from app import app
from app.auth.utils import create_jwt_token, create_url_safe_token, hash_password
from app.db.main import get_session
from app.db.models import Base, Book, Review, Role, Tag, User

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def test_engine() -> AsyncGenerator[AsyncEngine, None]:
    engine = create_async_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        yield engine
    finally:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await engine.dispose()


@pytest_asyncio.fixture
async def test_session(test_engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    async_session = async_sessionmaker(test_engine, expire_on_commit=False)
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def override_get_session(test_session: AsyncSession) -> AsyncGenerator[None, None]:
    async def _override_get_session() -> AsyncGenerator[AsyncSession, None]:
        yield test_session

    app.dependency_overrides[get_session] = _override_get_session
    yield
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def async_client(override_get_session) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client


@pytest.fixture
def mock_email_service(monkeypatch: pytest.MonkeyPatch):
    """Mock the email service functions."""

    async def mock_send_verification_email(*args, **kwargs):
        return None

    async def mock_send_password_reset_email(*args, **kwargs):
        return None

    monkeypatch.setattr("app.email_service.send_verification_email", mock_send_verification_email)
    monkeypatch.setattr("app.email_service.send_password_reset_email", mock_send_password_reset_email)
    return mock_send_verification_email, mock_send_password_reset_email


# @pytest.fixture
# def user_service() -> UserService:
#     return UserService()


# @pytest.fixture
# def book_service() -> BookService:
#     return BookService()


@pytest_asyncio.fixture
async def admin_user(test_session: AsyncSession) -> User:
    user_data = {
        "email": "admin@example.com",
        "username": "adminuser",
        "password_hash": hash_password("adminpass123"),
        "first_name": "Admin",
        "last_name": "User",
        "role": Role.ADMIN,
        "is_verified": True,
    }
    user = User(**user_data)
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_user(test_session: AsyncSession) -> User:
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password_hash": hash_password("testpassword123"),
        "first_name": "Test",
        "last_name": "User",
    }
    user = User(**user_data)
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def other_user(test_session: AsyncSession) -> User:
    user_data = {
        "email": "other@example.com",
        "username": "otheruser",
        "password_hash": hash_password("otherpassword123"),
        "first_name": "Other",
        "last_name": "User",
    }
    user = User(**user_data)
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)
    return user


@pytest.fixture
def admin_user_access_token(admin_user: User):
    return create_jwt_token({"email": admin_user.email, "uid": str(admin_user.uid), "role": admin_user.role})


@pytest.fixture
def test_user_access_token(test_user: User):
    return create_jwt_token({"email": test_user.email, "uid": str(test_user.uid), "role": test_user.role})


@pytest.fixture
def other_user_access_token(other_user: User):
    return create_jwt_token({"email": other_user.email, "uid": str(other_user.uid), "role": other_user.role})


@pytest.fixture
def url_safe_token(test_user: User):
    return create_url_safe_token({"email": test_user.email})


@pytest_asyncio.fixture
async def test_book(test_session: AsyncSession, test_user: User) -> Book:
    book_data = {
        "title": "Test Book",
        "author": "Test Author",
        "publisher": "Test Publisher",
        "page_count": 200,
        "language": "en",
        "published_date": date(2025, 1, 1),
        "user_uid": test_user.uid,
    }
    book = Book(**book_data)
    test_session.add(book)
    await test_session.commit()
    await test_session.refresh(book)
    return book


@pytest_asyncio.fixture
async def test_review(test_session: AsyncSession, test_book: Book, test_user: User) -> Review:
    review_data = {
        "rating": 4,
        "review_text": "Great book!",
        "book_uid": test_book.uid,
        "user_uid": test_user.uid,
    }
    review = Review(**review_data)
    test_session.add(review)
    await test_session.commit()
    await test_session.refresh(review)
    return review


@pytest_asyncio.fixture
async def test_tag(test_session: AsyncSession) -> Tag:
    tag_data = {"name": "Test Tag"}
    tag = Tag(**tag_data)
    test_session.add(tag)
    await test_session.commit()
    await test_session.refresh(tag)
    return tag
