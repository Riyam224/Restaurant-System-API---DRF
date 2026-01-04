# Postman Collection Guide

This guide explains how to use the Postman collection to test the Restaurant System API.

## Files Included

Located in the [postman/](../postman/) folder:

- **Restaurant_API.postman_collection.json** - Complete API endpoint collection
- **Restaurant_API.postman_environment.json** - Environment variables configuration

## Setup Instructions

### 1. Import Collection

1. Open Postman
2. Click **Import** button (top left)
3. Select **postman/Restaurant_API.postman_collection.json**
4. Click **Import**

### 2. Import Environment

1. Click **Import** again
2. Select **postman/Restaurant_API.postman_environment.json**
3. Click **Import**
4. Select **"Restaurant API - Local"** from the environment dropdown (top right)

### 3. Start Your Django Server

```bash
python manage.py runserver
```

The server should be running at `http://localhost:8000`

## Collection Structure

The collection is organized into 4 main folders:

### 1. Authentication (4 endpoints)

- **Register User** - Create a new account
- **Login** - Get JWT tokens
- **Refresh Token** - Refresh expired access token
- **Get Profile** - View user profile (requires authentication)

### 2. Menu (4 endpoints)

- **List Categories** - Get all product categories
- **List All Products** - Get all available products
- **List Products by Category** - Filter products by category
- **Get Product Details** - Get specific product information

### 3. Shopping Cart (3 endpoints)

- **Get Cart** - View current cart
- **Add Item to Cart** - Add products to cart
- **Remove Item from Cart** - Remove items from cart

### 4. Orders (4 endpoints)

- **Create Order from Cart** - Convert cart to order
- **List My Orders** - View order history
- **Get Order Details** - View specific order
- **Update Order Status** - Change order status (Admin only)

## Quick Start - Testing Workflow

Follow this sequence to test the complete user flow:

### Step 1: Register & Login

1. Run **Authentication > Register User**
   - Creates a new user account
   - Default username: `testuser`
   - Modify the request body to use your own credentials

2. Run **Authentication > Login**
   - Returns `access_token` and `refresh_token`
   - Tokens are **automatically saved** to environment variables
   - You're now authenticated!

3. (Optional) Run **Authentication > Get Profile**
   - Verify your authentication is working

### Step 2: Browse Menu

1. Run **Menu > List Categories**
   - View all categories
   - First category ID is **auto-saved** to `{{category_id}}`

2. Run **Menu > List All Products**
   - View all products
   - First product ID is **auto-saved** to `{{product_id}}`

3. Run **Menu > List Products by Category**
   - See products filtered by category

4. Run **Menu > Get Product Details**
   - View detailed product information

### Step 3: Shopping Cart

1. Run **Shopping Cart > Add Item to Cart**
   - Adds product to your cart
   - Modify `product_id` and `quantity` in request body
   - Cart item ID is **auto-saved** to `{{cart_item_id}}`

2. Run **Shopping Cart > Get Cart**
   - View your cart with all items
   - See total price and item count

3. Add more items by running **Add Item to Cart** again with different product IDs

4. (Optional) Run **Shopping Cart > Remove Item from Cart**
   - Remove specific item from cart

### Step 4: Create Order

1. Ensure your cart has items (Step 3)

2. Run **Orders > Create Order from Cart**
   - Converts cart items to an order
   - Cart is automatically cleared
   - Order ID is **auto-saved** to `{{order_id}}`

3. Run **Orders > List My Orders**
   - View all your orders

4. Run **Orders > Get Order Details**
   - View specific order with items

### Step 5: Admin - Update Order Status

1. Run **Orders > Update Order Status**
   - Change order status
   - Valid statuses:
     - `pending` (default)
     - `preparing`
     - `on_the_way`
     - `delivered`
     - `cancelled`

## Environment Variables

The collection uses these variables (automatically managed):

| Variable | Description | Auto-saved |
|----------|-------------|------------|
| `base_url` | API base URL | Manual |
| `access_token` | JWT access token | ✓ After login |
| `refresh_token` | JWT refresh token | ✓ After login |
| `user_id` | Current user ID | ✓ After register |
| `category_id` | Sample category ID | ✓ After list categories |
| `product_id` | Sample product ID | ✓ After list products |
| `cart_item_id` | Sample cart item ID | ✓ After add to cart |
| `order_id` | Sample order ID | ✓ After create order |

## Advanced Usage

### Manual Variable Updates

To use specific IDs instead of auto-saved ones:

1. Click the environment dropdown (top right)
2. Click the eye icon next to "Restaurant API - Local"
3. Edit the variable values
4. Click **Update**

### Testing with Different Users

1. Update the username/password in **Register User** request
2. Run Register → Login sequence
3. New tokens will overwrite previous ones

### Token Refresh

When access token expires (30 minutes):

1. Run **Authentication > Refresh Token**
2. New access token is auto-saved
3. Continue making requests

### Testing Different Order Statuses

1. Create an order
2. Run **Update Order Status** multiple times with different statuses:
   ```json
   {"status": "preparing"}
   {"status": "on_the_way"}
   {"status": "delivered"}
   ```

## Authentication

### Public Endpoints (No authentication required)

- List Categories
- List Products
- Get Product Details

### Protected Endpoints (Require authentication)

All other endpoints require the `Authorization: Bearer {{access_token}}` header.

The collection automatically adds this header for protected endpoints using Bearer Token authentication.

## Troubleshooting

### Error: "Authorization header missing"

**Solution:** Run Login request first to get access token

### Error: "Token is invalid or expired"

**Solution:** Run Refresh Token or Login again

### Error: "Cart is empty" when creating order

**Solution:** Add items to cart first using Add Item to Cart

### Error: "Product not found"

**Solution:**
1. Ensure Django server is running
2. Create products via Django admin or add sample data
3. Access admin at: `http://localhost:8000/admin/`

### Variables not auto-saving

**Solution:**
1. Check that "Restaurant API - Local" environment is selected
2. Check the "Tests" tab in requests - they contain scripts to save variables
3. Ensure requests return successful responses (2xx status codes)

## Sample Data Setup

To populate your database with sample data:

### Via Django Admin

1. Create superuser:
   ```bash
   python manage.py createsuperuser
   ```

2. Access admin: `http://localhost:8000/admin/`

3. Add categories and products manually

### Via Django Shell

```bash
python manage.py shell
```

```python
from menu.models import Category, Product

# Create categories
pizza = Category.objects.create(name="Pizza", is_active=True)
drinks = Category.objects.create(name="Drinks", is_active=True)

# Create products
Product.objects.create(
    category=pizza,
    name="Margherita Pizza",
    description="Classic tomato and mozzarella",
    price=12.99,
    is_available=True
)

Product.objects.create(
    category=drinks,
    name="Coca Cola",
    description="330ml can",
    price=2.50,
    is_available=True
)
```

## API Documentation

For detailed API documentation, visit:

- **Swagger UI**: http://localhost:8000/api/docs/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

## Tips

1. **Use Swagger UI alongside Postman** - Great for viewing response schemas
2. **Check Tests tab** - See how variables are auto-saved
3. **Save responses** - Click "Save Response" to create examples
4. **Use Collection Runner** - Run entire collection to test all endpoints
5. **Environment switching** - Create separate environments for dev/staging/production

## Support

For issues or questions:
- Check [README.md](../README.md) for project setup
- Review [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for endpoint details
- Open an issue in the repository

---

**Happy Testing!** 🚀
