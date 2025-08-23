# """
# notifications/push.py
#
# @Author:    Maro Okegbero
# @Date:      Nov 3, 2023
# @Time:      0:53 PM
# """
# from notifications.channels.base import AbstractNotificationService
#
# import firebase_admin
# from firebase_admin import messaging, credentials
# import json
#
#
# def initialize_push(cred):
#     """
#
#     :param cred:
#     :return:
#     """
#     credential = credentials.Certificate(cred)
#     fbase = firebase_admin.initialize_app(credential=credential)
#     return fbase
#
#
# class FireBasePush(AbstractNotificationService):
#     """
#     Local implementation of the fire base sdk for sending cloud messages to
#     various devices
#     """
#
#     def __init__(self, cred):
#         """the init method"""
#
#         self.firebase = initialize_push(cred)
#
#     @classmethod
#     def send(cls, data, store_ids=None):
#         """
#
#         :param data: the information to form the title and body of the notification (dict)
#         :param store_ids: the device ids to receive the notification (dict: eg - {'android':'<key>'})
#         :return:
#         """
#         # if not store_ids:
#         #     return None
#
#         # check if notification is for a group
#         if data.get('target') == "group":
#             message = messaging.Message(
#                 data=data,
#                 topic=data.get('topic')
#             )
#             return messaging.send(message)
#
#         push_type = data.get("push_type", None)
#         push_type = push_type if push_type else "mobile"
#         for client, token in store_ids.items():
#
#             try:
#                 if push_type != "mobile":
#                     return cls.data_push(token, data)
#                 push_method = getattr(cls, "%s_push" % client)
#                 return push_method(token, data)
#             except Exception as e:
#                 if getattr(e, "detail", None):
#                     return e.detail.response.json()
#
#                 return e
#
#     @classmethod
#     def data_push(cls, token, data):
#         """
#
#         push notification for all devices
#         :param token: device token
#         :param data: data to be sent
#         :return: response
#         """
#
#         title = data.get("title")
#         body = data.get("body")
#         badge = data.pop("badge", 1)
#         dumped_data = json.dumps(data, default=str)
#         message = messaging.Message(
#             notification=messaging.Notification(title=title, body=body),
#             data=dict(payload=dumped_data),
#             webpush=messaging.WebpushConfig(headers=dict(Urgency='high')),
#             apns=messaging.APNSConfig(
#                 headers={"apns-priority": "10"},
#                 payload=messaging.APNSPayload(
#                     aps=messaging.Aps(
#                         badge=int(badge),
#                         alert=messaging.ApsAlert(title=title, body=body),
#                         sound='default',
#                         content_available=1,
#                     ))
#             ),
#
#             android=messaging.AndroidConfig(
#                 priority='high',
#                 notification=messaging.AndroidNotification(
#                     title=data.get("title"),
#                     body=data.get("body"),
#                     color=data.get("color", '#f45342'),
#                     sound='default',
#                 ),
#             ),
#             token=token,
#         )
#         res = messaging.send(message)
#         return res
#
#     @classmethod
#     def ios_push(cls, token, data):
#         """
#         push notification for ios devices
#         :param token: device token
#         :param data: data to be sent
#         :return: response
#         """
#
#         title = data.get("title")
#
#         body = data.get("body")
#
#         badge = data.pop("badge", "1")
#         badge = badge if badge else 1
#         message = messaging.Message(
#             notification=messaging.Notification(title=title, body=body),
#             data=data,
#             webpush=messaging.WebpushConfig(headers=dict(Urgency='high')),
#             apns=messaging.APNSConfig(
#                 headers={"apns-priority": "10"},
#                 payload=messaging.APNSPayload(
#                     aps=messaging.Aps(alert=messaging.ApsAlert(title=title, body=body), sound='default',
#                                       badge=int(badge),
#                                       content_available=1)
#                 )
#             ),
#             token=token,
#         )
#         res = messaging.send(message)
#         return res
#
#     @classmethod
#     def android_push(cls, token, data):
#         """
#
#         :param token:
#         :param data:
#         :return:
#         """
#         title = data.get("title")
#         body = data.get("body")
#
#         data["badge"] = "1"
#         message = messaging.Message(
#             notification=messaging.Notification(title=title, body=body),
#             data=data,
#             android=messaging.AndroidConfig(priority='high',
#                                             notification=messaging.AndroidNotification(
#                                                 title=data.get("title"),
#                                                 body=data.get("body"),
#                                                 color=data.get("color", '#f45342'),
#                                                 sound='default',
#                                             ),
#                                             ),
#             token=token,
#         )
#         res = messaging.send(message)
#         return res
#
