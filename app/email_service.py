from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import EmailStr

from app.auth.utils import create_url_safe_token
from app.config import Config
from app.users.service import UserService

user_service = UserService()

connection_config = ConnectionConfig(
    MAIL_USERNAME=Config.MAIL_USERNAME,
    MAIL_PASSWORD=Config.MAIL_PASSWORD,  # type: ignore
    MAIL_SERVER=Config.MAIL_SERVER,
    MAIL_PORT=Config.MAIL_PORT,
    MAIL_FROM="Bookly <bookly@example.com>",
    MAIL_FROM_NAME="Bookly App",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)


fast_mail = FastMail(config=connection_config)


async def send_email(recipients: list[EmailStr], subject: str, body: str):
    message = MessageSchema(recipients=recipients, subject=subject, body=body, subtype=MessageType.html)
    if Config.USE_EMAIL:
        await fast_mail.send_message(message=message)
    else:
        print(body)


async def send_verification_email(user_email: EmailStr) -> None:
    token = create_url_safe_token({"email": user_email})
    link = f"{Config.BASE_URL}/auth/verify/{token}"
    html = f"""
    <h1>Verify your Email</h1>
    <p>Please click this <a href="{link}">link</a> to verify your email</p>
    <p>This link will expire in 1 hour</p>
    """
    await send_email(recipients=[user_email], subject="Verify Your email", body=html)


async def send_password_reset_email(user_email: EmailStr) -> None:
    token = create_url_safe_token({"email": user_email})
    link = f"{Config.BASE_URL}/auth/password-reset-confirm/{token}"
    html = f"""
    <h1>Reset Your Password</h1>
    <p>Please click this <a href="{link}">link</a> to Reset Your Password</p>
    """
    await send_email(recipients=[user_email], subject="Reset Your Password", body=html)
