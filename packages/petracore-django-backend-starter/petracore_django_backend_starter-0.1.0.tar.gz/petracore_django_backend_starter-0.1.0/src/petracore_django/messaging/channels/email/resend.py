"""
resend.py

@Author: Maro Okegbero
@Date: August 9, 2024
@Time: 11:24 AM

Resend email API integration.
"""
import requests

from ..base import AbstractNotificationService


class Resend(AbstractNotificationService):

    def __init__(self, settings, api_key=None, base_url=None, sender_id=None):
        self.api_key = api_key if api_key else settings.RESEND_API_KEY
        self.base_url = base_url if base_url else settings.RESEND_BASE_URL
        self.sender_id = sender_id if sender_id else settings.RESEND_SENDER_ID

    def headers(self):
        return {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

    def create_audience(self, name, contacts):
        url = f'{self.base_url}/audiences'
        data = {
            "name": name,
            "contacts": contacts
        }
        response = requests.post(url, headers=self.headers(), json=data)
        return response.json()

    def send(self, message, from_=None, recipients=None, subject=None, text_content=None, cc=None, bcc=None,
             reply_to=None, headers=None, attachments=None, **kwargs):
        url = f'{self.base_url}/email'
        from_ = from_ if from_ else self.sender_id
        print(from_, "this is frooommm")
        data = {
            "from": from_,
            "to": recipients,
            "subject": subject,
            "html": message,
            "text": text_content,
            "cc": cc,
            "bcc": bcc,
            "reply_to": reply_to,
            "headers": headers,
            "attachments": attachments
        }
        response = requests.post(url, headers=self.headers(), json=data)
        return response.json()

    def get_email(self, email_id):
        url = f'{self.base_url}/email/{email_id}'
        response = requests.get(url, headers=self.headers())
        return response.json()

    def create_domain(self, name):
        url = f'{self.base_url}/domains'
        data = {"name": name}
        response = requests.post(url, headers=self.headers(), json=data)
        return response.json()

    def verify_domain(self, domain_id):
        url = f'{self.base_url}/domains/{domain_id}/verify'
        response = requests.post(url, headers=self.headers())
        return response.json()

    def create_api_key(self, name, permission, domain_id=None):
        url = f'{self.base_url}/api-keys'
        data = {
            "name": name,
            "permission": permission,
            "domain_id": domain_id
        }
        response = requests.post(url, headers=self.headers(), json=data)
        return response.json()

    def list_api_keys(self):
        url = f'{self.base_url}/api-keys'
        response = requests.get(url, headers=self.headers())
        return response.json()

    def delete_api_key(self, api_key_id):
        url = f'{self.base_url}/api-keys/{api_key_id}'
        response = requests.delete(url, headers=self.headers())
        return response.json()

    def create_contact(self, audience_id, first_name, last_name, email, unsubscribed=False):
        url = f'{self.base_url}/audiences/{audience_id}/contacts'
        data = {
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "unsubscribed": unsubscribed
        }
        response = requests.post(url, headers=self.headers(), json=data)
        return response.json()

    def get_contact(self, audience_id, contact_id):
        url = f'{self.base_url}/audiences/{audience_id}/contacts/{contact_id}'
        response = requests.get(url, headers=self.headers())
        return response.json()

    def update_contact(self, audience_id, contact_id, attributes):
        url = f'{self.base_url}/audiences/{audience_id}/contacts/{contact_id}'
        response = requests.patch(url, headers=self.headers(), json=attributes)
        return response.json()

    def delete_contact(self, audience_id, contact_id):
        url = f'{self.base_url}/audiences/{audience_id}/contacts/{contact_id}'
        response = requests.delete(url, headers=self.headers())
        return response.json()
