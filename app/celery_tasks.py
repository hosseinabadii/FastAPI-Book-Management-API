from asgiref.sync import async_to_sync
from celery import Celery
from fastapi import BackgroundTasks

from app import email_service
from app.config import Config

celery_app = Celery()

celery_app.config_from_object("app.config")


@celery_app.task()
def send_verification_email(user_email: str):
    async_to_sync(email_service.send_verification_email)(user_email)
    print("Verification email sent")


@celery_app.task()
def send_password_reset_email(user_email: str):
    async_to_sync(email_service.send_password_reset_email)(user_email)
    print("Password reset email sent!")


class EmailTaskService:
    def __init__(self, background_tasks: BackgroundTasks):
        self.background_tasks = background_tasks

    async def send_verification_email(self, user_email: str):
        if Config.USE_CELERY:
            send_verification_email.delay(user_email)
        else:
            self.background_tasks.add_task(email_service.send_verification_email, user_email)

    async def send_password_reset_email(self, user_email: str):
        if Config.USE_CELERY:
            send_password_reset_email.delay(user_email)
        else:
            self.background_tasks.add_task(email_service.send_password_reset_email, user_email)
