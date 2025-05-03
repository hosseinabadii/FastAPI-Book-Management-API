from datetime import datetime
from typing import Annotated, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ReviewPublic(BaseModel):
    uid: UUID
    rating: Annotated[int, Field(ge=0, le=5)]
    review_text: Annotated[str, Field(min_length=1, max_length=255)]
    user_uid: Optional[UUID]
    book_uid: Optional[UUID]
    created_at: datetime
    updated_at: datetime


class ReviewCreate(BaseModel):
    rating: Annotated[int, Field(ge=0, le=5)]
    review_text: str


class ReviewUpdate(BaseModel):
    rating: Optional[Annotated[int, Field(ge=0, le=5)]] = None
    review_text: Optional[str] = None
