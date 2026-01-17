#!/usr/bin/env python
"""
Test Prediction System - Phase 4

Tests the predictive analytics endpoints.
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
    print_header("🔮 Phase 4: Predictions Demo")

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

    # Test 1: Predict Tomorrow's Orders
    print_header("Test 1: Tomorrow's Forecast 📈")

    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/analytics/predictions/tomorrow/",
            headers=headers,
            timeout=10
        )

        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()

            print(f"📅 Prediction for: {data['prediction_date']} ({data['day_of_week']})\n")

            print(f"Predicted Orders: {data['predicted_orders']}")
            print(f"Predicted Revenue: ${data['predicted_revenue']:.2f}")
            print(f"Confidence Score: {data['confidence_score']:.1f}%\n")

            print("Range Estimates:")
            print(f"  Orders: {data['ranges']['orders_min']} - {data['ranges']['orders_max']}")
            print(f"  Revenue: ${data['ranges']['revenue_min']:.2f} - ${data['ranges']['revenue_max']:.2f}\n")

            print("Historical Average:")
            print(f"  Orders: {data['historical_average']['orders']}")
            print(f"  Revenue: ${data['historical_average']['revenue']:.2f}\n")

            trend = data['recent_trend']
            trend_emoji = "📈" if trend['direction'] == 'increasing' else ("📉" if trend['direction'] == 'decreasing' else "➡️")
            print(f"Recent Trend: {trend_emoji} {trend['direction'].capitalize()} ({trend['percentage']:+.1f}%)")

        else:
            print(f"❌ Failed: {response.status_code}")
            print(response.text[:500])

    except Exception as e:
        print(f"❌ Error: {e}")

    # Test 2: Best Promo Times
    print_header("Test 2: Best Promotion Times 🎯")

    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/analytics/predictions/promo-times/?days_ahead=7",
            headers=headers,
            timeout=10
        )

        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()

            print(f"Analysis Period: Last {data['analysis_period_days']} days\n")

            print("Slowest Days (Best for Promos):")
            for slow_day in data['slow_days']:
                print(f"  • {slow_day['day']}: {slow_day['avg_orders']:.1f} avg orders")
                print(f"    Opportunity Score: {slow_day['opportunity_score']:.1f}%")

            print(f"\nCoupon Effectiveness: {data['coupon_effectiveness']['effectiveness'].upper()}")
            print(f"  Usage Rate: {data['coupon_effectiveness']['coupon_usage_rate']:.1f}%")
            print(f"  Avg Discount: ${data['coupon_effectiveness']['average_discount']:.2f}\n")

            print("Next 7 Days Recommendations:")
            for rec in data['recommendations'][:7]:
                if rec['recommended']:
                    print(f"  ✅ {rec['date']} ({rec['day']}) - {rec['priority'].upper()}")
                    print(f"     {rec['reason']}")
                    print(f"     Suggested: {rec['suggested_discount']} discount")
                    print(f"     Expected Lift: {rec['expected_lift']}")
                else:
                    print(f"  ⏭️  {rec['date']} ({rec['day']}) - {rec['reason']}")

        else:
            print(f"❌ Failed: {response.status_code}")
            print(response.text[:500])

    except Exception as e:
        print(f"❌ Error: {e}")

    # Test 3: Inventory Risks
    print_header("Test 3: Inventory Risk Forecast ⚠️")

    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/analytics/predictions/inventory-risks/?days_ahead=7",
            headers=headers,
            timeout=10
        )

        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()

            print(f"Forecast Period: Next {data['forecast_days']} days")
            print(f"Products Analyzed: {data['total_products_analyzed']}")
            print(f"High Risk Items: {data['high_risk_count']}\n")

            if data['warnings']:
                print("⚠️  Warnings:")
                for warning in data['warnings']:
                    print(f"  • {warning}")
                print()

            if data['risks']:
                print("Top Inventory Risks:")
                for i, risk in enumerate(data['risks'][:5], 1):
                    risk_emoji = "🚨" if risk['risk_level'] == 'critical' else ("⚠️" if risk['risk_level'] == 'high' else "ℹ️")
                    print(f"\n{risk_emoji} {i}. {risk['product_name']}")
                    print(f"   Current Stock: {risk['current_stock']} units")
                    print(f"   Daily Consumption: {risk['daily_consumption']:.2f} units/day")
                    print(f"   Days Remaining: {risk['remaining_days']:.1f} days")
                    print(f"   Risk Level: {risk['risk_level'].upper()}")
                    if risk['stockout_date']:
                        print(f"   Stock-Out Date: {risk['stockout_date']}")
                    print(f"   Recommended Reorder: {risk['recommended_reorder_quantity']} units")
            else:
                print("✅ No high-risk inventory items!")

            if data['recommendations']:
                print("\n📋 Recommendations:")
                for rec in data['recommendations']:
                    print(f"  • {rec}")

        else:
            print(f"❌ Failed: {response.status_code}")
            print(response.text[:500])

    except Exception as e:
        print(f"❌ Error: {e}")

    # Test 4: Prediction Summary
    print_header("Test 4: Comprehensive Prediction Summary 📊")

    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/analytics/predictions/summary/",
            headers=headers,
            timeout=10
        )

        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()

            print(f"Generated at: {data['generated_at']}\n")

            print("📈 Tomorrow's Forecast:")
            tomorrow = data['tomorrow']
            print(f"  {tomorrow['predicted_orders']} orders, ${tomorrow['predicted_revenue']:.2f} revenue")
            print(f"  Confidence: {tomorrow['confidence_score']:.1f}%\n")

            print("🎯 Promotions (Next 7 Days):")
            promos = data['promotions']
            print(f"  Best Days: {', '.join(promos['best_days'][:3])}")
            print(f"  Total Opportunities: {promos['next_7_days']}\n")

            print("📦 Inventory Status:")
            inventory = data['inventory']
            print(f"  High Risk Products: {inventory['high_risk_products']}")
            print(f"  Urgent Reorders: {inventory['urgent_reorders']}\n")

            if data['action_items']:
                print("🎯 Priority Action Items:")
                for action in data['action_items']:
                    priority_emoji = {'critical': '🚨', 'high': '⚠️', 'medium': 'ℹ️', 'low': '💡'}
                    emoji = priority_emoji.get(action['priority'], '•')
                    print(f"  {emoji} [{action['priority'].upper()}] {action['action']}")
                    print(f"     Impact: {action['impact']}")

        else:
            print(f"❌ Failed: {response.status_code}")
            print(response.text[:500])

    except Exception as e:
        print(f"❌ Error: {e}")

    # Summary
    print_header("✅ Phase 4 Tests Complete!")

    print("What you just tested:")
    print("  ✅ Tomorrow's order/revenue forecast")
    print("  ✅ Best promotional timing recommendations")
    print("  ✅ Inventory risk predictions")
    print("  ✅ Comprehensive prediction summary")
    print()
    print("Prediction Types:")
    print("  📈 Order Volume Forecasting - Based on day-of-week patterns")
    print("  🎯 Promotion Optimization - Identifies slow days")
    print("  📦 Inventory Risk Analysis - Predicts stock-outs")
    print()
    print("Next steps:")
    print("  1. Check Swagger UI: http://localhost:8000/api/docs/")
    print("  2. Integrate predictions into your dashboard")
    print("  3. Set up automated forecasting reports")
    print("  4. Use insights for staff scheduling and inventory planning")
    print()

if __name__ == "__main__":
    main()