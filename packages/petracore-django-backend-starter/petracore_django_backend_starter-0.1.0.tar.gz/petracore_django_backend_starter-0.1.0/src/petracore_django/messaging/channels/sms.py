# """
# notifications/sms.py
#
# @Author:    Maro Okegbero
# @Date:      Nov 3, 2023
# @Time:      0:53 PM
# """
# import africastalking
# import phonenumbers
# from unidecode import unidecode
#
# from notifications.channels.base import AbstractNotificationService
#
#
# class SMS(AbstractNotificationService):
#     """ Integration of Africastalking SMS API's """
#
#     def __init__(self,settings,  username=None, api_key=None, sender_id=None):
#
#         self.username = str(username) if username is not None else settings.AFT_USERNAME
#         self.api_key = str(api_key) if api_key is not None else settings.AFT_API_KEY
#         self.sender_id = str(sender_id) if sender_id is not None else settings.AFT_SENDER_ID
#         africastalking.initialize(self.username, self.api_key)
#         self.sms = africastalking.SMS
#
#     def send(self, message, recipients=None, **kwargs):
#         """
#         Send sms to recipient phone numbers.
#         """
#
#         if recipients is None:
#             recipients = []
#         recipients = [phonenumbers.format_number(phonenumbers.parse(arg, "NG"), phonenumbers.PhoneNumberFormat.E164) for arg
#                       in recipients]
#         message = unidecode(bytes(str(message).encode()).decode("utf-8"))
#
#         resp = self.sms.send(message=message, recipients=recipients, sender_id=self.sender_id)
#
#         data = resp.get("SMSMessageData", {})
#         comment = data.get("Message")
#         recipients = data.get("Recipients")
#
#         recipient = recipients[0] if len(recipients) > 0 else {}
#
#         status = recipient.get("status", "Failed")
#         number = recipient.get("number", "-1")
#         message_id = recipient.get("messageId", "-1")
#         cost = recipient.get("cost", "0")
#
#         return dict(status=status, phone=number, message_id=message_id, message=comment, cost=cost)
#
