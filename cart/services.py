"""
Cart Service Layer
Handles all cart-related business logic
"""
from decimal import Decimal
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError

from .models import Cart, CartItem
from menu.models import Product


class CartService:
    """Service class for cart operations"""

    @staticmethod
    def get_or_create_cart(user):
        """Get or create cart for user"""
        cart, created = Cart.objects.get_or_create(user=user)
        return cart

    @staticmethod
    def add_item_to_cart(user, product_id: int, quantity: int = 1):
        """
        Add item to user's cart

        Args:
            user: The user adding the item
            product_id: ID of the product to add
            quantity: Quantity to add (default 1)

        Returns:
            Cart instance

        Raises:
            ValidationError: If product not found or unavailable
        """
        # Validate quantity
        if quantity <= 0:
            raise ValidationError("Quantity must be positive")

        if quantity > 99:
            raise ValidationError("Maximum quantity per item is 99")

        # Get product
        product = get_object_or_404(Product, id=product_id)

        # Check availability
        if not product.is_available:
            raise ValidationError("This product is currently unavailable")

        # Check stock if inventory management is enabled
        if hasattr(product, 'inventory') and product.inventory:
            if product.inventory.quantity < quantity:
                raise ValidationError(
                    f"Only {product.inventory.quantity} items available in stock"
                )

        # Get or create cart
        cart = CartService.get_or_create_cart(user)

        with transaction.atomic():
            # Get or create cart item
            item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={"price": product.price, "quantity": 0}
            )

            if created:
                item.quantity = quantity
            else:
                item.quantity += quantity

                # Validate total quantity
                if item.quantity > 99:
                    raise ValidationError("Maximum quantity per item is 99")

            item.save()

        return cart

    @staticmethod
    def update_item_quantity(user, item_id: int, quantity: int):
        """
        Update cart item quantity

        Args:
            user: The user updating the item
            item_id: Cart item ID
            quantity: New quantity

        Returns:
            Cart instance

        Raises:
            ValidationError: If invalid quantity
        """
        if quantity <= 0:
            raise ValidationError("Quantity must be positive")

        if quantity > 99:
            raise ValidationError("Maximum quantity per item is 99")

        item = get_object_or_404(
            CartItem,
            id=item_id,
            cart__user=user
        )

        # Check stock if inventory management is enabled
        if hasattr(item.product, 'inventory') and item.product.inventory:
            if item.product.inventory.quantity < quantity:
                raise ValidationError(
                    f"Only {item.product.inventory.quantity} items available in stock"
                )

        item.quantity = quantity
        item.save()

        return item.cart

    @staticmethod
    def remove_item_from_cart(user, item_id: int):
        """
        Remove item from cart

        Args:
            user: The user removing the item
            item_id: Cart item ID

        Returns:
            Cart instance
        """
        item = get_object_or_404(
            CartItem,
            id=item_id,
            cart__user=user
        )

        cart = item.cart
        item.delete()

        return cart

    @staticmethod
    def clear_cart(user):
        """
        Clear all items from user's cart

        Args:
            user: The user whose cart to clear
        """
        CartItem.objects.filter(cart__user=user).delete()

    @staticmethod
    def get_cart_summary(cart):
        """
        Get cart summary with totals

        Args:
            cart: Cart instance

        Returns:
            dict with cart summary
        """
        return {
            "id": cart.id,
            "total_items": cart.total_items(),
            "total_price": cart.total_price(),
            "is_active": cart.is_active,
        }

    @staticmethod
    def validate_cart_for_checkout(user):
        """
        Validate cart is ready for checkout

        Args:
            user: The user checking out

        Returns:
            tuple: (is_valid, error_message, cart_items)

        Raises:
            ValidationError: If cart is invalid
        """
        cart_items = CartItem.objects.filter(
            cart__user=user
        ).select_related('product')

        if not cart_items.exists():
            raise ValidationError("Cart is empty")

        # Check product availability
        unavailable_products = []
        stock_issues = []

        for item in cart_items:
            if not item.product.is_available:
                unavailable_products.append(item.product.name)

            # Check stock
            if hasattr(item.product, 'inventory') and item.product.inventory:
                if item.product.inventory.quantity < item.quantity:
                    stock_issues.append(
                        f"{item.product.name} (only {item.product.inventory.quantity} available)"
                    )

        if unavailable_products:
            raise ValidationError(
                f"The following products are no longer available: {', '.join(unavailable_products)}"
            )

        if stock_issues:
            raise ValidationError(
                f"Insufficient stock: {', '.join(stock_issues)}"
            )

        return True, None, cart_items
