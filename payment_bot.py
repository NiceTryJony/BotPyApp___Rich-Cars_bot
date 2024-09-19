import requests
import os
from dotenv import load_dotenv

load_dotenv()

CRYPTOMUS_API_KEY = os.getenv('CRYPTOMUS_API_KEY')
CRYPTOMUS_SHOP_ID = os.getenv('CRYPTOMUS_SHOP_ID')
CRYPTOMUS_MERCHANT_ID = os.getenv('CRYPTOMUS_MERCHANT_ID')

def create_payment_link(user_id, amount):
    url = "https://api.cryptomus.com/v1/payment"
    headers = {
        'Authorization': f'Bearer {CRYPTOMUS_API_KEY}',
        'Content-Type': 'application/json'
    }
    payload = {
        'shop_id': CRYPTOMUS_SHOP_ID,
        'amount': amount,
        'currency': 'USDT',
        'order_id': str(user_id),
        'payment_method': 'crypto',
        'success_url': 'https://example.com/success',
        'fail_url': 'https://example.com/fail'
    }
    
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        return response.json().get('payment_url')
    return None

def generate_payment_url(user_id, amount):
    """Генерация ссылки на оплату через Cryptomus."""
    payment_url = f"https://cryptomus.com/pay?merchant_id={CRYPTOMUS_MERCHANT_ID}&amount={amount}&user_id={user_id}"
    return payment_url

async def check_payment_status(user_id, amount):
    """Проверка статуса платежа через Cryptomus."""
    # Этот код будет проверять оплату через API Cryptomus
    url = f"https://api.cryptomus.com/payments/check?user_id={user_id}&amount={amount}"
    headers = {'Authorization': f'Bearer {CRYPTOMUS_API_KEY}'}
    response = requests.get(url, headers=headers)
    data = response.json()

    if data['status'] == 'paid' and data['amount'] == amount:
        return True
    return False