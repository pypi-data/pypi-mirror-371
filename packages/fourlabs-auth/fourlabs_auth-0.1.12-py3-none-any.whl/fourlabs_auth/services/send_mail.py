import msal
import requests
from django.conf import settings
from django.template.loader import render_to_string
from typing import List, Optional, Dict


class GraphEmailClient:
    def __init__(self):
        self.client_id = settings.GRAPH_CLIENT_ID
        self.client_secret = settings.GRAPH_CLIENT_SECRET
        self.tenant_id = settings.GRAPH_TENANT_ID
        self.sender_email = settings.GRAPH_SENDER_EMAIL
        self.authority = f'https://login.microsoftonline.com/{self.tenant_id}'
        self.scope = ['https://graph.microsoft.com/.default']
        self.token = self._get_access_token()

    def _get_access_token(self) -> str:
        app = msal.ConfidentialClientApplication(
            self.client_id,
            authority=self.authority,
            client_credential=self.client_secret
        )
        result = app.acquire_token_for_client(scopes=self.scope)

        if "access_token" in result:
            return result["access_token"]
        else:
            raise Exception(f"Erro ao obter token: {result.get('error_description')}")

    def _build_email_payload(self, subject: str, html_content: str, to: List[str], cc: Optional[List[str]] = None) -> Dict:
        def format_recipients(emails):
            return [{"emailAddress": {"address": email}} for email in emails]

        payload = {
            "message": {
                "subject": subject,
                "body": {
                    "contentType": "HTML",
                    "content": html_content
                },
                "toRecipients": format_recipients(to)
            }
        }

        if cc:
            payload["message"]["ccRecipients"] = format_recipients(cc)

        return payload

    def send_email(
        self,
        subject: str,
        to: List[str],
        template_name: str,
        context: dict,
        cc: Optional[List[str]] = None
    ) -> bool:
        html_content = render_to_string(template_name, context)
        payload = self._build_email_payload(subject, html_content, to, cc)

        endpoint = f'https://graph.microsoft.com/v1.0/users/{self.sender_email}/sendMail'
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }

        response = requests.post(endpoint, headers=headers, json=payload)

        if response.status_code == 202:
            print("✅ Email enviado com sucesso!")
            return True
        else:
            print(f"❌ Erro ao enviar email: {response.status_code} {response.text}")
            return False
