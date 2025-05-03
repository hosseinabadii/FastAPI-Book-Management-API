from typing import Any, Callable

from fastapi import FastAPI, status
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError


class BooklyException(Exception):
    """This is the base class for all bookly errors"""


class InvalidToken(BooklyException):
    """User has provided an invalid or expired token"""


class RevokedToken(BooklyException):
    """User has provided a token that has been revoked"""


class AccessTokenRequired(BooklyException):
    """User has provided a refresh token when an access token is needed"""


class RefreshTokenRequired(BooklyException):
    """User has provided an access token when a refresh token is needed"""


class EmailAlreadyExists(BooklyException):
    """User has provided an email that already exists during sign up."""


class UsernameAlreadyExists(BooklyException):
    """User has provided a username that already exists during sign up."""


class InvalidCredentials(BooklyException):
    """User has provided wrong email or password during log in."""


class InsufficientPermission(BooklyException):
    """User does not have the neccessary permissions to perform an action."""


class BookNotFound(BooklyException):
    """Book Not found"""


class ReviewNotFound(BooklyException):
    """Review Not found"""


class TagNotFound(BooklyException):
    """Tag Not found"""


class TagAlreadyExists(BooklyException):
    """Tag already exists"""


class UserNotFound(BooklyException):
    """User Not found"""


class AccountNotVerified(Exception):
    """Account not yet verified"""


class AccountNotActive(Exception):
    """Account not yet active"""


class InvalidVerificationToken(Exception):
    """Invalid verification token"""


class PasswordsDoNotMatch(Exception):
    """Passwords do not match"""


def create_exception_handler(status_code: int, content: Any, headers: dict | None = None) -> Callable:
    async def exception_handler(request: Request, exc: BooklyException):
        return JSONResponse(content=content, status_code=status_code, headers=headers)

    return exception_handler


def register_all_errors(app: FastAPI):
    app.add_exception_handler(
        InvalidVerificationToken,
        create_exception_handler(
            content={
                "detail": "Invalid verification token",
                "error_code": "invalid_token",
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        ),
    )

    app.add_exception_handler(
        PasswordsDoNotMatch,
        create_exception_handler(
            content={
                "detail": "Passwords do not match",
                "error_code": "passwords_do_not_match",
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        ),
    )

    app.add_exception_handler(
        InvalidCredentials,
        create_exception_handler(
            content={
                "detail": "Invalid email or password",
                "error_code": "invalid_email_or_password",
            },
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers={"WWW-Authenticate": "Bearer"},
        ),
    )

    app.add_exception_handler(
        InvalidToken,
        create_exception_handler(
            content={
                "detail": "Token is invalid or expired",
                "resolution": "Please get new token",
                "error_code": "invalid_token",
            },
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers={"WWW-Authenticate": "Bearer"},
        ),
    )

    app.add_exception_handler(
        RevokedToken,
        create_exception_handler(
            content={
                "detail": "Token is invalid or has been revoked",
                "resolution": "Please get new token",
                "error_code": "token_revoked",
            },
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers={"WWW-Authenticate": "Bearer"},
        ),
    )

    app.add_exception_handler(
        AccessTokenRequired,
        create_exception_handler(
            content={
                "detail": "Please provide a valid access token",
                "resolution": "Please get an access token",
                "error_code": "access_token_required",
            },
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers={"WWW-Authenticate": "Bearer"},
        ),
    )

    app.add_exception_handler(
        RefreshTokenRequired,
        create_exception_handler(
            content={
                "detail": "Please provide a valid refresh token",
                "resolution": "Please get an refresh token",
                "error_code": "refresh_token_required",
            },
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers={"WWW-Authenticate": "Bearer"},
        ),
    )

    app.add_exception_handler(
        InsufficientPermission,
        create_exception_handler(
            content={
                "detail": "You do not have enough permissions to perform this action",
                "error_code": "insufficient_permissions",
            },
            status_code=status.HTTP_403_FORBIDDEN,
        ),
    )

    app.add_exception_handler(
        EmailAlreadyExists,
        create_exception_handler(
            content={
                "detail": "User with email already exists",
                "error_code": "email_exists",
            },
            status_code=status.HTTP_403_FORBIDDEN,
        ),
    )

    app.add_exception_handler(
        UsernameAlreadyExists,
        create_exception_handler(
            content={
                "detail": "User with username already exists",
                "error_code": "username_exists",
            },
            status_code=status.HTTP_403_FORBIDDEN,
        ),
    )

    app.add_exception_handler(
        TagAlreadyExists,
        create_exception_handler(
            content={
                "detail": "Tag already exists",
                "error_code": "tag_exists",
            },
            status_code=status.HTTP_403_FORBIDDEN,
        ),
    )

    app.add_exception_handler(
        AccountNotActive,
        create_exception_handler(
            content={
                "detail": "Account not active",
                "error_code": "account_not_active",
                "resolution": "Please contact the administrator to resolve this issue.",
            },
            status_code=status.HTTP_403_FORBIDDEN,
        ),
    )

    app.add_exception_handler(
        AccountNotVerified,
        create_exception_handler(
            content={
                "detail": "Account not verified",
                "error_code": "account_not_verified",
                "resolution": "Please check your email for verification details",
            },
            status_code=status.HTTP_403_FORBIDDEN,
        ),
    )

    app.add_exception_handler(
        UserNotFound,
        create_exception_handler(
            content={
                "detail": "User not found",
                "error_code": "user_not_found",
            },
            status_code=status.HTTP_404_NOT_FOUND,
        ),
    )

    app.add_exception_handler(
        BookNotFound,
        create_exception_handler(
            content={
                "detail": "Book not found",
                "error_code": "book_not_found",
            },
            status_code=status.HTTP_404_NOT_FOUND,
        ),
    )

    app.add_exception_handler(
        ReviewNotFound,
        create_exception_handler(
            content={
                "detail": "Review not found",
                "error_code": "review_not_found",
            },
            status_code=status.HTTP_404_NOT_FOUND,
        ),
    )

    app.add_exception_handler(
        TagNotFound,
        create_exception_handler(
            content={
                "detail": "Tag not found",
                "error_code": "tag_not_found",
            },
            status_code=status.HTTP_404_NOT_FOUND,
        ),
    )

    @app.exception_handler(500)
    async def internal_server_error(request, exc):
        return JSONResponse(
            content={
                "detail": "Oops! Something went wrong",
                "error_code": "server_error",
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    @app.exception_handler(SQLAlchemyError)
    async def database__error(request, exc):
        print(str(exc))
        return JSONResponse(
            content={
                "detail": "Oops! Something went wrong",
                "error_code": "server_error",
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
