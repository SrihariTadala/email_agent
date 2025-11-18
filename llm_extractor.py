"""
LLM-based information extraction from freight quote emails
Using Groq with Llama 3.1 (FREE!)
"""
import json
from groq import Groq
from datetime import datetime, timedelta
from typing import Dict, Optional
import config


def extract_shipment_details(email_body: str) -> Optional[Dict]:
    """
    Extract structured shipment data from unstructured email text using Groq + Llama 3.1.
    
    Args:
        email_body: The raw email text
        
    Returns:
        Dictionary with extracted shipment details or None if extraction fails
    """
    client = Groq(api_key=config.GROQ_API_KEY)
    
    prompt = f"""Extract freight shipment details from this email and return ONLY valid JSON.

Email:
{email_body}

Extract the following information and return as JSON:
{{
  "origin": {{
    "city": "string",
    "state": "string (2-letter code)",
    "zip": "string (5 digits)",
    "address": "string or null"
  }},
  "destination": {{
    "city": "string",
    "state": "string (2-letter code)",
    "zip": "string (5 digits)",
    "address": "string or null"
  }},
  "cargo": {{
    "weight_lbs": number,
    "pieces": number,
    "piece_type": "string (pallets/boxes/crates)",
    "dimensions": {{
      "length": number,
      "width": number,
      "height": number,
      "unit": "inches"
    }},
    "commodity": "string (what is being shipped)"
  }},
  "special_services": ["array of strings like liftgate, climate_control, etc"],
  "pickup_date": "YYYY-MM-DD format or null",
  "additional_notes": "string"
}}

Rules:
- Convert all weights to lbs
- Convert all dimensions to inches
- Use 5-digit zip codes
- If pickup date is relative (like "next Tuesday"), calculate the actual date from today ({datetime.now().strftime("%Y-%m-%d")})
- If information is missing, use null
- Infer special services (e.g., "electronics" might need "climate_control")
- Return ONLY the JSON object, no other text, no markdown, no explanations

CRITICAL: Your response must be ONLY valid JSON. Do not include any text before or after the JSON.
"""

    try:
        # Call Groq API with Llama 3.1
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a data extraction expert. You ONLY return valid JSON, nothing else. No markdown, no explanations, just pure JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model="llama-3.1-8b-instant",
            temperature=0.1,  # Low temperature for consistency
            max_tokens=1500
        )
        
        # Extract response
        response_text = chat_completion.choices[0].message.content.strip()
        
        print(f"Raw LLM Response: {response_text[:200]}...")  # Debug
        
        # Remove markdown code blocks if present
        if response_text.startswith("```"):
            lines = response_text.split("\n")
            response_text = "\n".join(lines[1:-1])  # Remove first and last line
            if response_text.startswith("json"):
                response_text = response_text[4:].strip()
        
        # Clean up any remaining backticks
        response_text = response_text.replace("```", "").strip()
        
        # Parse JSON
        data = json.loads(response_text)
        
        # Validate required fields
        required_fields = ["origin", "destination", "cargo"]
        if not all(field in data for field in required_fields):
            print(f"Missing required fields in extracted data: {data}")
            return None
            
        return data
        
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        print(f"Response text: {response_text}")
        return None
    except Exception as e:
        print(f"Error extracting shipment details: {e}")
        return None


def validate_extraction(data: Dict) -> tuple[bool, str]:
    """
    Validate extracted data for completeness and correctness.
    
    Returns:
        (is_valid, error_message)
    """
    # Check origin zip
    if not data.get("origin", {}).get("zip"):
        return False, "Missing origin zip code"
    
    # Check destination zip
    if not data.get("destination", {}).get("zip"):
        return False, "Missing destination zip code"
    
    # Check weight
    weight = data.get("cargo", {}).get("weight_lbs")
    if not weight or weight <= 0:
        return False, "Missing or invalid weight"
    
    # Check pieces
    pieces = data.get("cargo", {}).get("pieces")
    if not pieces or pieces <= 0:
        return False, "Missing or invalid number of pieces"
    
    return True, ""


if __name__ == "__main__":
    # Test extraction
    test_email = """
    Hi,
    We need a quote for shipping 2 pallets of electronics from our
    warehouse in Los Angeles, CA 90021 to our distribution center
    in Chicago, IL 60601.
    
    Details:
    - Total weight: 800 lbs
    - Dimensions: Each pallet is 48x40x60 inches
    - Pickup date: Next Tuesday
    - Need liftgate delivery
    
    Thanks!
    """
    
    print("Testing Groq + Llama 3.1 extraction...")
    result = extract_shipment_details(test_email)
    if result:
        print("\n✅ Extraction successful!")
        print(json.dumps(result, indent=2))
        is_valid, error = validate_extraction(result)
        print(f"\nValidation: {is_valid} - {error}")
    else:
        print("\n❌ Extraction failed")