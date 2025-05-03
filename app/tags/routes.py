from uuid import UUID

from fastapi import APIRouter, status

from app.auth.dependencies import CurrentUserDep, SessionDep

from .schemas import TagAdd, TagPublic, TagUpdate
from .service import TagService

tags_router = APIRouter()
tag_service = TagService()


@tags_router.get("/{tag_uid}", response_model=TagPublic)
async def get_tag(tag_uid: UUID, session: SessionDep):
    return await tag_service.get_tag(tag_uid, session)


@tags_router.get("/book/{book_uid}", response_model=list[TagPublic])
async def get_tags_of_book(book_uid: UUID, session: SessionDep):
    return await tag_service.get_tags_of_book(book_uid, session)


@tags_router.post("/book/{book_uid}", response_model=list[TagPublic])
async def add_tags_to_book(book_uid: UUID, tag_data: TagAdd, current_user: CurrentUserDep, session: SessionDep):
    return await tag_service.add_tags_to_book(book_uid, tag_data, current_user, session)


@tags_router.put("/book/{book_uid}/tag/{tag_uid}", response_model=list[TagPublic])
async def update_tag_of_book(
    book_uid: UUID, tag_uid: UUID, tag_update_data: TagUpdate, current_user: CurrentUserDep, session: SessionDep
):
    return await tag_service.update_tag_of_book(book_uid, tag_uid, tag_update_data, current_user, session)


@tags_router.delete("/book/{book_uid}/tag/{tag_uid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag_from_book(book_uid: UUID, tag_uid: UUID, current_user: CurrentUserDep, session: SessionDep):
    return await tag_service.delete_tag_from_book(book_uid, tag_uid, current_user, session)
