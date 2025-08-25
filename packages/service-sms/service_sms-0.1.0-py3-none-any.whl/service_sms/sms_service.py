import os
import requests

class SmsService:
    @staticmethod
    def send_sms(numero_telephone, message):
        username = os.getenv('AIR_TEL_USERNAME')
        password = os.getenv('AIR_TEL_PASSWORD')
        origin_addr = os.getenv("SMS_ORIGIN_ADDR")

        api_url = (
            f"https://messaging.airtel.ne:9002/smshttp/qs/"
            f"?REQUESTTYPE=SMSSubmitReq"
            f"&MOBILENO={numero_telephone}"
            f"&USERNAME={username}"
            f"&ORIGIN_ADDR={origin_addr}"
            f"&TYPE=0"
            f"&MESSAGE={requests.utils.quote(message)}"
            f"&PASSWORD={password}"
        )

        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.get(api_url, timeout=60)
                if response.status_code == 200 and "ERROR" not in response.text:
                    return True
            except requests.exceptions.RequestException:
                pass
        return False
