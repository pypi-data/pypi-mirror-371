# Service SMS 📱

Un package Python simple pour envoyer des **SMS via Airtel** et des **messages WhatsApp (OTP)**.

## 🚀 Installation

```bash
pip install service-sms



pip install .
```)

## 📌 Utilisation

```python
from service_sms import SmsService, WhatsAppService, generate_otp

# Génération OTP
otp = generate_otp()

# Envoi SMS
SmsService.send_sms("91234567", f"Votre code OTP est {otp}")

# Envoi WhatsApp
WhatsAppService.send_whatsapp("91234567", otp)
