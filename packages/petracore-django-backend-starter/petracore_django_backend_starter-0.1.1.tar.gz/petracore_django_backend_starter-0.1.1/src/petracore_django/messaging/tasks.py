# from celery import shared_task
from .base import NotificationDispatcher


# @shared_task(name="notifications.send_notification")
def send_notification(channel: str, message, recipients=None, subject=None):

    NotificationDispatcher.send(channel=channel, recipients=recipients, message=message, subject=subject)

