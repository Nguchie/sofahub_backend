#!/usr/bin/env python3
"""
M-Pesa Integration Debug Script
This script tests each component of the M-Pesa integration to identify issues.
"""

import os
import sys
import django
import requests
import base64
from datetime import datetime

# Add the project root to Python path
sys.path.append('/path/to/your/project')  # Update this path
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sofahub_backend.settings')
django.setup()

from django.conf import settings
from orders.services import get_mpesa_access_token, generate_mpesa_password, initiate_mpesa_payment

def test_environment_variables():
    """Test if all required M-Pesa environment variables are set"""
    print("🔍 Testing Environment Variables...")
    
    required_vars = [
        'MPESA_ENVIRONMENT',
        'MPESA_CONSUMER_KEY', 
        'MPESA_CONSUMER_SECRET',
        'MPESA_SHORTCODE',
        'MPESA_PASSKEY',
        'MPESA_CALLBACK_URL'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = getattr(settings, var, None)
        if not value:
            missing_vars.append(var)
            print(f"❌ {var}: Not set")
        else:
            # Mask sensitive values
            if 'KEY' in var or 'SECRET' in var or 'PASSKEY' in var:
                masked_value = value[:4] + '*' * (len(value) - 8) + value[-4:] if len(value) > 8 else '***'
                print(f"✅ {var}: {masked_value}")
            else:
                print(f"✅ {var}: {value}")
    
    if missing_vars:
        print(f"\n❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    
    print("✅ All environment variables are set")
    return True

def test_access_token():
    """Test M-Pesa access token generation"""
    print("\n🔍 Testing Access Token Generation...")
    
    try:
        access_token = get_mpesa_access_token()
        if access_token:
            print(f"✅ Access token generated successfully: {access_token[:20]}...")
            return access_token
        else:
            print("❌ Failed to generate access token")
            return None
    except Exception as e:
        print(f"❌ Error generating access token: {e}")
        return None

def test_password_generation():
    """Test M-Pesa password generation"""
    print("\n🔍 Testing Password Generation...")
    
    try:
        password, timestamp = generate_mpesa_password()
        print(f"✅ Password generated successfully")
        print(f"   Timestamp: {timestamp}")
        print(f"   Password: {password[:20]}...")
        return password, timestamp
    except Exception as e:
        print(f"❌ Error generating password: {e}")
        return None, None

def test_callback_url():
    """Test if callback URL is accessible"""
    print("\n🔍 Testing Callback URL Accessibility...")
    
    callback_url = settings.MPESA_CALLBACK_URL
    print(f"Testing URL: {callback_url}")
    
    try:
        # Test with a simple GET request first
        response = requests.get(callback_url, timeout=10)
        print(f"✅ Callback URL is accessible (Status: {response.status_code})")
        return True
    except requests.exceptions.Timeout:
        print("❌ Callback URL timeout - ngrok might be down")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Callback URL connection error - check ngrok tunnel")
        return False
    except Exception as e:
        print(f"❌ Callback URL error: {e}")
        return False

def test_stk_push():
    """Test STK push initiation"""
    print("\n🔍 Testing STK Push Initiation...")
    
    # Use test phone number for sandbox
    test_phone = "254708374149"  # Safaricom test number
    test_amount = 1  # Minimum amount for testing
    test_order_id = 999  # Test order ID
    
    try:
        result = initiate_mpesa_payment(test_phone, test_amount, test_order_id)
        
        if result.get('ResponseCode') == '0':
            print("✅ STK push initiated successfully")
            print(f"   CheckoutRequestID: {result.get('CheckoutRequestID')}")
            print(f"   CustomerMessage: {result.get('CustomerMessage')}")
            return True
        else:
            print(f"❌ STK push failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ STK push error: {e}")
        return False

def test_ngrok_tunnel():
    """Test ngrok tunnel status"""
    print("\n🔍 Testing Ngrok Tunnel...")
    
    try:
        # Check ngrok API for tunnel status
        ngrok_api_url = "http://127.0.0.1:4040/api/tunnels"
        response = requests.get(ngrok_api_url, timeout=5)
        
        if response.status_code == 200:
            tunnels = response.json().get('tunnels', [])
            if tunnels:
                for tunnel in tunnels:
                    if tunnel.get('proto') == 'https':
                        public_url = tunnel.get('public_url')
                        print(f"✅ Ngrok tunnel active: {public_url}")
                        
                        # Check if it matches our callback URL
                        if public_url in settings.MPESA_CALLBACK_URL:
                            print("✅ Callback URL matches ngrok tunnel")
                        else:
                            print("⚠️  Callback URL doesn't match ngrok tunnel")
                            print(f"   Expected: {public_url}")
                            print(f"   Configured: {settings.MPESA_CALLBACK_URL}")
                        return True
            else:
                print("❌ No active ngrok tunnels found")
                return False
        else:
            print("❌ Could not connect to ngrok API")
            return False
            
    except Exception as e:
        print(f"❌ Ngrok test error: {e}")
        print("   Make sure ngrok is running: ngrok http 8000")
        return False

def main():
    """Run all M-Pesa integration tests"""
    print("🚀 M-Pesa Integration Debug Script")
    print("=" * 50)
    
    # Test 1: Environment Variables
    env_ok = test_environment_variables()
    
    # Test 2: Ngrok Tunnel
    ngrok_ok = test_ngrok_tunnel()
    
    # Test 3: Callback URL
    callback_ok = test_callback_url()
    
    # Test 4: Access Token
    token_ok = test_access_token()
    
    # Test 5: Password Generation
    password_ok = test_password_generation()
    
    # Test 6: STK Push (only if all previous tests pass)
    if env_ok and ngrok_ok and callback_ok and token_ok and password_ok:
        stk_ok = test_stk_push()
    else:
        print("\n⚠️  Skipping STK push test due to previous failures")
        stk_ok = False
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    tests = [
        ("Environment Variables", env_ok),
        ("Ngrok Tunnel", ngrok_ok),
        ("Callback URL", callback_ok),
        ("Access Token", token_ok),
        ("Password Generation", password_ok),
        ("STK Push", stk_ok)
    ]
    
    passed = sum(1 for _, result in tests if result)
    total = len(tests)
    
    for test_name, result in tests:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! M-Pesa integration should be working.")
    else:
        print("🔧 Some tests failed. Check the issues above and fix them.")
        
        # Provide specific recommendations
        print("\n💡 RECOMMENDATIONS:")
        if not env_ok:
            print("- Set all required M-Pesa environment variables")
        if not ngrok_ok:
            print("- Start ngrok: ngrok http 8000")
            print("- Update MPESA_CALLBACK_URL with the new ngrok URL")
        if not callback_ok:
            print("- Ensure ngrok tunnel is active and accessible")
        if not token_ok:
            print("- Check M-Pesa consumer key and secret")
            print("- Verify you're using the correct environment (sandbox/production)")
        if not password_ok:
            print("- Check M-Pesa shortcode and passkey")

if __name__ == "__main__":
    main()
