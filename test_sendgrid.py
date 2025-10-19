#!/usr/bin/env python3
"""Test SendGrid API configuration"""

import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_sendgrid_api():
    """Test SendGrid API key and sender verification"""
    api_key = os.getenv('SENDGRID_API_KEY')
    sender_email = os.getenv('SENDER_EMAIL')
    
    print(f"Testing SendGrid API...")
    print(f"API Key: {api_key[:10]}...{api_key[-10:] if api_key else 'None'}")
    print(f"Sender Email: {sender_email}")
    print("-" * 50)
    
    if not api_key:
        print("❌ ERROR: SENDGRID_API_KEY not found in environment")
        return False
    
    if not sender_email:
        print("❌ ERROR: SENDER_EMAIL not found in environment")
        return False
    
    # Test 1: Check API key validity
    print("1. Testing API key validity...")
    try:
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get('https://api.sendgrid.com/v3/user/account', headers=headers)
        
        if response.status_code == 200:
            account_info = response.json()
            print(f"✅ API Key valid! Account: {account_info.get('username', 'Unknown')}")
        else:
            print(f"❌ API Key invalid! Status: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing API key: {e}")
        return False
    
    # Test 2: Check sender verification
    print("\n2. Checking sender verification...")
    try:
        response = requests.get('https://api.sendgrid.com/v3/verified_senders', headers=headers)
        
        if response.status_code == 200:
            senders = response.json()
            print(f"Verified senders found: {len(senders)}")
            print(f"Senders response: {senders}")
            
            # Handle both list and dict responses
            if isinstance(senders, list):
                verified_emails = [sender.get('from_email') for sender in senders if isinstance(sender, dict) and sender.get('verified')]
            else:
                # If it's not a list, try to extract from results key
                results = senders.get('results', [])
                verified_emails = [sender.get('from_email') for sender in results if isinstance(sender, dict) and sender.get('verified')]
            
            print(f"Verified emails: {verified_emails}")
            
            if sender_email in verified_emails:
                print(f"✅ Sender email {sender_email} is verified!")
                return True
            else:
                print(f"❌ Sender email {sender_email} is NOT verified!")
                print("You need to verify this email in your SendGrid dashboard.")
                return False
        else:
            print(f"❌ Failed to check senders! Status: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error checking senders: {e}")
        return False

def test_send_email():
    """Test sending a simple email"""
    api_key = os.getenv('SENDGRID_API_KEY')
    sender_email = os.getenv('SENDER_EMAIL')
    
    print("\n3. Testing email send...")
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    # Test email to yourself
    email_data = {
        "personalizations": [{
            "to": [{"email": sender_email}],
            "subject": "SendGrid Test Email"
        }],
        "from": {"email": sender_email},
        "content": [{
            "type": "text/plain",
            "value": "This is a test email from your SendGrid setup. If you receive this, your configuration is working!"
        }]
    }
    
    try:
        response = requests.post('https://api.sendgrid.com/v3/mail/send', 
                               headers=headers, 
                               json=email_data)
        
        if response.status_code == 202:
            print("✅ Test email sent successfully!")
            print("Check your inbox (and spam folder) for the test email.")
            return True
        else:
            print(f"❌ Failed to send test email! Status: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error sending test email: {e}")
        return False

if __name__ == "__main__":
    print("SendGrid Configuration Test")
    print("=" * 50)
    
    # Test API key and sender verification
    api_valid = test_sendgrid_api()
    
    if api_valid:
        # If API is valid, test sending an email
        test_send_email()
    else:
        print("\n❌ Cannot test email sending - fix the above issues first.")
        print("\nNext steps:")
        print("1. Go to https://app.sendgrid.com/settings/sender_auth/senders")
        print("2. Verify your sender email address")
        print("3. Make sure your API key has 'Mail Send' permissions")