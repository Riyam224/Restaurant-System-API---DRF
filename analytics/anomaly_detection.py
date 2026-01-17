"""
Anomaly Detection Service - Phase 3

Detects unusual patterns in restaurant operations:
- Revenue spikes/drops
- Order volume anomalies
- Coupon abuse patterns
- User behavior anomalies

Provides AI-powered explanations for detected anomalies.
"""

from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime, timedelta
from decimal import Decimal
from django.utils import timezone
from django.db.models import Sum, Count, Avg, Q
from django.core.cache import cache

from orders.models import Order
from coupons.models import CouponUsage
from django.contrib.auth import get_user_model

User = get_user_model()


class AnomalyDetector:
    """
    Detect anomalies in restaurant operations.

    Uses statistical methods and business rules to identify:
    - Unusual revenue patterns
    - Suspicious coupon usage
    - Order volume spikes/drops
    - User behavior anomalies
    """

    # Thresholds for anomaly detection
    REVENUE_SPIKE_THRESHOLD = 2.0  # 2x normal is a spike
    REVENUE_DROP_THRESHOLD = 0.5   # 50% of normal is a drop
    ORDER_SPIKE_THRESHOLD = 2.0
    ORDER_DROP_THRESHOLD = 0.5

    # Coupon abuse thresholds
    MAX_COUPON_USES_PER_USER_PER_DAY = 3
    MAX_COUPON_USERS_PER_IP = 10  # Same coupon from many users on same IP
    SUSPICIOUS_DISCOUNT_PERCENTAGE = 90  # Over 90% discount is suspicious

    @staticmethod
    def detect_all_anomalies(days: int = 7) -> List[Dict[str, Any]]:
        """
        Detect all types of anomalies in the specified period.

        Args:
            days: Number of days to analyze

        Returns:
            List of detected anomalies with severity and explanations
        """
        anomalies = []

        # Revenue anomalies
        revenue_anomalies = AnomalyDetector.detect_revenue_anomalies(days)
        anomalies.extend(revenue_anomalies)

        # Order volume anomalies
        order_anomalies = AnomalyDetector.detect_order_anomalies(days)
        anomalies.extend(order_anomalies)

        # Coupon abuse
        coupon_anomalies = AnomalyDetector.detect_coupon_abuse(days)
        anomalies.extend(coupon_anomalies)

        # User behavior anomalies
        user_anomalies = AnomalyDetector.detect_user_anomalies(days)
        anomalies.extend(user_anomalies)

        # Sort by severity (critical > warning > info)
        severity_order = {'critical': 0, 'warning': 1, 'info': 2}
        anomalies.sort(key=lambda x: severity_order.get(x['severity'], 3))

        return anomalies

    @staticmethod
    def detect_revenue_anomalies(days: int = 7) -> List[Dict[str, Any]]:
        """
        Detect unusual revenue patterns (spikes or drops).

        Compares daily revenue to historical baseline.
        """
        anomalies = []
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        baseline_start = start_date - timedelta(days=days * 2)

        # Get baseline (previous period average)
        baseline_orders = Order.objects.filter(
            created_at__range=[baseline_start, start_date],
            payment_status='paid'
        )
        baseline_revenue = baseline_orders.aggregate(
            total=Sum('total_price')
        )['total'] or Decimal('0')
        baseline_days = (start_date - baseline_start).days
        baseline_avg_per_day = float(baseline_revenue) / baseline_days if baseline_days > 0 else 0

        # Check each day in the period
        for day_offset in range(days):
            day_start = start_date + timedelta(days=day_offset)
            day_end = day_start + timedelta(days=1)

            # Get day's revenue
            day_revenue = Order.objects.filter(
                created_at__range=[day_start, day_end],
                payment_status='paid'
            ).aggregate(total=Sum('total_price'))['total'] or Decimal('0')
            day_revenue = float(day_revenue)

            # Compare to baseline
            if baseline_avg_per_day > 0:
                ratio = day_revenue / baseline_avg_per_day

                # Spike detected
                if ratio >= AnomalyDetector.REVENUE_SPIKE_THRESHOLD:
                    anomalies.append({
                        'type': 'revenue_spike',
                        'severity': 'info' if ratio < 3 else 'warning',
                        'date': day_start.date().isoformat(),
                        'metric': 'revenue',
                        'value': day_revenue,
                        'baseline': baseline_avg_per_day,
                        'change_ratio': ratio,
                        'change_percentage': (ratio - 1) * 100,
                        'title': f'Revenue Spike on {day_start.strftime("%A")}',
                        'description': f'Revenue reached ${day_revenue:.2f}, which is {ratio:.1f}x the normal daily average of ${baseline_avg_per_day:.2f}.',
                        'possible_reasons': AnomalyDetector._analyze_revenue_spike(day_start, day_end)
                    })

                # Drop detected
                elif ratio <= AnomalyDetector.REVENUE_DROP_THRESHOLD:
                    anomalies.append({
                        'type': 'revenue_drop',
                        'severity': 'warning' if ratio < 0.3 else 'info',
                        'date': day_start.date().isoformat(),
                        'metric': 'revenue',
                        'value': day_revenue,
                        'baseline': baseline_avg_per_day,
                        'change_ratio': ratio,
                        'change_percentage': (ratio - 1) * 100,
                        'title': f'Revenue Drop on {day_start.strftime("%A")}',
                        'description': f'Revenue was only ${day_revenue:.2f}, which is {(1-ratio)*100:.0f}% below the normal daily average of ${baseline_avg_per_day:.2f}.',
                        'possible_reasons': AnomalyDetector._analyze_revenue_drop(day_start, day_end)
                    })

        return anomalies

    @staticmethod
    def detect_order_anomalies(days: int = 7) -> List[Dict[str, Any]]:
        """
        Detect unusual order volume patterns.
        """
        anomalies = []
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        baseline_start = start_date - timedelta(days=days * 2)

        # Get baseline
        baseline_count = Order.objects.filter(
            created_at__range=[baseline_start, start_date]
        ).count()
        baseline_days = (start_date - baseline_start).days
        baseline_avg_per_day = baseline_count / baseline_days if baseline_days > 0 else 0

        # Check each day
        for day_offset in range(days):
            day_start = start_date + timedelta(days=day_offset)
            day_end = day_start + timedelta(days=1)

            day_count = Order.objects.filter(
                created_at__range=[day_start, day_end]
            ).count()

            if baseline_avg_per_day > 0:
                ratio = day_count / baseline_avg_per_day

                # Spike
                if ratio >= AnomalyDetector.ORDER_SPIKE_THRESHOLD:
                    anomalies.append({
                        'type': 'order_spike',
                        'severity': 'info',
                        'date': day_start.date().isoformat(),
                        'metric': 'orders',
                        'value': day_count,
                        'baseline': baseline_avg_per_day,
                        'change_ratio': ratio,
                        'change_percentage': (ratio - 1) * 100,
                        'title': f'Order Surge on {day_start.strftime("%A")}',
                        'description': f'Received {day_count} orders, {ratio:.1f}x the normal daily average of {baseline_avg_per_day:.1f}.',
                        'possible_reasons': ['Marketing campaign success', 'Weekend/holiday effect', 'Competitor closure', 'Special event nearby']
                    })

                # Drop
                elif ratio <= AnomalyDetector.ORDER_DROP_THRESHOLD:
                    anomalies.append({
                        'type': 'order_drop',
                        'severity': 'warning',
                        'date': day_start.date().isoformat(),
                        'metric': 'orders',
                        'value': day_count,
                        'baseline': baseline_avg_per_day,
                        'change_ratio': ratio,
                        'change_percentage': (ratio - 1) * 100,
                        'title': f'Low Order Volume on {day_start.strftime("%A")}',
                        'description': f'Only {day_count} orders received, {(1-ratio)*100:.0f}% below the normal daily average.',
                        'possible_reasons': ['Technical issues', 'Competitor promotion', 'Bad weather', 'Service disruption']
                    })

        return anomalies

    @staticmethod
    def detect_coupon_abuse(days: int = 7) -> List[Dict[str, Any]]:
        """
        Detect suspicious coupon usage patterns.
        """
        anomalies = []
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)

        # 1. Check for users with excessive coupon usage
        heavy_users = CouponUsage.objects.filter(
            used_at__range=[start_date, end_date]
        ).values('user').annotate(
            usage_count=Count('id'),
            total_discount=Sum('discount_amount')
        ).filter(
            usage_count__gt=AnomalyDetector.MAX_COUPON_USES_PER_USER_PER_DAY * days
        )

        for user_data in heavy_users:
            user = User.objects.get(id=user_data['user'])
            anomalies.append({
                'type': 'coupon_abuse_heavy_usage',
                'severity': 'warning',
                'date': timezone.now().date().isoformat(),
                'metric': 'coupon_usage',
                'value': user_data['usage_count'],
                'threshold': AnomalyDetector.MAX_COUPON_USES_PER_USER_PER_DAY * days,
                'user_id': user.id,
                'username': user.username,
                'title': f'Excessive Coupon Usage by {user.username}',
                'description': f'User has used coupons {user_data["usage_count"]} times in {days} days, receiving ${user_data["total_discount"]:.2f} in discounts.',
                'possible_reasons': ['Account sharing', 'Coupon farming', 'Multiple accounts', 'Legitimate power user'],
                'recommended_action': 'Review account activity and consider usage limits'
            })

        # 2. Check for suspiciously high discounts
        suspicious_orders_qs = Order.objects.filter(
            created_at__range=[start_date, end_date],
            coupon_code__isnull=False,
            subtotal__gt=0
        )

        # Calculate discount percentage in Python (not in SQL)
        suspicious_orders = []
        for order in suspicious_orders_qs:
            discount_pct = (float(order.discount_amount) / float(order.subtotal) * 100) if order.subtotal > 0 else 0
            if discount_pct >= AnomalyDetector.SUSPICIOUS_DISCOUNT_PERCENTAGE:
                suspicious_orders.append((order, discount_pct))

        for order, discount_pct in suspicious_orders[:5]:  # Limit to top 5
            anomalies.append({
                'type': 'coupon_abuse_high_discount',
                'severity': 'critical',
                'date': order.created_at.date().isoformat(),
                'metric': 'discount_percentage',
                'value': discount_pct,
                'threshold': AnomalyDetector.SUSPICIOUS_DISCOUNT_PERCENTAGE,
                'order_id': order.id,
                'user_id': order.user.id,
                'username': order.user.username,
                'coupon_code': order.coupon_code,
                'title': f'Suspicious Discount on Order #{order.id}',
                'description': f'Order received {discount_pct:.0f}% discount (${order.discount_amount:.2f} off ${order.subtotal:.2f}).',
                'possible_reasons': ['Stacked coupons', 'Coupon code error', 'System glitch', 'Fraudulent activity'],
                'recommended_action': 'Review coupon logic and order details'
            })

        return anomalies

    @staticmethod
    def detect_user_anomalies(days: int = 7) -> List[Dict[str, Any]]:
        """
        Detect unusual user behavior patterns.
        """
        anomalies = []
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)

        # 1. Check for sudden spike in new users
        new_users = User.objects.filter(
            date_joined__range=[start_date, end_date]
        ).count()

        baseline_users = User.objects.filter(
            date_joined__range=[start_date - timedelta(days=days*2), start_date]
        ).count()

        if baseline_users > 0 and new_users / baseline_users > 2.0:
            anomalies.append({
                'type': 'user_spike',
                'severity': 'info',
                'date': timezone.now().date().isoformat(),
                'metric': 'new_users',
                'value': new_users,
                'baseline': baseline_users,
                'change_ratio': new_users / baseline_users,
                'title': f'Unusual Surge in New Users',
                'description': f'{new_users} new users registered in the last {days} days, compared to {baseline_users} in the previous period.',
                'possible_reasons': ['Successful marketing campaign', 'Viral social media post', 'Partnership/referral program', 'Bot registrations'],
                'recommended_action': 'Verify registrations are legitimate'
            })

        # 2. Check for users with high order frequency
        heavy_orderers = Order.objects.filter(
            created_at__range=[start_date, end_date]
        ).values('user').annotate(
            order_count=Count('id')
        ).filter(order_count__gt=days * 3)  # More than 3 orders per day on average

        for user_data in heavy_orderers[:3]:
            user = User.objects.get(id=user_data['user'])
            anomalies.append({
                'type': 'high_frequency_ordering',
                'severity': 'info',
                'date': timezone.now().date().isoformat(),
                'metric': 'order_frequency',
                'value': user_data['order_count'],
                'user_id': user.id,
                'username': user.username,
                'title': f'Very Active Customer: {user.username}',
                'description': f'User has placed {user_data["order_count"]} orders in {days} days.',
                'possible_reasons': ['Business customer', 'Catering orders', 'Multiple households', 'Legitimate heavy user'],
                'recommended_action': 'Consider VIP treatment or loyalty rewards'
            })

        return anomalies

    @staticmethod
    def _analyze_revenue_spike(day_start: datetime, day_end: datetime) -> List[str]:
        """Analyze possible reasons for revenue spike."""
        reasons = []

        # Check order count
        orders = Order.objects.filter(
            created_at__range=[day_start, day_end],
            payment_status='paid'
        )
        order_count = orders.count()

        if order_count > 10:
            reasons.append(f'High order volume ({order_count} orders)')

        # Check average order value
        avg_value = orders.aggregate(avg=Avg('total_price'))['avg']
        if avg_value and avg_value > 50:
            reasons.append(f'Higher than usual order values (avg ${float(avg_value):.2f})')

        # Check for special day
        if day_start.weekday() in [4, 5, 6]:  # Fri, Sat, Sun
            reasons.append('Weekend effect')

        if not reasons:
            reasons.append('General increased demand')

        return reasons

    @staticmethod
    def _analyze_revenue_drop(day_start: datetime, day_end: datetime) -> List[str]:
        """Analyze possible reasons for revenue drop."""
        reasons = []

        # Check order count
        orders = Order.objects.filter(
            created_at__range=[day_start, day_end],
            payment_status='paid'
        )
        order_count = orders.count()

        if order_count < 3:
            reasons.append(f'Very few orders ({order_count} orders)')

        # Check for early weekday
        if day_start.weekday() in [0, 1]:  # Mon, Tue
            reasons.append('Early weekday slowdown')

        if not reasons:
            reasons.append('Decreased customer demand')

        return reasons

    @staticmethod
    def get_anomaly_summary(days: int = 7) -> Dict[str, Any]:
        """
        Get a summary of all anomalies with counts by type and severity.
        """
        anomalies = AnomalyDetector.detect_all_anomalies(days)

        # Count by severity
        severity_counts = {'critical': 0, 'warning': 0, 'info': 0}
        for anomaly in anomalies:
            severity_counts[anomaly['severity']] += 1

        # Count by type
        type_counts = {}
        for anomaly in anomalies:
            type_counts[anomaly['type']] = type_counts.get(anomaly['type'], 0) + 1

        return {
            'period_days': days,
            'total_anomalies': len(anomalies),
            'severity_counts': severity_counts,
            'type_counts': type_counts,
            'anomalies': anomalies[:10],  # Top 10 most important
            'has_critical': severity_counts['critical'] > 0,
            'has_warnings': severity_counts['warning'] > 0
        }