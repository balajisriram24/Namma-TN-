#!/usr/bin/env python
import requests
import json

BASE_URL = "http://127.0.0.1:5000/api"

def test_register():
    """Test citizen registration"""
    print("\n=== TEST 1: Citizen Registration ===")
    payload = {
        "name": "Rajesh Kumar",
        "email": "rajesh@test.com",
        "phone": "9876543210",
        "password": "test123"
    }
    resp = requests.post(f"{BASE_URL}/auth/register", json=payload)
    print(f"Status: {resp.status_code}")
    data = resp.json()
    print(json.dumps(data, indent=2))
    return data.get("token") if resp.status_code == 201 else None

def test_login(email, password):
    """Test login"""
    print("\n=== TEST 2: Citizen Login ===")
    payload = {"email": email, "password": password}
    resp = requests.post(f"{BASE_URL}/auth/login", json=payload)
    print(f"Status: {resp.status_code}")
    data = resp.json()
    print(json.dumps(data, indent=2))
    return data.get("token") if resp.status_code == 200 else None

def test_me(token):
    """Test get current user"""
    print("\n=== TEST 3: Get Current User ===")
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    print(f"Status: {resp.status_code}")
    data = resp.json()
    print(json.dumps(data, indent=2))

def test_analyze(token):
    """Test AI analyze"""
    print("\n=== TEST 4: AI Analyze (Tamil complaint) ===")
    payload = {"message": "enga street la 3 days ah street light work aagala"}
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.post(f"{BASE_URL}/ai/analyze", json=payload, headers=headers)
    print(f"Status: {resp.status_code}")
    data = resp.json()
    print(json.dumps(data, indent=2))
    return data

def test_create_complaint(token, analysis):
    """Test create complaint"""
    print("\n=== TEST 5: Create Complaint ===")
    payload = {
        "message": "enga street la 3 days ah street light work aagala",
        "category": analysis.get("category"),
        "severity": analysis.get("severity"),
        "district": "Thanjavur",
        "area": "Thiruvaiyaru",
        "duration": "3 days"
    }
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.post(f"{BASE_URL}/complaints", json=payload, headers=headers)
    print(f"Status: {resp.status_code}")
    data = resp.json()
    print(json.dumps(data, indent=2))
    return data.get("complaint_id") if resp.status_code == 201 else None

def test_my_complaints(token):
    """Test get my complaints"""
    print("\n=== TEST 6: Get My Complaints ===")
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(f"{BASE_URL}/complaints/my", headers=headers)
    print(f"Status: {resp.status_code}")
    data = resp.json()
    print(json.dumps(data, indent=2))

def test_admin_login():
    """Test admin login"""
    print("\n=== TEST 7: Admin Login ===")
    payload = {"email": "admin@namma.tn", "password": "admin123"}
    resp = requests.post(f"{BASE_URL}/auth/login", json=payload)
    print(f"Status: {resp.status_code}")
    data = resp.json()
    print(json.dumps(data, indent=2))
    return data.get("token") if resp.status_code == 200 else None

def test_list_all_complaints(admin_token):
    """Test list all complaints (admin only)"""
    print("\n=== TEST 8: List All Complaints (Admin) ===")
    headers = {"Authorization": f"Bearer {admin_token}"}
    resp = requests.get(f"{BASE_URL}/complaints", headers=headers)
    print(f"Status: {resp.status_code}")
    data = resp.json()
    print(json.dumps(data, indent=2))

if __name__ == "__main__":
    try:
        # Test citizen flow
        citizen_token = test_register()
        if citizen_token:
            test_me(citizen_token)
            analysis = test_analyze(citizen_token)
            complaint_id = test_create_complaint(citizen_token, analysis)
            test_my_complaints(citizen_token)
        
        # Test admin flow
        admin_token = test_admin_login()
        if admin_token:
            test_list_all_complaints(admin_token)
        
        print("\n✅ All tests completed!")
    except Exception as e:
        print(f"❌ Error: {e}")
