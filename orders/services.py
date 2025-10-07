import requests
import base64
from datetime import datetime
from django.conf import settings
import json


def get_mpesa_access_token():
    """
    Get M-Pesa API access token
    """
    if settings.MPESA_ENVIRONMENT == 'sandbox':
        url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
    else:
        url = 'https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'

    # Encode consumer key and secret
    auth_string = f"{settings.MPESA_CONSUMER_KEY}:{settings.MPESA_CONSUMER_SECRET}"
    encoded_auth = base64.b64encode(auth_string.encode()).decode()

    headers = {
        'Authorization': f'Basic {encoded_auth}'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()['access_token']
    except Exception as e:
        print(f"Error getting access token: {e}")
        return None


def generate_mpesa_password():
    """
    Generate M-Pesa API password using shortcode and passkey
    """
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    data_to_encode = f"{settings.MPESA_SHORTCODE}{settings.MPESA_PASSKEY}{timestamp}"
    encoded_password = base64.b64encode(data_to_encode.encode()).decode()
    return encoded_password, timestamp


def initiate_mpesa_payment(phone_number, amount, order_id):
    """
    Initiate STK push to customer's phone
    """
    access_token = get_mpesa_access_token()
    if not access_token:
        return {"ResponseCode": "1", "error": "Failed to get access token"}

    password, timestamp = generate_mpesa_password()

    if settings.MPESA_ENVIRONMENT == 'sandbox':
        url = 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
    else:
        url = 'https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest'

    # Format phone number (remove + and add country code if needed)
    if phone_number.startswith('+'):
        phone_number = phone_number[1:]
    if phone_number.startswith('0'):
        phone_number = '254' + phone_number[1:]

    payload = {
        "BusinessShortCode": settings.MPESA_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": int(amount),
        "PartyA": phone_number,
        "PartyB": settings.MPESA_SHORTCODE,
        "PhoneNumber": phone_number,
        "CallBackURL": settings.MPESA_CALLBACK_URL,
        "AccountReference": f"SOFAHUB{order_id}",
        "TransactionDesc": f"Payment for Order #{order_id}"
    }

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response_data = response.json()

        if response.status_code == 200:
            return response_data
        else:
            return {"ResponseCode": "1", "error": response_data.get('errorMessage', 'Unknown error')}
    except Exception as e:
        return {"ResponseCode": "1", "error": str(e)}


def send_whatsapp_message(phone_number, message):
    """
    Stub function for sending WhatsApp messages
    In a real implementation, this would integrate with WhatsApp Business API
    """
    print(f"WHATSAPP MESSAGE to {phone_number}: {message}")
    # This is a stub - in production, integrate with WhatsApp API
    return True


def confirm_mpesa_payment(checkout_request_id):
    """
    Check status of an M-Pesa payment
    """
    access_token = get_mpesa_access_token()
    if not access_token:
        return {"ResponseCode": "1", "error": "Failed to get access token"}

    if settings.MPESA_ENVIRONMENT == 'sandbox':
        url = 'https://sandbox.safaricom.co.ke/mpesa/stkpushquery/v1/query'
    else:
        url = 'https://api.safaricom.co.ke/mpesa/stkpushquery/v1/query'

    password, timestamp = generate_mpesa_password()

    payload = {
        "BusinessShortCode": settings.MPESA_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "CheckoutRequestID": checkout_request_id
    }

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        return response.json()
    except Exception as e:
        return {"ResponseCode": "1", "error": str(e)}