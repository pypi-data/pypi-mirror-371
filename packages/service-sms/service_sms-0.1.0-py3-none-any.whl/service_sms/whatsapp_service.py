import os
import requests
from .utils import format_number

class WhatsAppService:
    @staticmethod
    def send_whatsapp(numero_telephone, otp_code):
        access_token = os.getenv('WHATSAPP_ACCESS_TOKEN')
        business_id = os.getenv('WHATSAPP_PHONE_ID')

        api_url = f"https://graph.facebook.com/v18.0/{business_id}/messages"
        num = format_number(numero_telephone)

        payload = {
            "messaging_product": "whatsapp",
            "to": f"+{num}",
            "type": "template",
            "template": {
                "name": "one_time_password",
                "language": {"code": "fr", "policy": "deterministic"},
                "components": [
                    {
                        "type": "body",
                        "parameters": [{"type": "text", "text": otp_code}]
                    },
                    {
                        "type": "button",
                        "sub_type": "url",
                        "index": "0",
                        "parameters": [{"type": "text", "text": otp_code}]
                    }
                ]
            }
        }

        response = requests.post(
            api_url,
            headers={
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            },
            json=payload
        )

        if response.status_code != 200:
            error = response.json().get('error', {})
            raise Exception(f"Erreur WhatsApp [{error.get('code')}]: {error.get('message')}")
        return True
