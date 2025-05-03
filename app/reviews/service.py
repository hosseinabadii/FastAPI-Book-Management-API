from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.books.service import BookService
from app.db.models import Review, Role, User
from app.errors import InsufficientPermission, ReviewNotFound
from app.users.service import UserService

from .schemas import ReviewCreate, ReviewUpdate

user_service = UserService()
book_service = BookService()


class ReviewService:
    async def _check_permission(self, review: Review, current_user: User) -> None:
        """Raise if the user is not the owner and not admin."""
        if review.user_uid != current_user.uid and current_user.role != Role.ADMIN:
            raise InsufficientPermission()

    async def add_review_to_book(
        self, book_uid: UUID, review_data: ReviewCreate, current_user: User, session: AsyncSession
    ):
        book = await book_service.get_book(book_uid=book_uid, session=session)
        review_data_dict = review_data.model_dump()
        new_review = Review(**review_data_dict, book=book, user=current_user)
        session.add(new_review)
        await session.commit()
        return new_review

    async def get_all_reviews(self, session: AsyncSession) -> Sequence[Review]:
        """Get all reviews ordered by creation date."""
        statement = select(Review).order_by(desc(Review.created_at))
        result = await session.execute(statement)
        return result.scalars().all()

    async def get_review(self, review_uid: UUID, session: AsyncSession) -> Review:
        """Get a specific review by its UID."""
        review = await session.get(Review, review_uid)
        if review is None:
            raise ReviewNotFound()
        return review

    async def update_review(
        self, review_uid: UUID, update_data: ReviewUpdate, current_user: User, session: AsyncSession
    ) -> Review:
        """Update a review."""
        review = await self.get_review(review_uid, session)
        await self._check_permission(review, current_user)

        update_data_dict = update_data.model_dump(exclude_none=True)
        for key, value in update_data_dict.items():
            setattr(review, key, value)
        await session.commit()
        await session.refresh(review)
        return review

    async def delete_review(self, review_uid: UUID, current_user: User, session: AsyncSession) -> None:
        """Delete a review from a book"""
        review = await self.get_review(review_uid, session)
        await self._check_permission(review, current_user)
        await session.delete(review)
        await session.commit()
