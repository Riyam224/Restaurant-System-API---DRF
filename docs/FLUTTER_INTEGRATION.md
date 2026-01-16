# Flutter Integration Guide

## Overview

This is a production-ready REST API for a restaurant ordering system, built with Django REST Framework. This guide will help you integrate the API with your Flutter application.

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://web-production-e1bea.up.railway.app`

## Authentication

The API uses **JWT (JSON Web Token)** authentication.

### Registration

```
POST /api/v1/auth/register
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "secure_password123"
}
```

**Response (201 Created)**:
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com"
}
```

### Login

```
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "secure_password123"
}
```

**Response (200 OK)**:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Using JWT Tokens in Flutter

```dart
// Add this to your HTTP headers
final headers = {
  'Content-Type': 'application/json',
  'Authorization': 'Bearer ${accessToken}',
};
```

### Token Refresh

```
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response (200 OK)**:
```json
{
  "access": "new_access_token..."
}
```

## API Endpoints

### 1. Menu / Products

#### Get Categories

```
GET /api/v1/categories/
```

**Response (200 OK)**:
```json
[
  {
    "id": 1,
    "name": "Burgers",
    "image": "https://example.com/burgers.jpg",
    "is_active": true
  }
]
```

#### Get Products

```
GET /api/v1/products/
```

**Query Parameters**:
- `search`: Search by name or description
- `category_id`: Filter by category
- `min_price`: Minimum price
- `max_price`: Maximum price
- `sort_by`: `price_asc`, `price_desc`, `name`, `newest`

**Response (200 OK)**:
```json
{
  "count": 50,
  "next": "http://api/products/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "category_id": 1,
      "name": "Classic Burger",
      "description": "Juicy beef patty with lettuce and tomato",
      "price": "12.99",
      "image": "https://example.com/burger.jpg",
      "is_available": true
    }
  ]
}
```

#### Get Single Product

```
GET /api/v1/products/{id}/
```

### 2. Cart Management

#### Get User's Cart

```
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
      "name": "Classic Burger",
      "price": "12.50",
      "quantity": 2,
      "subtotal": "25.00"
    }
  ],
  "total_items": 2,
  "total_price": "25.00"
}
```

#### Add Item to Cart

```
POST /api/v1/cart/add/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "product_id": 10,
  "quantity": 2
}
```

**Response (200 OK)**:
```json
{
  "message": "Item added to cart",
  "cart": {
    "id": 1,
    "items": [...],
    "total_items": 2,
    "total_price": "25.00"
  }
}
```

#### Remove Item from Cart

```
DELETE /api/v1/cart/item/{item_id}/
Authorization: Bearer {access_token}
```

### 3. Addresses

#### List User Addresses

```
GET /api/v1/addresses/
Authorization: Bearer {access_token}
```

#### Create Address

```
POST /api/v1/addresses/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "label": "Home",
  "city": "New York",
  "street": "5th Avenue",
  "building": "123",
  "floor": "4",
  "apartment": "A",
  "latitude": 40.7128,
  "longitude": -74.0060
}
```

#### Update Address

```
PUT /api/v1/addresses/{id}/
Authorization: Bearer {access_token}
```

#### Delete Address

```
DELETE /api/v1/addresses/{id}/
Authorization: Bearer {access_token}
```

### 4. Orders

#### Create Order

```
POST /api/v1/orders/create/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "address_id": 1,
  "coupon_code": "SAVE10"  // Optional
}
```

**Response (201 Created)**:
```json
{
  "message": "Order created successfully",
  "order_id": 15,
  "status": "pending",
  "subtotal": "50.00",
  "discount_amount": "5.00",
  "coupon_code": "SAVE10",
  "total_price": "45.00"
}
```

**Possible Errors**:
- `400 Bad Request`: Cart is empty, invalid address, invalid coupon
- `401 Unauthorized`: Missing or invalid token

#### List My Orders

```
GET /api/v1/orders/
Authorization: Bearer {access_token}
```

**Response (200 OK)**:
```json
[
  {
    "id": 15,
    "address": {
      "label": "Home",
      "city": "New York",
      "street": "5th Avenue"
    },
    "status": "pending",
    "status_display": "Pending",
    "subtotal": "50.00",
    "discount_amount": "5.00",
    "coupon_code": "SAVE10",
    "total_price": "45.00",
    "created_at": "2026-01-16T10:30:00Z",
    "updated_at": "2026-01-16T10:30:00Z",
    "items": [
      {
        "id": 1,
        "product_id": 10,
        "product_name": "Classic Burger",
        "price": "12.50",
        "quantity": 2,
        "subtotal": "25.00"
      }
    ],
    "history": [
      {
        "id": 1,
        "status": "pending",
        "created_at": "2026-01-16T10:30:00Z"
      }
    ]
  }
]
```

#### Get Order Details

```
GET /api/v1/orders/{id}/
Authorization: Bearer {access_token}
```

#### Get Order Status

```
GET /api/v1/orders/{id}/status/
Authorization: Bearer {access_token}
```

**Response (200 OK)**:
```json
{
  "order_id": 12,
  "status": "on_the_way",
  "updated_at": "2026-01-16T12:30:00Z"
}
```

### 5. Coupons

#### List Available Coupons

```
GET /api/v1/coupons/
Authorization: Bearer {access_token}
```

#### Validate Coupon

```
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

### 6. Reviews

#### Create Review

```
POST /api/v1/reviews/create/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "product_id": 10,
  "rating": 5,
  "comment": "Excellent burger!"
}
```

#### List Product Reviews

```
GET /api/v1/reviews/?product_id=10
```

#### Get Product Rating Stats

```
GET /api/v1/products/{id}/ratings/
```

**Response (200 OK)**:
```json
{
  "product_id": 10,
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

## Error Handling

The API returns standard HTTP status codes:

- `200 OK`: Success
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid input data
- `401 Unauthorized`: Missing or invalid authentication
- `403 Forbidden`: Permission denied
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

**Error Response Format**:
```json
{
  "detail": "Error message here"
}
```

## Flutter HTTP Client Example

```dart
import 'package:http/http.dart' as http;
import 'dart:convert';

class ApiClient {
  static const String baseUrl = 'https://web-production-e1bea.up.railway.app';
  String? accessToken;

  Future<Map<String, dynamic>> login(String email, String password) async {
    final response = await http.post(
      Uri.parse('$baseUrl/api/v1/auth/login'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'email': email,
        'password': password,
      }),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      accessToken = data['access'];
      return data;
    } else {
      throw Exception('Login failed');
    }
  }

  Future<Map<String, dynamic>> getCart() async {
    final response = await http.get(
      Uri.parse('$baseUrl/api/v1/cart/'),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $accessToken',
      },
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to get cart');
    }
  }

  Future<void> addToCart(int productId, int quantity) async {
    final response = await http.post(
      Uri.parse('$baseUrl/api/v1/cart/add/'),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $accessToken',
      },
      body: jsonEncode({
        'product_id': productId,
        'quantity': quantity,
      }),
    );

    if (response.statusCode != 200) {
      throw Exception('Failed to add to cart');
    }
  }

  Future<Map<String, dynamic>> createOrder(int addressId, String? couponCode) async {
    final body = {
      'address_id': addressId,
    };
    if (couponCode != null) {
      body['coupon_code'] = couponCode;
    }

    final response = await http.post(
      Uri.parse('$baseUrl/api/v1/orders/create/'),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $accessToken',
      },
      body: jsonEncode(body),
    );

    if (response.statusCode == 201) {
      return jsonDecode(response.body);
    } else {
      final error = jsonDecode(response.body);
      throw Exception(error['detail'] ?? 'Failed to create order');
    }
  }
}
```

## Rate Limiting

- **Anonymous users**: 100 requests per hour
- **Authenticated users**: 2000 requests per day

When you hit the rate limit, you'll receive a `429 Too Many Requests` response.

## Pagination

List endpoints return paginated results with 20 items per page:

```json
{
  "count": 100,
  "next": "http://api/endpoint/?page=2",
  "previous": null,
  "results": [...]
}
```

## Order Status Flow

Orders follow this status progression:

1. `pending` → Initial order state
2. `preparing` → Restaurant is preparing the order
3. `on_the_way` → Order is out for delivery
4. `delivered` → Order completed successfully
5. `cancelled` → Order was cancelled

## Best Practices

1. **Token Management**:
   - Store tokens securely (e.g., using `flutter_secure_storage`)
   - Implement automatic token refresh
   - Handle 401 errors by refreshing token

2. **Error Handling**:
   - Always check HTTP status codes
   - Show user-friendly error messages
   - Implement retry logic for network errors

3. **Performance**:
   - Cache product images
   - Implement pagination scrolling
   - Use debouncing for search queries

4. **State Management**:
   - Use Provider/Riverpod/Bloc for cart state
   - Keep cart synced with server
   - Handle offline mode gracefully

## Support

For API documentation with interactive testing, visit:
- **Swagger UI**: `{base_url}/api/schema/swagger-ui/`
- **ReDoc**: `{base_url}/api/schema/redoc/`

## Changelog

### Version 1.0.0 (2026-01-16)
- Initial production release
- JWT authentication
- Complete ordering system
- Coupon support
- Reviews and ratings
- Inventory management
- Service layer architecture
- Comprehensive caching
- Full test coverage
