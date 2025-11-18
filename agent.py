"""
Main Agent Orchestration
Coordinates email monitoring, extraction, quoting, PDF generation, and replies
"""
import time
import requests
from datetime import datetime
from pathlib import Path
import config
from email_handler import EmailHandler, is_quote_request
from llm_extractor import extract_shipment_details, validate_extraction
from pdf_generator import generate_quote_pdf


class FreightQuoteAgent:
    """Autonomous agent for processing freight quote requests"""
    
    def __init__(self):
        self.email_handler = EmailHandler()
        self.api_base_url = f"http://localhost:{config.API_PORT}"
        self.output_dir = Path("./quotes")
        self.output_dir.mkdir(exist_ok=True)
        self.log_file = Path("./agent.log")
        
    def log(self, message: str):
        """Log message to console and file"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        
        with open(self.log_file, 'a') as f:
            f.write(log_message + '\n')
    
    def process_email(self, email_data: dict) -> bool:
        """
        Process a single freight quote request email.
        Returns:
            True if processed successfully, False otherwise
        """
        sender = email_data['from']
        subject = email_data['subject']
        body = email_data['body']
        self.log(f"Processing email from {sender}: {subject}")
        try:
            # Step 1: Extract shipment details using LLM
            self.log("Extracting shipment details with LLM...")
            shipment_data = extract_shipment_details(body)
            if not shipment_data:
                self.log("❌ Failed to extract shipment details")
                self.email_handler.send_error_reply(
                    sender, 
                    subject,
                    "We couldn't extract the necessary shipping information from your email. "
                    "Please provide the origin, destination, weight, and commodity details."
                )
                return False
            # Step 2: Validate extraction
            is_valid, error_msg = validate_extraction(shipment_data)
            
            if not is_valid:
                self.log(f"❌ Validation failed: {error_msg}")
                self.email_handler.send_error_reply(sender, subject, error_msg)
                return False
            
            self.log(f"✓ Extracted data: {shipment_data['origin']['city']} → {shipment_data['destination']['city']}")
            
            # Step 3: Call quote API
            self.log("Calling quote API...")
            quote_response = self.call_quote_api(shipment_data)
            
            if not quote_response:
                self.log("❌ Quote API call failed")
                self.email_handler.send_error_reply(
                    sender,
                    subject,
                    "We encountered an error calculating your quote. Please try again later."
                )
                return False
            
            self.log(f"✓ Quote calculated: ${quote_response['total_cost']} (ID: {quote_response['quote_id']})")
            # Step 4: Generate PDF
            self.log("Generating PDF quote...")
            pdf_path = self.output_dir / f"{quote_response['quote_id']}.pdf"
            generate_quote_pdf(quote_response, shipment_data, str(pdf_path))
            self.log(f"✓ PDF generated: {pdf_path}")
            # Step 5: Send reply email with PDF
            self.log("Sending reply email...")
            reply_subject = f"Re: {subject}"
            reply_body = self.create_reply_body(quote_response, shipment_data)
            
            success = self.email_handler.send_reply(
                sender,
                reply_subject,
                reply_body,
                str(pdf_path)
            )
            if success:
                self.log(f"✓ Reply sent to {sender}")
                self.email_handler.mark_as_read(email_data['id'])
                self.log(f"✓ Email marked as read")
                return True
            else:
                self.log(f"❌ Failed to send reply to {sender}")
                return False
        except Exception as e:
            self.log(f"❌ Error processing email: {e}")
            # Try to send error notification
            try:
                self.email_handler.send_error_reply(
                    sender,
                    subject,
                    "We encountered an unexpected error processing your request. "
                    "Our team has been notified and will follow up with you shortly."
                )
            except:
                pass
            return False
    def call_quote_api(self, shipment_data: dict) -> dict:
        """Call the quote API with extracted shipment data"""
        try:
            # Prepare API request
            origin = shipment_data['origin']
            destination = shipment_data['destination']
            cargo = shipment_data['cargo']
            
            request_data = {
                "origin_zip": origin['zip'],
                "destination_zip": destination['zip'],
                "weight_lbs": cargo['weight_lbs'],
                "pieces": cargo['pieces'],
                "dimensions": cargo['dimensions'],
                "special_services": shipment_data.get('special_services', []),
                "pickup_date": shipment_data.get('pickup_date', datetime.now().strftime("%Y-%m-%d")),
                "commodity": cargo.get('commodity', 'General Freight')
            }
            # Make API call
            response = requests.post(
                f"{self.api_base_url}/api/v1/quote",
                json=request_data,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                self.log(f"API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.log(f"Error calling quote API: {e}")
            return None
    
    def create_reply_body(self, quote_data: dict, shipment_data: dict) -> str:
        """Create email reply body text"""
        origin = shipment_data['origin']
        destination = shipment_data['destination']
        
        body = f"""Hello,

Thank you for your freight quote request! Please find your detailed quote attached.

QUOTE SUMMARY:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Quote ID: {quote_data['quote_id']}
Route: {origin['city']}, {origin['state']} → {destination['city']}, {destination['state']}
Total Cost: ${quote_data['total_cost']:.2f}
Transit Time: {quote_data['transit_days']} business days
Valid Until: {datetime.fromisoformat(quote_data['valid_until'].replace('Z', '')).strftime('%B %d, %Y')}

COST BREAKDOWN:
- Base Rate: ${quote_data['breakdown']['base_rate']:.2f}
- Fuel Surcharge: ${quote_data['breakdown']['fuel_surcharge']:.2f}
"""
        
        if quote_data['breakdown']['liftgate_fee'] > 0:
            body += f"• Liftgate Service: ${quote_data['breakdown']['liftgate_fee']:.2f}\n"
        
        if quote_data['breakdown'].get('climate_control_fee', 0) > 0:
            body += f"• Climate Control: ${quote_data['breakdown']['climate_control_fee']:.2f}\n"
        
        body += f"• Insurance: ${quote_data['breakdown']['insurance']:.2f}\n"
        
        body += f"""
To proceed with this shipment, please reply to this email or call us at {config.COMPANY_PHONE}.

Complete details are available in the attached PDF quote.

Best regards,
{config.COMPANY_NAME}
{config.COMPANY_PHONE}
{config.COMPANY_EMAIL}
"""
        
        return body
    
    def run(self, continuous=True):
        """
        Main agent loop.
        
        Args:
            continuous: If True, run continuously. If False, process once and exit.
        """
        self.log("=" * 60)
        self.log(f"Freight Quote Agent Started")
        self.log(f"Monitoring: {config.EMAIL_ADDRESS}")
        self.log(f"Check interval: {config.CHECK_INTERVAL} seconds")
        self.log("=" * 60)
        
        iteration = 0
        
        while True:
            iteration += 1
            self.log(f"\n--- Iteration {iteration} ---")
            
            try:
                # Fetch unread emails
                emails = self.email_handler.fetch_unread_emails()
                self.log(f"Found {len(emails)} unread emails")
                
                # Process each email
                for email_data in emails:
                    # Check if it's a quote request
                    if is_quote_request(email_data['subject'], email_data['body']):
                        self.log(f"📧 Quote request detected from {email_data['from']}")
                        self.process_email(email_data)
                    else:
                        self.log(f"⊘ Not a quote request, skipping: {email_data['subject']}")
                        # Optionally mark as read or leave for manual review
                
            except Exception as e:
                self.log(f"❌ Error in main loop: {e}")
            
            if not continuous:
                self.log("Single run completed, exiting...")
                break
            
            # Wait before next check
            self.log(f"Waiting {config.CHECK_INTERVAL} seconds before next check...")
            time.sleep(config.CHECK_INTERVAL)


if __name__ == "__main__":
    import sys
    
    # Check if API is running
    try:
        response = requests.get(f"http://localhost:{config.API_PORT}/", timeout=5)
        if response.status_code != 200:
            print("⚠️  Quote API doesn't seem to be running!")
            print(f"Please start it first: python quote_api.py")
            sys.exit(1)
    except requests.exceptions.ConnectionError:
        print("❌ Quote API is not running!")
        print(f"Please start it first: python quote_api.py")
        sys.exit(1)
    
    # Create and run agent
    agent = FreightQuoteAgent()
    
    # Run once if --once flag is provided, otherwise run continuously
    continuous = "--once" not in sys.argv
    
    try:
        agent.run(continuous=continuous)
    except KeyboardInterrupt:
        agent.log("\n\nAgent stopped by user")
        sys.exit(0)