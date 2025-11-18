"""
Setup Verification Script
Run this to check if everything is configured correctly
"""
import os
from pathlib import Path

def check_file(filename):
    """Check if a file exists"""
    if Path(filename).exists():
        print(f"✅ {filename} exists")
        return True
    else:
        print(f"❌ {filename} missing")
        return False

def check_env_var(var_name):
    """Check if environment variable is set"""
    value = os.getenv(var_name)
    if value and value != f"your-{var_name.lower().replace('_', '-')}-here":
        print(f"✅ {var_name} is configured")
        return True
    else:
        print(f"❌ {var_name} not configured")
        return False

def test_imports():
    """Test if all required packages are installed"""
    packages = [
        'fastapi',
        'uvicorn', 
        'anthropic',
        'reportlab',
        'requests',
        'dotenv'
    ]
    
    print("\n📦 Checking Python packages...")
    all_good = True
    
    for package in packages:
        try:
            __import__(package)
            print(f"✅ {package} installed")
        except ImportError:
            print(f"❌ {package} not installed")
            all_good = False
    
    return all_good

def test_api_connection():
    """Test if Quote API is running"""
    import requests
    
    print("\n🌐 Checking Quote API...")
    try:
        response = requests.get("http://localhost:8000/", timeout=2)
        if response.status_code == 200:
            print("✅ Quote API is running")
            return True
        else:
            print(f"⚠️  Quote API returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Quote API is not running (start with: python quote_api.py)")
        return False
    except Exception as e:
        print(f"❌ Error checking API: {e}")
        return False

def main():
    print("=" * 60)
    print("Freight Quote Agent - Setup Verification")
    print("=" * 60)
    
    # Check files
    print("\n📁 Checking files...")
    files_ok = all([
        check_file("config.py"),
        check_file("agent.py"),
        check_file("quote_api.py"),
        check_file("llm_extractor.py"),
        check_file("pdf_generator.py"),
        check_file("email_handler.py"),
        check_file("requirements.txt"),
    ])
    
    # Check .env file
    print("\n🔧 Checking environment configuration...")
    env_file_exists = check_file(".env")
    
    if env_file_exists:
        from dotenv import load_dotenv
        load_dotenv()
        
        env_ok = all([
            check_env_var("EMAIL_ADDRESS"),
            check_env_var("EMAIL_PASSWORD"),
            check_env_var("GROQ_API_KEY"),  # Changed from ANTHROPIC_API_KEY
        ])
    else:
        print("\n⚠️  .env file not found!")
        print("   Copy .env.example to .env and configure it")
        env_ok = False
    
    # Check packages
    packages_ok = test_imports()
    
    # Check API (optional)
    api_ok = test_api_connection()
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    if files_ok and env_ok and packages_ok:
        print("✅ All checks passed! You're ready to run the agent.")
        print("\nNext steps:")
        print("1. Terminal 1: python quote_api.py")
        print("2. Terminal 2: python agent.py")
        print("3. Send a test email to your configured address")
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        
        if not env_ok:
            print("\n⚠️  Configuration issue:")
            print("   - Copy .env.example to .env")
            print("   - Add your Gmail and API credentials")
            
        if not packages_ok:
            print("\n⚠️  Package issue:")
            print("   - Run: pip install -r requirements.txt")
    
    print("\nFor detailed setup instructions, see README.md")
    print("=" * 60)

if __name__ == "__main__":
    main()
