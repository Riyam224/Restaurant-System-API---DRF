#!/usr/bin/env python
"""
Quick test of AI Insights with admin2 credentials.
"""

import sys
import os

# Add the project directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import requests
import json

BASE_URL = "http://localhost:8000"
USERNAME = "admin2"
PASSWORD = "1234"

def print_header(text):
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70 + "\n")

def main():
    print_header("🤖 AI Insights Demo - Quick Test")

    # Login
    print("🔑 Logging in as admin2...")
    try:
        login_response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            json={"username": USERNAME, "password": PASSWORD},
            timeout=10
        )

        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            print(f"Response: {login_response.text}")
            return

        token = login_response.json().get('access')
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Login successful!\n")

    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nMake sure the server is running: python manage.py runserver")
        return

    # Demo 1: What Happened Today?
    print_header("Demo 1: What Happened Today? 📊")

    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/analytics/insights/today/",
            headers=headers,
            timeout=10
        )

        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()

            # Print headline
            print(f"\n📌 {data.get('headline', 'N/A')}\n")

            # Print summary
            print("Summary:")
            print(f"  {data.get('summary', 'N/A')}\n")

            # Print metrics
            if 'metrics' in data:
                print("Today's Metrics:")
                metrics = data['metrics']
                print(f"  💰 Revenue: ${metrics.get('revenue', 0):.2f}")
                print(f"  📦 Orders: {metrics.get('orders', 0)}")
                print(f"  📊 Average Order Value: ${metrics.get('average_order_value', 0):.2f}\n")

            # Print insights
            if data.get('insights'):
                print("Key Insights:")
                for insight in data['insights']:
                    print(f"  💡 {insight}")
        else:
            print(f"❌ Failed: {response.status_code}")
            print(f"Response: {response.text[:500]}")

    except Exception as e:
        print(f"❌ Error: {e}")

    # Demo 2: Why Did Revenue Change?
    print_header("Demo 2: Why Did Revenue Change? 💡")

    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/analytics/insights/explain/?metric=revenue&days=30",
            headers=headers,
            timeout=10
        )

        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()

            # Print explanation
            print(f"\nMetric: {data.get('metric', 'N/A').upper()}")
            print(f"Trend: {data.get('trend', 'N/A').upper()}")
            print(f"Change: {data.get('change', 0):.2f} ({data.get('change_percentage', 0):.1f}%)\n")

            print("Explanation:")
            print(f"  {data.get('explanation', 'N/A')}\n")

            # Print contributing factors
            if data.get('contributing_factors'):
                print("Contributing Factors:")
                for factor in data['contributing_factors']:
                    print(f"  ✓ {factor}")

            print(f"\nCurrent Value: ${data.get('current_value', 0):.2f}")
            print(f"Previous Value: ${data.get('previous_value', 0):.2f}")
        else:
            print(f"❌ Failed: {response.status_code}")
            print(f"Response: {response.text[:500]}")

    except Exception as e:
        print(f"❌ Error: {e}")

    # Demo 3: Business Insights
    print_header("Demo 3: Business Insights & Recommendations 🎯")

    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/analytics/insights/business/?days=30",
            headers=headers,
            timeout=10
        )

        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()

            # Print overview
            print(f"\nPeriod: {data.get('period', 'N/A')}\n")
            print("Business Overview:")
            print(f"  {data.get('overview', 'N/A')}\n")

            # Print opportunities
            if data.get('opportunities'):
                print("🌟 Opportunities:")
                for opp in data['opportunities']:
                    print(f"  • {opp}")
                print()

            # Print warnings
            if data.get('warnings'):
                print("⚠️  Warnings:")
                for warning in data['warnings']:
                    print(f"  • {warning}")
                print()

            # Print recommendations
            if data.get('recommendations'):
                print("💡 Recommendations:")
                for rec in data['recommendations']:
                    print(f"  • {rec}")
                print()

        else:
            print(f"❌ Failed: {response.status_code}")
            print(f"Response: {response.text[:500]}")

    except Exception as e:
        print(f"❌ Error: {e}")

    # Summary
    print_header("✅ Test Complete!")

    print("What you just tested:")
    print("  ✅ Natural language daily summaries")
    print("  ✅ 'Why' explanations for metric changes")
    print("  ✅ Business insights and recommendations")
    print()
    print("Next steps:")
    print("  1. Try in Swagger UI: http://localhost:8000/api/docs/")
    print("  2. Run the full demo: python demo_ai_insights.py")
    print("  3. Integrate into your dashboard")
    print()

if __name__ == "__main__":
    main()