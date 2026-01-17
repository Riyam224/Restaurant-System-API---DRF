#!/usr/bin/env python
"""
Test Anomaly Detection System - Phase 3

Tests the anomaly detection endpoints with real data.
"""

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
    print_header("🔍 Phase 3: Anomaly Detection Demo")

    # Login
    print("🔑 Logging in...")
    try:
        login_response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            json={"username": USERNAME, "password": PASSWORD},
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
        return

    # Test 1: Anomaly Summary
    print_header("Test 1: Anomaly Summary 📊")

    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/analytics/anomalies/summary/?days=7",
            headers=headers,
            timeout=10
        )

        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()

            print(f"Period: Last {data['period_days']} days")
            print(f"Total Anomalies: {data['total_anomalies']}\n")

            print("Severity Breakdown:")
            for severity, count in data['severity_counts'].items():
                emoji = "🚨" if severity == "critical" else ("⚠️" if severity == "warning" else "ℹ️")
                print(f"  {emoji} {severity.capitalize()}: {count}")

            if data['type_counts']:
                print("\nTypes of Anomalies:")
                for anomaly_type, count in data['type_counts'].items():
                    print(f"  • {anomaly_type.replace('_', ' ').title()}: {count}")

        else:
            print(f"❌ Failed: {response.status_code}")
            print(response.text[:500])

    except Exception as e:
        print(f"❌ Error: {e}")

    # Test 2: Detailed Anomaly Detection
    print_header("Test 2: Detailed Anomaly Detection 🔍")

    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/analytics/anomalies/detect/?days=7",
            headers=headers,
            timeout=10
        )

        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()

            print(f"Summary: {data.get('summary', 'N/A')}\n")
            print(f"Pattern Analysis:\n  {data.get('pattern_analysis', 'N/A')}\n")

            # Show top anomalies
            anomalies = data.get('anomalies', [])
            if anomalies:
                print(f"Detected Anomalies ({len(anomalies)} total):\n")

                for i, anomaly in enumerate(anomalies[:5], 1):  # Top 5
                    severity_emoji = {
                        'critical': '🚨',
                        'warning': '⚠️',
                        'info': 'ℹ️'
                    }.get(anomaly['severity'], '•')

                    print(f"{severity_emoji} {i}. {anomaly['title']}")
                    print(f"   {anomaly.get('description', 'N/A')}")

                    if 'ai_explanation' in anomaly:
                        print(f"   💡 {anomaly['ai_explanation']}")

                    print()
            else:
                print("✅ No anomalies detected - operations appear normal!")

            # Recommendations
            if data.get('recommended_actions'):
                print("📋 Recommended Actions:")
                for action in data['recommended_actions']:
                    print(f"  • {action}")

        else:
            print(f"❌ Failed: {response.status_code}")
            print(response.text[:500])

    except Exception as e:
        print(f"❌ Error: {e}")

    # Test 3: Daily Digest
    print_header("Test 3: Daily Anomaly Digest 📧")

    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/analytics/anomalies/digest/",
            headers=headers,
            timeout=10
        )

        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()

            print(f"Date: {data['date']}")
            print(f"Anomalies: {data['anomaly_count']}")
            print(f"Has Critical: {'YES' if data['has_critical'] else 'No'}\n")

            print("Digest:")
            print(data['digest'])

        else:
            print(f"❌ Failed: {response.status_code}")
            print(response.text[:500])

    except Exception as e:
        print(f"❌ Error: {e}")

    # Summary
    print_header("✅ Phase 3 Tests Complete!")

    print("What you just tested:")
    print("  ✅ Anomaly summary (counts by severity/type)")
    print("  ✅ Detailed anomaly detection with explanations")
    print("  ✅ Daily digest (for notifications)")
    print()
    print("Anomaly Types Detected:")
    print("  • Revenue spikes/drops")
    print("  • Order volume anomalies")
    print("  • Coupon abuse patterns")
    print("  • User behavior anomalies")
    print()
    print("Next steps:")
    print("  1. Check Swagger UI: http://localhost:8000/api/docs/")
    print("  2. Test with different time periods")
    print("  3. Enable AI explanations: add ?use_ai=true")
    print("  4. Set up automated alerts/notifications")
    print()

if __name__ == "__main__":
    main()