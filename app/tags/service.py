from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.books.service import BookService
from app.db.models import Book, Role, Tag, User
from app.errors import InsufficientPermission, TagNotFound

from .schemas import TagAdd, TagUpdate

book_service = BookService()


class TagService:
    async def _check_permission(self, book: Book, current_user: User) -> None:
        """Raise if the user is not the owner and not admin."""
        if book.user_uid != current_user.uid and current_user.role != Role.ADMIN:
            raise InsufficientPermission()

    async def get_tags_of_book(self, book_uid: UUID, session: AsyncSession) -> list[Tag]:
        """Get all tags of a specific book"""
        db_book = await book_service.get_book_with_tags(book_uid=book_uid, session=session)
        return db_book.tags

    async def get_tag(self, tag_uid: UUID, session: AsyncSession) -> Tag:
        """Get a specific tag by its UID."""
        tag = await session.get(Tag, tag_uid)
        if tag is None:
            raise TagNotFound()
        return tag

    async def add_tags_to_book(
        self, book_uid: UUID, tags_data: TagAdd, current_user: User, session: AsyncSession
    ) -> list[Tag]:
        """Add tags to a book"""
        db_book = await book_service.get_book_with_tags(book_uid=book_uid, session=session)
        await self._check_permission(db_book, current_user)
        for tag_item in tags_data.tags:
            result = await session.execute(select(Tag).where(Tag.name == tag_item.name))
            tag = result.scalar_one_or_none()
            if tag is None:
                tag = Tag(**tag_item.model_dump())
                db_book.tags.append(tag)
            elif tag not in db_book.tags:
                db_book.tags.append(tag)
        session.add(db_book)
        await session.commit()
        return db_book.tags

    async def update_tag_of_book(
        self, book_uid: UUID, tag_uid: UUID, tag_update_data: TagUpdate, current_user: User, session: AsyncSession
    ) -> list[Tag]:
        """Update a tag of a book"""
        db_tag = await self.get_tag(tag_uid, session)
        db_book = await book_service.get_book_with_tags(book_uid=book_uid, session=session)
        if db_tag not in db_book.tags:
            raise TagNotFound
        await self._check_permission(db_book, current_user)

        result = await session.execute(select(Tag).where(Tag.name == tag_update_data.name))
        tag = result.scalar_one_or_none()
        if tag and tag in db_book.tags:
            return db_book.tags

        if tag is None:
            tag = Tag(**tag_update_data.model_dump())
        db_book.tags.remove(db_tag)
        db_book.tags.append(tag)
        await session.commit()
        return db_book.tags

    async def delete_tag_from_book(self, book_uid: UUID, tag_uid: UUID, current_user: User, session: AsyncSession):
        """Delete a tag"""
        db_tag = await self.get_tag(tag_uid, session)
        db_book = await book_service.get_book_with_tags(book_uid=book_uid, session=session)
        await self._check_permission(db_book, current_user)
        if db_tag not in db_book.tags:
            raise TagNotFound
        db_book.tags.remove(db_tag)
        await session.commit()
