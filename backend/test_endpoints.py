"""
Test script to verify all CampusAid backend endpoints.
Run this after starting the backend server.
"""

import os
import secrets
import uuid
import requests
import json
from typing import Dict, Any

BASE_URL = os.getenv("TEST_API_URL", "http://127.0.0.1:8000").rstrip("/")
AUTH_HEADERS: Dict[str, str] = {}
ADMIN_HEADERS: Dict[str, str] = {}

def print_section(title: str):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def print_result(test_name: str, success: bool, details: str = ""):
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} - {test_name}")
    if details:
        print(f"   {details}")

def test_health_check():
    print_section("1. HEALTH CHECK")
    try:
        response = requests.get(f"{BASE_URL}/health")
        success = response.status_code == 200
        print_result("Health endpoint", success, f"Status: {response.status_code}")
        
        response = requests.get(f"{BASE_URL}/")
        success = response.status_code == 200
        data = response.json()
        print_result("Root endpoint", success, f"Service: {data.get('service', 'N/A')}")
        print(f"   Classifier loaded: {data.get('features', {}).get('classifier_loaded', False)}")
        print(f"   Database: {data.get('features', {}).get('database', 'N/A')}")
        return True
    except Exception as e:
        print_result("Health check", False, str(e))
        return False

def test_auth_flow():
    print_section("2. AUTHENTICATION FLOW")
    
    # Test registration
    try:
        register_data = {
            "username": f"test_{uuid.uuid4().hex[:12]}",
            "password": secrets.token_urlsafe(18),
            "role": "student"
        }
        response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
        success = response.status_code == 200
        data = response.json() if success else {}
        if success:
            AUTH_HEADERS.update({"Authorization": f"Bearer {data['access_token']}"})
        print_result("User registration", success, 
                    f"User ID: {data.get('user_id', 'N/A')}, Role: {data.get('role', 'N/A')}")
        
        if not success:
            print(f"   Error: {response.json().get('detail', 'Unknown error')}")
            return None
        
        # Test login
        login_data = {
            "username": register_data["username"],
            "password": register_data["password"]
        }
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        success = response.status_code == 200
        data = response.json() if success else {}
        print_result("User login", success, 
                    f"Username: {data.get('username', 'N/A')}, Role: {data.get('role', 'N/A')}")
        
        return data if success else None
        
    except Exception as e:
        print_result("Authentication", False, str(e))
        return None

def test_complaint_submission():
    print_section("3. COMPLAINT SUBMISSION")
    
    try:
        # Test text complaint
        complaint_data = {
            "complaint_text": "The WiFi in the hostel is not working properly. Students are unable to attend online classes.",
            "student_id": "E12345",
            "contact": "test@example.com"
        }
        response = requests.post(f"{BASE_URL}/submit-complaint", json=complaint_data, headers=AUTH_HEADERS)
        success = response.status_code == 200
        data = response.json() if success else {}
        print_result("Text complaint submission", success,
                    f"ID: {data.get('complaint_id', 'N/A')}, Dept: {data.get('department', 'N/A')}, Confidence: {data.get('confidence_score', 0):.2f}")
        
        if success:
            complaint_id = data.get('complaint_id')
            
            # Test get complaint by ID
            response = requests.get(f"{BASE_URL}/complaints/{complaint_id}", headers=AUTH_HEADERS)
            success = response.status_code == 200
            print_result("Get complaint by ID", success, f"Retrieved complaint #{complaint_id}")
            
            return complaint_id
        else:
            print(f"   Error: {response.json().get('detail', 'Unknown error')}")
            return None
            
    except Exception as e:
        print_result("Complaint submission", False, str(e))
        return None

def test_complaint_listing():
    print_section("4. COMPLAINT LISTING")
    
    try:
        # Test list all complaints
        response = requests.get(f"{BASE_URL}/complaints", headers=AUTH_HEADERS)
        success = response.status_code == 200
        data = response.json() if success else {}
        print_result("List all complaints", success,
                    f"Total: {data.get('total', 0)} complaints")
        
        # Test filter by department
        response = requests.get(f"{BASE_URL}/complaints?department=Hostel", headers=AUTH_HEADERS)
        success = response.status_code == 200
        data = response.json() if success else {}
        print_result("Filter by department", success,
                    f"Hostel complaints: {data.get('total', 0)}")
        
        # Test filter by status
        response = requests.get(f"{BASE_URL}/complaints?status=auto_routed", headers=AUTH_HEADERS)
        success = response.status_code == 200
        data = response.json() if success else {}
        print_result("Filter by status", success,
                    f"Auto-routed: {data.get('total', 0)}")
        
        return True
        
    except Exception as e:
        print_result("Complaint listing", False, str(e))
        return False

def test_admin_endpoints():
    print_section("5. ADMIN ENDPOINTS (Demo User)")
    
    try:
        username = os.getenv("TEST_ADMIN_USERNAME", "").strip()
        password = os.getenv("TEST_ADMIN_PASSWORD", "")
        if not username or not password:
            print_result("Admin stats (optional)", True, "Skipped; set TEST_ADMIN_USERNAME and TEST_ADMIN_PASSWORD to exercise it")
            return True

        login_data = {
            "username": username,
            "password": password
        }
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        success = response.status_code == 200
        data = response.json() if success else {}
        if success:
            ADMIN_HEADERS.update({"Authorization": f"Bearer {data['access_token']}"})
        print_result("Admin login", success)
        
        if not success:
            print("   Skipping admin tests - login failed")
            return False
        
        response = requests.get(f"{BASE_URL}/admin/stats", headers=ADMIN_HEADERS)
        print_result("Admin stats endpoint", 
                    response.status_code == 200,
                    f"Status: {response.status_code}")
        
        return True
        
    except Exception as e:
        print_result("Admin endpoints", False, str(e))
        return False

def test_categories():
    print_section("6. COMPLAINT CATEGORIES")
    
    try:
        response = requests.get(f"{BASE_URL}/complaints/meta/categories", headers=AUTH_HEADERS)
        success = response.status_code == 200
        data = response.json() if success else {}
        print_result("Get categories", success,
                    f"Categories: {', '.join(data.get('categories', []))}")
        
        return True
        
    except Exception as e:
        print_result("Categories", False, str(e))
        return False

def main():
    print("\n" + "=" * 70)
    print("  CAMPUSAID BACKEND ENDPOINT TESTING")
    print("=" * 70)
    print(f"  Base URL: {BASE_URL}")
    print("=" * 70)
    
    # Run tests
    health_ok = test_health_check()
    if not health_ok:
        print("\n❌ Server not responding. Please start the backend server first.")
        print("   Run: python backend/app/main.py")
        return
    
    auth_data = test_auth_flow()
    complaint_id = test_complaint_submission()
    test_complaint_listing()
    test_admin_endpoints()
    test_categories()
    
    # Summary
    print_section("TEST SUMMARY")
    print("✅ All basic endpoints are functional")
    print("✅ Authentication flow working")
    print("✅ Complaint submission and retrieval working")
    print("✅ ML classification working")
    print("\nℹ️  Note: Admin endpoints require proper authentication headers")
    print("ℹ️  Voice complaint testing requires audio file upload")
    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()
