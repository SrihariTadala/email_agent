#!/usr/bin/env python3
"""
OAuth2 Setup Verification and Testing
Run this to test your Gmail API OAuth2 setup
"""
from pathlib import Path
import sys


def check_credentials_file():
    """Check if credentials.json exists"""
    creds_file = Path("credentials.json")
    
    if not creds_file.exists():
        print("\n❌ credentials.json NOT FOUND!")
        print("\n" + "="*60)
        print("HOW TO GET credentials.json:")
        print("="*60)
        print("1. Go to: https://console.cloud.google.com/")
        print("2. Select your project (or create one)")
        print("3. Enable Gmail API:")
        print("   - APIs & Services → Library")
        print("   - Search 'Gmail API' → Enable")
        print("4. Configure OAuth consent screen:")
        print("   - APIs & Services → OAuth consent screen")
        print("   - External → Fill in app details")
        print("   - Add scopes: gmail.readonly, gmail.send, gmail.modify")
        print("   - Add your email as test user")
        print("5. Create credentials:")
        print("   - APIs & Services → Credentials")
        print("   - Create Credentials → OAuth client ID")
        print("   - Application type: Desktop app")
        print("   - Download JSON file")
        print("6. Rename downloaded file to 'credentials.json'")
        print("7. Move it to your project folder")
        print("="*60 + "\n")
        return False
    
    print("✅ credentials.json found!")
    
    # Try to parse it
    try:
        import json
        with open(creds_file) as f:
            creds = json.load(f)
        
        # Check structure
        if 'installed' in creds or 'web' in creds:
            print("✅ credentials.json format looks valid")
            return True
        else:
            print("⚠️  credentials.json format may be incorrect")
            print("   Make sure you downloaded 'OAuth 2.0 Client ID' credentials")
            return False
    except Exception as e:
        print(f"⚠️  Error reading credentials.json: {e}")
        return False


def check_token_file():
    """Check if token already exists"""
    token_file = Path("token.pickle")
    
    if token_file.exists():
        print("✅ token.pickle found (you're already authenticated)")
        return True
    else:
        print("ℹ️  token.pickle not found (will be created on first run)")
        return False


def test_oauth_flow():
    """Test the OAuth2 flow"""
    print("\n" + "="*60)
    print("TESTING GMAIL API OAUTH2")
    print("="*60)
    
    try:
        from gmail_oauth_handler import GmailOAuthHandler
        
        print("\nInitializing OAuth2 handler...")
        print("If this is your first time, a browser will open for authorization.")
        print("\n")
        
        handler = GmailOAuthHandler()
        
        print("\n✅ OAuth2 authentication successful!")
        print("✅ Gmail API service is ready")
        
        # Test fetching emails
        print("\nTesting email fetching...")
        emails = handler.fetch_unread_emails(max_emails=3)
        
        print(f"\n✅ Successfully fetched {len(emails)} email(s)")
        
        if emails:
            print("\nPreview of emails:")
            for i, email in enumerate(emails, 1):
                print(f"\n  Email {i}:")
                print(f"    From: {email['from']}")
                print(f"    Subject: {email['subject'][:50]}...")
        else:
            print("\n(No unread emails in inbox)")
        
        return True
        
    except FileNotFoundError as e:
        print(f"\n❌ {e}")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_dependencies():
    """Check if required packages are installed"""
    print("\n" + "="*60)
    print("CHECKING DEPENDENCIES")
    print("="*60)
    
    required = [
        'google.auth',
        'google_auth_oauthlib',
        'google_auth_httplib2',
        'googleapiclient'
    ]
    
    all_good = True
    
    for package in required:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} not installed")
            all_good = False
    
    if not all_good:
        print("\n⚠️  Some packages are missing!")
        print("   Install with: pip install -r requirements_oauth.txt")
        return False
    
    print("\n✅ All dependencies installed!")
    return True


def main():
    print("\n" + "="*70)
    print("GMAIL API OAUTH2 SETUP VERIFICATION")
    print("="*70)
    
    # Step 1: Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Step 2: Check credentials file
    print("\n" + "="*60)
    print("CHECKING CREDENTIALS")
    print("="*60)
    
    if not check_credentials_file():
        sys.exit(1)
    
    # Step 3: Check token
    check_token_file()
    
    # Step 4: Test OAuth flow
    print("\n" + "="*60)
    input("\nPress Enter to test Gmail API OAuth2 authentication...")
    
    if test_oauth_flow():
        print("\n" + "="*70)
        print("SUCCESS! 🎉")
        print("="*70)
        print("\nYour Gmail API OAuth2 is configured correctly!")
        print("You can now run: python agent_oauth.py")
        print("="*70)
    else:
        print("\n" + "="*70)
        print("SETUP INCOMPLETE")
        print("="*70)
        print("\nPlease fix the errors above and try again.")
        print("="*70)
        sys.exit(1)


if __name__ == "__main__":
    main()