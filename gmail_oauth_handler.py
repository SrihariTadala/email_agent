"""
Gmail API Handler with OAuth2 Authentication - FIXED VERSION
Now includes proper email threading!
"""
import os
import base64
import pickle
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Dict, Optional
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import config

# Gmail API scopes
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.modify'
]


class GmailOAuthHandler:
    """Gmail API handler with OAuth2 authentication"""
    
    def __init__(self):
        self.creds = None
        self.service = None
        self.token_file = Path("token.pickle")
        self.credentials_file = Path("credentials.json")
        
        # Authenticate on initialization
        self.authenticate()
    
    def authenticate(self):
        """
        Authenticate with Gmail API using OAuth2.
        
        First run: Opens browser for authorization
        Subsequent runs: Uses saved token
        """
        # Check if token already exists
        if self.token_file.exists():
            print("[OAuth2] Loading saved credentials...")
            with open(self.token_file, 'rb') as token:
                self.creds = pickle.load(token)
        
        # If no valid credentials, authenticate
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                print("[OAuth2] Refreshing expired token...")
                try:
                    self.creds.refresh(Request())
                except Exception as e:
                    print(f"[OAuth2] Token refresh failed: {e}")
                    print("[OAuth2] Re-authenticating...")
                    self.creds = None
            
            if not self.creds:
                if not self.credentials_file.exists():
                    raise FileNotFoundError(
                        "\n❌ credentials.json not found!\n"
                        "Please download it from Google Cloud Console:\n"
                        "1. Go to: https://console.cloud.google.com/\n"
                        "2. APIs & Services → Credentials\n"
                        "3. Download OAuth 2.0 Client ID\n"
                        "4. Save as 'credentials.json' in project folder\n"
                    )
                
                print("\n" + "="*60)
                print("GMAIL API OAUTH2 AUTHENTICATION")
                print("="*60)
                print("A browser window will open for you to authorize this app.")
                print("This only needs to be done once!")
                print("="*60 + "\n")
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.credentials_file), 
                    SCOPES
                )
                self.creds = flow.run_local_server(port=0)
                
                # Save credentials for future runs
                with open(self.token_file, 'wb') as token:
                    pickle.dump(self.creds, token)
                
                print("\n✅ Authentication successful!")
                print(f"✅ Token saved to {self.token_file}")
                print("="*60 + "\n")
        
        # Build Gmail service
        try:
            self.service = build('gmail', 'v1', credentials=self.creds)
            print("[OAuth2] ✅ Gmail API service initialized")
        except Exception as e:
            raise Exception(f"Failed to build Gmail service: {e}")
    
    def fetch_unread_emails(self, max_emails: int = 3) -> List[Dict]:
        """
        Fetch unread emails from inbox using Gmail API.
        
        Args:
            max_emails: Maximum number of emails to fetch
            
        Returns:
            List of email dictionaries
        """
        emails = []
        
        try:
            print(f"[Gmail API] Fetching unread emails (max: {max_emails})...")
            
            # Query for unread emails
            results = self.service.users().messages().list(
                userId='me',
                labelIds=['INBOX', 'UNREAD'],
                maxResults=max_emails
            ).execute()
            
            messages = results.get('messages', [])
            
            if not messages:
                print("[Gmail API] No unread emails found")
                return emails
            
            print(f"[Gmail API] Found {len(messages)} unread email(s)")
            
            # Fetch each email's details
            for msg in messages:
                try:
                    email_data = self._get_email_details(msg['id'])
                    if email_data:
                        emails.append(email_data)
                except Exception as e:
                    print(f"[Gmail API] Error fetching email {msg['id']}: {e}")
                    continue
            
            print(f"[Gmail API] Successfully fetched {len(emails)} emails")
            
        except HttpError as error:
            print(f"[Gmail API] HTTP error: {error}")
        except Exception as e:
            print(f"[Gmail API] Error: {e}")
        
        return emails
    
    def _get_email_details(self, msg_id: str) -> Optional[Dict]:
        """Get full details of a specific email"""
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=msg_id,
                format='full'
            ).execute()
            
            # Extract headers
            headers = message['payload']['headers']
            subject = self._get_header(headers, 'Subject')
            from_header = self._get_header(headers, 'From')
            message_id = self._get_header(headers, 'Message-ID')
            references = self._get_header(headers, 'References')
            
            # Extract sender email
            if '<' in from_header and '>' in from_header:
                from_email = from_header.split('<')[1].split('>')[0]
                from_name = from_header.split('<')[0].strip()
            else:
                from_email = from_header
                from_name = from_header
            
            # Extract body
            body = self._get_email_body(message['payload'])
            
            return {
                'id': msg_id,
                'from': from_email,
                'from_name': from_name,
                'subject': subject,
                'body': body,
                'thread_id': message['threadId'],
                'message_id': message_id,  # FIXED: Added for threading
                'references': references    # FIXED: Added for threading
            }
            
        except Exception as e:
            print(f"Error getting email details for {msg_id}: {e}")
            return None
    
    def _get_header(self, headers: List[Dict], name: str) -> str:
        """Extract specific header value"""
        for header in headers:
            if header['name'].lower() == name.lower():
                return header['value']
        return ''
    
    def _get_email_body(self, payload: Dict) -> str:
        """Extract email body from payload"""
        body = ""
        
        if 'parts' in payload:
            # Multipart message
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        body = base64.urlsafe_b64decode(
                            part['body']['data']
                        ).decode('utf-8', errors='ignore')
                        break
        else:
            # Simple message
            if 'data' in payload['body']:
                body = base64.urlsafe_b64decode(
                    payload['body']['data']
                ).decode('utf-8', errors='ignore')
        
        return body.strip()
    
    def mark_as_read(self, msg_id: str):
        """Mark an email as read (remove UNREAD label)"""
        try:
            self.service.users().messages().modify(
                userId='me',
                id=msg_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            print(f"[Gmail API] ✅ Marked email {msg_id} as read")
        except Exception as e:
            print(f"[Gmail API] Error marking email as read: {e}")
    
    def mark_all_as_read(self) -> int:
        """Mark all unread emails as read"""
        try:
            print("[Gmail API] Fetching all unread emails...")
            
            results = self.service.users().messages().list(
                userId='me',
                labelIds=['UNREAD'],
                maxResults=500  # Gmail API max per request
            ).execute()
            
            messages = results.get('messages', [])
            total = len(messages)
            
            if total == 0:
                print("[Gmail API] No unread emails found")
                return 0
            
            print(f"[Gmail API] Marking {total} emails as read...")
            
            # Batch modify
            self.service.users().messages().batchModify(
                userId='me',
                body={
                    'ids': [msg['id'] for msg in messages],
                    'removeLabelIds': ['UNREAD']
                }
            ).execute()
            
            print(f"[Gmail API] ✅ Successfully marked {total} emails as read")
            return total
            
        except Exception as e:
            print(f"[Gmail API] Error marking all emails as read: {e}")
            return 0
    
    def send_reply(self,
                   to_email: str,
                   subject: str,
                   body: str,
                   pdf_path: Optional[str] = None,
                   thread_id: Optional[str] = None,
                   original_message_id: Optional[str] = None,
                   original_references: Optional[str] = None) -> bool:
        """
        Send email reply with optional PDF attachment and PROPER THREADING.
        
        Args:
            to_email: Recipient email
            subject: Email subject
            body: Email body
            pdf_path: Optional PDF attachment path
            thread_id: Optional thread ID for replies (Gmail API)
            original_message_id: Message-ID from original email (for threading)
            original_references: References from original email (for threading)
            
        Returns:
            True if sent successfully
        """
        try:
            # Create message
            message = MIMEMultipart()
            message['To'] = to_email
            message['Subject'] = subject
            
            # FIXED: Add threading headers for proper conversation grouping
            if original_message_id:
                message['In-Reply-To'] = original_message_id
                
                # Build References header
                if original_references:
                    message['References'] = f"{original_references} {original_message_id}"
                else:
                    message['References'] = original_message_id
            
            # Add body
            message.attach(MIMEText(body, 'plain'))
            
            # Add PDF attachment if provided
            if pdf_path and os.path.exists(pdf_path):
                try:
                    with open(pdf_path, 'rb') as f:
                        part = MIMEBase('application', 'pdf')
                        part.set_payload(f.read())
                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename={os.path.basename(pdf_path)}'
                        )
                        message.attach(part)
                except Exception as e:
                    print(f"[Gmail API] Error attaching PDF: {e}")
                    return False
            
            # Encode message
            raw_message = base64.urlsafe_b64encode(
                message.as_bytes()
            ).decode('utf-8')
            
            # Prepare send request
            send_message = {'raw': raw_message}
            if thread_id:
                send_message['threadId'] = thread_id
            
            # Send via Gmail API
            self.service.users().messages().send(
                userId='me',
                body=send_message
            ).execute()
            
            print(f"[Gmail API] ✅ Email sent successfully to {to_email}")
            if original_message_id:
                print(f"[Gmail API] ✅ Threaded with original message")
            return True
            
        except HttpError as error:
            print(f"[Gmail API] HTTP error sending email: {error}")
            return False
        except Exception as e:
            print(f"[Gmail API] Error sending email: {e}")
            return False
    
    def send_error_reply(self, 
                        to_email: str, 
                        original_subject: str, 
                        error_message: str,
                        thread_id: Optional[str] = None,
                        original_message_id: Optional[str] = None,
                        original_references: Optional[str] = None) -> bool:
        """Send an error notification email"""
        subject = f"Re: {original_subject}"
        
        body = f"""Hello,

Thank you for your freight quote request. Unfortunately, we encountered an issue processing your request:

{error_message}

Please reply to this email with the following information:
- Origin city, state, and zip code
- Destination city, state, and zip code
- Total weight in pounds
- Number of pieces (pallets, boxes, etc.)
- Commodity description
- Any special service requirements

We'll get you a quote as soon as possible.

Best regards,
{config.COMPANY_NAME}
{config.COMPANY_PHONE}
{config.COMPANY_EMAIL}
"""
        
        return self.send_reply(
            to_email, 
            subject, 
            body, 
            thread_id=thread_id,
            original_message_id=original_message_id,
            original_references=original_references
        )


def is_quote_request(subject: str, body: str) -> bool:
    """
    Determine if an email is a freight quote request.
    Simple keyword matching for demo purposes.
    """
    keywords = [
        'quote', 'freight', 'shipping', 'ship', 'transport',
        'delivery', 'pickup', 'pallet', 'lbs', 'weight'
    ]
    
    text = (subject + ' ' + body).lower()
    
    # Check if at least 2 keywords are present
    matches = sum(1 for keyword in keywords if keyword in text)
    return matches >= 2


if __name__ == "__main__":
    # Test Gmail API OAuth2 handler
    print("Testing Gmail API OAuth2 Handler...")
    
    try:
        handler = GmailOAuthHandler()
        
        print("\n✅ Authentication successful!")
        print("\nFetching unread emails...")
        emails = handler.fetch_unread_emails(max_emails=3)
        
        print(f"\nFound {len(emails)} unread emails:")
        for email_data in emails:
            print(f"\n  From: {email_data['from']}")
            print(f"  Subject: {email_data['subject']}")
            print(f"  Thread ID: {email_data['thread_id']}")
            print(f"  Message ID: {email_data.get('message_id', 'N/A')}")
            print(f"  Body preview: {email_data['body'][:100]}...")
            
            if is_quote_request(email_data['subject'], email_data['body']):
                print("  ✅ This appears to be a quote request")
        
        print("\n✅ Test completed successfully!")
        
    except FileNotFoundError as e:
        print(f"\n❌ {e}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()