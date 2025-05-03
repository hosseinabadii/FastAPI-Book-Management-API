from datetime import date, datetime
from enum import StrEnum
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, SmallInteger, String, func
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Role(StrEnum):
    USER = "user"
    ADMIN = "admin"


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    uid: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    username: Mapped[str] = mapped_column(String(16), unique=True)
    email: Mapped[str] = mapped_column(String(40), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    first_name: Mapped[str] = mapped_column(String(25), nullable=True)
    last_name: Mapped[str] = mapped_column(String(25), nullable=True)
    role: Mapped[Role] = mapped_column(String(25), default=Role.USER)
    is_verified: Mapped[bool] = mapped_column(default=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    books: Mapped[list["Book"]] = relationship(back_populates="user")
    reviews: Mapped[list["Review"]] = relationship(back_populates="user")

    def __repr__(self):
        return f"<User {self.username}>"


class Book(Base):
    __tablename__ = "books"
    uid: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(String(255))
    author: Mapped[str] = mapped_column(String(100))
    publisher: Mapped[str] = mapped_column(String(100))
    language: Mapped[str] = mapped_column(String(10))  # ISO codes like 'en', 'fr', etc.
    published_date: Mapped[date]
    page_count: Mapped[int]
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())
    user_uid: Mapped[Optional[UUID]] = mapped_column(ForeignKey("users.uid"), nullable=True)

    user: Mapped[Optional[User]] = relationship(back_populates="books")
    reviews: Mapped[list["Review"]] = relationship(back_populates="book")
    tags: Mapped[list["Tag"]] = relationship(secondary="book_tags", back_populates="books")

    def __repr__(self):
        return f"<Book {self.title}>"


class Tag(Base):
    __tablename__ = "tags"
    uid: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    books: Mapped[list[Book]] = relationship(secondary="book_tags", back_populates="tags")

    def __repr__(self) -> str:
        return f"<Tag {self.name}>"


class BookTag(Base):
    __tablename__ = "book_tags"
    book_uid: Mapped[UUID] = mapped_column(ForeignKey("books.uid", ondelete="CASCADE"), primary_key=True)
    tag_uid: Mapped[UUID] = mapped_column(ForeignKey("tags.uid", ondelete="CASCADE"), primary_key=True)


class Review(Base):
    __tablename__ = "reviews"
    uid: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    rating: Mapped[int] = mapped_column(SmallInteger())
    review_text: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())
    user_uid: Mapped[Optional[UUID]] = mapped_column(ForeignKey("users.uid"), nullable=True)
    book_uid: Mapped[Optional[UUID]] = mapped_column(ForeignKey("books.uid"), nullable=True)

    user: Mapped[Optional[User]] = relationship(back_populates="reviews")
    book: Mapped[Optional[Book]] = relationship(back_populates="reviews")

    def __repr__(self):
        return f"<Review for book {self.book_uid} by user {self.user_uid}>"
