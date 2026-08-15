#!/usr/bin/env python3
"""
End-to-end verification script for NammaTN project
Tests all critical flows
"""

import requests
import json
import time
import sys

BASE_URL = "http://127.0.0.1:5000/api"
PASSES = 0
FAILURES = 0

def test(description, condition, details=""):
    global PASSES, FAILURES
    if condition:
        print(f"✅ {description}")
        if details:
            print(f"   {details}")
        PASSES += 1
    else:
        print(f"❌ {description}")
        if details:
            print(f"   {details}")
        FAILURES += 1

def test_citizen_registration():
    """Test 1: Citizen registration"""
    print("\n" + "="*60)
    print("TEST 1: CITIZEN REGISTRATION")
    print("="*60)
    
    email = f"citizen_{int(time.time())}@test.com"
    payload = {
        "name": "Test Citizen",
        "email": email,
        "phone": "9876543210",
        "password": "password123"
    }
    
    resp = requests.post(f"{BASE_URL}/auth/register", json=payload)
    test("Registration endpoint returns 201", resp.status_code == 201, f"Got {resp.status_code}")
    
    data = resp.json()
    token = data.get("token")
    test("Response contains token", bool(token), f"Token: {token[:20] if token else 'None'}...")
    test("User role is 'citizen'", data.get("user", {}).get("role") == "citizen", 
         f"Got role: {data.get('user', {}).get('role')}")
    test("User name in response", data.get("user", {}).get("name") == "Test Citizen", 
         f"Got name: {data.get('user', {}).get('name')}")
    
    return token, email

def test_citizen_login(email, password="password123"):
    """Test 2: Citizen login"""
    print("\n" + "="*60)
    print("TEST 2: CITIZEN LOGIN")
    print("="*60)
    
    payload = {"email": email, "password": password}
    resp = requests.post(f"{BASE_URL}/auth/login", json=payload)
    test("Login endpoint returns 200", resp.status_code == 200, f"Got {resp.status_code}")
    
    data = resp.json()
    token = data.get("token")
    test("Login response contains token", bool(token), f"Token: {token[:20] if token else 'None'}...")
    test("Login user role is 'citizen'", data.get("user", {}).get("role") == "citizen",
         f"Got role: {data.get('user', {}).get('role')}")
    
    return token

def test_get_current_user(token):
    """Test 3: Get current user info"""
    print("\n" + "="*60)
    print("TEST 3: GET CURRENT USER")
    print("="*60)
    
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    test("GET /auth/me returns 200", resp.status_code == 200, f"Got {resp.status_code}")
    
    data = resp.json()
    test("Current user has role", bool(data.get("role")), f"Role: {data.get('role')}")
    test("Current user role is 'citizen'", data.get("role") == "citizen",
         f"Got role: {data.get('role')}")

def test_ai_analysis_tamil(token):
    """Test 4: AI analyze Tamil complaint"""
    print("\n" + "="*60)
    print("TEST 4: AI ANALYSIS - TAMIL COMPLAINT")
    print("="*60)
    
    message = "enga street la 3 days ah street light work aagala"
    payload = {"message": message}
    
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.post(f"{BASE_URL}/ai/analyze", json=payload, headers=headers)
    test("AI analyze returns 200", resp.status_code == 200, f"Got {resp.status_code}")
    
    data = resp.json()
    test("Response has category", bool(data.get("category")), f"Category: {data.get('category')}")
    test("Category is 'streetlight'", data.get("category") == "streetlight",
         f"Got category: {data.get('category')}")
    test("Response has severity", bool(data.get("severity")), f"Severity: {data.get('severity')}")
    test("Severity is valid", data.get("severity") in ["low", "medium", "high"],
         f"Got severity: {data.get('severity')}")
    
    return data

def test_ai_analysis_tanglish(token):
    """Test 5: AI analyze Tanglish complaint"""
    print("\n" + "="*60)
    print("TEST 5: AI ANALYSIS - TANGLISH COMPLAINT")
    print("="*60)
    
    message = "Thiruvaiyaru main road la periya pothole irukku"
    payload = {"message": message}
    
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.post(f"{BASE_URL}/ai/analyze", json=payload, headers=headers)
    test("AI analyze Tanglish returns 200", resp.status_code == 200, f"Got {resp.status_code}")
    
    data = resp.json()
    test("Tanglish category detected", bool(data.get("category")), f"Category: {data.get('category')}")

def test_ai_analysis_english(token):
    """Test 6: AI analyze English complaint"""
    print("\n" + "="*60)
    print("TEST 6: AI ANALYSIS - ENGLISH COMPLAINT")
    print("="*60)
    
    message = "Water is not supplied to our area for 3 days"
    payload = {"message": message}
    
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.post(f"{BASE_URL}/ai/analyze", json=payload, headers=headers)
    test("AI analyze English returns 200", resp.status_code == 200, f"Got {resp.status_code}")
    
    data = resp.json()
    test("English category detected", bool(data.get("category")), f"Category: {data.get('category')}")

def test_create_complaint(token, analysis_data):
    """Test 7: Create complaint"""
    print("\n" + "="*60)
    print("TEST 7: CREATE COMPLAINT")
    print("="*60)
    
    payload = {
        "message": "enga street la 3 days ah street light work aagala",
        "category": analysis_data.get("category"),
        "severity": analysis_data.get("severity"),
        "district": "Thanjavur",
        "area": "Thiruvaiyaru",
        "duration": "3 days"
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.post(f"{BASE_URL}/complaints", json=payload, headers=headers)
    test("Create complaint returns 201", resp.status_code == 201, f"Got {resp.status_code}")
    
    data = resp.json()
    complaint_id = data.get("complaint_id")
    test("Response has complaint_id", bool(complaint_id), f"ID: {complaint_id}")
    test("Response has user_id", bool(data.get("user_id")), f"User ID: {bool(data.get('user_id'))}")
    test("Initial status is 'Submitted'", data.get("status") == "Submitted",
         f"Got status: {data.get('status')}")
    test("Message is stored", data.get("message") == payload["message"],
         f"Got message: {data.get('message')[:50]}...")
    test("Category is stored", data.get("category") == analysis_data.get("category"),
         f"Got category: {data.get('category')}")
    
    return complaint_id, data.get("user_id")

def test_citizen_my_complaints(token, expected_count=1):
    """Test 8: Citizen can view only their own complaints"""
    print("\n" + "="*60)
    print("TEST 8: CITIZEN VIEW OWN COMPLAINTS")
    print("="*60)
    
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(f"{BASE_URL}/complaints/my", headers=headers)
    test("GET /complaints/my returns 200", resp.status_code == 200, f"Got {resp.status_code}")
    
    data = resp.json()
    test("Response is a list", isinstance(data, list), f"Got type: {type(data)}")
    test(f"Citizen has at least {expected_count} complaint(s)", len(data) >= expected_count,
         f"Got {len(data)} complaints")
    
    if data:
        first_complaint = data[0]
        test("Complaint has complaint_id", bool(first_complaint.get("complaint_id")),
             f"ID: {first_complaint.get('complaint_id')}")
        test("Complaint has status", bool(first_complaint.get("status")),
             f"Status: {first_complaint.get('status')}")
    
    return data

def test_citizen_cannot_access_admin_api(token):
    """Test 9: Citizen cannot access admin-only endpoints"""
    print("\n" + "="*60)
    print("TEST 9: CITIZEN CANNOT ACCESS ADMIN ENDPOINTS")
    print("="*60)
    
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(f"{BASE_URL}/complaints", headers=headers)
    test("GET /complaints (admin only) returns 403 for citizen", resp.status_code == 403,
         f"Got {resp.status_code}")
    
    error = resp.json().get("error")
    test("Error message indicates forbidden", "Forbidden" in error or "forbidden" in error.lower(),
         f"Error: {error}")

def test_admin_login():
    """Test 10: Admin login"""
    print("\n" + "="*60)
    print("TEST 10: ADMIN LOGIN")
    print("="*60)
    
    payload = {
        "email": "admin@namma.tn",
        "password": "admin123"
    }
    
    resp = requests.post(f"{BASE_URL}/auth/login", json=payload)
    test("Admin login returns 200", resp.status_code == 200, f"Got {resp.status_code}")
    
    data = resp.json()
    token = data.get("token")
    test("Admin login has token", bool(token), f"Token: {token[:20] if token else 'None'}...")
    test("Admin role is 'admin'", data.get("user", {}).get("role") == "admin",
         f"Got role: {data.get('user', {}).get('role')}")
    
    return token

def test_admin_list_all_complaints(admin_token):
    """Test 11: Admin can view all complaints"""
    print("\n" + "="*60)
    print("TEST 11: ADMIN VIEW ALL COMPLAINTS")
    print("="*60)
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    resp = requests.get(f"{BASE_URL}/complaints", headers=headers)
    test("GET /complaints (admin) returns 200", resp.status_code == 200, f"Got {resp.status_code}")
    
    data = resp.json()
    test("Response is a list", isinstance(data, list), f"Got type: {type(data)}")
    test("Admin sees all complaints", len(data) >= 1, f"Got {len(data)} complaints")
    
    return data

def test_admin_update_complaint_status(admin_token, complaint_id):
    """Test 12: Admin can update complaint status"""
    print("\n" + "="*60)
    print("TEST 12: ADMIN UPDATE COMPLAINT STATUS")
    print("="*60)
    
    # Update to In Progress
    payload = {"status": "In Progress"}
    headers = {"Authorization": f"Bearer {admin_token}"}
    resp = requests.patch(f"{BASE_URL}/complaints/{complaint_id}", json=payload, headers=headers)
    test("PATCH status to 'In Progress' returns 200", resp.status_code == 200, f"Got {resp.status_code}")
    
    data = resp.json()
    test("Status updated to 'In Progress'", data.get("status") == "In Progress",
         f"Got status: {data.get('status')}")
    
    # Update to Resolved
    payload = {"status": "Resolved"}
    resp = requests.patch(f"{BASE_URL}/complaints/{complaint_id}", json=payload, headers=headers)
    test("PATCH status to 'Resolved' returns 200", resp.status_code == 200, f"Got {resp.status_code}")
    
    data = resp.json()
    test("Status updated to 'Resolved'", data.get("status") == "Resolved",
         f"Got status: {data.get('status')}")

def test_citizen_sees_updated_status(token, complaint_id):
    """Test 13: Citizen can see updated complaint status"""
    print("\n" + "="*60)
    print("TEST 13: CITIZEN SEES UPDATED STATUS")
    print("="*60)
    
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(f"{BASE_URL}/complaints/{complaint_id}", headers=headers)
    test("GET complaint by ID returns 200", resp.status_code == 200, f"Got {resp.status_code}")
    
    data = resp.json()
    test("Complaint status is 'Resolved'", data.get("status") == "Resolved",
         f"Got status: {data.get('status')}")

def test_logout(token):
    """Test 14: Logout works"""
    print("\n" + "="*60)
    print("TEST 14: LOGOUT")
    print("="*60)
    
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.post(f"{BASE_URL}/auth/logout", headers=headers)
    test("Logout returns 200", resp.status_code == 200, f"Got {resp.status_code}")
    
    data = resp.json()
    test("Logout response has status OK", data.get("status") == "ok",
         f"Got status: {data.get('status')}")

def run_all_tests():
    """Run all verification tests"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + "  NammaTN E2E VERIFICATION TEST SUITE".center(58) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝")
    
    global PASSES, FAILURES
    try:
        # Test citizen registration and login
        citizen_token, citizen_email = test_citizen_registration()
        citizen_token = test_citizen_login(citizen_email)
        test_get_current_user(citizen_token)
        
        # Test AI analysis
        tamil_analysis = test_ai_analysis_tamil(citizen_token)
        test_ai_analysis_tanglish(citizen_token)
        test_ai_analysis_english(citizen_token)
        
        # Test complaint creation
        complaint_id, user_id = test_create_complaint(citizen_token, tamil_analysis)
        
        # Test citizen complaint access
        complaints = test_citizen_my_complaints(citizen_token)
        test_citizen_cannot_access_admin_api(citizen_token)
        
        # Test admin login and actions
        admin_token = test_admin_login()
        all_complaints = test_admin_list_all_complaints(admin_token)
        test_admin_update_complaint_status(admin_token, complaint_id)
        
        # Verify citizen sees updates
        test_citizen_sees_updated_status(citizen_token, complaint_id)
        
        # Test logout
        test_logout(citizen_token)
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        FAILURES += 1
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"✅ PASSED: {PASSES}")
    print(f"❌ FAILED: {FAILURES}")
    total = PASSES + FAILURES
    print(f"📊 TOTAL:  {total}")
    print(f"📈 PASS RATE: {(PASSES/total*100):.1f}%" if total > 0 else "")
    print("="*60)
    
    return FAILURES == 0

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
