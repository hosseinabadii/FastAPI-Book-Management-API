from uuid import UUID

from fastapi import APIRouter, status

from app.auth.dependencies import CurrentUserDep
from app.db.main import SessionDep

from .schemas import ReviewCreate, ReviewPublic, ReviewUpdate
from .service import ReviewService

review_router = APIRouter()
review_service = ReviewService()


@review_router.get("/", response_model=list[ReviewPublic])
async def get_all_reviews(session: SessionDep):
    return await review_service.get_all_reviews(session)


@review_router.get("/{review_uid}", response_model=ReviewPublic)
async def get_review(review_uid: UUID, session: SessionDep):
    return await review_service.get_review(review_uid, session)


@review_router.post("/book/{book_uid}", response_model=ReviewPublic, status_code=status.HTTP_201_CREATED)
async def add_review_to_book(
    book_uid: UUID, review_data: ReviewCreate, current_user: CurrentUserDep, session: SessionDep
):
    return await review_service.add_review_to_book(book_uid, review_data, current_user, session)


@review_router.put("/{review_uid}", response_model=ReviewPublic)
async def update_review(
    review_uid: UUID, review_update_data: ReviewUpdate, current_user: CurrentUserDep, session: SessionDep
):
    return await review_service.update_review(review_uid, review_update_data, current_user, session)


@review_router.delete("/{review_uid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(review_uid: UUID, current_user: CurrentUserDep, session: SessionDep):
    return await review_service.delete_review(review_uid, current_user, session)
