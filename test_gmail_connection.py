"""
Gmail Connection Diagnostic Tool
Run this to identify IMAP/SMTP connection issues
"""
import imaplib
import smtplib
import sys
import socket
from dotenv import load_dotenv
import os

load_dotenv()

def test_imap_connection():
    """Test IMAP connection to Gmail"""
    print("\n" + "="*60)
    print("TESTING IMAP CONNECTION")
    print("="*60)
    
    email_address = os.getenv("EMAIL_ADDRESS")
    email_password = os.getenv("EMAIL_PASSWORD")
    imap_server = os.getenv("IMAP_SERVER", "imap.gmail.com")
    
    if not email_address or not email_password:
        print("❌ EMAIL_ADDRESS or EMAIL_PASSWORD not configured in .env")
        return False
    
    print(f"📧 Email: {email_address}")
    print(f"🔑 Password: {'*' * len(email_password)} ({len(email_password)} chars)")
    print(f"🌐 IMAP Server: {imap_server}")
    
    try:
        # Test DNS resolution
        print(f"\n[1/5] Testing DNS resolution for {imap_server}...")
        ip_address = socket.gethostbyname(imap_server)
        print(f"✅ DNS resolved to: {ip_address}")
        
        # Test port connectivity
        print(f"\n[2/5] Testing port 993 connectivity...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex((imap_server, 993))
        sock.close()
        
        if result == 0:
            print(f"✅ Port 993 is open and reachable")
        else:
            print(f"❌ Port 993 is not reachable (error code: {result})")
            return False
        
        # Test IMAP SSL connection
        print(f"\n[3/5] Establishing IMAP SSL connection...")
        mail = imaplib.IMAP4_SSL(imap_server, timeout=30)
        print(f"✅ IMAP SSL connection established")
        
        # Test authentication
        print(f"\n[4/5] Attempting login...")
        try:
            mail.login(email_address, email_password)
            print(f"✅ Login successful!")
        except imaplib.IMAP4.error as e:
            print(f"❌ Login failed: {e}")
            print("\n🔧 TROUBLESHOOTING:")
            print("   1. Make sure you're using an App Password, not your regular Gmail password")
            print("   2. Enable 2-Step Verification in your Google Account")
            print("   3. Generate an App Password: https://myaccount.google.com/apppasswords")
            print("   4. Enable IMAP in Gmail settings")
            return False
        
        # Test inbox access
        print(f"\n[5/5] Testing inbox access...")
        mail.select('INBOX')
        status, messages = mail.search(None, 'ALL')
        
        if status == 'OK':
            num_emails = len(messages[0].split()) if messages[0] else 0
            print(f"✅ Successfully accessed inbox ({num_emails} total emails)")
        else:
            print(f"❌ Failed to access inbox")
            return False
        
        # Cleanup
        mail.close()
        mail.logout()
        
        print("\n" + "="*60)
        print("✅ ALL IMAP TESTS PASSED!")
        print("="*60)
        return True
        
    except socket.timeout:
        print(f"❌ Connection timed out after 30 seconds")
        print("   Check your internet connection and firewall settings")
        return False
    except socket.gaierror:
        print(f"❌ Failed to resolve {imap_server}")
        print("   Check your DNS settings or internet connection")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_smtp_connection():
    """Test SMTP connection to Gmail"""
    print("\n" + "="*60)
    print("TESTING SMTP CONNECTION")
    print("="*60)
    
    email_address = os.getenv("EMAIL_ADDRESS")
    email_password = os.getenv("EMAIL_PASSWORD")
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    
    if not email_address or not email_password:
        print("❌ EMAIL_ADDRESS or EMAIL_PASSWORD not configured in .env")
        return False
    
    print(f"📧 Email: {email_address}")
    print(f"🌐 SMTP Server: {smtp_server}:{smtp_port}")
    
    try:
        # Test SMTP connection
        print(f"\n[1/3] Establishing SMTP connection...")
        server = smtplib.SMTP(smtp_server, smtp_port, timeout=30)
        print(f"✅ SMTP connection established")
        
        # Test STARTTLS
        print(f"\n[2/3] Starting TLS encryption...")
        server.starttls()
        print(f"✅ TLS encryption enabled")
        
        # Test authentication
        print(f"\n[3/3] Attempting login...")
        server.login(email_address, email_password)
        print(f"✅ Login successful!")
        
        server.quit()
        
        print("\n" + "="*60)
        print("✅ ALL SMTP TESTS PASSED!")
        print("="*60)
        return True
        
    except socket.timeout:
        print(f"❌ Connection timed out after 30 seconds")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_gmail_settings():
    """Display Gmail settings checklist"""
    print("\n" + "="*60)
    print("GMAIL SETTINGS CHECKLIST")
    print("="*60)
    print("""
To use this agent, ensure you have:

1. ✓ Enabled 2-Step Verification
   → Go to: https://myaccount.google.com/security

2. ✓ Enabled IMAP in Gmail
   → Go to Gmail Settings → Forwarding and POP/IMAP
   → Enable IMAP access

3. ✓ Generated an App Password
   → Go to: https://myaccount.google.com/apppasswords
   → Select "Mail" and "Other (Custom name)"
   → Copy the 16-character password to your .env file

4. ✓ Updated .env file with correct credentials
   → EMAIL_ADDRESS=your.email@gmail.com
   → EMAIL_PASSWORD=xxxx xxxx xxxx xxxx (16-char app password)

5. ✓ Allow less secure apps (if needed)
   → Some accounts may need this enabled
    """)


def main():
    print("\n" + "="*60)
    print("GMAIL CONNECTION DIAGNOSTIC TOOL")
    print("="*60)
    
    # Check environment variables
    if not os.path.exists(".env"):
        print("❌ .env file not found!")
        print("   Create a .env file with your Gmail credentials")
        sys.exit(1)
    
    # Show settings checklist
    check_gmail_settings()
    
    input("Press Enter to start testing...")
    
    # Run tests
    imap_ok = test_imap_connection()
    smtp_ok = test_smtp_connection()
    
    # Summary
    print("\n" + "="*60)
    print("DIAGNOSTIC SUMMARY")
    print("="*60)
    print(f"IMAP Connection: {'✅ PASSED' if imap_ok else '❌ FAILED'}")
    print(f"SMTP Connection: {'✅ PASSED' if smtp_ok else '❌ FAILED'}")
    
    if imap_ok and smtp_ok:
        print("\n🎉 All tests passed! Your Gmail is configured correctly.")
        print("   You can now run: python agent.py")
    else:
        print("\n⚠️  Some tests failed. Please review the errors above.")
        print("   Follow the troubleshooting steps in the checklist.")
    
    print("="*60)


if __name__ == "__main__":
    main()
