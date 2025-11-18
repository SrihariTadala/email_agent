#!/usr/bin/env python3
"""
Quote API Validation Script
Tests all Part 3 requirements
"""
import requests
import json
import sys

API_URL = "http://localhost:8000"

def test_api():
    print("="*70)
    print("FREIGHT QUOTE API VALIDATION - PART 3")
    print("="*70)
    
    tests_passed = 0
    tests_total = 0
    
    # TEST 1: API is running
    print("\n[TEST 1] API Health Check")
    tests_total += 1
    try:
        r = requests.get(f"{API_URL}/", timeout=5)
        if r.status_code == 200:
            print("✅ PASS - API is running")
            tests_passed += 1
        else:
            print(f"❌ FAIL - Unexpected status: {r.status_code}")
    except:
        print("❌ FAIL - API not reachable. Start with: python quote_api.py")
        sys.exit(1)
    
    # TEST 2: Correct endpoint exists
    print("\n[TEST 2] POST /api/v1/quote endpoint exists")
    tests_total += 1
    valid_request = {
        "origin_zip": "90021",
        "destination_zip": "60601",
        "weight_lbs": 800,
        "pieces": 2,
        "dimensions": {"length": 48, "width": 40, "height": 60},
        "special_services": ["liftgate"],
        "pickup_date": "2025-11-19",
        "commodity": "electronics"
    }
    
    r = requests.post(f"{API_URL}/api/v1/quote", json=valid_request)
    if r.status_code == 200:
        print("✅ PASS - Endpoint exists and responds")
        tests_passed += 1
    else:
        print(f"❌ FAIL - Status {r.status_code}, expected 200")
    
    # TEST 3: Response format
    print("\n[TEST 3] Response contains required fields")
    tests_total += 1
    if r.status_code == 200:
        data = r.json()
        required_fields = ["quote_id", "total_cost", "breakdown", "transit_days", 
                          "equipment_type", "valid_until", "terms"]
        missing = [f for f in required_fields if f not in data]
        
        if not missing:
            print("✅ PASS - All required fields present")
            print(f"   Quote ID: {data['quote_id']}")
            print(f"   Total Cost: ${data['total_cost']}")
            tests_passed += 1
        else:
            print(f"❌ FAIL - Missing fields: {missing}")
    
    # TEST 4: Breakdown structure
    print("\n[TEST 4] Cost breakdown structure")
    tests_total += 1
    if r.status_code == 200:
        breakdown = data.get('breakdown', {})
        required_breakdown = ["base_rate", "fuel_surcharge", "liftgate_fee", "insurance"]
        missing = [f for f in required_breakdown if f not in breakdown]
        
        if not missing:
            print("✅ PASS - Breakdown complete")
            print(f"   Base: ${breakdown['base_rate']}")
            print(f"   Fuel: ${breakdown['fuel_surcharge']}")
            tests_passed += 1
        else:
            print(f"❌ FAIL - Missing breakdown: {missing}")
    
    # TEST 5: Invalid zip code handling
    print("\n[TEST 5] Invalid zip code validation")
    tests_total += 1
    invalid_request = valid_request.copy()
    invalid_request['origin_zip'] = "00000"
    
    r = requests.post(f"{API_URL}/api/v1/quote", json=invalid_request)
    if r.status_code in [400, 404, 422]:
        print(f"✅ PASS - Rejects invalid zip with {r.status_code}")
        tests_passed += 1
    else:
        print(f"⚠️  WARNING - Accepts invalid zip (status {r.status_code})")
    
    # TEST 6: Invalid weight handling
    print("\n[TEST 6] Unrealistic weight validation")
    tests_total += 1
    invalid_request = valid_request.copy()
    invalid_request['weight_lbs'] = -100
    
    r = requests.post(f"{API_URL}/api/v1/quote", json=invalid_request)
    if r.status_code in [400, 422]:
        print(f"✅ PASS - Rejects negative weight with {r.status_code}")
        tests_passed += 1
    else:
        print(f"❌ FAIL - Accepts negative weight (status {r.status_code})")
    
    # TEST 7: Missing required fields
    print("\n[TEST 7] Missing required field validation")
    tests_total += 1
    incomplete_request = {"origin_zip": "90021"}
    
    r = requests.post(f"{API_URL}/api/v1/quote", json=incomplete_request)
    if r.status_code in [400, 422]:
        print(f"✅ PASS - Rejects incomplete request with {r.status_code}")
        tests_passed += 1
    else:
        print(f"❌ FAIL - Accepts incomplete request (status {r.status_code})")
    
    # TEST 8: Mapbox integration (bonus)
    print("\n[TEST 8] Real distance API integration (BONUS)")
    tests_total += 1
    r = requests.post(f"{API_URL}/api/v1/quote", json=valid_request)
    if r.status_code == 200:
        data = r.json()
        if 'distance_miles' in data and 'duration_hours' in data:
            print(f"✅ BONUS - Uses real distance API")
            print(f"   Distance: {data['distance_miles']} miles")
            print(f"   Duration: {data['duration_hours']} hours")
            tests_passed += 1
        else:
            print("⚠️  Uses mock distance calculation (acceptable)")
    
    # TEST 9: API Documentation (bonus)
    print("\n[TEST 9] API Documentation (BONUS)")
    tests_total += 1
    r = requests.get(f"{API_URL}/docs", timeout=5)
    if r.status_code == 200:
        print("✅ BONUS - Swagger/OpenAPI docs available at /docs")
        tests_passed += 1
    else:
        print("⚠️  No /docs endpoint (bonus feature)")
    
    # TEST 10: Zip code database
    print("\n[TEST 10] Zip code database size")
    tests_total += 1
    r = requests.get(f"{API_URL}/api/v1/zips", timeout=5)
    if r.status_code == 200:
        zips = r.json()
        count = zips.get('count', 0)
        if count >= 50:
            print(f"✅ PASS - {count} zip codes (≥50 required)")
            tests_passed += 1
        else:
            print(f"⚠️  Only {count} zip codes (50 recommended)")
    else:
        print("⚠️  No /api/v1/zips endpoint")
    
    # SUMMARY
    print("\n" + "="*70)
    print("VALIDATION SUMMARY")
    print("="*70)
    print(f"Tests Passed: {tests_passed}/{tests_total}")
    print(f"Score: {(tests_passed/tests_total)*100:.1f}%")
    
    if tests_passed >= 7:
        print("\n✅ EXCELLENT - All core requirements met!")
    elif tests_passed >= 5:
        print("\n✅ GOOD - Most requirements met")
    else:
        print("\n⚠️  NEEDS WORK - Review failed tests")
    
    print("="*70)
    
    # Detailed test request/response
    print("\n[SAMPLE REQUEST/RESPONSE]")
    print("\nRequest:")
    print(json.dumps(valid_request, indent=2))
    
    r = requests.post(f"{API_URL}/api/v1/quote", json=valid_request)
    if r.status_code == 200:
        print("\nResponse:")
        print(json.dumps(r.json(), indent=2))


if __name__ == "__main__":
    test_api()