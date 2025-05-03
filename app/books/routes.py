from uuid import UUID

from fastapi import APIRouter, status

from app.auth.dependencies import CurrentUserDep
from app.db.main import SessionDep

from .schemas import BookCreate, BookDetail, BookPublic, BookUpdate
from .service import BookService

book_router = APIRouter()
book_service = BookService()


@book_router.post("/", response_model=BookPublic, status_code=status.HTTP_201_CREATED)
async def create_book(book_data: BookCreate, user: CurrentUserDep, session: SessionDep):
    return await book_service.create_book(book_data, user.uid, session)


@book_router.get("/", response_model=list[BookPublic])
async def get_all_books(session: SessionDep):
    return await book_service.get_all_books(session)


@book_router.get("/{book_uid}", response_model=BookDetail)
async def get_book_detail(book_uid: UUID, session: SessionDep):
    return await book_service.get_book_detail(book_uid, session)


@book_router.put("/{book_uid}", response_model=BookPublic)
async def update_book(book_uid: UUID, book_update_data: BookUpdate, user: CurrentUserDep, session: SessionDep):
    return await book_service.update_book(book_uid, book_update_data, user, session)


@book_router.delete("/{book_uid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_uid: UUID, user: CurrentUserDep, session: SessionDep):
    return await book_service.delete_book(book_uid, user, session)


@book_router.get("/user/{user_uid}/", response_model=list[BookPublic])
async def get_user_book_submissions(user_uid: UUID, session: SessionDep):
    return await book_service.get_user_books(user_uid, session)
