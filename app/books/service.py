from collections.abc import Sequence
from typing import Optional
from uuid import UUID

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.db.models import Book, Role, User
from app.errors import BookNotFound, InsufficientPermission

from .schemas import BookCreate, BookUpdate


class BookService:
    async def _check_permission(self, book: Book, user: User) -> None:
        """Raise if the user is not the owner and not admin."""
        if book.user_uid != user.uid and user.role != Role.ADMIN:
            raise InsufficientPermission()

    async def create_book(self, book_data: BookCreate, user_uid: Optional[UUID], session: AsyncSession) -> Book:
        """Create a new book."""
        book_data_dict = book_data.model_dump()
        new_book = Book(**book_data_dict, user_uid=user_uid)
        session.add(new_book)
        await session.commit()
        return new_book

    async def get_all_books(self, session: AsyncSession) -> Sequence[Book]:
        """Get all books ordered by creation date."""
        statement = select(Book).order_by(desc(Book.created_at))
        result = await session.execute(statement)
        return result.scalars().all()

    async def get_book(self, book_uid: UUID, session: AsyncSession) -> Book:
        """Get a specific book by its UID."""
        book = await session.get(Book, book_uid)
        if book is None:
            raise BookNotFound()
        return book

    async def get_book_detail(self, book_uid: UUID, session: AsyncSession) -> Book:
        """Get a specific book with details by its UID."""
        statement = select(Book).where(Book.uid == book_uid).options(joinedload(Book.reviews), joinedload(Book.tags))
        result = await session.execute(statement)
        book = result.unique().scalar_one_or_none()
        if book is None:
            raise BookNotFound()
        return book

    async def get_book_with_tags(self, book_uid: UUID, session: AsyncSession) -> Book:
        """Get a specific book with details by its UID."""
        statement = select(Book).where(Book.uid == book_uid).options(joinedload(Book.tags))
        result = await session.execute(statement)
        book = result.unique().scalar_one_or_none()
        if book is None:
            raise BookNotFound()
        return book

    async def update_book(self, book_uid: UUID, update_data: BookUpdate, user: User, session: AsyncSession) -> Book:
        """Update an existing book."""
        db_book = await self.get_book(book_uid, session)
        await self._check_permission(db_book, user)
        update_data_dict = update_data.model_dump(exclude_none=True)
        for key, value in update_data_dict.items():
            setattr(db_book, key, value)
        await session.commit()
        await session.refresh(db_book)
        return db_book

    async def delete_book(self, book_uid: UUID, user: User, session: AsyncSession) -> None:
        """Delete a book."""
        db_book = await self.get_book(book_uid, session)
        await self._check_permission(db_book, user)
        await session.delete(db_book)
        await session.commit()

    async def get_user_books(self, user_uid: UUID, session: AsyncSession) -> Sequence[Book]:
        """Get all books submitted by a specific user."""
        statement = select(Book).where(Book.user_uid == user_uid).order_by(desc(Book.created_at))
        result = await session.execute(statement)
        return result.scalars().all()
