# Restaurant System - Complete API Documentation

## Table of Contents
1. [Quick Start](#quick-start)
2. [Authentication](#authentication)
3. [Core API Endpoints](#core-api-endpoints)
4. [Analytics API](#analytics-api)
5. [Request/Response Examples](#requestresponse-examples)
6. [Error Handling](#error-handling)
7. [Rate Limiting](#rate-limiting)
8. [Best Practices](#best-practices)

---

## Quick Start

### Base URLs
- **Development**: `http://localhost:8000`
- **Production**: `https://web-production-e1bea.up.railway.app`
- **API Base**: `/api/v1/`
- **Interactive Docs**: `/api/schema/swagger-ui/`

### Quick Test
```bash
# 1. Start server
python manage.py runserver

# 2. Visit Swagger UI
open http://localhost:8000/api/schema/swagger-ui/

# 3. Test an endpoint
curl http://localhost:8000/api/v1/products/
```

---

## Authentication

### JWT Token-Based Authentication

The API uses JSON Web Tokens (JWT) for secure authentication.

#### Token Lifetimes
- **Access Token**: 30 minutes
- **Refresh Token**: 7 days

#### Register New User

```http
POST /api/v1/auth/register/
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "SecurePass123!"
}
```

**Response (201 Created)**:
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "is_staff": false
}
```

#### Login

```http
POST /api/v1/auth/login/
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "SecurePass123!"
}
```

**Response (200 OK)**:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### Refresh Access Token

```http
POST /api/v1/auth/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response (200 OK)**:
```json
{
  "access": "new_access_token_here..."
}
```

#### Get User Profile

```http
GET /api/v1/profile/
Authorization: Bearer {access_token}
```

**Response (200 OK)**:
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "is_staff": false,
  "date_joined": "2026-01-15T10:30:00Z"
}
```

### Using JWT in Requests

Include the access token in the Authorization header:

```http
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

### Google OAuth Authentication

```http
POST /api/v1/auth/google/
Content-Type: application/json

{
  "id_token": "google_id_token_from_firebase"
}
```

---

## Core API Endpoints

### Menu / Products

#### List All Categories

```http
GET /api/v1/categories/
```

**Response (200 OK)**:
```json
[
  {
    "id": 1,
    "name": "Burgers",
    "image": "https://example.com/images/burgers.jpg",
    "is_active": true
  },
  {
    "id": 2,
    "name": "Pizza",
    "image": "https://example.com/images/pizza.jpg",
    "is_active": true
  }
]
```

#### List Products (with filtering and pagination)

```http
GET /api/v1/products/
GET /api/v1/products/?search=burger
GET /api/v1/products/?category_id=1
GET /api/v1/products/?min_price=10&max_price=20
GET /api/v1/products/?sort_by=price_asc
```

**Query Parameters**:
- `search`: Search by name or description
- `category_id`: Filter by category
- `min_price`: Minimum price filter
- `max_price`: Maximum price filter
- `sort_by`: Sort order (`price_asc`, `price_desc`, `name`, `newest`)
- `page`: Page number (default: 1)

**Response (200 OK)**:
```json
{
  "count": 50,
  "next": "http://localhost:8000/api/v1/products/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "category_id": 1,
      "category_name": "Burgers",
      "name": "Classic Burger",
      "description": "Juicy beef patty with lettuce, tomato, and special sauce",
      "price": "12.99",
      "image": "https://example.com/images/classic-burger.jpg",
      "is_available": true,
      "stock_quantity": 50,
      "average_rating": 4.5,
      "total_reviews": 120
    }
  ]
}
```

#### Get Single Product

```http
GET /api/v1/products/{id}/
```

**Response (200 OK)**:
```json
{
  "id": 1,
  "category_id": 1,
  "category_name": "Burgers",
  "name": "Classic Burger",
  "description": "Juicy beef patty with lettuce, tomato, and special sauce",
  "price": "12.99",
  "image": "https://example.com/images/classic-burger.jpg",
  "is_available": true,
  "stock_quantity": 50,
  "average_rating": 4.5,
  "total_reviews": 120,
  "created_at": "2026-01-10T08:00:00Z",
  "updated_at": "2026-01-15T12:30:00Z"
}
```

#### Get Product Rating Statistics

```http
GET /api/v1/products/{id}/ratings/
```

**Response (200 OK)**:
```json
{
  "product_id": 1,
  "average_rating": 4.5,
  "total_reviews": 120,
  "distribution": {
    "5": 80,
    "4": 30,
    "3": 8,
    "2": 1,
    "1": 1,
    "total": 120
  }
}
```

---

### Shopping Cart

**Note**: All cart endpoints require authentication.

#### Get User's Cart

```http
GET /api/v1/cart/
Authorization: Bearer {access_token}
```

**Response (200 OK)**:
```json
{
  "id": 1,
  "items": [
    {
      "id": 5,
      "product_id": 10,
      "product_name": "Classic Burger",
      "product_image": "https://example.com/burger.jpg",
      "price": "12.50",
      "quantity": 2,
      "subtotal": "25.00"
    }
  ],
  "total_items": 2,
  "total_price": "25.00",
  "created_at": "2026-01-15T10:00:00Z",
  "updated_at": "2026-01-15T14:30:00Z"
}
```

#### Add Item to Cart

```http
POST /api/v1/cart/add/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "product_id": 10,
  "quantity": 2
}
```

**Validation Rules**:
- Product must exist and be available
- Product must have sufficient stock
- Maximum quantity per item: 99
- Quantity must be positive integer

**Response (200 OK)**:
```json
{
  "message": "Item added to cart successfully",
  "cart": {
    "id": 1,
    "items": [...],
    "total_items": 2,
    "total_price": "25.00"
  }
}
```

**Error Responses**:
```json
// 400 Bad Request - Product unavailable
{
  "error": "Product is not available"
}

// 400 Bad Request - Insufficient stock
{
  "error": "Insufficient stock. Only 5 items available"
}

// 400 Bad Request - Invalid quantity
{
  "error": "Quantity must be between 1 and 99"
}
```

#### Update Cart Item Quantity

```http
PATCH /api/v1/cart/item/{item_id}/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "quantity": 3
}
```

#### Remove Item from Cart

```http
DELETE /api/v1/cart/item/{item_id}/
Authorization: Bearer {access_token}
```

**Response (204 No Content)**

#### Clear Cart

```http
DELETE /api/v1/cart/clear/
Authorization: Bearer {access_token}
```

---

### Addresses

#### List User Addresses

```http
GET /api/v1/addresses/
Authorization: Bearer {access_token}
```

**Response (200 OK)**:
```json
[
  {
    "id": 1,
    "label": "Home",
    "city": "New York",
    "street": "5th Avenue",
    "building": "123",
    "floor": "4",
    "apartment": "A",
    "latitude": 40.7128,
    "longitude": -74.0060,
    "is_default": true,
    "created_at": "2026-01-10T10:00:00Z"
  }
]
```

#### Create Address

```http
POST /api/v1/addresses/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "label": "Work",
  "city": "New York",
  "street": "Broadway",
  "building": "456",
  "floor": "10",
  "apartment": "B",
  "latitude": 40.7580,
  "longitude": -73.9855,
  "is_default": false
}
```

#### Update Address

```http
PUT /api/v1/addresses/{id}/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "label": "Home - Updated",
  "is_default": true
}
```

#### Delete Address

```http
DELETE /api/v1/addresses/{id}/
Authorization: Bearer {access_token}
```

---

### Orders

#### Create Order from Cart

```http
POST /api/v1/orders/create/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "address_id": 1,
  "coupon_code": "SAVE10"
}
```

**Validation**:
- Cart must not be empty
- Address must exist and belong to user
- Coupon (if provided) must be valid
- All cart items must have sufficient stock

**Response (201 Created)**:
```json
{
  "message": "Order created successfully",
  "order_id": 15,
  "status": "pending",
  "subtotal": "50.00",
  "discount_amount": "5.00",
  "coupon_code": "SAVE10",
  "total_price": "45.00",
  "items_count": 3,
  "created_at": "2026-01-16T10:30:00Z"
}
```

**Error Responses**:
```json
// 400 Bad Request - Empty cart
{
  "error": "Cart is empty"
}

// 400 Bad Request - Invalid address
{
  "error": "Address not found"
}

// 400 Bad Request - Invalid coupon
{
  "error": "Coupon is expired or invalid"
}

// 400 Bad Request - Insufficient stock
{
  "error": "Product 'Classic Burger' has insufficient stock"
}
```

#### List My Orders

```http
GET /api/v1/orders/
Authorization: Bearer {access_token}
```

**Response (200 OK)**:
```json
[
  {
    "id": 15,
    "address": {
      "id": 1,
      "label": "Home",
      "city": "New York",
      "street": "5th Avenue",
      "full_address": "123 5th Avenue, Floor 4, Apt A, New York"
    },
    "status": "pending",
    "status_display": "Pending",
    "subtotal": "50.00",
    "discount_amount": "5.00",
    "coupon_code": "SAVE10",
    "total_price": "45.00",
    "items_count": 3,
    "created_at": "2026-01-16T10:30:00Z",
    "updated_at": "2026-01-16T10:30:00Z"
  }
]
```

#### Get Order Details

```http
GET /api/v1/orders/{id}/
Authorization: Bearer {access_token}
```

**Response (200 OK)**:
```json
{
  "id": 15,
  "address": {
    "id": 1,
    "label": "Home",
    "full_address": "123 5th Avenue, Floor 4, Apt A, New York"
  },
  "status": "preparing",
  "status_display": "Preparing",
  "subtotal": "50.00",
  "discount_amount": "5.00",
  "coupon_code": "SAVE10",
  "total_price": "45.00",
  "items": [
    {
      "id": 1,
      "product_id": 10,
      "product_name": "Classic Burger",
      "product_image": "https://example.com/burger.jpg",
      "price": "12.50",
      "quantity": 2,
      "subtotal": "25.00"
    }
  ],
  "history": [
    {
      "id": 1,
      "status": "pending",
      "status_display": "Pending",
      "created_at": "2026-01-16T10:30:00Z"
    },
    {
      "id": 2,
      "status": "preparing",
      "status_display": "Preparing",
      "created_at": "2026-01-16T10:45:00Z"
    }
  ],
  "created_at": "2026-01-16T10:30:00Z",
  "updated_at": "2026-01-16T10:45:00Z"
}
```

#### Get Order Status

```http
GET /api/v1/orders/{id}/status/
Authorization: Bearer {access_token}
```

**Response (200 OK)**:
```json
{
  "order_id": 15,
  "status": "on_the_way",
  "status_display": "On the way",
  "updated_at": "2026-01-16T12:30:00Z"
}
```

#### Update Order Status (Admin Only)

```http
PATCH /api/v1/orders/{id}/status/
Authorization: Bearer {admin_access_token}
Content-Type: application/json

{
  "status": "preparing"
}
```

**Valid Status Transitions**:
- `pending` → `preparing`, `cancelled`
- `preparing` → `on_the_way`, `cancelled`
- `on_the_way` → `delivered`, `cancelled`
- `delivered` → (final state)
- `cancelled` → (final state)

**Order Status Flow**:
```
pending → preparing → on_the_way → delivered
   ↓          ↓            ↓
   └──────────┴────────────┴─────→ cancelled
```

#### Cancel Order

```http
POST /api/v1/orders/{id}/cancel/
Authorization: Bearer {access_token}
```

**Note**: Orders can only be cancelled if status is `pending` or `preparing`.

---

### Coupons

#### List Available Coupons

```http
GET /api/v1/coupons/
Authorization: Bearer {access_token}
```

**Response (200 OK)**:
```json
[
  {
    "id": 1,
    "code": "SAVE10",
    "discount_type": "percentage",
    "discount_value": "10.00",
    "minimum_order_amount": "30.00",
    "maximum_discount": "50.00",
    "usage_limit": 100,
    "usage_limit_per_user": 1,
    "valid_from": "2026-01-01T00:00:00Z",
    "valid_to": "2026-02-28T23:59:59Z",
    "is_active": true
  }
]
```

#### Validate Coupon

```http
POST /api/v1/coupons/validate/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "code": "SAVE10",
  "order_amount": 50.00
}
```

**Response (200 OK)**:
```json
{
  "valid": true,
  "coupon_code": "SAVE10",
  "discount_type": "percentage",
  "discount_value": "10.00",
  "order_amount": "50.00",
  "discount_amount": "5.00",
  "final_amount": "45.00",
  "savings": "5.00"
}
```

**Error Response (400 Bad Request)**:
```json
{
  "valid": false,
  "error": "Coupon has expired"
}

// Other possible errors:
// "Coupon not found"
// "Minimum order amount is $30.00"
// "Coupon usage limit exceeded"
// "You have already used this coupon"
```

#### Get Coupon Details

```http
GET /api/v1/coupons/{code}/
Authorization: Bearer {access_token}
```

#### My Coupon Usage History

```http
GET /api/v1/coupons/my-usage/
Authorization: Bearer {access_token}
```

**Response (200 OK)**:
```json
[
  {
    "id": 1,
    "coupon_code": "SAVE10",
    "order_id": 15,
    "discount_amount": "5.00",
    "used_at": "2026-01-16T10:30:00Z"
  }
]
```

---

### Reviews

#### Create Review

```http
POST /api/v1/reviews/create/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "product_id": 10,
  "rating": 5,
  "comment": "Excellent burger! Best I've ever had."
}
```

**Validation**:
- Rating must be between 1 and 5
- User must have purchased the product
- One review per user per product

**Response (201 Created)**:
```json
{
  "id": 1,
  "product_id": 10,
  "product_name": "Classic Burger",
  "user": "john_doe",
  "rating": 5,
  "comment": "Excellent burger! Best I've ever had.",
  "is_verified_purchase": true,
  "is_approved": false,
  "helpful_count": 0,
  "created_at": "2026-01-16T15:00:00Z"
}
```

#### List Product Reviews

```http
GET /api/v1/reviews/?product_id=10
GET /api/v1/reviews/?product_id=10&rating=5
```

**Query Parameters**:
- `product_id`: Filter by product (required)
- `rating`: Filter by rating (1-5)
- `is_approved`: Filter by approval status (admin only)

#### Update Review (within 7 days)

```http
PUT /api/v1/reviews/{id}/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "rating": 4,
  "comment": "Updated review: Very good burger"
}
```

**Note**: Reviews can only be updated within 7 days of creation.

#### Delete Review

```http
DELETE /api/v1/reviews/{id}/
Authorization: Bearer {access_token}
```

#### Vote Review Helpfulness

```http
POST /api/v1/reviews/helpful/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "review_id": 1,
  "is_helpful": true
}
```

---

## Analytics API

**Note**: All analytics endpoints require admin authentication (`is_staff=True`).

### Dashboard KPIs

```http
GET /api/v1/analytics/dashboard/?days=30
Authorization: Bearer {admin_access_token}
```

**Query Parameters**:
- `days`: Number of days to analyze (default: 30)

**Response (200 OK)**:
```json
{
  "period_days": 30,
  "revenue": {
    "current": 12500.00,
    "previous": 10000.00,
    "growth_percentage": 25.0
  },
  "orders": {
    "current": 450,
    "previous": 380,
    "growth_percentage": 18.4
  },
  "average_order_value": 27.78,
  "total_users": 1250,
  "active_users": 380,
  "conversion_rate": 36.0,
  "order_status": [
    {"status": "pending", "count": 25},
    {"status": "preparing", "count": 15},
    {"status": "on_the_way", "count": 10},
    {"status": "delivered", "count": 400}
  ]
}
```

### Revenue Analytics

```http
GET /api/v1/analytics/revenue/metrics/?start_date=2026-01-01&end_date=2026-01-31
Authorization: Bearer {admin_access_token}
```

**Response (200 OK)**:
```json
{
  "total_revenue": 12500.00,
  "total_orders": 450,
  "average_order_value": 27.78,
  "total_discount": 1250.00,
  "gross_revenue": 13750.00,
  "period": {
    "start": "2026-01-01T00:00:00Z",
    "end": "2026-01-31T23:59:59Z"
  }
}
```

### Daily Revenue

```http
GET /api/v1/analytics/revenue/daily/?start_date=2026-01-01&end_date=2026-01-31
Authorization: Bearer {admin_access_token}
```

**Response (200 OK)**:
```json
{
  "dates": ["2026-01-01", "2026-01-02", ...],
  "revenue": [450.00, 520.00, ...],
  "order_count": [15, 18, ...]
}
```

### Order Analytics

```http
GET /api/v1/analytics/orders/status/
Authorization: Bearer {admin_access_token}
```

**Response (200 OK)**:
```json
{
  "by_status": [
    {"status": "pending", "count": 25, "percentage": 5.6},
    {"status": "preparing", "count": 15, "percentage": 3.3},
    {"status": "on_the_way", "count": 10, "percentage": 2.2},
    {"status": "delivered", "count": 400, "percentage": 88.9}
  ],
  "total_orders": 450
}
```

### User Analytics

```http
GET /api/v1/analytics/users/metrics/?days=30
Authorization: Bearer {admin_access_token}
```

**Response (200 OK)**:
```json
{
  "total_users": 1250,
  "new_users": 85,
  "active_users": 380,
  "retention_rate": 72.5,
  "average_orders_per_user": 2.3
}
```

### Product Performance

```http
GET /api/v1/analytics/products/performance/?limit=10
Authorization: Bearer {admin_access_token}
```

**Response (200 OK)**:
```json
{
  "top_products": [
    {
      "product_id": 10,
      "product_name": "Classic Burger",
      "total_revenue": 2500.00,
      "total_orders": 200,
      "units_sold": 350,
      "average_rating": 4.5
    }
  ],
  "total_products": 45,
  "average_revenue_per_product": 277.78
}
```

### Coupon Performance

```http
GET /api/v1/analytics/coupons/performance/
Authorization: Bearer {admin_access_token}
```

**Response (200 OK)**:
```json
{
  "coupons": [
    {
      "code": "SAVE10",
      "usage_count": 150,
      "total_discount": 750.00,
      "revenue_impact": 7500.00,
      "roi": 10.0
    }
  ],
  "total_discount_given": 1250.00,
  "orders_with_coupons": 180,
  "coupon_usage_rate": 40.0
}
```

### Review Analytics

```http
GET /api/v1/analytics/reviews/metrics/
Authorization: Bearer {admin_access_token}
```

**Response (200 OK)**:
```json
{
  "total_reviews": 850,
  "average_rating": 4.3,
  "distribution": {
    "5": 520,
    "4": 210,
    "3": 85,
    "2": 25,
    "1": 10
  },
  "verified_purchases": 720,
  "pending_approval": 15
}
```

### AI-Powered Insights

```http
GET /api/v1/analytics/insights/business/?days=30
Authorization: Bearer {admin_access_token}
```

**Response (200 OK)**:
```json
{
  "overview": "Revenue increased 25% compared to last month with strong growth in dinner orders.",
  "opportunities": [
    "Peak ordering time is 6-8 PM. Consider happy hour promotion.",
    "Top 3 products generate 60% of revenue. Expand similar items."
  ],
  "warnings": [
    "Delivery times averaging 45min, above target of 30min.",
    "Cart abandonment rate at 35%, up from 28% last month."
  ],
  "recommendations": [
    "Launch a loyalty program to improve retention",
    "Optimize delivery routing to reduce wait times",
    "A/B test checkout flow to reduce abandonment"
  ]
}
```

### Anomaly Detection

```http
GET /api/v1/analytics/anomalies/detect/?days=7&use_ai=true
Authorization: Bearer {admin_access_token}
```

**Response (200 OK)**:
```json
{
  "anomalies": [
    {
      "type": "revenue_spike",
      "severity": "warning",
      "date": "2026-01-15",
      "metric": "daily_revenue",
      "value": 1500.00,
      "expected": 450.00,
      "explanation": "Revenue spike detected on Jan 15. This is 3.3x higher than the average daily revenue, possibly due to a successful promotion or event."
    }
  ],
  "total_anomalies": 1
}
```

### Predictions

```http
GET /api/v1/analytics/predictions/tomorrow/
Authorization: Bearer {admin_access_token}
```

**Response (200 OK)**:
```json
{
  "date": "2026-01-17",
  "predicted_revenue": 485.50,
  "predicted_orders": 18,
  "confidence": 0.85
}
```

---

## Request/Response Examples

### Successful Response Format

```json
{
  "id": 1,
  "field": "value",
  "nested": {
    "data": "here"
  }
}
```

### Paginated Response Format

```json
{
  "count": 100,
  "next": "http://localhost:8000/api/v1/endpoint/?page=2",
  "previous": null,
  "results": [
    {"id": 1, "data": "..."},
    {"id": 2, "data": "..."}
  ]
}
```

### Error Response Format

```json
{
  "detail": "Error message here"
}

// or for field-specific errors

{
  "field_name": ["Error message for this field"],
  "another_field": ["Another error message"]
}
```

---

## Error Handling

### HTTP Status Codes

| Status Code | Meaning | When It Occurs |
|------------|---------|----------------|
| **200 OK** | Success | Request completed successfully |
| **201 Created** | Resource created | POST request created new resource |
| **204 No Content** | Success, no data | DELETE request successful |
| **400 Bad Request** | Invalid input | Validation failed, missing required fields |
| **401 Unauthorized** | Authentication required | Missing or invalid token |
| **403 Forbidden** | Permission denied | Authenticated but not authorized |
| **404 Not Found** | Resource not found | Requested resource doesn't exist |
| **409 Conflict** | Conflict | Resource already exists (e.g., duplicate review) |
| **429 Too Many Requests** | Rate limit exceeded | Too many requests in short time |
| **500 Internal Server Error** | Server error | Unexpected server-side error |

### Common Error Scenarios

#### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}

{
  "detail": "Given token not valid for any token type"
}
```

**Solution**: Include valid JWT token in Authorization header.

#### 400 Bad Request
```json
{
  "product_id": ["This field is required."],
  "quantity": ["Ensure this value is greater than or equal to 1."]
}
```

**Solution**: Check request body for missing or invalid fields.

#### 403 Forbidden
```json
{
  "detail": "You do not have permission to perform this action."
}
```

**Solution**: User lacks required permissions (e.g., not admin for analytics endpoints).

#### 404 Not Found
```json
{
  "detail": "Not found."
}
```

**Solution**: Check that resource ID is correct and exists.

#### 429 Rate Limited
```json
{
  "detail": "Request was throttled. Expected available in 3600 seconds."
}
```

**Solution**: Wait before making more requests, or upgrade to authenticated access for higher limits.

---

## Rate Limiting

### Throttling Limits

| User Type | Limit | Scope |
|-----------|-------|-------|
| **Anonymous** | 100 requests | per hour |
| **Authenticated** | 2000 requests | per day |
| **Admin** | No limit | - |

### Rate Limit Headers

Responses include rate limit information:

```http
X-RateLimit-Limit: 2000
X-RateLimit-Remaining: 1950
X-RateLimit-Reset: 1642348800
```

### Handling Rate Limits

```python
import time
import requests

def make_request_with_retry(url, headers, max_retries=3):
    for attempt in range(max_retries):
        response = requests.get(url, headers=headers)

        if response.status_code == 429:
            retry_after = int(response.headers.get('Retry-After', 60))
            print(f"Rate limited. Waiting {retry_after} seconds...")
            time.sleep(retry_after)
            continue

        return response

    raise Exception("Max retries exceeded")
```

---

## Best Practices

### 1. Authentication

```python
# ✅ Good: Store tokens securely
from flutter_secure_storage import FlutterSecureStorage

storage = FlutterSecureStorage()
await storage.write(key: 'access_token', value: token)

# ❌ Bad: Store in plain text
localStorage.setItem('token', token)  # Insecure!
```

### 2. Token Refresh

```python
# ✅ Good: Automatic token refresh
async def api_request(endpoint):
    try:
        response = await http.get(endpoint, headers=auth_headers)
        return response
    except Unauthorized:
        # Token expired, refresh it
        new_token = await refresh_access_token()
        # Retry request with new token
        return await http.get(endpoint, headers={'Authorization': f'Bearer {new_token}'})
```

### 3. Error Handling

```python
# ✅ Good: Comprehensive error handling
try:
    response = requests.post(url, json=data, headers=headers)
    response.raise_for_status()
    return response.json()
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 400:
        # Handle validation errors
        errors = e.response.json()
        show_validation_errors(errors)
    elif e.response.status_code == 401:
        # Redirect to login
        redirect_to_login()
    else:
        # Show generic error
        show_error_message()
except requests.exceptions.ConnectionError:
    show_offline_message()
```

### 4. Pagination

```python
# ✅ Good: Fetch all pages
def fetch_all_products():
    products = []
    url = f"{BASE_URL}/api/v1/products/"

    while url:
        response = requests.get(url, headers=headers)
        data = response.json()
        products.extend(data['results'])
        url = data['next']  # Next page URL or None

    return products
```

### 5. Caching

```python
# ✅ Good: Cache frequently accessed data
from functools import lru_cache
from datetime import datetime, timedelta

@lru_cache(maxsize=100)
def get_categories():
    response = requests.get(f"{BASE_URL}/api/v1/categories/")
    return response.json()

# Cache with expiration
class Cache:
    def __init__(self, ttl=300):  # 5 minutes
        self.cache = {}
        self.ttl = ttl

    def get(self, key):
        if key in self.cache:
            data, timestamp = self.cache[key]
            if datetime.now() - timestamp < timedelta(seconds=self.ttl):
                return data
        return None

    def set(self, key, value):
        self.cache[key] = (value, datetime.now())
```

### 6. Search Optimization

```python
# ✅ Good: Debounce search requests
import asyncio

class SearchDebouncer:
    def __init__(self, delay=0.5):
        self.delay = delay
        self.timer = None

    async def debounce(self, func, *args):
        if self.timer:
            self.timer.cancel()

        self.timer = asyncio.create_task(
            self._delayed_call(func, *args)
        )

    async def _delayed_call(self, func, *args):
        await asyncio.sleep(self.delay)
        await func(*args)

# Usage
debouncer = SearchDebouncer()
await debouncer.debounce(search_products, search_query)
```

### 7. Request Validation

```python
# ✅ Good: Validate data before sending
from pydantic import BaseModel, validator

class CreateOrderRequest(BaseModel):
    address_id: int
    coupon_code: Optional[str] = None

    @validator('address_id')
    def validate_address_id(cls, v):
        if v <= 0:
            raise ValueError('Invalid address ID')
        return v

# Use it
try:
    order_data = CreateOrderRequest(
        address_id=1,
        coupon_code="SAVE10"
    )
    response = requests.post(url, json=order_data.dict())
except ValueError as e:
    print(f"Validation error: {e}")
```

---

## Versioning

The API is currently at version 1 (`/api/v1/`). When breaking changes are introduced, a new version will be released (`/api/v2/`) while maintaining support for v1.

**Current Version**: 1.0.0
**Last Updated**: February 2026

---

## Support Resources

- **Interactive API Docs**: [http://localhost:8000/api/schema/swagger-ui/](http://localhost:8000/api/schema/swagger-ui/)
- **ReDoc Documentation**: [http://localhost:8000/api/schema/redoc/](http://localhost:8000/api/schema/redoc/)
- **OpenAPI Schema**: [http://localhost:8000/api/schema/](http://localhost:8000/api/schema/)
- **Admin Panel**: [http://localhost:8000/admin/](http://localhost:8000/admin/)

---

**API Version**: 1.0.0
**Last Updated**: February 14, 2026
**Status**: Production Ready ✅
