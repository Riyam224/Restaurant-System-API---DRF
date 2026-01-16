# Analytics API Endpoints

**Base URL:** `/api/v1/analytics/`

**Authentication:** Admin only (JWT + `is_staff=True`)

---

## Dashboard

### Get Dashboard KPIs
```http
GET /api/v1/analytics/dashboard/
```

**Query Parameters:**
- `days` (optional): Number of days to look back (1-365, default: 30)

**Response:**
```json
{
  "period_days": 30,
  "revenue": {
    "current": 12500.00,
    "previous": 10000.00,
    "growth_percentage": 25.0
  },
  "orders": {
    "current": 150,
    "previous": 120,
    "growth_percentage": 25.0
  },
  "average_order_value": 83.33,
  "total_users": 500,
  "active_users": 75,
  "conversion_rate": 45.5,
  "order_status": [
    {
      "status": "delivered",
      "count": 100,
      "total_value": 8500.00
    }
  ]
}
```

---

## Revenue

### Get Revenue Metrics
```http
GET /api/v1/analytics/revenue/metrics/
```

**Query Parameters:**
- `start_date` (optional): YYYY-MM-DD format
- `end_date` (optional): YYYY-MM-DD format

**Response:**
```json
{
  "total_revenue": 12500.00,
  "total_orders": 150,
  "average_order_value": 83.33,
  "total_discount": 1250.00,
  "gross_revenue": 13750.00,
  "period": {
    "start": "2026-01-01T00:00:00Z",
    "end": "2026-01-31T23:59:59Z"
  }
}
```

### Get Daily Revenue
```http
GET /api/v1/analytics/revenue/daily/
```

**Query Parameters:**
- `start_date` (optional): YYYY-MM-DD format
- `end_date` (optional): YYYY-MM-DD format

**Response:**
```json
[
  {
    "date": "2026-01-01",
    "revenue": 450.00,
    "orders": 5,
    "average_order_value": 90.00
  },
  {
    "date": "2026-01-02",
    "revenue": 520.00,
    "orders": 6,
    "average_order_value": 86.67
  }
]
```

---

## Orders

### Get Order Status Breakdown
```http
GET /api/v1/analytics/orders/status/
```

**Response:**
```json
{
  "by_status": [
    {
      "status": "delivered",
      "count": 100,
      "total_value": 8500.00
    },
    {
      "status": "pending",
      "count": 30,
      "total_value": 2500.00
    }
  ],
  "total_orders": 150
}
```

---

## Users

### Get User Metrics
```http
GET /api/v1/analytics/users/metrics/
```

**Response:**
```json
{
  "total_users": 500,
  "users_with_orders": 250,
  "active_users_30d": 75,
  "conversion_rate": 50.0,
  "top_customers": [
    {
      "user_id": 123,
      "username": "john_doe",
      "order_count": 25,
      "total_spent": 2500.00
    }
  ]
}
```

---

## Products

### Get Product Performance
```http
GET /api/v1/analytics/products/performance/
```

**Response:**
```json
[
  {
    "product_id": 1,
    "product_name": "Margherita Pizza",
    "total_quantity": 150,
    "total_revenue": 2250.00,
    "order_count": 120
  }
]
```

---

## Coupons

### Get Coupon Performance
```http
GET /api/v1/analytics/coupons/performance/
```

**Response:**
```json
{
  "total_discount_given": 1250.00,
  "orders_with_coupons": 45,
  "by_coupon": [
    {
      "coupon_code": "SAVE10",
      "usage_count": 25,
      "total_discount": 250.00,
      "total_revenue": 2250.00
    }
  ]
}
```

---

## Reviews

### Get Review Metrics
```http
GET /api/v1/analytics/reviews/metrics/
```

**Response:**
```json
{
  "total_reviews": 150,
  "average_rating": 4.5,
  "rating_distribution": [
    {
      "rating": 5,
      "count": 80
    },
    {
      "rating": 4,
      "count": 50
    },
    {
      "rating": 3,
      "count": 15
    },
    {
      "rating": 2,
      "count": 3
    },
    {
      "rating": 1,
      "count": 2
    }
  ]
}
```

---

## Error Responses

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
  "detail": "Only admin users can access analytics data."
}
```

### 400 Bad Request (Invalid Parameters)
```json
{
  "error": "Days must be between 1 and 365"
}
```

```json
{
  "error": "Invalid date format. Use YYYY-MM-DD"
}
```

---

## Testing with cURL

### 1. Login as Admin
```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin_password"}'
```

### 2. Get Dashboard KPIs
```bash
curl -X GET "http://localhost:8000/api/v1/analytics/dashboard/?days=7" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 3. Get Revenue Metrics
```bash
curl -X GET "http://localhost:8000/api/v1/analytics/revenue/metrics/?start_date=2026-01-01&end_date=2026-01-31" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 4. Get Daily Revenue
```bash
curl -X GET "http://localhost:8000/api/v1/analytics/revenue/daily/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## OpenAPI/Swagger Documentation

All endpoints are documented in the OpenAPI schema and available at:

**Swagger UI:** `http://localhost:8000/api/docs/`

**Schema JSON:** `http://localhost:8000/api/schema/`

All analytics endpoints are tagged as **"Analytics"** in the documentation.
