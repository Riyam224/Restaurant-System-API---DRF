# API Documentation

Complete reference for all API endpoints in the Restaurant System.

## Table of Contents

- [Overview](#overview)
- [Authentication](#authentication)
- [Base URL](#base-url)
- [Response Format](#response-format)
- [Error Codes](#error-codes)
- [Endpoints](#endpoints)
  - [Authentication Endpoints](#authentication-endpoints)
  - [Menu Endpoints](#menu-endpoints)
  - [Cart Endpoints](#cart-endpoints)
  - [Order Endpoints](#order-endpoints)

## Overview

The Restaurant System API is a RESTful API that uses JSON for request and response bodies. All endpoints follow REST conventions and return appropriate HTTP status codes.

### API Version
- **Current Version**: v1
- **Base Path**: `/api/v1/`

### Content Type
All requests and responses use:
```
Content-Type: application/json
```

## Authentication

The API uses **JWT (JSON Web Token)** authentication for protected endpoints.

### Token Types

| Token Type | Lifetime | Purpose |
|------------|----------|---------|
| Access Token | 30 minutes | Authenticate API requests |
| Refresh Token | 7 days | Obtain new access tokens |

### Using Authentication

Include the access token in the Authorization header:

```http
Authorization: Bearer <access_token>
```

### Token Flow Diagram

```
┌─────────┐                                    ┌─────────┐
│ Client  │                                    │   API   │
└────┬────┘                                    └────┬────┘
     │                                              │
     │ 1. POST /api/v1/auth/login                   │
     │  {username, password}                        │
     │─────────────────────────────────────────────>│
     │                                              │
     │ 2. Response: {access, refresh}               │
     │<─────────────────────────────────────────────│
     │                                              │
     │ 3. GET /api/v1/cart/                         │
     │  Authorization: Bearer <access_token>        │
     │─────────────────────────────────────────────>│
     │                                              │
     │ 4. Response: {cart_data}                     │
     │<─────────────────────────────────────────────│
     │                                              │
     │ ... (30 minutes later, token expires)        │
     │                                              │
     │ 5. POST /api/v1/auth/refresh/                │
     │  {refresh: <refresh_token>}                  │
     │─────────────────────────────────────────────>│
     │                                              │
     │ 6. Response: {access: <new_access_token>}    │
     │<─────────────────────────────────────────────│
     │                                              │
```

## Base URL

**Development:**
```
http://localhost:8000/api/v1/
```

**Production:**
```
https://your-domain.com/api/v1/
```

## Response Format

### Success Response
```json
{
  "id": 1,
  "field1": "value1",
  "field2": "value2"
}
```

### Error Response
```json
{
  "detail": "Error message describing what went wrong",
  "code": "error_code"
}
```

### Paginated List Response
```json
{
  "count": 45,
  "next": "http://localhost:8000/api/v1/products/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "field": "value"
    },
    {
      "id": 2,
      "field": "value"
    }
  ]
}
```

### Non-Paginated List Response
```json
[
  {
    "id": 1,
    "field": "value"
  },
  {
    "id": 2,
    "field": "value"
  }
]
```

## Error Codes

| Status Code | Meaning | Common Causes |
|-------------|---------|---------------|
| 200 | OK | Successful GET request |
| 201 | Created | Successful POST request creating a resource |
| 204 | No Content | Successful DELETE request |
| 400 | Bad Request | Invalid data, validation errors |
| 401 | Unauthorized | Missing or invalid authentication token |
| 403 | Forbidden | Valid token but insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 405 | Method Not Allowed | Wrong HTTP method for endpoint |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server-side error |

## Endpoints

---

## Authentication Endpoints

### 1. Register User

Create a new user account.

**Endpoint:** `POST /api/v1/auth/register/`

**Authentication:** Not required

**Request Body:**
```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "securepass123",
  "password2": "securepass123"
}
```

**Field Requirements:**
- `username` (required): 3-150 characters, letters, digits, and @/./+/-/_ only
- `email` (required): Valid email address
- `password` (required): Minimum 8 characters
- `password2` (required): Must match password

**Success Response (201 Created):**
```json
{
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com"
  },
  "message": "User created successfully"
}
```

**Error Response (400 Bad Request):**
```json
{
  "username": ["A user with that username already exists."],
  "password": ["This password is too short. It must contain at least 8 characters."]
}
```

---

### 2. Login

Authenticate and receive JWT tokens.

**Endpoint:** `POST /api/v1/auth/login/`

**Authentication:** Not required

**Request Body:**
```json
{
  "username": "johndoe",
  "password": "securepass123"
}
```

**Success Response (200 OK):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Error Response (401 Unauthorized):**
```json
{
  "detail": "No active account found with the given credentials"
}
```

---

### 3. Refresh Token

Get a new access token using refresh token.

**Endpoint:** `POST /api/v1/auth/refresh/`

**Authentication:** Not required

**Request Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Success Response (200 OK):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Error Response (401 Unauthorized):**
```json
{
  "detail": "Token is invalid or expired",
  "code": "token_not_valid"
}
```

---

### 4. Get User Profile

Retrieve authenticated user's profile information.

**Endpoint:** `GET /api/v1/profile/`

**Authentication:** Required

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Success Response (200 OK):**
```json
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Error Response (401 Unauthorized):**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

---

## Menu Endpoints

### 5. List Categories

Get all active menu categories (paginated, 20 items per page).

**Endpoint:** `GET /api/v1/categories/`

**Authentication:** Not required

**Query Parameters:**
- `page` (optional): Page number (default: 1)

**Success Response (200 OK):**
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Appetizers",
      "image_url": "https://example.com/appetizers.jpg",
      "is_active": true,
      "created_at": "2025-01-01T10:00:00Z",
      "updated_at": "2025-01-01T10:00:00Z"
    },
    {
      "id": 2,
      "name": "Main Courses",
      "image_url": "https://example.com/main.jpg",
      "is_active": true,
      "created_at": "2025-01-01T10:00:00Z",
      "updated_at": "2025-01-01T10:00:00Z"
    }
  ]
}
```

---

### 6. List Products

Get all available products, optionally filtered by category (paginated, 20 items per page).

**Endpoint:** `GET /api/v1/products/`

**Authentication:** Not required

**Query Parameters:**
- `category_id` (optional): Filter by category ID
- `page` (optional): Page number (default: 1)

**Examples:**
```http
GET /api/v1/products/
GET /api/v1/products/?category_id=1
GET /api/v1/products/?page=2
GET /api/v1/products/?category_id=1&page=2
```

**Success Response (200 OK):**
```json
{
  "count": 45,
  "next": "http://localhost:8000/api/v1/products/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Margherita Pizza",
      "description": "Classic pizza with tomato sauce, mozzarella, and basil",
      "price": "12.99",
      "category": 2,
      "category_name": "Main Courses",
      "image_url": "https://example.com/pizza.jpg",
      "is_available": true,
      "created_at": "2025-01-01T10:00:00Z",
      "updated_at": "2025-01-01T10:00:00Z"
    },
    {
      "id": 2,
      "name": "Caesar Salad",
      "description": "Romaine lettuce, croutons, parmesan, Caesar dressing",
      "price": "8.99",
      "category": 1,
      "category_name": "Appetizers",
      "image_url": "https://example.com/salad.jpg",
      "is_available": true,
      "created_at": "2025-01-01T10:00:00Z",
      "updated_at": "2025-01-01T10:00:00Z"
    }
  ]
}
```

---

### 7. Get Product Details

Retrieve details for a specific product.

**Endpoint:** `GET /api/v1/products/{id}/`

**Authentication:** Not required

**Path Parameters:**
- `id` (required): Product ID

**Success Response (200 OK):**
```json
{
  "id": 1,
  "name": "Margherita Pizza",
  "description": "Classic pizza with tomato sauce, mozzarella, and basil",
  "price": "12.99",
  "category": 2,
  "category_name": "Main Courses",
  "image_url": "https://example.com/pizza.jpg",
  "is_available": true,
  "created_at": "2025-01-01T10:00:00Z",
  "updated_at": "2025-01-01T10:00:00Z"
}
```

**Error Response (404 Not Found):**
```json
{
  "detail": "Not found."
}
```

---

## Cart Endpoints

### 8. Get Cart

Retrieve the current user's cart with all items.

**Endpoint:** `GET /api/v1/cart/`

**Authentication:** Required

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Success Response (200 OK):**
```json
{
  "id": 1,
  "user": 1,
  "items": [
    {
      "id": 1,
      "product": {
        "id": 1,
        "name": "Margherita Pizza",
        "price": "12.99",
        "image_url": "https://example.com/pizza.jpg"
      },
      "quantity": 2,
      "subtotal": "25.98"
    },
    {
      "id": 2,
      "product": {
        "id": 3,
        "name": "Tiramisu",
        "price": "6.99",
        "image_url": "https://example.com/tiramisu.jpg"
      },
      "quantity": 1,
      "subtotal": "6.99"
    }
  ],
  "total_items": 3,
  "total_price": "32.97",
  "created_at": "2025-01-01T10:00:00Z",
  "updated_at": "2025-01-01T12:30:00Z"
}
```

**Empty Cart Response (200 OK):**
```json
{
  "id": 1,
  "user": 1,
  "items": [],
  "total_items": 0,
  "total_price": "0.00",
  "created_at": "2025-01-01T10:00:00Z",
  "updated_at": "2025-01-01T10:00:00Z"
}
```

---

### 9. Add to Cart

Add a product to the cart or update quantity if already exists.

**Endpoint:** `POST /api/v1/cart/add/`

**Authentication:** Required

**Headers:**
```http
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "product_id": 1,
  "quantity": 2
}
```

**Field Requirements:**
- `product_id` (required): Valid product ID
- `quantity` (required): Positive integer

**Success Response (201 Created):**
```json
{
  "id": 1,
  "product": {
    "id": 1,
    "name": "Margherita Pizza",
    "price": "12.99"
  },
  "quantity": 2,
  "subtotal": "25.98"
}
```

**Error Responses:**

**400 Bad Request - Invalid Product:**
```json
{
  "error": "Product not found or not available"
}
```

**400 Bad Request - Invalid Quantity:**
```json
{
  "quantity": ["Ensure this value is greater than or equal to 1."]
}
```

---

### 10. Remove from Cart

Remove a specific item from the cart.

**Endpoint:** `DELETE /api/v1/cart/item/{item_id}/`

**Authentication:** Required

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Path Parameters:**
- `item_id` (required): Cart item ID

**Success Response (204 No Content):**
```
No response body
```

**Error Response (404 Not Found):**
```json
{
  "detail": "Not found."
}
```

---

## Order Endpoints

### 11. Create Order

Create a new order from the current cart items.

**Endpoint:** `POST /api/v1/orders/create/`

**Authentication:** Required

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{}
```
*Note: No body required, order is created from current cart*

**Success Response (201 Created):**
```json
{
  "id": 1,
  "user": 1,
  "items": [
    {
      "id": 1,
      "product_id": 1,
      "product_name": "Margherita Pizza",
      "price": "12.99",
      "quantity": 2,
      "subtotal": "25.98"
    },
    {
      "id": 2,
      "product_id": 3,
      "product_name": "Tiramisu",
      "price": "6.99",
      "quantity": 1,
      "subtotal": "6.99"
    }
  ],
  "total_price": "32.97",
  "status": "pending",
  "created_at": "2025-01-01T13:00:00Z"
}
```

**Error Response (400 Bad Request):**
```json
{
  "error": "Cart is empty"
}
```

**Order Creation Flow:**
```
1. Validate cart is not empty
2. Create Order object
3. For each cart item:
   - Create OrderItem with product snapshot
   - Store: product_id, product_name, price, quantity
4. Calculate total_price
5. Clear cart
6. Return order details
```

---

### 12. List Orders

Get all orders for the authenticated user (paginated, 20 items per page).

**Endpoint:** `GET /api/v1/orders/`

**Authentication:** Required

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `page` (optional): Page number (default: 1)

**Success Response (200 OK):**
```json
{
  "count": 25,
  "next": "http://localhost:8000/api/v1/orders/?page=2",
  "previous": null,
  "results": [
    {
      "id": 2,
      "total_price": "45.50",
      "status": "delivered",
      "created_at": "2025-01-02T14:00:00Z"
    },
    {
      "id": 1,
      "total_price": "32.97",
      "status": "pending",
      "created_at": "2025-01-01T13:00:00Z"
    }
  ]
}
```

*Note: Orders are sorted by creation date (newest first)*

---

### 13. Get Order Details

Retrieve details for a specific order.

**Endpoint:** `GET /api/v1/orders/{id}/`

**Authentication:** Required

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Path Parameters:**
- `id` (required): Order ID

**Success Response (200 OK):**
```json
{
  "id": 1,
  "user": 1,
  "items": [
    {
      "id": 1,
      "product_id": 1,
      "product_name": "Margherita Pizza",
      "price": "12.99",
      "quantity": 2,
      "subtotal": "25.98"
    },
    {
      "id": 2,
      "product_id": 3,
      "product_name": "Tiramisu",
      "price": "6.99",
      "quantity": 1,
      "subtotal": "6.99"
    }
  ],
  "total_price": "32.97",
  "status": "pending",
  "created_at": "2025-01-01T13:00:00Z"
}
```

**Error Response (404 Not Found):**
```json
{
  "detail": "Not found."
}
```

**Security Note:** Users can only view their own orders. Attempting to access another user's order will return 404.

---

### 14. Update Order Status

Update the status of an order (Admin only).

**Endpoint:** `PATCH /api/v1/orders/{id}/status/`

**Authentication:** Required (Admin users only)

**Headers:**
```http
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Path Parameters:**
- `id` (required): Order ID

**Request Body:**
```json
{
  "status": "preparing"
}
```

**Valid Status Values:**
- `pending` - Order placed, awaiting preparation
- `preparing` - Order is being prepared
- `on_the_way` - Order is out for delivery
- `delivered` - Order has been delivered
- `cancelled` - Order was cancelled

**Success Response (200 OK):**
```json
{
  "id": 1,
  "status": "preparing",
  "message": "Order status updated successfully"
}
```

**Error Responses:**

**400 Bad Request - Invalid Status:**
```json
{
  "status": ["\"invalid_status\" is not a valid choice."]
}
```

**403 Forbidden - Not Admin:**
```json
{
  "detail": "You do not have permission to perform this action."
}
```

**Order Status Workflow:**
```
pending ──> preparing ──> on_the_way ──> delivered
   │
   └──────> cancelled
```

---

## Rate Limiting

The API implements rate limiting to prevent abuse and ensure fair usage for all users.

### Current Configuration

- **Authenticated Users**: 100 requests per minute
- **Throttle Class**: `UserRateThrottle` (Django REST Framework)

### Rate Limit Headers

When rate limiting is active, responses include the following headers:

- `X-RateLimit-Limit`: Maximum requests allowed in the time window
- `X-RateLimit-Remaining`: Requests remaining in current window
- `X-RateLimit-Reset`: Time when the rate limit resets

### Rate Limit Exceeded (429 Response)

When you exceed the rate limit, you'll receive:

```json
{
  "detail": "Request was throttled. Expected available in 45 seconds."
}
```

**Status Code**: `429 Too Many Requests`

### Best Practices

- Implement exponential backoff when receiving 429 responses
- Cache responses where appropriate to reduce API calls
- Use webhooks or polling with appropriate intervals instead of frequent requests
- Spread requests over time rather than bursting

## Pagination

The API automatically paginates list endpoints to improve performance and reduce response sizes.

### Current Configuration

- **Pagination Style**: Page Number Pagination
- **Page Size**: 20 items per page
- **Pagination Class**: `PageNumberPagination` (Django REST Framework)

### Paginated Endpoints

The following endpoints return paginated results:

- `GET /api/v1/categories/` - Category listings
- `GET /api/v1/products/` - Product listings
- `GET /api/v1/orders/` - User order history

### Paginated Response Format

```json
{
  "count": 100,
  "next": "http://localhost:8000/api/v1/products/?page=3",
  "previous": "http://localhost:8000/api/v1/products/?page=1",
  "results": [
    {
      "id": 21,
      "name": "Product 21",
      "price": "15.99"
    },
    {
      "id": 22,
      "name": "Product 22",
      "price": "12.99"
    }
  ]
}
```

**Response Fields:**

- `count` (integer): Total number of items across all pages
- `next` (string|null): URL to the next page, or `null` if on last page
- `previous` (string|null): URL to the previous page, or `null` if on first page
- `results` (array): Array of items for current page (max 20 items)

### Using Pagination

**Request First Page:**
```http
GET /api/v1/products/
```

**Request Specific Page:**
```http
GET /api/v1/products/?page=2
```

**Request with Filters and Pagination:**
```http
GET /api/v1/products/?category_id=1&page=3
```

### Pagination Metadata

You can determine pagination state from the response:

- **First Page**: `previous` is `null`
- **Last Page**: `next` is `null`
- **Total Pages**: Calculate as `Math.ceil(count / 20)`
- **Current Page**: Extract from URL or track client-side

## CORS (Cross-Origin Resource Sharing)

Configure CORS headers to allow requests from your frontend domains.

**Development:**
```python
CORS_ALLOW_ALL_ORIGINS = True
```

**Production:**
```python
CORS_ALLOWED_ORIGINS = [
    "https://yourfrontend.com",
    "https://www.yourfrontend.com"
]
```

## Testing the API

### Using cURL

**Register:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"testpass123","password2":"testpass123"}'
```

**Login:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass123"}'
```

**Get Products:**
```bash
curl http://localhost:8000/api/v1/products/
```

**Add to Cart:**
```bash
curl -X POST http://localhost:8000/api/v1/cart/add/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{"product_id":1,"quantity":2}'
```

### Using Swagger UI

Navigate to `http://localhost:8000/api/docs/` for an interactive API explorer where you can:
- View all endpoints
- Test endpoints directly
- See request/response schemas
- Authenticate with JWT tokens

---

**API Version:** 1.0.0 | **Last Updated:** January 2025
