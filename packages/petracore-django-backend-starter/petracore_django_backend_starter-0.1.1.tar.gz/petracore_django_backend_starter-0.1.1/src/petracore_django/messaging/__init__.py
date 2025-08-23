"""
@Author: Maro Okegbero
"""
from .tasks import send_notification


class MessagingService:
    @classmethod
    def send_email(cls, recipients: list, subject: str, message: str):
        """
        sends an email to a list of recipients
        """
        send_notification(channel="email", recipients=recipients, message=message, subject=subject)

    @classmethod
    def send_text(cls, recipients: list, message: str):
        """
        sends text to a list of recipients
        """
        send_notification(channel="sms", recipients=recipients, message=message)

    @classmethod
    def send_push(cls, recipients, message: str, **kwargs):
        """
        send push notifications to a list of recipients
        """
        send_notification(channel="push", recipients=recipients, message=message)
