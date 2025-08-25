import random

def format_number(numero):
    """Formate le numéro pour WhatsApp avec indicatif 227 (Niger)."""
    num = ''.join(filter(str.isdigit, str(numero)))
    if not num.startswith('227'):
        num = '227' + num.lstrip('0')
    return num

def generate_otp(length=6):
    """Génère un OTP numérique aléatoire."""
    return ''.join(str(random.randint(0, 9)) for _ in range(length))
