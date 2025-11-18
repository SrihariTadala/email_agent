"""
Configuration for Freight Quote Agent - OAuth2 Version
No email passwords needed! 🎉
"""
import os
from dotenv import load_dotenv

load_dotenv()

# OAuth2 Configuration
# No EMAIL_ADDRESS or EMAIL_PASSWORD needed!
# Authentication is handled by OAuth2 flow

# LLM Configuration - GROQ (FREE!)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# API Configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))

# Company Information
COMPANY_NAME = "Swift Freight Solutions"
COMPANY_EMAIL = os.getenv("COMPANY_EMAIL", "your-email@gmail.com")  # Just for display in PDFs
COMPANY_PHONE = "(555) 123-4567"
COMPANY_ADDRESS = "123 Logistics Way, Chicago, IL 60601"

# Processing Configuration
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "60"))  # seconds
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))

# OAuth2 Files (automatically created)
CREDENTIALS_FILE = "credentials.json"  # Download from Google Cloud Console
TOKEN_FILE = "token.pickle"  # Auto-generated after first auth