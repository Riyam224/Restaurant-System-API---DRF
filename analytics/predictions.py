"""
Prediction Engine - Phase 4

Provides future insights:
- Order volume forecasting
- Optimal promotion timing
- Inventory risk signals

Uses statistical methods and pattern recognition.
For advanced ML predictions, integrate scikit-learn or similar libraries.
"""

from typing import Dict, List, Any, Tuple
from datetime import datetime, timedelta, time
from decimal import Decimal
from collections import defaultdict
from django.utils import timezone
from django.db.models import Sum, Count, Avg, F, Q
from django.core.cache import cache

from orders.models import Order, OrderItem
from menu.models import Product, ProductInventory
from coupons.models import Coupon, CouponUsage
from django.contrib.auth import get_user_model

User = get_user_model()


class PredictionEngine:
    """
    Generate predictions for restaurant operations.

    Uses historical data and pattern recognition to forecast:
    - Tomorrow's order volume
    - Best times for promotions
    - Inventory risks
    """

    @staticmethod
    def predict_tomorrow_orders() -> Dict[str, Any]:
        """
        Predict tomorrow's order volume and revenue.

        Uses:
        - Day-of-week patterns
        - Recent trend
        - Historical averages
        """
        cache_key = 'prediction_tomorrow_orders'
        cached = cache.get(cache_key)
        if cached:
            return cached

        tomorrow = timezone.now() + timedelta(days=1)
        tomorrow_weekday = tomorrow.weekday()  # 0=Monday, 6=Sunday

        # Get historical data for same day of week
        lookback_days = 28  # 4 weeks
        same_weekday_dates = []
        for weeks_back in range(1, 5):  # Last 4 occurrences of this weekday
            date = tomorrow - timedelta(weeks=weeks_back)
            same_weekday_dates.append(date)

        # Calculate average for this weekday
        weekday_orders = []
        weekday_revenue = []

        for date in same_weekday_dates:
            day_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)

            day_data = Order.objects.filter(
                created_at__range=[day_start, day_end],
                payment_status='paid'
            ).aggregate(
                order_count=Count('id'),
                total_revenue=Sum('total_price')
            )

            weekday_orders.append(day_data['order_count'] or 0)
            weekday_revenue.append(float(day_data['total_revenue'] or 0))

        # Calculate averages
        avg_orders = sum(weekday_orders) / len(weekday_orders) if weekday_orders else 0
        avg_revenue = sum(weekday_revenue) / len(weekday_revenue) if weekday_revenue else 0

        # Get recent trend (last 7 days vs previous 7 days)
        recent_trend = PredictionEngine._calculate_trend(days=7)

        # Adjust prediction based on trend
        trend_multiplier = 1.0 + (recent_trend / 100)  # Convert % to multiplier
        predicted_orders = int(avg_orders * trend_multiplier)
        predicted_revenue = avg_revenue * trend_multiplier

        # Calculate confidence based on data consistency
        if weekday_orders:
            variance = sum((x - avg_orders) ** 2 for x in weekday_orders) / len(weekday_orders)
            std_dev = variance ** 0.5
            confidence = max(0, min(100, 100 - (std_dev / avg_orders * 100))) if avg_orders > 0 else 50
        else:
            confidence = 0

        result = {
            'prediction_date': tomorrow.date().isoformat(),
            'day_of_week': tomorrow.strftime('%A'),
            'predicted_orders': predicted_orders,
            'predicted_revenue': round(predicted_revenue, 2),
            'confidence_score': round(confidence, 1),
            'historical_average': {
                'orders': round(avg_orders, 1),
                'revenue': round(avg_revenue, 2)
            },
            'recent_trend': {
                'percentage': round(recent_trend, 1),
                'direction': 'increasing' if recent_trend > 5 else ('decreasing' if recent_trend < -5 else 'stable')
            },
            'ranges': {
                'orders_min': max(0, int(predicted_orders * 0.8)),
                'orders_max': int(predicted_orders * 1.2),
                'revenue_min': round(predicted_revenue * 0.8, 2),
                'revenue_max': round(predicted_revenue * 1.2, 2)
            }
        }

        # Cache for 12 hours
        cache.set(cache_key, result, 43200)

        return result

    @staticmethod
    def predict_best_promo_times(days_ahead: int = 7) -> Dict[str, Any]:
        """
        Predict the best times to run promotions.

        Analyzes:
        - Low-traffic time periods
        - Day-of-week patterns
        - Historical coupon effectiveness
        - Slow business days
        """
        cache_key = f'prediction_promo_times_{days_ahead}'
        cached = cache.get(cache_key)
        if cached:
            return cached

        # Analyze historical patterns
        lookback_days = 60
        end_date = timezone.now()
        start_date = end_date - timedelta(days=lookback_days)

        # Get order volume by day of week
        weekday_volumes = defaultdict(list)

        current = start_date
        while current < end_date:
            day_start = current.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)

            count = Order.objects.filter(
                created_at__range=[day_start, day_end]
            ).count()

            weekday = current.weekday()
            weekday_volumes[weekday].append(count)

            current += timedelta(days=1)

        # Calculate average volume per weekday
        weekday_averages = {}
        for weekday, volumes in weekday_volumes.items():
            weekday_averages[weekday] = sum(volumes) / len(volumes) if volumes else 0

        # Find slowest days (best for promos)
        weekday_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        sorted_weekdays = sorted(weekday_averages.items(), key=lambda x: x[1])

        slow_days = []
        max_avg = max(weekday_averages.values()) if weekday_averages else 0
        for weekday, avg_orders in sorted_weekdays[:3]:  # Top 3 slowest days
            if max_avg > 0:
                opportunity_score = round((1 - avg_orders / max_avg) * 100, 1)
            else:
                opportunity_score = 0
            slow_days.append({
                'day': weekday_names[weekday],
                'weekday': weekday,
                'avg_orders': round(avg_orders, 1),
                'opportunity_score': opportunity_score
            })

        # Analyze historical coupon effectiveness
        coupon_effectiveness = PredictionEngine._analyze_coupon_effectiveness()

        # Generate recommendations for next N days
        recommendations = []
        for day_offset in range(days_ahead):
            date = timezone.now() + timedelta(days=day_offset + 1)
            weekday = date.weekday()

            is_slow_day = any(d['weekday'] == weekday for d in slow_days)
            avg_orders = weekday_averages.get(weekday, 0)

            if is_slow_day:
                recommendations.append({
                    'date': date.date().isoformat(),
                    'day': date.strftime('%A'),
                    'recommended': True,
                    'reason': f'Historically slow day (avg {avg_orders:.0f} orders)',
                    'suggested_discount': '15-20%',
                    'expected_lift': '25-40%',
                    'priority': 'high' if avg_orders < weekday_averages.get((weekday + 1) % 7, 0) * 0.7 else 'medium'
                })
            else:
                recommendations.append({
                    'date': date.date().isoformat(),
                    'day': date.strftime('%A'),
                    'recommended': False,
                    'reason': f'Normal traffic day (avg {avg_orders:.0f} orders)',
                    'suggested_discount': None,
                    'priority': 'low'
                })

        result = {
            'analysis_period_days': lookback_days,
            'slow_days': slow_days,
            'coupon_effectiveness': coupon_effectiveness,
            'recommendations': recommendations,
            'best_promo_days': [r for r in recommendations if r['recommended']]
        }

        # Cache for 24 hours
        cache.set(cache_key, result, 86400)

        return result

    @staticmethod
    def predict_inventory_risks(days_ahead: int = 7) -> Dict[str, Any]:
        """
        Predict inventory risks and stock-out probabilities.

        Analyzes:
        - Current stock levels
        - Historical consumption rates
        - Predicted demand
        - Lead time considerations
        """
        cache_key = f'prediction_inventory_risks_{days_ahead}'
        cached = cache.get(cache_key)
        if cached:
            return cached

        risks = []
        warnings = []

        # Calculate average daily consumption (last 30 days)
        lookback = 30

        # Get all products with inventory
        inventories = ProductInventory.objects.select_related('product').all()

        for inventory in inventories:
            product = inventory.product

            start_date = timezone.now() - timedelta(days=lookback)

            sold_quantity = OrderItem.objects.filter(
                order__created_at__gte=start_date,
                order__payment_status='paid',
                product_id=product.id
            ).aggregate(total=Sum('quantity'))['total'] or 0

            daily_consumption = sold_quantity / lookback if lookback > 0 else 0

            # Predict consumption for next N days
            predicted_consumption = daily_consumption * days_ahead

            # Calculate risk
            current_stock = inventory.quantity
            remaining_days = (current_stock / daily_consumption) if daily_consumption > 0 else 999

            # Determine risk level
            if remaining_days <= 2:
                risk_level = 'critical'
                priority = 1
            elif remaining_days <= 5:
                risk_level = 'high'
                priority = 2
            elif remaining_days <= 10:
                risk_level = 'medium'
                priority = 3
            else:
                risk_level = 'low'
                priority = 4

            risk_data = {
                'product_id': product.id,
                'product_name': product.name,
                'current_stock': current_stock,
                'daily_consumption': round(daily_consumption, 2),
                'predicted_consumption': round(predicted_consumption, 2),
                'remaining_days': round(remaining_days, 1),
                'risk_level': risk_level,
                'priority': priority,
                'stockout_date': (timezone.now() + timedelta(days=remaining_days)).date().isoformat() if remaining_days < 999 else None,
                'recommended_reorder_quantity': max(0, int(daily_consumption * 14 - current_stock))  # 2 weeks supply
            }

            if risk_level in ['critical', 'high']:
                risks.append(risk_data)
                warnings.append(f"{product.name}: Only {remaining_days:.1f} days of stock remaining")

        # Sort by priority
        risks.sort(key=lambda x: x['priority'])

        result = {
            'analysis_period_days': lookback,
            'forecast_days': days_ahead,
            'total_products_analyzed': inventories.count(),
            'high_risk_count': len([r for r in risks if r['risk_level'] in ['critical', 'high']]),
            'risks': risks[:20],  # Top 20 risks
            'warnings': warnings[:10],  # Top 10 warnings
            'recommendations': PredictionEngine._generate_inventory_recommendations(risks)
        }

        # Cache for 6 hours
        cache.set(cache_key, result, 21600)

        return result

    @staticmethod
    def _calculate_trend(days: int = 7) -> float:
        """
        Calculate recent trend percentage.

        Returns positive % for growth, negative % for decline.
        """
        end_date = timezone.now()
        mid_date = end_date - timedelta(days=days)
        start_date = mid_date - timedelta(days=days)

        # Recent period
        recent_revenue = Order.objects.filter(
            created_at__range=[mid_date, end_date],
            payment_status='paid'
        ).aggregate(total=Sum('total_price'))['total'] or Decimal('0')

        # Previous period
        previous_revenue = Order.objects.filter(
            created_at__range=[start_date, mid_date],
            payment_status='paid'
        ).aggregate(total=Sum('total_price'))['total'] or Decimal('0')

        if previous_revenue > 0:
            trend = ((float(recent_revenue) - float(previous_revenue)) / float(previous_revenue)) * 100
        else:
            trend = 0.0

        return trend

    @staticmethod
    def _analyze_coupon_effectiveness() -> Dict[str, Any]:
        """Analyze how effective coupons have been historically."""
        lookback_days = 60
        start_date = timezone.now() - timedelta(days=lookback_days)

        # Get coupon usage data
        coupon_orders = Order.objects.filter(
            created_at__gte=start_date,
            coupon_code__isnull=False
        ).count()

        total_orders = Order.objects.filter(
            created_at__gte=start_date
        ).count()

        coupon_usage_rate = (coupon_orders / total_orders * 100) if total_orders > 0 else 0

        # Get average discount amount
        avg_discount = Order.objects.filter(
            created_at__gte=start_date,
            coupon_code__isnull=False
        ).aggregate(avg=Avg('discount_amount'))['avg'] or 0

        return {
            'coupon_usage_rate': round(coupon_usage_rate, 1),
            'average_discount': round(float(avg_discount), 2),
            'total_coupon_orders': coupon_orders,
            'effectiveness': 'high' if coupon_usage_rate > 30 else ('medium' if coupon_usage_rate > 15 else 'low')
        }

    @staticmethod
    def _generate_inventory_recommendations(risks: List[Dict]) -> List[str]:
        """Generate actionable inventory recommendations."""
        recommendations = []

        critical_items = [r for r in risks if r['risk_level'] == 'critical']
        high_risk_items = [r for r in risks if r['risk_level'] == 'high']

        if critical_items:
            recommendations.append(
                f"URGENT: Reorder {len(critical_items)} critical items immediately (stock < 2 days)"
            )

        if high_risk_items:
            recommendations.append(
                f"HIGH PRIORITY: Plan reorders for {len(high_risk_items)} items (stock < 5 days)"
            )

        if not (critical_items or high_risk_items):
            recommendations.append("Inventory levels are healthy - no immediate action needed")

        # Add specific product recommendations
        for risk in risks[:3]:  # Top 3
            if risk['risk_level'] in ['critical', 'high']:
                recommendations.append(
                    f"Reorder {risk['product_name']}: {risk['recommended_reorder_quantity']} units "
                    f"(current: {risk['current_stock']}, {risk['remaining_days']:.1f} days left)"
                )

        return recommendations

    @staticmethod
    def get_prediction_summary() -> Dict[str, Any]:
        """
        Get a comprehensive prediction summary.

        Combines all prediction types for a dashboard overview.
        """
        tomorrow_prediction = PredictionEngine.predict_tomorrow_orders()
        promo_recommendations = PredictionEngine.predict_best_promo_times(days_ahead=7)
        inventory_risks = PredictionEngine.predict_inventory_risks(days_ahead=7)

        return {
            'generated_at': timezone.now().isoformat(),
            'tomorrow': tomorrow_prediction,
            'promotions': {
                'next_7_days': len(promo_recommendations['best_promo_days']),
                'best_days': [p['day'] for p in promo_recommendations['best_promo_days'][:3]],
                'slow_days': promo_recommendations['slow_days']
            },
            'inventory': {
                'high_risk_products': inventory_risks['high_risk_count'],
                'top_warnings': inventory_risks['warnings'][:5],
                'urgent_reorders': len([r for r in inventory_risks['risks'] if r['risk_level'] == 'critical'])
            },
            'action_items': PredictionEngine._generate_action_items(
                tomorrow_prediction,
                promo_recommendations,
                inventory_risks
            )
        }

    @staticmethod
    def _generate_action_items(
        tomorrow: Dict,
        promos: Dict,
        inventory_risks: Dict
    ) -> List[Dict[str, Any]]:
        """Generate prioritized action items from predictions."""
        actions = []

        # Tomorrow's preparation
        if tomorrow['predicted_orders'] > tomorrow['historical_average']['orders'] * 1.2:
            actions.append({
                'priority': 'high',
                'category': 'operations',
                'action': f"Prepare for high demand tomorrow: {tomorrow['predicted_orders']} orders expected",
                'impact': 'Avoid delays and stock-outs'
            })

        # Inventory urgency
        urgent_reorders = len([r for r in inventory_risks.get('risks', []) if r['risk_level'] == 'critical'])
        if urgent_reorders > 0:
            actions.append({
                'priority': 'critical',
                'category': 'inventory',
                'action': f"URGENT: Reorder {urgent_reorders} critical items",
                'impact': 'Prevent stock-outs and lost sales'
            })

        # Promotion opportunities
        if promos.get('best_promo_days'):
            next_promo = promos['best_promo_days'][0]
            actions.append({
                'priority': 'medium',
                'category': 'marketing',
                'action': f"Schedule promotion for {next_promo['day']} ({next_promo.get('reason', 'N/A')})",
                'impact': f"Expected {next_promo.get('expected_lift', 'N/A')} sales lift"
            })

        return sorted(actions, key=lambda x: {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}[x['priority']])