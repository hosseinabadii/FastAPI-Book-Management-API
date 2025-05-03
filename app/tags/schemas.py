from datetime import datetime
from typing import Annotated, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class TagPublic(BaseModel):
    uid: UUID
    name: Annotated[str, Field(min_length=1, max_length=100)]
    created_at: datetime


class TagCreate(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=100)]


class TagUpdate(BaseModel):
    name: Optional[Annotated[str, Field(min_length=1, max_length=100)]] = None


class TagAdd(BaseModel):
    tags: list[TagCreate]
