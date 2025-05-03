from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str
    TOKEN_BEARER_URL: str
    BASE_URL: str
    ITSDANGEROUS_SECRET_KEY: str
    JWT_SECRET: str
    JWT_ALGORITHM: str
    REDIS_JTI_EXPIRY: int
    ACCESS_TOKEN_EXPIRY_MINS: int
    REFRESH_TOKEN_EXPIRY_DAYS: int
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_SERVER: str
    MAIL_PORT: int
    EMAIL_VERIFICATION_MAX_AGE: int
    USE_EMAIL: bool
    USE_REDIS: bool
    USE_CELERY: bool
    USE_SQLAlCHEMY_MONITOR: bool

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


Config = Settings()  # type: ignore


broker_url = Config.REDIS_URL
result_backend = Config.REDIS_URL
broker_connection_retry_on_startup = True
