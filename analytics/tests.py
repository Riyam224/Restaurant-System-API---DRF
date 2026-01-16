"""
Tests for analytics endpoints and queries.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from decimal import Decimal
from django.utils import timezone

from orders.models import Order, OrderItem
from addresses.models import Address

User = get_user_model()


class AnalyticsPermissionsTestCase(APITestCase):
    """Test that analytics endpoints require admin permissions."""

    def setUp(self):
        """Create test users."""
        self.admin_user = User.objects.create_user(
            username='admin',
            password='admin123',
            is_staff=True,
            is_superuser=True
        )
        self.regular_user = User.objects.create_user(
            username='regular',
            password='regular123',
            is_staff=False
        )

    def test_unauthenticated_access_denied(self):
        """Test that unauthenticated users cannot access analytics."""
        response = self.client.get('/api/v1/analytics/dashboard/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_regular_user_access_denied(self):
        """Test that regular users cannot access analytics."""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get('/api/v1/analytics/dashboard/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_user_access_allowed(self):
        """Test that admin users can access analytics."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/api/v1/analytics/dashboard/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class AnalyticsQueriesTestCase(TestCase):
    """Test analytics query functions."""

    def setUp(self):
        """Create test data."""
        # Create users
        self.user1 = User.objects.create_user(
            username='testuser1',
            password='test123'
        )
        self.user2 = User.objects.create_user(
            username='testuser2',
            password='test123'
        )

        # Create address
        self.address = Address.objects.create(
            user=self.user1,
            label='Home',
            street='123 Test St',
            city='Test City',
            building='Apt 1',
            lat=40.7128,
            lng=-74.0060
        )

        # Create paid orders
        self.order1 = Order.objects.create(
            user=self.user1,
            address=self.address,
            subtotal=Decimal('100.00'),
            discount_amount=Decimal('10.00'),
            total_price=Decimal('90.00'),
            coupon_code='TEST10',
            payment_status='paid',
            status='delivered'
        )

        self.order2 = Order.objects.create(
            user=self.user2,
            address=self.address,
            subtotal=Decimal('50.00'),
            discount_amount=Decimal('0.00'),
            total_price=Decimal('50.00'),
            payment_status='paid',
            status='pending'
        )

        # Create pending order (not paid)
        self.order3 = Order.objects.create(
            user=self.user1,
            address=self.address,
            subtotal=Decimal('200.00'),
            discount_amount=Decimal('0.00'),
            total_price=Decimal('200.00'),
            payment_status='pending',
            status='pending'
        )

    def test_revenue_metrics_calculation(self):
        """Test that revenue metrics are calculated correctly."""
        from analytics.queries import AnalyticsQueries

        metrics = AnalyticsQueries.get_revenue_metrics()

        # Only paid orders should count
        self.assertEqual(metrics['total_revenue'], 140.00)  # 90 + 50
        self.assertEqual(metrics['total_orders'], 2)
        self.assertEqual(metrics['average_order_value'], 70.00)
        self.assertEqual(metrics['total_discount'], 10.00)
        self.assertEqual(metrics['gross_revenue'], 150.00)  # 100 + 50

    def test_order_status_breakdown(self):
        """Test order status breakdown."""
        from analytics.queries import AnalyticsQueries

        breakdown = AnalyticsQueries.get_order_status_breakdown()

        self.assertEqual(breakdown['total_orders'], 3)
        self.assertTrue(len(breakdown['by_status']) > 0)

    def test_user_metrics(self):
        """Test user metrics calculation."""
        from analytics.queries import AnalyticsQueries

        metrics = AnalyticsQueries.get_user_metrics()

        self.assertEqual(metrics['total_users'], 2)
        self.assertEqual(metrics['users_with_orders'], 2)
        self.assertTrue(metrics['conversion_rate'] > 0)


class AnalyticsEndpointsTestCase(APITestCase):
    """Test analytics API endpoints."""

    def setUp(self):
        """Create admin user and test data."""
        self.admin_user = User.objects.create_user(
            username='admin',
            password='admin123',
            is_staff=True,
            is_superuser=True
        )
        self.client.force_authenticate(user=self.admin_user)

        # Create minimal test data
        self.user = User.objects.create_user(
            username='testuser',
            password='test123'
        )

    def test_dashboard_kpis_endpoint(self):
        """Test dashboard KPIs endpoint."""
        response = self.client.get('/api/v1/analytics/dashboard/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('revenue', response.data)
        self.assertIn('orders', response.data)
        self.assertIn('total_users', response.data)

    def test_dashboard_with_custom_days(self):
        """Test dashboard with custom days parameter."""
        response = self.client.get('/api/v1/analytics/dashboard/?days=7')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['period_days'], 7)

    def test_dashboard_invalid_days(self):
        """Test dashboard with invalid days parameter."""
        response = self.client.get('/api/v1/analytics/dashboard/?days=500')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_revenue_metrics_endpoint(self):
        """Test revenue metrics endpoint."""
        response = self.client.get('/api/v1/analytics/revenue/metrics/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_revenue', response.data)
        self.assertIn('average_order_value', response.data)

    def test_daily_revenue_endpoint(self):
        """Test daily revenue endpoint."""
        response = self.client.get('/api/v1/analytics/revenue/daily/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)

    def test_order_status_endpoint(self):
        """Test order status endpoint."""
        response = self.client.get('/api/v1/analytics/orders/status/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('by_status', response.data)
        self.assertIn('total_orders', response.data)

    def test_user_metrics_endpoint(self):
        """Test user metrics endpoint."""
        response = self.client.get('/api/v1/analytics/users/metrics/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_users', response.data)
        self.assertIn('conversion_rate', response.data)

    def test_product_performance_endpoint(self):
        """Test product performance endpoint."""
        response = self.client.get('/api/v1/analytics/products/performance/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)

    def test_coupon_performance_endpoint(self):
        """Test coupon performance endpoint."""
        response = self.client.get('/api/v1/analytics/coupons/performance/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_discount_given', response.data)

    def test_review_metrics_endpoint(self):
        """Test review metrics endpoint."""
        response = self.client.get('/api/v1/analytics/reviews/metrics/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_reviews', response.data)
        self.assertIn('average_rating', response.data)
