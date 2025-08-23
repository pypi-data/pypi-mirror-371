# """
# notifications/email.py
#
# @Author:    Maro Okegbero
# @Date:      Aug 9, 2024
# @Time:      0:53 PM
# """
# import json
# from pprint import pprint
#
# import requests
#
# import settings
# from ..base import AbstractNotificationService
#
#
# class Postmark(AbstractNotificationService):
#     @staticmethod
#     def clean_payload(payload):
#         """ Remove empty keys from dict """
#
#         return dict((k, v) for k, v in payload.items() if v is not None)
#
#     @staticmethod
#     def build_header(extras=None):
#         """ Build server header information """
#         if extras is None:
#             extras = {}
#         header = {
#             "Accept": "application/json",
#             "Content-Type": "application/json",
#             "X-Postmark-Server-Token": settings.POSTMARK_SEVER_KEY
#         }
#
#         header.update(extras)
#
#         return header
#
#     def build_payload(self, from_=None, reply_to=None, to=None, cc=None, bcc=None, subject=None, html=None, text=None,
#                       template_id=None, template_alias=None, attachments=None, metadata=None,
#                       tag=None, email_headers=None, inline_css=True, data=None, **kwargs):
#         """ Send email to a list of recipients"""
#
#         if email_headers is None:
#             email_headers = []
#         if attachments is None:
#             attachments = []
#         if metadata is None:
#             metadata = {}
#         if bcc is None:
#             bcc = []
#         if cc is None:
#             cc = []
#         if to is None:
#             to = []
#         if not from_:
#             from_ = settings.POSTMARK_SENDER
#
#         if isinstance(to, (list, tuple)):
#             to = ",".join(to)
#
#         if isinstance(cc, (list, tuple)):
#             cc = ",".join(cc)
#
#         if isinstance(bcc, (list, tuple)):
#             bcc = ",".join(bcc)
#
#         payload = dict(
#             From=from_,
#             To=to, ReplyTo=reply_to, Cc=cc, Bcc=bcc,  # Recipients
#             HtmlBody=html, TextBody=text,  # Used with regular and bulk email send
#             Subject=subject,
#             TemplateId=template_id,  # Used with templating - optional if template_alias is present
#             TemplateAlias=template_alias,  # Used with templating - optional if template_id is present
#             TemplateModel=data,  # Used with templating to send the data for template processing
#             Headers=email_headers, Metadata=metadata, Tag=tag,
#             TrackOpens=True, TrackLinks="HtmlAndText",
#         )
#         attachments_ = []
#
#         # convert attachments into base64 string. Attachments must come in as a stream object (file, StringIO, etc)
#         for attachment in attachments:
#             name, content_type, content = attachment.get("name"), attachment.get("content_type"), attachment.get(
#                 "content")
#             attachments_.append(dict(Name=name, ContentType=content_type, Content=content))
#         # Assuming there are attachments
#         payload.update(dict(Attachments=attachments_))
#         payload = Postmark.clean_payload(payload)
#
#         return payload
#
#     def send(self, message, recipients=None, from_=None, reply_to=None, cc=None, bcc=None, subject=None,
#              text=None, attachments=None, metadata=None, tag=None, email_headers=None):
#         """ Build and send a single email """
#
#         if email_headers is None:
#             email_headers = []
#         if metadata is None:
#             metadata = {}
#         if attachments is None:
#             attachments = []
#         if bcc is None:
#             bcc = []
#         if cc is None:
#             cc = []
#         if recipients is None:
#             recipients = []
#         kwargs = locals()  # Use this to fetch all args. Line needs to come first
#
#         headers = Postmark.build_header()
#         url = settings.POSTMARK_URL
#         payload = self.build_payload(from_=from_, reply_to=reply_to, to=recipients, cc=cc, bcc=bcc, subject=subject,
#                                      html=message, text=message, attachments=attachments, metadata=metadata, tag=tag,
#                                      email_headers=email_headers)
#         pprint(payload)
#
#         resp = requests.post(url, headers=headers, data=json.dumps(payload))
#         status = resp.json()
#         print(status, "status...........")
#         return status
