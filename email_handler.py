"""
Email handling with IMAP/SMTP for Gmail
"""
import imaplib
import smtplib
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.utils import parseaddr
from typing import List, Dict, Optional, Tuple
import config


class EmailHandler:
    """Simple IMAP/SMTP email handler for Gmail"""
    
    def __init__(self):
        self.email_address = config.EMAIL_ADDRESS
        self.email_password = config.EMAIL_PASSWORD
        self.imap_server = config.IMAP_SERVER
        self.smtp_server = config.SMTP_SERVER
        self.smtp_port = config.SMTP_PORT
        
    def connect_imap(self) -> imaplib.IMAP4_SSL:
        """Connect to Gmail IMAP server with timeout"""
        try:
            print(f"[DEBUG] Connecting to IMAP server: {self.imap_server}")
            # Add timeout to prevent hanging (30 seconds)
            mail = imaplib.IMAP4_SSL(self.imap_server, timeout=30)
            print(f"[DEBUG] Logging in as: {self.email_address}")
            mail.login(self.email_address, self.email_password)
            print(f"[DEBUG] IMAP login successful")
            return mail
        except Exception as e:
            print(f"IMAP connection error: {e}")
            raise
    
    def fetch_unread_emails(self, max_emails: int = 20) -> List[Dict]:
        """
        Fetch unread emails from inbox.
        
        Args:
            max_emails: Maximum number of recent emails to fetch (default: 20)
        
        Returns:
            List of email dictionaries with 'id', 'from', 'subject', 'body'
        """
        emails = []
        
        try:
            print(f"[DEBUG] Starting to fetch unread emails (max: {max_emails})...")
            mail = self.connect_imap()
            
            print("[DEBUG] Selecting INBOX...")
            mail.select('INBOX')
            
            print("[DEBUG] Searching for unread emails...")
            # Search for unread emails
            status, messages = mail.search(None, 'UNSEEN')
            
            if status != 'OK':
                print("[DEBUG] No unread emails found")
                return emails
            
            email_ids = messages[0].split()
            total_unread = len(email_ids)
            
            # ⚠️ LIMIT TO MOST RECENT EMAILS
            if total_unread > max_emails:
                print(f"[DEBUG] Found {total_unread} unread emails, fetching only the {max_emails} most recent")
                email_ids = email_ids[-max_emails:]  # Get the last N (most recent)
            else:
                print(f"[DEBUG] Found {total_unread} unread email(s)")
            
            for email_id in email_ids:
                try:
                    print(f"[DEBUG] Fetching email ID: {email_id.decode()}")
                    # Fetch email
                    status, msg_data = mail.fetch(email_id, '(RFC822)')
                    
                    if status != 'OK':
                        continue
                    
                    # Parse email
                    raw_email = msg_data[0][1]
                    email_message = email.message_from_bytes(raw_email)
                    
                    # Extract sender
                    from_header = email_message.get('From', '')
                    from_name, from_email = parseaddr(from_header)
                    
                    # Extract subject
                    subject = email_message.get('Subject', '')
                    
                    # Extract body
                    body = self._extract_body(email_message)
                    
                    emails.append({
                        'id': email_id.decode(),
                        'from': from_email,
                        'from_name': from_name,
                        'subject': subject,
                        'body': body,
                        'raw': email_message
                    })
                    
                except Exception as e:
                    print(f"[DEBUG] Error processing email {email_id}: {e}")
                    continue
            
            print(f"[DEBUG] Closing IMAP connection...")
            mail.close()
            mail.logout()
            print(f"[DEBUG] Successfully fetched {len(emails)} emails")
            
        except Exception as e:
            print(f"Error fetching emails: {e}")
            import traceback
            traceback.print_exc()
        
        return emails
    
    def _extract_body(self, email_message) -> str:
        """Extract email body text"""
        body = ""
        
        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                
                if content_type == 'text/plain':
                    try:
                        body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        break
                    except:
                        continue
        else:
            try:
                body = email_message.get_payload(decode=True).decode('utf-8', errors='ignore')
            except:
                body = str(email_message.get_payload())
        
        return body.strip()
    
    def mark_as_read(self, email_id: str):
        """Mark an email as read"""
        try:
            mail = self.connect_imap()
            mail.select('INBOX')
            mail.store(email_id.encode(), '+FLAGS', '\\Seen')
            mail.close()
            mail.logout()
        except Exception as e:
            print(f"Error marking email as read: {e}")
    
    def mark_all_as_read(self):
        """Mark all unread emails as read - useful for starting fresh"""
        try:
            print("[DEBUG] Connecting to mark all emails as read...")
            mail = self.connect_imap()
            mail.select('INBOX')
            
            print("[DEBUG] Searching for all unread emails...")
            status, messages = mail.search(None, 'UNSEEN')
            
            if status != 'OK':
                print("No unread emails to mark")
                return 0
            
            email_ids = messages[0].split()
            total = len(email_ids)
            
            if total == 0:
                print("No unread emails found")
                return 0
            
            print(f"[DEBUG] Marking {total} emails as read...")
            
            # Mark all as read in one command
            for email_id in email_ids:
                mail.store(email_id, '+FLAGS', '\\Seen')
            
            mail.close()
            mail.logout()
            
            print(f"✅ Successfully marked {total} emails as read")
            return total
            
        except Exception as e:
            print(f"Error marking all emails as read: {e}")
            import traceback
            traceback.print_exc()
            return 0
    
    def send_reply(self, 
                   to_email: str, 
                   subject: str, 
                   body: str, 
                   pdf_path: Optional[str] = None) -> bool:
        """
        Send email reply with optional PDF attachment.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body text
            pdf_path: Optional path to PDF attachment
            
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email_address
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add body
            msg.attach(MIMEText(body, 'plain'))
            
            # Add PDF attachment if provided
            if pdf_path:
                try:
                    with open(pdf_path, 'rb') as f:
                        pdf_attachment = MIMEApplication(f.read(), _subtype='pdf')
                        pdf_attachment.add_header('Content-Disposition', 'attachment', 
                                                filename=pdf_path.split('/')[-1])
                        msg.attach(pdf_attachment)
                except Exception as e:
                    print(f"Error attaching PDF: {e}")
                    return False
            
            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_address, self.email_password)
            server.send_message(msg)
            server.quit()
            
            print(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
    
    def send_error_reply(self, to_email: str, original_subject: str, error_message: str) -> bool:
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
        
        return self.send_reply(to_email, subject, body)


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
    # Test email handler
    handler = EmailHandler()
    
    print("Testing IMAP connection...")
    emails = handler.fetch_unread_emails()
    print(f"Found {len(emails)} unread emails")
    
    for email_data in emails:
        print(f"\nFrom: {email_data['from']}")
        print(f"Subject: {email_data['subject']}")
        print(f"Body preview: {email_data['body'][:100]}...")
        
        if is_quote_request(email_data['subject'], email_data['body']):
            print("✓ This appears to be a quote request")