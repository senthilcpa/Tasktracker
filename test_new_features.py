#!/usr/bin/env python3
"""Comprehensive test for new features"""

import requests
from urllib.parse import urljoin

BASE_URL = 'http://localhost:5001'

def test_feature(name, url, expected_text=None):
    """Test a feature by making a request and checking for expected text"""
    try:
        response = requests.get(url)
        if response.status_code == 200:
            if expected_text is None or expected_text in response.text:
                print(f"✓ {name}: PASSED")
                return True
            else:
                print(f"✗ {name}: FAILED (expected text not found)")
                return False
        else:
            print(f"✗ {name}: FAILED (status {response.status_code})")
            return False
    except Exception as e:
        print(f"✗ {name}: FAILED ({str(e)})")
        return False

print("=" * 50)
print("Testing New Features")
print("=" * 50)

# Test reports page with clickable stat cards
test_feature("Reports page with clickable stat cards", 
             urljoin(BASE_URL, '/reports'),
             'stat-card-link')

# Test drill-down for all tasks
test_feature("Drill-down: All Tasks",
             urljoin(BASE_URL, '/reports/tasks/all'),
             'Showing')

# Test drill-down for completed tasks
test_feature("Drill-down: Completed Tasks",
             urljoin(BASE_URL, '/reports/tasks/completed'),
             'Showing')

# Test drill-down for pending tasks
test_feature("Drill-down: Pending Tasks",
             urljoin(BASE_URL, '/reports/tasks/pending'),
             'Showing')

# Test drill-down for overdue tasks
test_feature("Drill-down: Overdue Tasks",
             urljoin(BASE_URL, '/reports/tasks/overdue'),
             'Showing')

# Test search page
test_feature("Search page",
             urljoin(BASE_URL, '/search'),
             'Search Tasks')

# Test search functionality
test_feature("Search for 'meditation'",
             urljoin(BASE_URL, '/search?q=meditation'),
             'Found')

# Test search with filters
test_feature("Search with priority filter",
             urljoin(BASE_URL, '/search?q=task&priority=very_important'),
             'Found')

# Test dashboard with priority breakdown
test_feature("Dashboard with priority breakdown",
             urljoin(BASE_URL, '/'),
             'priority-breakdown-compact')

# Test navigation has search link
test_feature("Navigation has search link",
             urljoin(BASE_URL, '/'),
             '🔍 Search')

print("=" * 50)
print("All tests completed!")
print("=" * 50)
