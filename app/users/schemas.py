from datetime import datetime
from typing import Annotated, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.books.schemas import BookPublic
from app.reviews.schemas import ReviewPublic


class UserPublic(BaseModel):
    uid: UUID
    username: Annotated[str, Field(min_length=3, max_length=16)]
    email: EmailStr
    first_name: Annotated[str, Field(max_length=25)]
    last_name: Annotated[str, Field(max_length=25)]
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserBooks(UserPublic):
    books: list[BookPublic]
    reviews: list[ReviewPublic]


class UserCreate(BaseModel):
    username: Annotated[str, Field(min_length=3, max_length=16)]
    email: EmailStr
    password: Annotated[str, Field(min_length=8, max_length=32)]
    first_name: Annotated[str, Field(max_length=25, default="")]
    last_name: Annotated[str, Field(max_length=25, default="")]

    model_config = {
        "json_schema_extra": {
            "example": {
                "username": "johndoe",
                "email": "johndoe123@co.com",
                "password": "testpass123",
                "first_name": "John",
                "last_name": "Doe",
            }
        }
    }


class UserUpdate(BaseModel):
    username: Optional[Annotated[str, Field(min_length=3, max_length=16)]] = None
    email: Optional[EmailStr] = None
    first_name: Optional[Annotated[str, Field(min_length=3, max_length=25)]] = None
    last_name: Optional[Annotated[str, Field(min_length=3, max_length=25)]] = None
