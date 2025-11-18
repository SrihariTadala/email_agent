#!/usr/bin/env python3
"""
Mark All Emails As Read - OAuth2 Version
Uses Gmail API instead of IMAP
"""
import sys


def main():
    print("=" * 70)
    print("MARK ALL EXISTING EMAILS AS READ (OAuth2)")
    print("=" * 70)
    print()
    print("⚠️  WARNING: This will mark ALL unread emails in your inbox as read!")
    print()
    print("This is useful before starting the agent so it only processes")
    print("NEW emails from now on.")
    print()
    
    response = input("Do you want to continue? (yes/no): ").strip().lower()
    
    if response not in ['yes', 'y']:
        print("\nOperation cancelled.")
        sys.exit(0)
    
    print("\nInitializing Gmail API OAuth2...")
    
    try:
        from gmail_oauth_handler import GmailOAuthHandler
        
        handler = GmailOAuthHandler()
        
        print("\nMarking all unread emails as read...")
        total_marked = handler.mark_all_as_read()
        
        print("\n" + "=" * 70)
        print(f"✅ SUCCESS! Marked {total_marked} emails as read")
        print("=" * 70)
        print()
        print("Your inbox is now clean!")
        print("You can now start the agent: python agent_oauth.py")
        print()
        print("From now on, only NEW emails will be processed.")
        print("=" * 70)
        
    except FileNotFoundError as e:
        print(f"\n❌ {e}")
        print("\nPlease download credentials.json from Google Cloud Console")
        print("See OAUTH2_GUIDE.md for instructions")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()