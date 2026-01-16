"""
Tests for Order Service Layer
"""
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError

from orders.services import OrderService
from orders.models import Order
from cart.services import CartService
from addresses.models import Address
from menu.models import Category, Product
from coupons.models import Coupon
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class OrderServiceTest(TestCase):
    """Test order service operations"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )

        self.category = Category.objects.create(
            name="Test Category",
            is_active=True
        )

        self.product = Product.objects.create(
            category=self.category,
            name="Test Product",
            description="Test Description",
            price=Decimal("10.00"),
            is_available=True
        )

        self.address = Address.objects.create(
            user=self.user,
            label="Home",
            city="Test City",
            street="Test Street",
            building="123",
            floor="1",
            apartment="A"
        )

        # Create valid coupon
        self.coupon = Coupon.objects.create(
            code="TEST10",
            description="10% off",
            discount_type="percentage",
            discount_value=Decimal("10.00"),
            minimum_order_amount=Decimal("5.00"),
            max_usage_per_user=1,
            is_active=True,
            valid_from=timezone.now() - timedelta(days=1),
            valid_until=timezone.now() + timedelta(days=30)
        )

    def test_create_order_success(self):
        """Test successful order creation"""
        # Add item to cart
        CartService.add_item_to_cart(self.user, self.product.id, 2)

        # Create order
        order = OrderService.create_order(self.user, self.address.id)

        self.assertIsNotNone(order)
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.address, self.address)
        self.assertEqual(order.subtotal, Decimal("20.00"))
        self.assertEqual(order.total_price, Decimal("20.00"))
        self.assertEqual(order.items.count(), 2)
        self.assertEqual(order.status, "pending")

        # Cart should be cleared
        cart = CartService.get_or_create_cart(self.user)
        self.assertEqual(cart.items.count(), 0)

    def test_create_order_with_coupon(self):
        """Test order creation with coupon"""
        CartService.add_item_to_cart(self.user, self.product.id, 2)

        order = OrderService.create_order(
            self.user,
            self.address.id,
            coupon_code="TEST10"
        )

        self.assertEqual(order.subtotal, Decimal("20.00"))
        self.assertEqual(order.discount_amount, Decimal("2.00"))
        self.assertEqual(order.total_price, Decimal("18.00"))
        self.assertEqual(order.coupon_code, "TEST10")

    def test_create_order_with_invalid_coupon(self):
        """Test order creation with invalid coupon fails"""
        CartService.add_item_to_cart(self.user, self.product.id, 1)

        with self.assertRaises(ValidationError):
            OrderService.create_order(
                self.user,
                self.address.id,
                coupon_code="INVALID"
            )

    def test_create_order_empty_cart_fails(self):
        """Test order creation with empty cart fails"""
        with self.assertRaises(ValidationError) as context:
            OrderService.create_order(self.user, self.address.id)
        self.assertIn("empty", str(context.exception).lower())

    def test_create_order_with_coupon_below_minimum(self):
        """Test order fails when below coupon minimum"""
        # Product costs $10, coupon requires $5 minimum
        # This should work
        CartService.add_item_to_cart(self.user, self.product.id, 1)

        # Create order - should succeed
        order = OrderService.create_order(
            self.user,
            self.address.id,
            coupon_code="TEST10"
        )
        self.assertIsNotNone(order)

    def test_update_order_status(self):
        """Test updating order status"""
        CartService.add_item_to_cart(self.user, self.product.id, 1)
        order = OrderService.create_order(self.user, self.address.id)

        # Update to preparing
        updated_order = OrderService.update_order_status(
            order.id,
            "preparing"
        )
        self.assertEqual(updated_order.status, "preparing")

    def test_invalid_status_transition(self):
        """Test invalid status transition fails"""
        CartService.add_item_to_cart(self.user, self.product.id, 1)
        order = OrderService.create_order(self.user, self.address.id)

        # Try to transition directly from pending to delivered (invalid)
        with self.assertRaises(ValidationError):
            OrderService.update_order_status(order.id, "delivered")

    def test_valid_status_transitions(self):
        """Test valid status transition sequence"""
        CartService.add_item_to_cart(self.user, self.product.id, 1)
        order = OrderService.create_order(self.user, self.address.id)

        # pending -> preparing
        order = OrderService.update_order_status(order.id, "preparing")
        self.assertEqual(order.status, "preparing")

        # preparing -> on_the_way
        order = OrderService.update_order_status(order.id, "on_the_way")
        self.assertEqual(order.status, "on_the_way")

        # on_the_way -> delivered
        order = OrderService.update_order_status(order.id, "delivered")
        self.assertEqual(order.status, "delivered")

    def test_cancel_order(self):
        """Test cancelling order"""
        CartService.add_item_to_cart(self.user, self.product.id, 1)
        order = OrderService.create_order(self.user, self.address.id)

        cancelled_order = OrderService.cancel_order(order.id, self.user)
        self.assertEqual(cancelled_order.status, "cancelled")

    def test_cancel_delivered_order_fails(self):
        """Test cannot cancel delivered order"""
        CartService.add_item_to_cart(self.user, self.product.id, 1)
        order = OrderService.create_order(self.user, self.address.id)

        # Deliver the order
        order.status = "delivered"
        order.save()

        with self.assertRaises(ValidationError):
            OrderService.cancel_order(order.id, self.user)

    def test_get_order_summary(self):
        """Test getting order summary"""
        CartService.add_item_to_cart(self.user, self.product.id, 2)
        order = OrderService.create_order(self.user, self.address.id)

        summary = OrderService.get_order_summary(order.id, self.user)

        self.assertIn("id", summary)
        self.assertIn("status", summary)
        self.assertIn("subtotal", summary)
        self.assertIn("total_price", summary)
        self.assertEqual(summary["status"], "pending")
        self.assertEqual(summary["subtotal"], "20.00")
