"""
Configuration for Freight Quote Agent
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Email Configuration
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")  # App password for Gmail
IMAP_SERVER = os.getenv("IMAP_SERVER", "imap.gmail.com")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))

# LLM Configuration - GROQ (FREE!)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# API Configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))

# Company Information
COMPANY_NAME = "Swift Freight Solutions"
COMPANY_EMAIL = EMAIL_ADDRESS
COMPANY_PHONE = "(555) 123-4567"
COMPANY_ADDRESS = "123 Logistics Way, Chicago, IL 60601"

# Processing Configuration
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "60"))  # seconds
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))