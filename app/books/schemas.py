from datetime import date, datetime
from typing import Annotated, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.reviews.schemas import ReviewPublic
from app.tags.schemas import TagPublic


class BookPublic(BaseModel):
    uid: UUID
    title: Annotated[str, Field(min_length=1, max_length=200)]
    author: Annotated[str, Field(min_length=1, max_length=100)]
    publisher: Annotated[str, Field(min_length=1, max_length=100)]
    page_count: Annotated[int, Field(gt=0)]
    language: Annotated[str, Field(min_length=2, max_length=10)]
    published_date: date
    created_at: datetime
    updated_at: datetime
    user_uid: Optional[UUID] = None


class BookDetail(BookPublic):
    reviews: list[ReviewPublic]
    tags: list[TagPublic]


class BookCreate(BaseModel):
    title: Annotated[str, Field(min_length=1, max_length=200)]
    author: Annotated[str, Field(min_length=1, max_length=100)]
    publisher: Annotated[str, Field(min_length=1, max_length=100)]
    page_count: Annotated[int, Field(gt=0)]
    language: Annotated[str, Field(min_length=2, max_length=10)]
    published_date: date

    @field_validator("published_date")
    @classmethod
    def validate_published_date(cls, v: date) -> date:
        if v > date.today():
            raise ValueError("Published date cannot be in the future")
        return v


class BookUpdate(BaseModel):
    title: Optional[Annotated[str, Field(min_length=1, max_length=200)]] = None
    author: Optional[Annotated[str, Field(min_length=1, max_length=100)]] = None
    publisher: Optional[Annotated[str, Field(min_length=1, max_length=100)]] = None
    page_count: Optional[Annotated[int, Field(gt=0)]] = None
    language: Optional[Annotated[str, Field(min_length=2, max_length=10)]] = None
