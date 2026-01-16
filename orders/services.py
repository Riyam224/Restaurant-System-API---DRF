"""
Order Service Layer
Handles all order-related business logic
"""
from decimal import Decimal
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError

from .models import Order, OrderItem
from cart.models import CartItem
from cart.services import CartService
from addresses.models import Address
from coupons.models import Coupon, CouponUsage


class OrderService:
    """Service class for order operations"""

    @staticmethod
    def create_order(user, address_id: int, coupon_code: str = None):
        """
        Create order from user's cart

        Args:
            user: The user creating the order
            address_id: Delivery address ID
            coupon_code: Optional coupon code

        Returns:
            Order instance

        Raises:
            ValidationError: If order creation fails
        """
        # Validate address
        address = get_object_or_404(Address, id=address_id, user=user)

        # Validate cart
        is_valid, error_msg, cart_items = CartService.validate_cart_for_checkout(user)

        # Calculate order subtotal using snapshot prices from cart
        subtotal = sum(item.price * item.quantity for item in cart_items)

        # Handle coupon if provided
        coupon = None
        discount_amount = Decimal("0.00")
        final_amount = subtotal

        if coupon_code:
            coupon_code = coupon_code.upper().strip()
            coupon, discount_amount, final_amount = OrderService._apply_coupon(
                user, coupon_code, subtotal
            )

        # Create order with atomic transaction
        with transaction.atomic():
            # Create order
            order = Order.objects.create(
                user=user,
                address=address,
                subtotal=subtotal,
                discount_amount=discount_amount,
                total_price=final_amount,
                coupon_code=coupon_code if coupon else "",
            )

            # Create order items
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product_id=item.product.id,
                    product_name=item.product.name,
                    price=item.price,
                    quantity=item.quantity,
                )

                # Decrement inventory if enabled
                if hasattr(item.product, 'inventory') and item.product.inventory:
                    inventory = item.product.inventory
                    inventory.quantity -= item.quantity
                    inventory.save(update_fields=['quantity'])

            # Record coupon usage
            if coupon:
                CouponUsage.objects.create(
                    coupon=coupon,
                    user=user,
                    order_id=order.id,
                    order_amount=subtotal,
                    discount_amount=discount_amount,
                    final_amount=final_amount,
                )
                coupon.increment_usage()

            # Clear cart
            CartService.clear_cart(user)

        return order

    @staticmethod
    def _apply_coupon(user, coupon_code: str, subtotal: Decimal):
        """
        Validate and apply coupon

        Args:
            user: The user applying the coupon
            coupon_code: Coupon code to apply
            subtotal: Order subtotal

        Returns:
            tuple: (coupon, discount_amount, final_amount)

        Raises:
            ValidationError: If coupon is invalid
        """
        try:
            coupon = Coupon.objects.get(code=coupon_code)
        except Coupon.DoesNotExist:
            raise ValidationError("Invalid coupon code")

        # Check if user can use coupon
        can_use, message = coupon.can_user_use(user)
        if not can_use:
            raise ValidationError(message)

        # Check minimum order amount
        if subtotal < coupon.minimum_order_amount:
            raise ValidationError(
                f"Minimum order amount of ${coupon.minimum_order_amount} required for this coupon"
            )

        # Calculate discount
        discount_amount, final_amount = coupon.calculate_discount(subtotal)

        return coupon, discount_amount, final_amount

    @staticmethod
    def update_order_status(order_id: int, new_status: str, user=None):
        """
        Update order status

        Args:
            order_id: Order ID
            new_status: New status value
            user: Optional user (for permission checking)

        Returns:
            Order instance

        Raises:
            ValidationError: If status update fails
        """
        order = get_object_or_404(Order, id=order_id)

        # Validate status choice
        valid_statuses = [choice[0] for choice in Order.STATUS_CHOICES]
        if new_status not in valid_statuses:
            raise ValidationError(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")

        # Validate status transitions
        if not OrderService._is_valid_status_transition(order.status, new_status):
            raise ValidationError(
                f"Cannot transition from '{order.status}' to '{new_status}'"
            )

        order.status = new_status
        order.save(update_fields=['status'])

        return order

    @staticmethod
    def _is_valid_status_transition(current_status: str, new_status: str) -> bool:
        """
        Validate status transition is allowed

        Args:
            current_status: Current order status
            new_status: New status to transition to

        Returns:
            bool: True if transition is valid
        """
        # Define valid transitions
        valid_transitions = {
            'pending': ['preparing', 'cancelled'],
            'preparing': ['on_the_way', 'cancelled'],
            'on_the_way': ['delivered', 'cancelled'],
            'delivered': [],  # Terminal state
            'cancelled': [],  # Terminal state
        }

        # Allow staying in same status
        if current_status == new_status:
            return True

        return new_status in valid_transitions.get(current_status, [])

    @staticmethod
    def cancel_order(order_id: int, user):
        """
        Cancel order and restore inventory

        Args:
            order_id: Order ID
            user: User cancelling the order

        Returns:
            Order instance

        Raises:
            ValidationError: If cancellation fails
        """
        order = get_object_or_404(Order, id=order_id, user=user)

        # Check if order can be cancelled
        if order.status in ['delivered', 'cancelled']:
            raise ValidationError(
                f"Cannot cancel order with status '{order.status}'"
            )

        with transaction.atomic():
            # Restore inventory
            for item in order.items.all():
                if hasattr(item.product, 'inventory') and item.product.inventory:
                    inventory = item.product.inventory
                    inventory.quantity += item.quantity
                    inventory.save(update_fields=['quantity'])

            # Update order status
            order.status = 'cancelled'
            order.save(update_fields=['status'])

        return order

    @staticmethod
    def get_order_summary(order_id: int, user=None):
        """
        Get detailed order summary

        Args:
            order_id: Order ID
            user: Optional user for permission checking

        Returns:
            dict with order summary
        """
        if user:
            order = get_object_or_404(Order, id=order_id, user=user)
        else:
            order = get_object_or_404(Order, id=order_id)

        return {
            "id": order.id,
            "status": order.status,
            "status_display": order.get_status_display(),
            "subtotal": str(order.subtotal),
            "discount_amount": str(order.discount_amount),
            "total_price": str(order.total_price),
            "coupon_code": order.coupon_code,
            "payment_status": order.payment_status,
            "created_at": order.created_at,
            "updated_at": order.updated_at,
        }
