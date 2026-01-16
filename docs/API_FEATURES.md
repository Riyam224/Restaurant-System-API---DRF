# Restaurant API - Complete Features List

## Quick Reference

- **Base URL**: `http://localhost:8000/api/v1/`
- **Production**: `https://web-production-e1bea.up.railway.app`
- **API Docs**: `/api/schema/swagger-ui/`
- **Version**: 2.0.0

## Authentication

### JWT Token System
- **Access Token**: 30 minutes lifetime
- **Refresh Token**: 7 days lifetime
- **Header Format**: `Authorization: Bearer {token}`

### Endpoints
```
POST /auth/register/    - Register new user
POST /auth/login/       - Login and get tokens
POST /auth/refresh/     - Refresh access token
GET  /profile/          - Get user profile
```

## Core Features

### 1. Menu Management
- Categorized products
- Search and filter products
- Pagination (20 items/page)
- Product availability status
- Image support

### 2. Shopping Cart
- One cart per user
- Snapshot pricing (preserved when added)
- Automatic totals
- Stock validation
- Max quantity: 99/item

### 3. Order Management
- Create from cart
- Order history
- Status tracking (pending → preparing → on_the_way → delivered)
- Coupon support
- Inventory integration

### 4. Coupon System
- Percentage/fixed discounts
- Usage limits
- User-specific coupons
- Minimum order requirements
- Validation API

### 5. Reviews & Ratings
- 1-5 star ratings
- Verified purchases
- Admin moderation
- Helpfulness voting
- Rating statistics

### 6. Address Management
- Multiple addresses per user
- Geolocation support
- Label organization

### 7. Inventory Management
- Real-time stock tracking
- Low stock alerts
- Auto-disable on zero stock
- Complete audit trail

## Technical Features

### Performance
- Caching system (local/Redis)
- Query optimization
- Database indexes
- Efficient pagination

### Security
- JWT authentication
- Rate limiting
- CORS support
- Password hashing
- Input validation

### Quality
- 80%+ test coverage
- Service layer architecture
- SOLID principles
- Clean code

### Monitoring
- Rotating logs
- Error tracking
- App-specific loggers

## Database Models

```
User (Django built-in)
├── Cart (1:1)
│   └── CartItem (1:N)
├── Order (1:N)
│   ├── OrderItem (1:N)
│   └── OrderStatusHistory (1:N)
├── Address (1:N)
├── Review (1:N)
└── CouponUsage (1:N)

Category (1:N) → Product
├── ProductInventory (1:1)
    └── InventoryTransaction (1:N)

Coupon (1:N) → CouponUsage
```

## API Response Format

### Success Response
```json
{
  "id": 1,
  "data": {...}
}
```

### Paginated Response
```json
{
  "count": 100,
  "next": "http://api/endpoint/?page=2",
  "previous": null,
  "results": [...]
}
```

### Error Response
```json
{
  "detail": "Error message"
}
```

## Status Codes

- `200 OK` - Success
- `201 Created` - Resource created
- `204 No Content` - Success, no data
- `400 Bad Request` - Invalid input
- `401 Unauthorized` - Auth required
- `403 Forbidden` - Permission denied
- `404 Not Found` - Resource not found
- `429 Too Many Requests` - Rate limited
- `500 Internal Server Error` - Server error

## Rate Limits

- **Anonymous**: 100 requests/hour
- **Authenticated**: 2000 requests/day

## Deployment

### Environment Variables
```
DEBUG=False
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://...
ALLOWED_HOSTS=your-domain.com
CORS_ALLOWED_ORIGINS=https://your-frontend.com
```

### Production Checklist
- ✅ Set DEBUG=False
- ✅ Configure SECRET_KEY
- ✅ Set DATABASE_URL
- ✅ Run migrations
- ✅ Collect static files
- ✅ Configure allowed hosts
- ✅ Set up Redis cache
- ✅ Configure logging

## Quick Start

```bash
# Install
pip install -r requirements.txt

# Migrate
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run server
python manage.py runserver

# Run tests
python manage.py test

# Coverage
coverage run --source='.' manage.py test
coverage report
```

## Support

- **Swagger UI**: `/api/schema/swagger-ui/`
- **ReDoc**: `/api/schema/redoc/`
- **Admin Panel**: `/admin/`
- **Logs**: `logs/restaurant.log`, `logs/errors.log`

---

**Version 2.0.0** | **Production Ready** ✅
