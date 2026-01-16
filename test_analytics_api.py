#!/usr/bin/env python
"""
Quick test script for Analytics API endpoints.

Usage:
    python test_analytics_api.py

Make sure the server is running:
    python manage.py runserver
"""

import requests
import json
from getpass import getpass

# Configuration
BASE_URL = "http://localhost:8000"

def print_section(title):
    """Print a formatted section header."""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def print_json(data):
    """Pretty print JSON data."""
    print(json.dumps(data, indent=2))

def main():
    print_section("Analytics API Test Script")

    # Get credentials
    print("\nEnter your ADMIN credentials:")
    username = input("Username: ")
    password = getpass("Password: ")

    # Step 1: Login
    print_section("Step 1: Login")
    try:
        login_response = requests.post(
            f"{BASE_URL}/api/v1/auth/login/",
            json={"username": username, "password": password},
            timeout=10
        )

        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            print(login_response.text)
            return

        token = login_response.json().get('access')
        print(f"✅ Login successful!")
        print(f"Token: {token[:20]}...")

    except requests.exceptions.ConnectionError:
        print("❌ Error: Cannot connect to server.")
        print("Make sure the server is running: python manage.py runserver")
        return
    except Exception as e:
        print(f"❌ Error during login: {e}")
        return

    # Set up headers
    headers = {"Authorization": f"Bearer {token}"}

    # Step 2: Test Dashboard KPIs
    print_section("Step 2: Dashboard KPIs")
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/analytics/dashboard/?days=30",
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:
            print("✅ Dashboard KPIs retrieved successfully!")
            print_json(response.json())
        elif response.status_code == 403:
            print("❌ Access denied. Your user must be an admin (is_staff=True)")
        else:
            print(f"❌ Failed: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Error: {e}")

    # Step 3: Test Revenue Metrics
    print_section("Step 3: Revenue Metrics")
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/analytics/revenue/metrics/",
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:
            print("✅ Revenue metrics retrieved successfully!")
            print_json(response.json())
        else:
            print(f"❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

    # Step 4: Test Daily Revenue
    print_section("Step 4: Daily Revenue")
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/analytics/revenue/daily/",
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Daily revenue data retrieved! ({len(data)} days)")
            if data:
                print("\nFirst 3 days:")
                print_json(data[:3])
            else:
                print("(No data - database might be empty)")
        else:
            print(f"❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

    # Step 5: Test Order Status
    print_section("Step 5: Order Status Breakdown")
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/analytics/orders/status/",
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:
            print("✅ Order status retrieved successfully!")
            print_json(response.json())
        else:
            print(f"❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

    # Step 6: Test User Metrics
    print_section("Step 6: User Metrics")
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/analytics/users/metrics/",
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:
            print("✅ User metrics retrieved successfully!")
            print_json(response.json())
        else:
            print(f"❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

    # Step 7: Test Product Performance
    print_section("Step 7: Product Performance")
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/analytics/products/performance/",
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Product performance retrieved! ({len(data)} products)")
            if data:
                print("\nTop 3 products:")
                print_json(data[:3])
            else:
                print("(No data - no paid orders with products yet)")
        else:
            print(f"❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

    # Step 8: Test Coupon Performance
    print_section("Step 8: Coupon Performance")
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/analytics/coupons/performance/",
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:
            print("✅ Coupon performance retrieved successfully!")
            print_json(response.json())
        else:
            print(f"❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

    # Step 9: Test Review Metrics
    print_section("Step 9: Review Metrics")
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/analytics/reviews/metrics/",
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:
            print("✅ Review metrics retrieved successfully!")
            print_json(response.json())
        else:
            print(f"❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

    # Summary
    print_section("Test Complete!")
    print("\n✅ All analytics endpoints are working!")
    print("\nNext steps:")
    print("1. View full API docs: http://localhost:8000/api/docs/")
    print("2. Create test data if responses are empty")
    print("3. Check TEST_ANALYTICS.md for more examples")

if __name__ == "__main__":
    main()
