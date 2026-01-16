"""
Read-only analytics queries for business intelligence.
All queries are optimized for read performance and use Django ORM efficiently.
"""
from django.db.models import (
    Sum, Count, Avg, Q, F, DecimalField,
    ExpressionWrapper, CharField, Value
)
from django.db.models.functions import TruncDate, Coalesce
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from orders.models import Order, OrderItem
from reviews.models import Review

User = get_user_model()


class AnalyticsQueries:
    """
    Centralized analytics queries for the restaurant system.
    All methods are read-only and use select_related/prefetch_related for optimization.
    """

    @staticmethod
    def get_revenue_metrics(start_date=None, end_date=None):
        """
        Calculate revenue metrics for a given date range.

        Args:
            start_date: Start date for filtering (defaults to 30 days ago)
            end_date: End date for filtering (defaults to now)

        Returns:
            dict: Revenue metrics including total, average, and count
        """
        if not start_date:
            start_date = timezone.now() - timedelta(days=30)
        if not end_date:
            end_date = timezone.now()

        orders = Order.objects.filter(
            created_at__gte=start_date,
            created_at__lte=end_date,
            payment_status='paid'
        )

        metrics = orders.aggregate(
            total_revenue=Coalesce(Sum('total_price'), Decimal('0.00')),
            total_orders=Count('id'),
            average_order_value=Coalesce(Avg('total_price'), Decimal('0.00')),
            total_discount=Coalesce(Sum('discount_amount'), Decimal('0.00')),
            gross_revenue=Coalesce(Sum('subtotal'), Decimal('0.00'))
        )

        return {
            'total_revenue': float(metrics['total_revenue']),
            'total_orders': metrics['total_orders'],
            'average_order_value': float(metrics['average_order_value']),
            'total_discount': float(metrics['total_discount']),
            'gross_revenue': float(metrics['gross_revenue']),
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            }
        }

    @staticmethod
    def get_revenue_by_day(start_date=None, end_date=None):
        """
        Get daily revenue breakdown.

        Args:
            start_date: Start date for filtering (defaults to 30 days ago)
            end_date: End date for filtering (defaults to now)

        Returns:
            list: Daily revenue data with date and revenue
        """
        if not start_date:
            start_date = timezone.now() - timedelta(days=30)
        if not end_date:
            end_date = timezone.now()

        daily_revenue = Order.objects.filter(
            created_at__gte=start_date,
            created_at__lte=end_date,
            payment_status='paid'
        ).annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            revenue=Coalesce(Sum('total_price'), Decimal('0.00')),
            orders=Count('id'),
            avg_order=Coalesce(Avg('total_price'), Decimal('0.00'))
        ).order_by('date')

        return [
            {
                'date': item['date'].isoformat(),
                'revenue': float(item['revenue']),
                'orders': item['orders'],
                'average_order_value': float(item['avg_order'])
            }
            for item in daily_revenue
        ]

    @staticmethod
    def get_order_status_breakdown():
        """
        Get count of orders by status.

        Returns:
            dict: Order counts by status
        """
        status_counts = Order.objects.values('status').annotate(
            count=Count('id'),
            total_value=Coalesce(Sum('total_price'), Decimal('0.00'))
        ).order_by('-count')

        return {
            'by_status': [
                {
                    'status': item['status'],
                    'count': item['count'],
                    'total_value': float(item['total_value'])
                }
                for item in status_counts
            ],
            'total_orders': Order.objects.count()
        }

    @staticmethod
    def get_user_metrics():
        """
        Get user-related metrics.

        Returns:
            dict: User statistics including total users, active users, etc.
        """
        total_users = User.objects.count()
        users_with_orders = User.objects.filter(orders__isnull=False).distinct().count()

        # Users who ordered in last 30 days
        thirty_days_ago = timezone.now() - timedelta(days=30)
        active_users = User.objects.filter(
            orders__created_at__gte=thirty_days_ago
        ).distinct().count()

        # Top customers by order count
        top_customers = User.objects.annotate(
            order_count=Count('orders'),
            total_spent=Coalesce(
                Sum('orders__total_price', filter=Q(orders__payment_status='paid')),
                Decimal('0.00')
            )
        ).filter(order_count__gt=0).order_by('-total_spent')[:10]

        return {
            'total_users': total_users,
            'users_with_orders': users_with_orders,
            'active_users_30d': active_users,
            'conversion_rate': round((users_with_orders / total_users * 100), 2) if total_users > 0 else 0,
            'top_customers': [
                {
                    'user_id': user.id,
                    'username': user.username,
                    'order_count': user.order_count,
                    'total_spent': float(user.total_spent)
                }
                for user in top_customers
            ]
        }

    @staticmethod
    def get_product_performance():
        """
        Get product sales performance metrics.

        Returns:
            list: Top selling products with quantity and revenue
        """
        top_products = OrderItem.objects.filter(
            order__payment_status='paid'
        ).values('product_id', 'product_name').annotate(
            total_quantity=Sum('quantity'),
            total_revenue=Sum(
                ExpressionWrapper(
                    F('price') * F('quantity'),
                    output_field=DecimalField()
                )
            ),
            order_count=Count('order', distinct=True)
        ).order_by('-total_revenue')[:20]

        return [
            {
                'product_id': item['product_id'],
                'product_name': item['product_name'],
                'total_quantity': item['total_quantity'],
                'total_revenue': float(item['total_revenue']),
                'order_count': item['order_count']
            }
            for item in top_products
        ]

    @staticmethod
    def get_coupon_performance():
        """
        Get coupon usage and discount metrics.

        Returns:
            dict: Coupon usage statistics
        """
        orders_with_coupons = Order.objects.exclude(
            Q(coupon_code='') | Q(coupon_code__isnull=True)
        ).filter(payment_status='paid')

        coupon_stats = orders_with_coupons.values('coupon_code').annotate(
            usage_count=Count('id'),
            total_discount=Coalesce(Sum('discount_amount'), Decimal('0.00')),
            total_revenue=Coalesce(Sum('total_price'), Decimal('0.00'))
        ).order_by('-usage_count')

        total_discount = Order.objects.filter(
            payment_status='paid'
        ).aggregate(
            total=Coalesce(Sum('discount_amount'), Decimal('0.00'))
        )

        return {
            'total_discount_given': float(total_discount['total']),
            'orders_with_coupons': orders_with_coupons.count(),
            'by_coupon': [
                {
                    'coupon_code': item['coupon_code'],
                    'usage_count': item['usage_count'],
                    'total_discount': float(item['total_discount']),
                    'total_revenue': float(item['total_revenue'])
                }
                for item in coupon_stats
            ]
        }

    @staticmethod
    def get_review_metrics():
        """
        Get review and rating metrics.

        Returns:
            dict: Review statistics
        """
        reviews = Review.objects.all()

        metrics = reviews.aggregate(
            total_reviews=Count('id'),
            average_rating=Avg('rating', output_field=DecimalField())
        )

        # Default to 0.00 if no reviews
        avg_rating = metrics['average_rating'] if metrics['average_rating'] is not None else Decimal('0.00')

        # Rating distribution
        rating_distribution = reviews.values('rating').annotate(
            count=Count('id')
        ).order_by('-rating')

        return {
            'total_reviews': metrics['total_reviews'],
            'average_rating': float(avg_rating),
            'rating_distribution': [
                {
                    'rating': item['rating'],
                    'count': item['count']
                }
                for item in rating_distribution
            ]
        }

    @staticmethod
    def get_dashboard_kpis(days=30):
        """
        Get key performance indicators for dashboard.

        Args:
            days: Number of days to look back (default: 30)

        Returns:
            dict: Comprehensive KPIs for the dashboard
        """
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)

        # Current period metrics
        current_revenue = AnalyticsQueries.get_revenue_metrics(start_date, end_date)

        # Previous period for comparison
        prev_end = start_date
        prev_start = prev_end - timedelta(days=days)
        previous_revenue = AnalyticsQueries.get_revenue_metrics(prev_start, prev_end)

        # Calculate growth rates
        def calculate_growth(current, previous):
            if previous == 0:
                return 100.0 if current > 0 else 0.0
            return round(((current - previous) / previous) * 100, 2)

        revenue_growth = calculate_growth(
            current_revenue['total_revenue'],
            previous_revenue['total_revenue']
        )

        order_growth = calculate_growth(
            current_revenue['total_orders'],
            previous_revenue['total_orders']
        )

        # User metrics
        user_metrics = AnalyticsQueries.get_user_metrics()

        # Order status
        status_breakdown = AnalyticsQueries.get_order_status_breakdown()

        return {
            'period_days': days,
            'revenue': {
                'current': current_revenue['total_revenue'],
                'previous': previous_revenue['total_revenue'],
                'growth_percentage': revenue_growth
            },
            'orders': {
                'current': current_revenue['total_orders'],
                'previous': previous_revenue['total_orders'],
                'growth_percentage': order_growth
            },
            'average_order_value': current_revenue['average_order_value'],
            'total_users': user_metrics['total_users'],
            'active_users': user_metrics['active_users_30d'],
            'conversion_rate': user_metrics['conversion_rate'],
            'order_status': status_breakdown['by_status']
        }
