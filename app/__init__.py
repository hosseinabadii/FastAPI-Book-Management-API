from fastapi import FastAPI

from app.auth.routes import auth_router
from app.books.routes import book_router
from app.reviews.routes import review_router
from app.tags.routes import tags_router
from app.users.routes import user_router

from .errors import register_all_errors
from .lifespan import lifespan
from .middleware import register_middleware

version = "v1"

description = """
A REST API for a book review web service.

This REST API is able to;
- Create Read Update And delete books
- Add reviews to books
- Add tags to Books e.t.c.
    """

version_prefix = f"/api/{version}"

app = FastAPI(
    title="Bookly",
    description=description,
    version=version,
    license_info={"name": "MIT License", "url": "https://opensource.org/license/mit"},
    contact={
        "name": "Ssali Jonathan",
        "url": "https://github.com/jod35",
        "email": "ssalijonathank@gmail.com",
    },
    terms_of_service="httpS://example.com/tos",
    openapi_url=f"{version_prefix}/openapi.json",
    docs_url=f"{version_prefix}/docs",
    redoc_url=f"{version_prefix}/redoc",
    lifespan=lifespan,
)

register_all_errors(app)
register_middleware(app)
app.include_router(auth_router, prefix=f"{version_prefix}/auth", tags=["Authentication"])
app.include_router(user_router, prefix=f"{version_prefix}/users", tags=["Users"])
app.include_router(book_router, prefix=f"{version_prefix}/books", tags=["Books"])
app.include_router(review_router, prefix=f"{version_prefix}/reviews", tags=["Reviews"])
app.include_router(tags_router, prefix=f"{version_prefix}/tags", tags=["Tags"])
