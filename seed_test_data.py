#!/usr/bin/env python
"""
Seed test data for analytics testing.

This creates sample orders, users, and data to test the analytics endpoints.

Usage:
    python seed_test_data.py
"""

import os
import sys
import django
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from orders.models import Order, OrderItem
from addresses.models import Address
from menu.models import Product, Category
from reviews.models import Review

User = get_user_model()

def create_test_data():
    """Create test data for analytics."""
    print("Creating test data for analytics...\n")

    # Create users
    print("1. Creating users...")
    users = []
    for i in range(5):
        username = f'testuser{i+1}'
        user, created = User.objects.get_or_create(
            username=username,
            defaults={'email': f'{username}@test.com'}
        )
        if created:
            user.set_password('test123')
            user.save()
            print(f"   ✅ Created user: {username}")
        else:
            print(f"   ⏭️  User already exists: {username}")
        users.append(user)

    # Create category
    print("\n2. Creating product category...")
    category, created = Category.objects.get_or_create(
        name='Test Category',
        defaults={'description': 'Test category for analytics'}
    )
    if created:
        print("   ✅ Created category")
    else:
        print("   ⏭️  Category already exists")

    # Create products
    print("\n3. Creating products...")
    products = []
    product_names = ['Pizza', 'Burger', 'Pasta', 'Salad', 'Sandwich']
    prices = [15.99, 12.99, 18.99, 8.99, 10.99]

    for name, price in zip(product_names, prices):
        product, created = Product.objects.get_or_create(
            name=name,
            category=category,
            defaults={
                'description': f'Delicious {name}',
                'price': Decimal(str(price)),
                'is_available': True
            }
        )
        if created:
            print(f"   ✅ Created product: {name} (${price})")
        else:
            print(f"   ⏭️  Product already exists: {name}")
        products.append(product)

    # Create addresses
    print("\n4. Creating addresses...")
    addresses = []
    for user in users[:3]:  # Only first 3 users
        address, created = Address.objects.get_or_create(
            user=user,
            label='Home',
            defaults={
                'street': f'{user.id * 100} Main St',
                'city': 'New York',
                'building': f'Apt {user.id}',
                'lat': Decimal('40.7128'),
                'lng': Decimal('-74.0060')
            }
        )
        if created:
            print(f"   ✅ Created address for {user.username}")
        else:
            print(f"   ⏭️  Address already exists for {user.username}")
        addresses.append(address)

    # Create orders (over the last 30 days)
    print("\n5. Creating orders...")
    order_count = 0
    statuses = ['delivered', 'delivered', 'delivered', 'preparing', 'pending']

    for day in range(30):
        date = timezone.now() - timedelta(days=day)

        # Create 1-3 orders per day
        for _ in range(min(3, len(addresses))):
            user = users[order_count % len(users[:3])]
            address = addresses[order_count % len(addresses)]
            status_choice = statuses[order_count % len(statuses)]

            # Random product selection
            product = products[order_count % len(products)]
            quantity = (order_count % 3) + 1
            subtotal = product.price * quantity
            discount = Decimal('5.00') if order_count % 3 == 0 else Decimal('0.00')
            total = subtotal - discount

            # Create order
            order = Order.objects.create(
                user=user,
                address=address,
                subtotal=subtotal,
                discount_amount=discount,
                total_price=total,
                coupon_code='SAVE5' if discount > 0 else '',
                payment_status='paid' if status_choice == 'delivered' else 'pending',
                status=status_choice,
                created_at=date
            )

            # Create order item
            OrderItem.objects.create(
                order=order,
                product_id=product.id,
                product_name=product.name,
                price=product.price,
                quantity=quantity
            )

            order_count += 1

    print(f"   ✅ Created {order_count} orders")

    # Create reviews
    print("\n6. Creating reviews...")
    review_count = 0
    for i, product in enumerate(products[:3]):  # Review first 3 products
        for j, user in enumerate(users[:2]):  # 2 users review each
            try:
                Review.objects.create(
                    user=user,
                    product_id=product.id,
                    rating=(i + j) % 5 + 1,  # Mix of ratings 1-5
                    comment=f"Great {product.name}!",
                    is_verified_purchase=True,
                    is_approved=True
                )
                review_count += 1
            except:
                pass  # Skip if review already exists

    print(f"   ✅ Created {review_count} reviews")

    # Summary
    print("\n" + "="*60)
    print("✅ TEST DATA SEEDING COMPLETE!")
    print("="*60)
    print(f"\nCreated:")
    print(f"  • {len(users)} users")
    print(f"  • {len(products)} products")
    print(f"  • {len(addresses)} addresses")
    print(f"  • {order_count} orders (last 30 days)")
    print(f"  • {review_count} reviews")

    # Calculate analytics summary
    paid_orders = Order.objects.filter(payment_status='paid')
    total_revenue = sum(order.total_price for order in paid_orders)

    print(f"\nAnalytics Preview:")
    print(f"  • Total Revenue: ${total_revenue:.2f}")
    print(f"  • Paid Orders: {paid_orders.count()}")
    print(f"  • Average Order Value: ${total_revenue / paid_orders.count():.2f}" if paid_orders.count() > 0 else "  • Average Order Value: $0.00")

    print("\n🎉 Ready to test analytics!")
    print("\nNext steps:")
    print("  1. Run the server: python manage.py runserver")
    print("  2. Test API: python test_analytics_api.py")
    print("  3. Or visit: http://localhost:8000/api/docs/")

if __name__ == '__main__':
    try:
        create_test_data()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
