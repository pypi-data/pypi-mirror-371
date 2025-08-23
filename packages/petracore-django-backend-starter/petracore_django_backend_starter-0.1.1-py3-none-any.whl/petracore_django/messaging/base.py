"""
notifications/base.py

@Author:    Maro Okegbero
@Date:      Nov 3, 2023
@Time: 0:53 AM
"""


from pprint import pprint
from .channels.email.resend import Resend
# from .channels.sms import SMS

def _get_settings():
    from django.conf import settings as dj_settings
    return dj_settings

class NotificationDispatcher:

    @classmethod
    def get_service(cls, channel):
        """
        return the right notification channel
        """
        s = _get_settings()
        # sms = SMS(settings=s)
        email = Resend(settings=s)
        push = getattr(s, "FIREBASE_INSTANCE", None)
        # service_dict = {"sms": sms, "email": email, "push": push}
        service_dict = {"email": email}

        return service_dict.get(channel.lower())

    @classmethod
    def send(cls, channel, message, recipients, **kwargs):

        try:
            service = cls.get_service(channel)
            res = service.send(message=message, recipients=recipients, **kwargs)
            pprint(res)
        except Exception as e:
            # Log any exceptions that occur during thread execution
            print(e, "The Exception .............................")
