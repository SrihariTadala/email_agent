"""
Test Script: Compare Mock Distance vs Real Distance APIs
Run this to see the difference!
"""
import requests
import json
from typing import Dict

def test_quote_api(origin: str, dest: str) -> Dict:
    """Test the quote API and return results"""
    
    response = requests.post(
        "http://localhost:8000/api/v1/quote",
        json={
            "origin_zip": origin,
            "destination_zip": dest,
            "weight_lbs": 800,
            "pieces": 2,
            "dimensions": {"length": 48, "width": 40, "height": 60},
            "special_services": ["liftgate"],
            "pickup_date": "2025-11-20",
            "commodity": "electronics"
        },
        timeout=10
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        return None


def format_duration(hours: float) -> str:
    """Format duration hours into readable string"""
    h = int(hours)
    m = int((hours - h) * 60)
    return f"{h}h {m}m"


def run_comparison():
    """Run comparison tests"""
    
    print("\n" + "="*80)
    print("DISTANCE API COMPARISON TEST")
    print("="*80)
    print()
    print("This compares MOCK distances (Haversine) vs REAL distances (API)")
    print()
    
    test_routes = [
        ("77001", "78701", "Houston, TX → Austin, TX"),
        ("90021", "60601", "Los Angeles, CA → Chicago, IL"),
        ("10001", "94102", "New York, NY → San Francisco, CA"),
        ("30303", "33602", "Atlanta, GA → Tampa, FL"),
        ("98101", "97201", "Seattle, WA → Portland, OR"),
    ]
    
    print(f"{'Route':<35} {'Distance':<20} {'Duration':<15} {'Cost':<10}")
    print("-" * 80)
    
    for origin, dest, route_name in test_routes:
        try:
            result = test_quote_api(origin, dest)
            
            if result:
                distance = result.get('distance_miles', 'N/A')
                duration = result.get('duration_hours', 0)
                cost = result.get('total_cost', 0)
                
                distance_str = f"{distance:.1f} miles" if isinstance(distance, float) else str(distance)
                duration_str = format_duration(duration) if duration else "N/A"
                cost_str = f"${cost:.2f}"
                
                print(f"{route_name:<35} {distance_str:<20} {duration_str:<15} {cost_str:<10}")
                
                # Show map URL if available
                if result.get('route_map_url'):
                    print(f"  📍 Map: {result['route_map_url'][:60]}...")
            else:
                print(f"{route_name:<35} {'ERROR':<20} {'ERROR':<15} {'ERROR':<10}")
                
        except Exception as e:
            print(f"{route_name:<35} ERROR: {str(e)}")
        
        print()
    
    print("="*80)
    print()
    print("💡 TIP: Open the map URLs in your browser to see the routes!")
    print()
    print("To see maps in PDFs:")
    print("  1. Send a test quote request email")
    print("  2. Run: python agent_oauth.py --once")
    print("  3. Open the generated PDF in ./quotes/")
    print()


if __name__ == "__main__":
    import sys
    
    # Check if API is running
    try:
        health = requests.get("http://localhost:8000/", timeout=5)
        if health.status_code == 200:
            api_info = health.json()
            print(f"\n✅ Connected to: {api_info.get('service', 'Quote API')}")
            print(f"   Version: {api_info.get('version', 'Unknown')}")
            
            # Check which API is being used
            if 'mapbox' in api_info:
                print(f"   Mapbox: {api_info['mapbox']}")
            elif 'google_maps' in api_info:
                print(f"   Google Maps: {api_info['google_maps']}")
            
            run_comparison()
        else:
            print("\n❌ Quote API is running but returned unexpected status")
            sys.exit(1)
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Quote API is not running!")
        print("\nPlease start the API first:")
        print("  python quote_api.py")
        print()
        print("Or if using Mapbox/Google Maps:")
        print("  python quote_api_mapbox.py")
        print("  python quote_api_google_maps.py")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        sys.exit(1)
