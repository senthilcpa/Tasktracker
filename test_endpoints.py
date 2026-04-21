#!/usr/bin/env python3
"""
Task Dashboard HTTP Endpoint Testing
Tests all API endpoints and form submissions
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5001"

def test_endpoint(method, endpoint, data=None, expected_status=200):
    """Test an endpoint and return result"""
    url = f"{BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url, timeout=5)
        elif method == "POST":
            response = requests.post(url, data=data, timeout=5, allow_redirects=True)
        else:
            return False, f"Unknown method: {method}"
        
        status_ok = response.status_code == expected_status
        return status_ok, response.status_code
    except Exception as e:
        return False, str(e)

print("=" * 50)
print("Task Dashboard - HTTP Endpoint Testing")
print("=" * 50)

tests = [
    ("Dashboard Home", "GET", "/", None, 200),
    ("Add Task Form", "GET", "/add", None, 200),
    ("API Stats", "GET", "/api/stats", None, 200),
    ("API Tasks List", "GET", "/api/tasks", None, 200),
]

print("\n1. Testing Basic Endpoints:")
passed = 0
for name, method, endpoint, data, expected in tests:
    success, code = test_endpoint(method, endpoint, data, expected)
    status_text = "✓ PASS" if success else f"✗ FAIL ({code})"
    print(f"   {status_text} - {name}")
    if success:
        passed += 1

print("\n2. Testing Task Creation:")
task_data = {
    "title": "Integration Test Task",
    "description": "Testing task creation via POST",
    "due_date": "2026-03-27",
    "recurrence_type": "once"
}

success, code = test_endpoint("POST", "/add", task_data, 200)
status_text = "✓ PASS" if success else f"✗ FAIL ({code})"
print(f"   {status_text} - Create Single Task (HTTP {code})")
if success:
    passed += 1

print("\n3. Testing Daily Recurring Task:")
daily_task_data = {
    "title": "Daily Test Task",
    "description": "Daily recurring task",
    "due_date": "2026-03-26",
    "recurrence_type": "daily",
    "recurrence_end_date": "2026-04-05"
}

success, code = test_endpoint("POST", "/add", daily_task_data, 200)
status_text = "✓ PASS" if success else f"✗ FAIL ({code})"
print(f"   {status_text} - Create Daily Task (HTTP {code})")
if success:
    passed += 1

print("\n4. Testing Selective Dates Task:")
selective_task_data = {
    "title": "Selective Dates Task",
    "description": "Task with selective dates",
    "due_date": "2026-03-26",
    "recurrence_type": "selective",
    "selective_dates": json.dumps(["2026-03-27", "2026-03-29", "2026-03-31"])
}

success, code = test_endpoint("POST", "/add", selective_task_data, 200)
status_text = "✓ PASS" if success else f"✗ FAIL ({code})"
print(f"   {status_text} - Create Selective Dates Task (HTTP {code})")
if success:
    passed += 1

print("\n5. Testing API Responses:")
try:
    response = requests.get(f"{BASE_URL}/api/tasks", timeout=5)
    tasks = response.json()
    print(f"   ✓ PASS - API returns {len(tasks)} tasks")
    passed += 1
except Exception as e:
    print(f"   ✗ FAIL - {str(e)}")

try:
    response = requests.get(f"{BASE_URL}/api/stats", timeout=5)
    stats = response.json()
    print(f"   ✓ PASS - Stats: {stats['total']} total, {stats['completed']} completed, {stats['pending']} pending")
    passed += 1
except Exception as e:
    print(f"   ✗ FAIL - {str(e)}")

print("\n6. Testing Static Files:")
for file_path, file_name in [("/static/styles.css", "CSS"), ("/static/script.js", "JavaScript")]:
    success, code = test_endpoint("GET", file_path, None, 200)
    status_text = "✓ PASS" if success else f"✗ FAIL ({code})"
    print(f"   {status_text} - {file_name} file loads")
    if success:
        passed += 1

total_tests = 11
print("\n" + "=" * 50)
print(f"Results: {passed}/{total_tests} tests passed")
print("=" * 50)

if passed == total_tests:
    print("\n✓ ALL TESTS PASSED - APP IS FULLY FUNCTIONAL!")
else:
    print(f"\n⚠ {total_tests - passed} test(s) failed - Please check the errors above")
