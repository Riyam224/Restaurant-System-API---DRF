# Database Schema Documentation

This document describes the database structure, relationships, and data models for the Restaurant System.

## Table of Contents

- [Overview](#overview)
- [Entity Relationship Diagram](#entity-relationship-diagram)
- [Database Tables](#database-tables)
- [Relationships](#relationships)
- [Indexes and Constraints](#indexes-and-constraints)
- [Data Flow](#data-flow)

## Overview

The Restaurant System uses **SQLite3** as the database engine (suitable for development). For production, PostgreSQL or MySQL is recommended.

### Database Statistics
- **Total Tables**: 8 (including Django default tables)
- **Custom Tables**: 5 (Category, Product, Cart, CartItem, Order, OrderItem)
- **Authentication**: Django's built-in User model
- **Database Size**: Lightweight (SQLite)

## Entity Relationship Diagram

### Complete ER Diagram

```
┌─────────────────────┐
│       User          │ (Django built-in)
│─────────────────────│
│ PK │ id             │
│────┼─────────────────│
│    │ username       │
│    │ email          │
│    │ password       │
│    │ first_name     │
│    │ last_name      │
│    │ date_joined    │
│    │ is_active      │
│    │ is_staff       │
└──────────┬──────────┘
           │
           │ 1:1
           │
           ▼
┌─────────────────────┐        1:N         ┌─────────────────────┐
│       Cart          │◄────────────────────│     CartItem        │
│─────────────────────│                     │─────────────────────│
│ PK │ id             │                     │ PK │ id             │
│────┼─────────────────│                     │────┼─────────────────│
│ FK │ user_id        │                     │ FK │ cart_id        │
│    │ created_at     │                     │ FK │ product_id     │
│    │ updated_at     │                     │    │ quantity       │
└────────────────────┘                     └──────────┬──────────┘
                                                      │
                                                      │ N:1
                                                      │
                                                      ▼
┌─────────────────────┐                     ┌─────────────────────┐
│     Category        │                     │      Product        │
│─────────────────────│         1:N         │─────────────────────│
│ PK │ id             │◄────────────────────│ PK │ id             │
│────┼─────────────────│                     │────┼─────────────────│
│    │ name           │                     │ FK │ category_id    │
│    │ image_url      │                     │    │ name           │
│    │ is_active      │                     │    │ description    │
│    │ created_at     │                     │    │ price          │
│    │ updated_at     │                     │    │ image_url      │
└────────────────────┘                     │    │ is_available   │
                                                 │    │ created_at     │
                                                 │    │ updated_at     │
                                                 └────────────────────┘

┌─────────────────────┐
│       User          │
│─────────────────────│
│ PK │ id             │
└──────────┬──────────┘
           │
           │ 1:N
           │
           ▼
┌─────────────────────┐        1:N         ┌─────────────────────┐
│       Order         │◄────────────────────│    OrderItem        │
│─────────────────────│                     │─────────────────────│
│ PK │ id             │                     │ PK │ id             │
│────┼─────────────────│                     │────┼─────────────────│
│ FK │ user_id        │                     │ FK │ order_id       │
│    │ total_price    │                     │    │ product_id     │
│    │ status         │                     │    │ product_name   │
│    │ created_at     │                     │    │ price          │
└────────────────────┘                     │    │ quantity       │
                                                 └────────────────────┘
```

### Simplified Relationship Overview

```
User ──(1:1)── Cart ──(1:N)── CartItem ──(N:1)── Product ──(N:1)── Category
 │
 └───(1:N)── Order ──(1:N)── OrderItem
```

## Database Tables

### 1. User (Django Built-in: `auth_user`)

Stores user account information using Django's authentication system.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO INCREMENT | Unique user identifier |
| username | VARCHAR(150) | UNIQUE, NOT NULL | User login name |
| email | VARCHAR(254) | NOT NULL | User email address |
| password | VARCHAR(128) | NOT NULL | Hashed password |
| first_name | VARCHAR(150) | | User's first name |
| last_name | VARCHAR(150) | | User's last name |
| is_active | BOOLEAN | DEFAULT TRUE | Account active status |
| is_staff | BOOLEAN | DEFAULT FALSE | Staff/admin status |
| is_superuser | BOOLEAN | DEFAULT FALSE | Superuser status |
| date_joined | DATETIME | NOT NULL | Registration timestamp |
| last_login | DATETIME | | Last login timestamp |

**Indexes:**
- PRIMARY KEY on `id`
- UNIQUE on `username`

---

### 2. Category (`menu_category`)

Stores menu categories for organizing products.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO INCREMENT | Unique category identifier |
| name | VARCHAR(100) | NOT NULL | Category name |
| image_url | VARCHAR(500) | | Category image URL |
| is_active | BOOLEAN | DEFAULT TRUE | Category visibility status |
| created_at | DATETIME | NOT NULL | Creation timestamp |
| updated_at | DATETIME | NOT NULL | Last update timestamp |

**Indexes:**
- PRIMARY KEY on `id`
- INDEX on `is_active` (for filtering)

**Example Data:**
```sql
INSERT INTO menu_category (name, image_url, is_active, created_at, updated_at)
VALUES
  ('Appetizers', 'https://example.com/appetizers.jpg', TRUE, NOW(), NOW()),
  ('Main Courses', 'https://example.com/main.jpg', TRUE, NOW(), NOW()),
  ('Desserts', 'https://example.com/desserts.jpg', TRUE, NOW(), NOW());
```

---

### 3. Product (`menu_product`)

Stores individual menu items/products.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO INCREMENT | Unique product identifier |
| category_id | INTEGER | FOREIGN KEY → Category(id) | Reference to category |
| name | VARCHAR(200) | NOT NULL | Product name |
| description | TEXT | | Product description |
| price | DECIMAL(10,2) | NOT NULL | Product price |
| image_url | VARCHAR(500) | | Product image URL |
| is_available | BOOLEAN | DEFAULT TRUE | Availability status |
| created_at | DATETIME | NOT NULL | Creation timestamp |
| updated_at | DATETIME | NOT NULL | Last update timestamp |

**Indexes:**
- PRIMARY KEY on `id`
- FOREIGN KEY on `category_id`
- INDEX on `is_available` (for filtering)
- INDEX on `category_id, is_available` (composite)

**Constraints:**
- `price` must be >= 0
- `category_id` must reference existing Category

**Example Data:**
```sql
INSERT INTO menu_product (category_id, name, description, price, image_url, is_available, created_at, updated_at)
VALUES
  (1, 'Caesar Salad', 'Fresh romaine lettuce with Caesar dressing', 8.99, 'https://example.com/salad.jpg', TRUE, NOW(), NOW()),
  (2, 'Margherita Pizza', 'Classic pizza with tomato and mozzarella', 12.99, 'https://example.com/pizza.jpg', TRUE, NOW(), NOW());
```

---

### 4. Cart (`cart_cart`)

Stores user shopping carts (one per user).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO INCREMENT | Unique cart identifier |
| user_id | INTEGER | FOREIGN KEY → User(id), UNIQUE | Reference to user |
| created_at | DATETIME | NOT NULL | Creation timestamp |
| updated_at | DATETIME | NOT NULL | Last update timestamp |

**Indexes:**
- PRIMARY KEY on `id`
- UNIQUE on `user_id` (one cart per user)
- FOREIGN KEY on `user_id`

**Constraints:**
- One cart per user enforced by UNIQUE constraint
- Cart deleted when user is deleted (CASCADE)

---

### 5. CartItem (`cart_cartitem`)

Stores individual items in shopping carts.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO INCREMENT | Unique item identifier |
| cart_id | INTEGER | FOREIGN KEY → Cart(id) | Reference to cart |
| product_id | INTEGER | FOREIGN KEY → Product(id) | Reference to product |
| quantity | INTEGER | NOT NULL, >= 1 | Item quantity |

**Indexes:**
- PRIMARY KEY on `id`
- FOREIGN KEY on `cart_id`
- FOREIGN KEY on `product_id`
- UNIQUE on `(cart_id, product_id)` (prevent duplicates)

**Constraints:**
- `quantity` must be >= 1
- CartItem deleted when Cart is deleted (CASCADE)
- CartItem deleted when Product is deleted (CASCADE)

**Computed Fields (not stored):**
- `subtotal = quantity * product.price`

---

### 6. Order (`orders_order`)

Stores customer orders.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO INCREMENT | Unique order identifier |
| user_id | INTEGER | FOREIGN KEY → User(id) | Reference to user |
| total_price | DECIMAL(10,2) | NOT NULL | Total order amount |
| status | VARCHAR(20) | NOT NULL | Order status |
| created_at | DATETIME | NOT NULL | Order creation time |

**Indexes:**
- PRIMARY KEY on `id`
- FOREIGN KEY on `user_id`
- INDEX on `created_at` (for sorting)
- INDEX on `user_id, created_at` (composite)

**Status Values:**
- `pending` - Order placed, awaiting preparation
- `preparing` - Being prepared
- `on_the_way` - Out for delivery
- `delivered` - Completed
- `cancelled` - Cancelled

**Constraints:**
- `total_price` must be >= 0
- `status` must be one of the valid choices

---

### 7. OrderItem (`orders_orderitem`)

Stores individual items in orders with historical product data.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO INCREMENT | Unique item identifier |
| order_id | INTEGER | FOREIGN KEY → Order(id) | Reference to order |
| product_id | INTEGER | NOT NULL | Product ID (reference only) |
| product_name | VARCHAR(200) | NOT NULL | Product name snapshot |
| price | DECIMAL(10,2) | NOT NULL | Price snapshot |
| quantity | INTEGER | NOT NULL | Quantity ordered |

**Indexes:**
- PRIMARY KEY on `id`
- FOREIGN KEY on `order_id`
- INDEX on `order_id` (for order retrieval)

**Constraints:**
- `quantity` must be >= 1
- `price` must be >= 0
- OrderItem deleted when Order is deleted (CASCADE)

**Design Note:** Product data is denormalized to preserve historical information even if the product is updated or deleted later.

**Computed Fields (not stored):**
- `subtotal = quantity * price`

---

## Relationships

### 1. User ↔ Cart (One-to-One)

```sql
Cart.user_id → User.id (UNIQUE)
ON DELETE CASCADE
```

**Behavior:**
- Each user has exactly one cart
- Cart auto-created on first cart operation
- Deleting user deletes their cart

**Query Example:**
```python
# Get or create cart for user
cart, created = Cart.objects.get_or_create(user=request.user)
```

---

### 2. Cart ↔ CartItem (One-to-Many)

```sql
CartItem.cart_id → Cart.id
ON DELETE CASCADE
```

**Behavior:**
- One cart can have multiple items
- Deleting cart removes all items
- Same product can't appear twice (enforced by unique constraint)

**Query Example:**
```python
# Get all items in cart
cart_items = CartItem.objects.filter(cart=cart)
```

---

### 3. Product ↔ CartItem (One-to-Many)

```sql
CartItem.product_id → Product.id
ON DELETE CASCADE
```

**Behavior:**
- One product can be in multiple carts
- Deleting product removes from all carts

**Query Example:**
```python
# Get all carts containing a product
cart_items = CartItem.objects.filter(product_id=product_id)
```

---

### 4. Category ↔ Product (One-to-Many)

```sql
Product.category_id → Category.id
ON DELETE CASCADE
```

**Behavior:**
- One category contains multiple products
- Deleting category deletes all its products

**Query Example:**
```python
# Get all products in a category
products = Product.objects.filter(category_id=category_id)
```

---

### 5. User ↔ Order (One-to-Many)

```sql
Order.user_id → User.id
ON DELETE CASCADE
```

**Behavior:**
- One user can have multiple orders
- Deleting user deletes their orders

**Query Example:**
```python
# Get user's order history
orders = Order.objects.filter(user=request.user).order_by('-created_at')
```

---

### 6. Order ↔ OrderItem (One-to-Many)

```sql
OrderItem.order_id → Order.id
ON DELETE CASCADE
```

**Behavior:**
- One order contains multiple items
- Deleting order removes all items

**Query Example:**
```python
# Get all items in an order
order_items = OrderItem.objects.filter(order=order)
```

---

## Indexes and Constraints

### Primary Keys
All tables use auto-incrementing integer primary keys:
```sql
id INTEGER PRIMARY KEY AUTOINCREMENT
```

### Foreign Key Constraints

| Table | Column | References | On Delete |
|-------|--------|------------|-----------|
| Cart | user_id | User.id | CASCADE |
| CartItem | cart_id | Cart.id | CASCADE |
| CartItem | product_id | Product.id | CASCADE |
| Product | category_id | Category.id | CASCADE |
| Order | user_id | User.id | CASCADE |
| OrderItem | order_id | Order.id | CASCADE |

### Unique Constraints

| Table | Columns | Purpose |
|-------|---------|---------|
| User | username | Prevent duplicate usernames |
| Cart | user_id | One cart per user |
| CartItem | (cart_id, product_id) | Prevent duplicate products in cart |

### Check Constraints

| Table | Column | Constraint |
|-------|--------|------------|
| Product | price | price >= 0 |
| CartItem | quantity | quantity >= 1 |
| Order | total_price | total_price >= 0 |
| OrderItem | quantity | quantity >= 1 |
| OrderItem | price | price >= 0 |

### Performance Indexes

```sql
-- Category filtering
CREATE INDEX idx_category_active ON menu_category(is_active);

-- Product filtering and lookup
CREATE INDEX idx_product_available ON menu_product(is_available);
CREATE INDEX idx_product_category ON menu_product(category_id, is_available);

-- Order history
CREATE INDEX idx_order_user_date ON orders_order(user_id, created_at DESC);

-- Cart item lookup
CREATE INDEX idx_cartitem_cart ON cart_cartitem(cart_id);
CREATE INDEX idx_orderitem_order ON orders_orderitem(order_id);
```

---

## Data Flow

### 1. Product Browsing Flow

```
┌──────────┐
│  Client  │
└────┬─────┘
     │
     ├─> GET /categories/
     │   └─> SELECT * FROM menu_category WHERE is_active = TRUE
     │
     ├─> GET /products/?category_id=1
     │   └─> SELECT * FROM menu_product
     │       WHERE category_id = 1 AND is_available = TRUE
     │
     └─> GET /products/5/
         └─> SELECT * FROM menu_product WHERE id = 5
```

### 2. Cart Operations Flow

```
┌──────────┐
│  Client  │
└────┬─────┘
     │
     ├─> POST /cart/add/ {product_id: 1, quantity: 2}
     │   ├─> Get or Create Cart for user
     │   │   INSERT INTO cart_cart (user_id) VALUES (?)
     │   │   ON CONFLICT DO NOTHING
     │   │
     │   └─> Insert or Update CartItem
     │       INSERT INTO cart_cartitem (cart_id, product_id, quantity)
     │       VALUES (?, ?, ?)
     │       ON CONFLICT (cart_id, product_id)
     │       DO UPDATE SET quantity = quantity + ?
     │
     ├─> GET /cart/
     │   └─> SELECT * FROM cart_cart
     │       JOIN cart_cartitem ON cart.id = cart_cartitem.cart_id
     │       JOIN menu_product ON cart_cartitem.product_id = product.id
     │       WHERE cart.user_id = ?
     │
     └─> DELETE /cart/item/5/
         └─> DELETE FROM cart_cartitem WHERE id = 5 AND cart.user_id = ?
```

### 3. Order Creation Flow

```
┌──────────┐
│  Client  │
└────┬─────┘
     │
     └─> POST /orders/create/
         │
         ├─> 1. Get Cart Items
         │   SELECT * FROM cart_cartitem
         │   JOIN menu_product ON cart_cartitem.product_id = product.id
         │   WHERE cart.user_id = ?
         │
         ├─> 2. Begin Transaction
         │
         ├─> 3. Create Order
         │   INSERT INTO orders_order (user_id, total_price, status)
         │   VALUES (?, ?, 'pending')
         │
         ├─> 4. Create Order Items
         │   For each cart item:
         │     INSERT INTO orders_orderitem
         │     (order_id, product_id, product_name, price, quantity)
         │     VALUES (?, ?, ?, ?, ?)
         │
         ├─> 5. Clear Cart
         │   DELETE FROM cart_cartitem WHERE cart_id = ?
         │
         └─> 6. Commit Transaction
```

### 4. Database Transaction Example

```sql
BEGIN TRANSACTION;

-- Create order
INSERT INTO orders_order (user_id, total_price, status, created_at)
VALUES (1, 32.97, 'pending', '2025-01-01 13:00:00');

-- Get the order ID
SET @order_id = LAST_INSERT_ID();

-- Create order items from cart
INSERT INTO orders_orderitem (order_id, product_id, product_name, price, quantity)
SELECT @order_id, p.id, p.name, p.price, ci.quantity
FROM cart_cartitem ci
JOIN menu_product p ON ci.product_id = p.id
WHERE ci.cart_id = (SELECT id FROM cart_cart WHERE user_id = 1);

-- Clear cart
DELETE FROM cart_cartitem
WHERE cart_id = (SELECT id FROM cart_cart WHERE user_id = 1);

COMMIT;
```

---

## Data Integrity

### Referential Integrity
- All foreign keys use CASCADE delete
- Orphaned records automatically cleaned up
- Database enforces relationships

### Data Validation
- Django ORM validates before database
- Check constraints prevent invalid values
- Unique constraints prevent duplicates

### Concurrency
- SQLite supports concurrent reads
- Write operations are serialized
- For production, use PostgreSQL with proper locking

---

## Migration History

Django tracks schema changes in the `django_migrations` table:

```sql
SELECT * FROM django_migrations ORDER BY applied;
```

Initial migrations:
1. `0001_initial` - Create User tables
2. `menu.0001_initial` - Create Category, Product
3. `cart.0001_initial` - Create Cart, CartItem
4. `orders.0001_initial` - Create Order, OrderItem

---

## Database Backup

### SQLite Backup
```bash
# Backup
sqlite3 db.sqlite3 ".backup backup.db"

# Restore
sqlite3 db.sqlite3 ".restore backup.db"
```

### Django Data Export
```bash
# Export all data
python manage.py dumpdata > backup.json

# Export specific app
python manage.py dumpdata menu > menu_backup.json

# Import data
python manage.py loaddata backup.json
```

---

**Database Schema Version:** 1.0 | **Last Updated:** January 2025
