import asyncio
from datetime import date
from uuid import uuid4

from app.auth.utils import hash_password
from app.db.main import async_session
from app.db.models import Book, BookTag, Review, Role, Tag, User


async def main() -> None:
    print("Populating database...")
    async with async_session() as session:
        admin = User(
            uid=uuid4(),
            username="admin",
            email="admin@test.com",
            password_hash=hash_password("test1234"),
            first_name="Admin",
            last_name="User",
            role=Role.ADMIN,
            is_verified=True,
        )

        user1 = User(
            uid=uuid4(),
            username="user1",
            email="user1@test.com",
            password_hash=hash_password("test1234"),
            first_name="John",
            last_name="Doe",
            is_verified=True,
        )

        user2 = User(
            uid=uuid4(),
            username="user2",
            email="user2@test.com",
            password_hash=hash_password("test1234"),
            first_name="Jane",
            last_name="Smith",
            is_verified=True,
        )

        session.add_all([admin, user1, user2])
        await session.flush()

        admin_books = [
            Book(
                uid=uuid4(),
                title="Admin's Guide to Everything",
                author="Admin User",
                publisher="Admin Publications",
                language="en",
                published_date=date(2020, 1, 15),
                page_count=300,
                user_uid=admin.uid,
            ),
            Book(
                uid=uuid4(),
                title="The Art of Administration",
                author="Admin User",
                publisher="Admin Publications",
                language="en",
                published_date=date(2021, 5, 20),
                page_count=250,
                user_uid=admin.uid,
            ),
            Book(
                uid=uuid4(),
                title="System Management 101",
                author="Admin User",
                publisher="Tech Books Inc.",
                language="en",
                published_date=date(2019, 11, 10),
                page_count=400,
                user_uid=admin.uid,
            ),
        ]

        user1_books = [
            Book(
                uid=uuid4(),
                title="The Mystery of Python",
                author="John Doe",
                publisher="Code Press",
                language="en",
                published_date=date(2022, 3, 5),
                page_count=350,
                user_uid=user1.uid,
            ),
            Book(
                uid=uuid4(),
                title="FastAPI for Beginners",
                author="John Doe",
                publisher="Web Books",
                language="en",
                published_date=date(2021, 7, 12),
                page_count=200,
                user_uid=user1.uid,
            ),
            Book(
                uid=uuid4(),
                title="SQLAlchemy Deep Dive",
                author="John Doe",
                publisher="Database Publishing",
                language="en",
                published_date=date(2020, 9, 8),
                page_count=450,
                user_uid=user1.uid,
            ),
        ]

        user2_books = [
            Book(
                uid=uuid4(),
                title="The Art of Fiction",
                author="Jane Smith",
                publisher="Literary Press",
                language="en",
                published_date=date(2018, 4, 22),
                page_count=320,
                user_uid=user2.uid,
            ),
            Book(
                uid=uuid4(),
                title="Creative Writing Handbook",
                author="Jane Smith",
                publisher="Writer's World",
                language="en",
                published_date=date(2020, 6, 18),
                page_count=280,
                user_uid=user2.uid,
            ),
            Book(
                uid=uuid4(),
                title="Poetry for Everyone",
                author="Jane Smith",
                publisher="Poetry House",
                language="en",
                published_date=date(2021, 2, 14),
                page_count=150,
                user_uid=user2.uid,
            ),
        ]

        all_books = admin_books + user1_books + user2_books
        session.add_all(all_books)
        await session.flush()

        tags = [
            Tag(uid=uuid4(), name="Fiction"),
            Tag(uid=uuid4(), name="Science Fiction"),
            Tag(uid=uuid4(), name="Fantasy"),
            Tag(uid=uuid4(), name="Mystery"),
            Tag(uid=uuid4(), name="Romance"),
            Tag(uid=uuid4(), name="Thriller"),
            Tag(uid=uuid4(), name="Biography"),
            Tag(uid=uuid4(), name="History"),
            Tag(uid=uuid4(), name="Self-Help"),
            Tag(uid=uuid4(), name="Technology"),
        ]
        session.add_all(tags)
        await session.flush()  # Ensure tag IDs are available

        # Assign tags to books (each book gets 3 random tags)
        for book in all_books:
            # Get 3 random tags (in a real app, you might want to use a better selection method)
            selected_tags = tags[:3]  # Just taking first 3 for simplicity
            for tag in selected_tags:
                session.add(BookTag(book_uid=book.uid, tag_uid=tag.uid))

        reviews = []

        # Reviews for admin's books
        reviews.extend(
            [
                Review(
                    uid=uuid4(),
                    rating=5,
                    review_text="Excellent guide for admins!",
                    user_uid=user1.uid,
                    book_uid=admin_books[0].uid,
                ),
                Review(
                    uid=uuid4(),
                    rating=4,
                    review_text="Very helpful, but could use more examples.",
                    user_uid=user2.uid,
                    book_uid=admin_books[0].uid,
                ),
                Review(
                    uid=uuid4(),
                    rating=5,
                    review_text="The best book on administration I've read!",
                    user_uid=admin.uid,
                    book_uid=admin_books[1].uid,
                ),
                Review(
                    uid=uuid4(),
                    rating=3,
                    review_text="Good content but the writing style is a bit dry.",
                    user_uid=user1.uid,
                    book_uid=admin_books[1].uid,
                ),
                Review(
                    uid=uuid4(),
                    rating=4,
                    review_text="Comprehensive coverage of system management.",
                    user_uid=user2.uid,
                    book_uid=admin_books[2].uid,
                ),
            ]
        )

        # Reviews for user1's books
        reviews.extend(
            [
                Review(
                    uid=uuid4(),
                    rating=5,
                    review_text="Great introduction to Python mysteries!",
                    user_uid=admin.uid,
                    book_uid=user1_books[0].uid,
                ),
                Review(
                    uid=uuid4(),
                    rating=4,
                    review_text="Well written and informative.",
                    user_uid=user2.uid,
                    book_uid=user1_books[0].uid,
                ),
                Review(
                    uid=uuid4(),
                    rating=5,
                    review_text="Perfect for FastAPI beginners!",
                    user_uid=admin.uid,
                    book_uid=user1_books[1].uid,
                ),
                Review(
                    uid=uuid4(),
                    rating=3,
                    review_text="Good but some topics could be explained better.",
                    user_uid=user2.uid,
                    book_uid=user1_books[1].uid,
                ),
                Review(
                    uid=uuid4(),
                    rating=5,
                    review_text="The SQLAlchemy book I've been waiting for!",
                    user_uid=admin.uid,
                    book_uid=user1_books[2].uid,
                ),
            ]
        )

        # Reviews for user2's books
        reviews.extend(
            [
                Review(
                    uid=uuid4(),
                    rating=4,
                    review_text="Insightful look at fiction writing.",
                    user_uid=admin.uid,
                    book_uid=user2_books[0].uid,
                ),
                Review(
                    uid=uuid4(),
                    rating=5,
                    review_text="Changed my perspective on creative writing!",
                    user_uid=user1.uid,
                    book_uid=user2_books[0].uid,
                ),
                Review(
                    uid=uuid4(),
                    rating=5,
                    review_text="Excellent handbook for writers.",
                    user_uid=admin.uid,
                    book_uid=user2_books[1].uid,
                ),
                Review(
                    uid=uuid4(),
                    rating=4,
                    review_text="Very practical advice for creative writers.",
                    user_uid=user1.uid,
                    book_uid=user2_books[1].uid,
                ),
                Review(
                    uid=uuid4(),
                    rating=5,
                    review_text="Made me love poetry!",
                    user_uid=admin.uid,
                    book_uid=user2_books[2].uid,
                ),
                Review(
                    uid=uuid4(),
                    rating=4,
                    review_text="Great introduction to poetry for beginners.",
                    user_uid=user1.uid,
                    book_uid=user2_books[2].uid,
                ),
            ]
        )

        session.add_all(reviews)
        await session.commit()
        print("Successfully Done!")


if __name__ == "__main__":
    asyncio.run(main())
