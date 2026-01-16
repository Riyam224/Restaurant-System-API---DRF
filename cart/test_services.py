"""
Tests for Cart Service Layer
"""
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError

from cart.services import CartService
from cart.models import Cart, CartItem
from menu.models import Category, Product

User = get_user_model()


class CartServiceTest(TestCase):
    """Test cart service operations"""

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
            price=Decimal("10.99"),
            is_available=True
        )

        self.unavailable_product = Product.objects.create(
            category=self.category,
            name="Unavailable Product",
            description="Unavailable",
            price=Decimal("15.99"),
            is_available=False
        )

    def test_get_or_create_cart(self):
        """Test cart creation"""
        cart = CartService.get_or_create_cart(self.user)
        self.assertIsNotNone(cart)
        self.assertEqual(cart.user, self.user)

        # Second call should return same cart
        cart2 = CartService.get_or_create_cart(self.user)
        self.assertEqual(cart.id, cart2.id)

    def test_add_item_to_cart(self):
        """Test adding item to cart"""
        cart = CartService.add_item_to_cart(self.user, self.product.id, 2)

        self.assertEqual(cart.items.count(), 1)
        item = cart.items.first()
        self.assertEqual(item.product, self.product)
        self.assertEqual(item.quantity, 2)
        self.assertEqual(item.price, self.product.price)

    def test_add_unavailable_product_raises_error(self):
        """Test adding unavailable product raises error"""
        with self.assertRaises(ValidationError) as context:
            CartService.add_item_to_cart(
                self.user,
                self.unavailable_product.id,
                1
            )
        self.assertIn("unavailable", str(context.exception).lower())

    def test_add_item_with_invalid_quantity(self):
        """Test adding item with invalid quantity"""
        # Zero quantity
        with self.assertRaises(ValidationError):
            CartService.add_item_to_cart(self.user, self.product.id, 0)

        # Negative quantity
        with self.assertRaises(ValidationError):
            CartService.add_item_to_cart(self.user, self.product.id, -1)

        # Excessive quantity
        with self.assertRaises(ValidationError):
            CartService.add_item_to_cart(self.user, self.product.id, 100)

    def test_add_same_item_increases_quantity(self):
        """Test adding same item increases quantity"""
        CartService.add_item_to_cart(self.user, self.product.id, 2)
        cart = CartService.add_item_to_cart(self.user, self.product.id, 3)

        self.assertEqual(cart.items.count(), 1)
        item = cart.items.first()
        self.assertEqual(item.quantity, 5)

    def test_remove_item_from_cart(self):
        """Test removing item from cart"""
        cart = CartService.add_item_to_cart(self.user, self.product.id, 2)
        item_id = cart.items.first().id

        cart = CartService.remove_item_from_cart(self.user, item_id)
        self.assertEqual(cart.items.count(), 0)

    def test_clear_cart(self):
        """Test clearing cart"""
        CartService.add_item_to_cart(self.user, self.product.id, 2)
        CartService.clear_cart(self.user)

        cart = CartService.get_or_create_cart(self.user)
        self.assertEqual(cart.items.count(), 0)

    def test_get_cart_summary(self):
        """Test getting cart summary"""
        cart = CartService.add_item_to_cart(self.user, self.product.id, 2)
        summary = CartService.get_cart_summary(cart)

        self.assertIn("id", summary)
        self.assertIn("total_items", summary)
        self.assertIn("total_price", summary)
        self.assertEqual(summary["total_items"], 2)
        self.assertEqual(summary["total_price"], Decimal("21.98"))

    def test_validate_cart_for_checkout_empty_cart(self):
        """Test validation fails for empty cart"""
        with self.assertRaises(ValidationError) as context:
            CartService.validate_cart_for_checkout(self.user)
        self.assertIn("empty", str(context.exception).lower())

    def test_validate_cart_for_checkout_unavailable_product(self):
        """Test validation fails for unavailable products"""
        # Add available product first
        CartService.add_item_to_cart(self.user, self.product.id, 1)

        # Manually add unavailable product to cart
        cart = CartService.get_or_create_cart(self.user)
        CartItem.objects.create(
            cart=cart,
            product=self.unavailable_product,
            price=self.unavailable_product.price,
            quantity=1
        )

        with self.assertRaises(ValidationError) as context:
            CartService.validate_cart_for_checkout(self.user)
        self.assertIn("no longer available", str(context.exception).lower())

    def test_validate_cart_for_checkout_success(self):
        """Test successful cart validation"""
        CartService.add_item_to_cart(self.user, self.product.id, 2)

        is_valid, error, cart_items = CartService.validate_cart_for_checkout(
            self.user
        )

        self.assertTrue(is_valid)
        self.assertIsNone(error)
        self.assertEqual(len(cart_items), 1)
