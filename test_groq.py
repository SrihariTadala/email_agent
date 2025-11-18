#!/usr/bin/env python3
"""
Test Groq API Connection
Quick diagnostic to see if Groq is working
"""
import sys
from dotenv import load_dotenv
import os

load_dotenv()

print("=" * 70)
print("TESTING GROQ API")
print("=" * 70)

# Check API key
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    print("❌ GROQ_API_KEY not found in .env file")
    sys.exit(1)

print(f"✅ GROQ_API_KEY found: {api_key[:10]}...{api_key[-4:]}")

# Check groq package
print("\n[1/4] Checking groq package installation...")
try:
    import groq
    print(f"✅ groq package installed (version: {groq.__version__})")
except ImportError:
    print("❌ groq package not installed")
    print("   Run: pip install groq --upgrade")
    sys.exit(1)

# Try to initialize client
print("\n[2/4] Initializing Groq client...")
try:
    from groq import Groq
    client = Groq(api_key=api_key)
    print("✅ Groq client initialized successfully")
except TypeError as e:
    print(f"❌ TypeError during initialization: {e}")
    print("\n🔧 SOLUTION: Upgrade groq package")
    print("   Run: pip install groq --upgrade")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

# Try a simple API call
print("\n[3/4] Testing API call...")
try:
    completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": "Say 'test successful' in exactly 2 words."
            }
        ],
        model="llama-3.1-8b-instant",
        temperature=0.1,
        max_tokens=50
    )
    
    response = completion.choices[0].message.content
    print(f"✅ API call successful!")
    print(f"   Response: {response}")
except Exception as e:
    print(f"❌ API call failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test with actual extraction
print("\n[4/4] Testing shipment extraction...")
test_email = """
Hi,
We need a quote for shipping 2 pallets from Los Angeles, CA 90021
to Chicago, IL 60601.

Weight: 800 lbs
Dimensions: 48x40x60 inches each

Thanks!
"""

try:
    prompt = f"""Extract freight shipment details from this email and return ONLY valid JSON.

Email:
{test_email}

Extract the following information and return as JSON:
{{
  "origin": {{"city": "string", "state": "string", "zip": "string"}},
  "destination": {{"city": "string", "state": "string", "zip": "string"}},
  "cargo": {{"weight_lbs": number, "pieces": number}}
}}

Return ONLY the JSON object, no other text.
"""

    completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a data extraction expert. You ONLY return valid JSON."},
            {"role": "user", "content": prompt}
        ],
        model="llama-3.1-8b-instant",
        temperature=0.1,
        max_tokens=500
    )
    
    response_text = completion.choices[0].message.content.strip()
    
    # Try to parse as JSON
    import json
    # Remove markdown if present
    if response_text.startswith("```"):
        lines = response_text.split("\n")
        response_text = "\n".join(lines[1:-1])
        if response_text.startswith("json"):
            response_text = response_text[4:].strip()
    
    data = json.loads(response_text)
    print(f"✅ Extraction successful!")
    print(f"   Origin: {data['origin']['city']}, {data['origin']['state']}")
    print(f"   Destination: {data['destination']['city']}, {data['destination']['state']}")
    print(f"   Weight: {data['cargo']['weight_lbs']} lbs")
    
except Exception as e:
    print(f"❌ Extraction failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 70)
print("✅ ALL TESTS PASSED!")
print("=" * 70)
print("\nYour Groq API is working correctly!")
print("The agent should work now.")