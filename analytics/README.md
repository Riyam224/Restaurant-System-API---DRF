# Analytics App

Phase 1 — Analytics Foundation (NO AI)

Clean, reliable metrics for business intelligence.

## Features

### Admin-Only Analytics Endpoints

All analytics endpoints require admin authentication (`is_staff=True`).

### Available Endpoints

#### 1. Dashboard KPIs
**GET** `/api/v1/analytics/dashboard/`

Comprehensive dashboard with key performance indicators.

**Parameters:**
- `days` (optional, default: 30) - Number of days to look back (1-365)

**Returns:**
- Revenue metrics (current vs previous period)
- Order metrics (current vs previous period)
- Growth percentages
- User statistics
- Order status breakdown

#### 2. Revenue Metrics
**GET** `/api/v1/analytics/revenue/metrics/`

Detailed revenue metrics for a date range.

**Parameters:**
- `start_date` (optional, format: YYYY-MM-DD) - Default: 30 days ago
- `end_date` (optional, format: YYYY-MM-DD) - Default: today

**Returns:**
- Total revenue
- Total orders
- Average order value
- Total discount given
- Gross revenue (before discounts)

#### 3. Daily Revenue
**GET** `/api/v1/analytics/revenue/daily/`

Daily revenue breakdown for charts.

**Parameters:**
- `start_date` (optional, format: YYYY-MM-DD)
- `end_date` (optional, format: YYYY-MM-DD)

**Returns:**
Array of daily data:
- Date
- Revenue
- Order count
- Average order value

#### 4. Order Status Breakdown
**GET** `/api/v1/analytics/orders/status/`

Order counts by status.

**Returns:**
- Orders by status (pending, preparing, on_the_way, delivered, cancelled)
- Total orders

#### 5. User Metrics
**GET** `/api/v1/analytics/users/metrics/`

User statistics and top customers.

**Returns:**
- Total users
- Users with orders
- Active users (last 30 days)
- Conversion rate
- Top 10 customers by spending

#### 6. Product Performance
**GET** `/api/v1/analytics/products/performance/`

Top selling products.

**Returns:**
Top 20 products with:
- Product ID and name
- Total quantity sold
- Total revenue
- Number of orders

#### 7. Coupon Performance
**GET** `/api/v1/analytics/coupons/performance/`

Coupon usage and discount metrics.

**Returns:**
- Total discounts given
- Orders with coupons
- Breakdown by coupon code

#### 8. Review Metrics
**GET** `/api/v1/analytics/reviews/metrics/`

Review statistics.

**Returns:**
- Total reviews
- Average rating
- Rating distribution (1-5 stars)

## Architecture

### Read-Only Queries
All queries are read-only and optimized for performance:
- Uses Django ORM aggregation functions
- Efficient use of `select_related` and `prefetch_related`
- No database writes from analytics endpoints

### Data Aggregation
Located in `queries.py`:
- Centralized analytics logic
- Reusable query methods
- Optimized for large datasets

### Permissions
Custom permission class `IsAdminUser`:
- Requires authentication
- Requires `is_staff=True`
- Returns 403 Forbidden for non-admin users

### Serializers
Type-safe API responses:
- Clear field definitions
- Nested serializers for complex data
- Consistent response format

## Usage Example

```python
# Get dashboard KPIs for last 7 days
GET /api/v1/analytics/dashboard/?days=7

# Get revenue for a specific date range
GET /api/v1/analytics/revenue/metrics/?start_date=2026-01-01&end_date=2026-01-15

# Get daily revenue for charts
GET /api/v1/analytics/revenue/daily/?start_date=2026-01-01&end_date=2026-01-31
```

## Testing

All endpoints require admin JWT token:

```bash
# Login as admin
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin_password"}'

# Use the access token
curl -X GET http://localhost:8000/api/v1/analytics/dashboard/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Future Enhancements (Phase 2+)

Phase 1 focuses on clean, reliable metrics. Future phases may include:
- AI-powered insights
- Predictive analytics
- Custom report generation
- Export functionality
- Real-time dashboards
