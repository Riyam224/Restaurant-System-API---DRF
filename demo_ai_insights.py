#!/usr/bin/env python
"""
Live demo of Phase 2 AI Insights.

Shows real examples of natural language analytics.
"""

import requests
import json
from getpass import getpass

BASE_URL = "http://localhost:8000"

def print_header(text):
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70 + "\n")

def print_insight(data):
    """Pretty print an insight."""
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, list):
                print(f"{key.replace('_', ' ').title()}:")
                for item in value:
                    print(f"  • {item}")
            elif isinstance(value, dict):
                print(f"\n{key.replace('_', ' ').title()}:")
                for k, v in value.items():
                    print(f"  {k.replace('_', ' ').title()}: {v}")
            else:
                print(f"{key.replace('_', ' ').title()}: {value}")
            print()

def main():
    print_header("🤖 Phase 2: AI Insights Demo")

    # Get credentials
    print("Enter your ADMIN credentials:")
    username = input("Username: ")
    password = getpass("Password: ")

    # Login
    print("\n🔑 Logging in...")
    try:
        login_response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            json={"username": username, "password": password},
            timeout=10
        )

        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
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

        if response.status_code == 200:
            data = response.json()

            # Print headline
            print(f"📌 {data['headline']}\n")

            # Print summary
            print("Summary:")
            print(f"  {data['summary']}\n")

            # Print metrics
            print("Today's Metrics:")
            metrics = data['metrics']
            print(f"  💰 Revenue: ${metrics['revenue']:.2f}")
            print(f"  📦 Orders: {metrics['orders']}")
            print(f"  📊 Average Order Value: ${metrics['average_order_value']:.2f}\n")

            # Print insights
            if data['insights']:
                print("Key Insights:")
                for insight in data['insights']:
                    print(f"  💡 {insight}")
        else:
            print(f"❌ Failed: {response.status_code}")

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

        if response.status_code == 200:
            data = response.json()

            # Print explanation
            print(f"Metric: {data['metric'].upper()}")
            print(f"Trend: {data['trend'].upper()}")
            print(f"Change: {data['change']:.2f} ({data['change_percentage']:.1f}%)\n")

            print("Explanation:")
            print(f"  {data['explanation']}\n")

            # Print contributing factors
            if data['contributing_factors']:
                print("Contributing Factors:")
                for factor in data['contributing_factors']:
                    print(f"  ✓ {factor}")

            print(f"\nCurrent Value: ${data['current_value']:.2f}")
            print(f"Previous Value: ${data['previous_value']:.2f}")
        else:
            print(f"❌ Failed: {response.status_code}")

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

        if response.status_code == 200:
            data = response.json()

            # Print overview
            print(f"Period: {data['period']}\n")
            print("Business Overview:")
            print(f"  {data['overview']}\n")

            # Print opportunities
            if data['opportunities']:
                print("🌟 Opportunities:")
                for opp in data['opportunities']:
                    print(f"  • {opp}")
                print()

            # Print warnings
            if data['warnings']:
                print("⚠️  Warnings:")
                for warning in data['warnings']:
                    print(f"  • {warning}")
                print()

            # Print recommendations
            if data['recommendations']:
                print("💡 Recommendations:")
                for rec in data['recommendations']:
                    print(f"  • {rec}")
                print()

        else:
            print(f"❌ Failed: {response.status_code}")

    except Exception as e:
        print(f"❌ Error: {e}")

    # Summary
    print_header("✅ Phase 2 Demo Complete!")

    print("You just saw:")
    print("  ✅ Natural language daily summaries")
    print("  ✅ 'Why' explanations for metric changes")
    print("  ✅ Business insights and recommendations")
    print()
    print("All in plain English - no data science degree needed! 🎉")
    print()
    print("Next steps:")
    print("  1. Try in Swagger UI: http://localhost:8000/api/docs/")
    print("  2. Test different dates and metrics")
    print("  3. Integrate into your dashboard")
    print()
    print("Documentation:")
    print("  📖 docs/ANALYTICS_PHASE_2.md")
    print("  🧪 TEST_AI_INSIGHTS.md")

if __name__ == "__main__":
    main()
