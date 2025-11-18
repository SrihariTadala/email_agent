#!/usr/bin/env python3.11
"""
Mark All Emails As Read - Utility Script

Run this BEFORE starting the agent to mark all existing unread emails as read.
This lets the agent start fresh and only process NEW emails from now on.

Usage:
    python mark_all_read.py
"""
import sys
from email_handler import EmailHandler


def main():
    print("=" * 70)
    print("MARK ALL EXISTING EMAILS AS READ")
    print("=" * 70)
    print()
    print("⚠️  WARNING: This will mark ALL unread emails in your inbox as read!")
    print()
    print("This is useful before starting the agent so it only processes")
    print("NEW emails from now on, not your existing 2,600+ unread emails.")
    print()
    
    response = input("Do you want to continue? (yes/no): ").strip().lower()
    
    if response not in ['yes', 'y']:
        print("\nOperation cancelled.")
        sys.exit(0)
    
    print("\nConnecting to Gmail...")
    
    try:
        handler = EmailHandler()
        total_marked = handler.mark_all_as_read()
        
        print("\n" + "=" * 70)
        print(f"✅ SUCCESS! Marked {total_marked} emails as read")
        print("=" * 70)
        print()
        print("Your inbox is now clean!")
        print("You can now start the agent: python3.11 agent.py")
        print()
        print("From now on, only NEW emails will be processed.")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()