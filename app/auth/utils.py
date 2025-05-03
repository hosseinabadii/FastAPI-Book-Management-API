import uuid
from datetime import UTC, datetime, timedelta

import bcrypt
import jwt
from itsdangerous import URLSafeTimedSerializer
from loguru import logger

from app.config import Config

from .schemas import TokenData


def hash_password(password: str) -> str:
    pwd_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt)
    return hashed_password.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    plain_password_byte_enc = plain_password.encode("utf-8")
    hash_password_byte_enc = hashed_password.encode("utf-8")
    return bcrypt.checkpw(password=plain_password_byte_enc, hashed_password=hash_password_byte_enc)


def create_jwt_token(user_data: dict, refresh: bool = False) -> str:
    if refresh:
        expiry = timedelta(days=Config.REFRESH_TOKEN_EXPIRY_DAYS)
    else:
        expiry = timedelta(minutes=Config.ACCESS_TOKEN_EXPIRY_MINS)

    payload = {
        "user": user_data,
        "exp": datetime.now(tz=UTC) + expiry,
        "jti": str(uuid.uuid4()),
        "refresh": refresh,
    }
    token = jwt.encode(payload=payload, key=Config.JWT_SECRET, algorithm=Config.JWT_ALGORITHM)
    return token


def decode_token(token: str) -> TokenData | None:
    try:
        token_data = jwt.decode(jwt=token, key=Config.JWT_SECRET, algorithms=[Config.JWT_ALGORITHM])
        return TokenData(**token_data)
    except jwt.PyJWTError as e:
        logger.error(e)
        return None


serializer = URLSafeTimedSerializer(secret_key=Config.ITSDANGEROUS_SECRET_KEY, salt="email-configuration")


def create_url_safe_token(data: dict[str, str]) -> str:
    token = serializer.dumps(data)
    return token


def decode_url_safe_token(token: str) -> dict[str, str] | None:
    try:
        token_data = serializer.loads(token, max_age=Config.EMAIL_VERIFICATION_MAX_AGE)
        return token_data
    except Exception as e:
        logger.error(e)
        return None
