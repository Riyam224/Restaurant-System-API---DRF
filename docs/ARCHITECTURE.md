# System Architecture

This document describes the architecture, design patterns, and system flow of the Restaurant System API.

## Table of Contents

- [High-Level Architecture](#high-level-architecture)
- [Application Layers](#application-layers)
- [Module Architecture](#module-architecture)
- [Design Patterns](#design-patterns)
- [Data Flow](#data-flow)
- [Security Architecture](#security-architecture)

## High-Level Architecture

The Restaurant System follows a **monolithic architecture** using Django's Model-View-Template (MVT) pattern, adapted for RESTful API development with Django REST Framework.

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Layer                             │
│  (Mobile Apps, Web Browsers, Third-party Integrations)          │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ HTTPS/REST
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                     API Gateway Layer                            │
│                    (Django URL Router)                           │
└────────────────────────┬────────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
┌───────▼───────┐ ┌─────▼──────┐ ┌──────▼──────┐
│  Middleware   │ │   CORS     │ │    JWT      │
│   Pipeline    │ │  Headers   │ │    Auth     │
└───────┬───────┘ └─────┬──────┘ └──────┬──────┘
        │                │                │
        └────────────────┼────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                    Application Layer                             │
│  ┌──────────┐  ┌──────┐  ┌──────┐  ┌────────┐  ┌──────┐       │
│  │ Accounts │  │ Menu │  │ Cart │  │ Orders │  │ Core │       │
│  │  Module  │  │Module│  │Module│  │ Module │  │Module│       │
│  └────┬─────┘  └───┬──┘  └───┬──┘  └────┬───┘  └───┬──┘       │
│       │            │          │          │          │           │
│  ┌────▼────────────▼──────────▼──────────▼──────────▼────┐     │
│  │              Django ORM (Models Layer)               │     │
│  └────────────────────────┬──────────────────────────────┘     │
└───────────────────────────┼────────────────────────────────────┘
                            │
┌───────────────────────────▼────────────────────────────────────┐
│                     Data Layer                                  │
│                   SQLite Database                               │
└─────────────────────────────────────────────────────────────────┘
```

## Application Layers

### 1. Client Layer
- Mobile applications (iOS/Android)
- Web applications (React, Vue, Angular)
- Third-party integrations
- API testing tools (Postman, Swagger UI)

### 2. API Gateway Layer
**Django URL Router** (`config/urls.py`)
- Routes incoming requests to appropriate modules
- Handles API versioning (`/api/v1/`)
- Serves API documentation endpoints

```python
# URL Structure
/api/v1/auth/*        → accounts module
/api/v1/categories/*  → menu module
/api/v1/products/*    → menu module
/api/v1/cart/*        → cart module
/api/v1/orders/*      → orders module
/api/docs/            → Swagger UI
/api/schema/          → OpenAPI schema
/admin/               → Django admin
```

### 3. Middleware Pipeline
**Request Processing Order:**
1. **SecurityMiddleware** - Security headers
2. **SessionMiddleware** - Session management
3. **CommonMiddleware** - Common operations
4. **CsrfViewMiddleware** - CSRF protection
5. **AuthenticationMiddleware** - User authentication
6. **MessageMiddleware** - Flash messages

### 4. Application Layer
Each module implements the **MVT pattern**:

```
┌─────────────────────────────────────────────────────────┐
│                    Django App Module                     │
│                                                          │
│  ┌──────────┐      ┌─────────────┐      ┌──────────┐   │
│  │  Views   │─────>│ Serializers │─────>│  Models  │   │
│  │  (API    │      │   (Data     │      │  (Data   │   │
│  │Endpoints)│      │Validation)  │      │Structure)│   │
│  └────┬─────┘      └─────────────┘      └────┬─────┘   │
│       │                                       │         │
│       │            ┌─────────────┐           │         │
│       └───────────>│ Permissions │<──────────┘         │
│                    │ (Access     │                     │
│                    │  Control)   │                     │
│                    └─────────────┘                     │
└─────────────────────────────────────────────────────────┘
```

### 5. Data Layer
- **SQLite Database** (development)
- Django ORM abstraction
- Migration management
- Query optimization

## Module Architecture

### Accounts Module
**Purpose**: User authentication and authorization

```
accounts/
├── views.py
│   ├── RegisterView (POST)
│   ├── LoginView (POST)
│   ├── TokenRefreshView (POST)
│   └── ProfileView (GET)
├── serializers.py
│   ├── RegisterSerializer
│   └── UserSerializer
└── models.py (uses Django's User model)

Flow:
Client → View → Serializer → Django User Model → Database
```

**Key Features:**
- Password validation (min 8 characters)
- JWT token generation
- Token refresh mechanism
- User profile retrieval

### Menu Module
**Purpose**: Product catalog management

```
menu/
├── views.py
│   ├── CategoryListView (GET)
│   ├── ProductListView (GET)
│   └── ProductDetailView (GET)
├── serializers.py
│   ├── CategorySerializer
│   └── ProductSerializer
└── models.py
    ├── Category
    └── Product

Relationships:
Category (1) ──< (N) Product
```

**Key Features:**
- Category-based organization
- Product filtering by category
- Image URL support
- Active/inactive status management

### Cart Module
**Purpose**: Shopping cart management

```
cart/
├── views.py
│   ├── CartView (GET)
│   ├── AddToCartView (POST)
│   └── RemoveFromCartView (DELETE)
├── serializers.py
│   ├── CartSerializer
│   └── CartItemSerializer
└── models.py
    ├── Cart
    └── CartItem

Relationships:
User (1) ──(1) Cart (1) ──< (N) CartItem >──(1) Product
```

**Key Features:**
- One cart per user (auto-created)
- Quantity management
- Automatic total calculation
- Product reference preservation

### Orders Module
**Purpose**: Order lifecycle management

```
orders/
├── views.py
│   ├── CreateOrderView (POST)
│   ├── OrderListView (GET)
│   ├── OrderDetailView (GET)
│   └── UpdateOrderStatusView (PATCH)
├── serializers.py
│   ├── OrderSerializer
│   └── OrderItemSerializer
└── models.py
    ├── Order
    └── OrderItem

Relationships:
User (1) ──< (N) Order (1) ──< (N) OrderItem
OrderItem → Product (reference only)
```

**Key Features:**
- Order creation from cart
- Status workflow management
- Historical data preservation
- User order history

## Design Patterns

### 1. Repository Pattern (via Django ORM)
```python
# Models act as repositories
Product.objects.filter(is_available=True)
Cart.objects.get_or_create(user=user)
Order.objects.filter(user=user).order_by('-created_at')
```

### 2. Serializer Pattern
```python
# Data transformation and validation
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'description']
```

### 3. ViewSet/APIView Pattern
```python
# Endpoint logic encapsulation
class ProductListView(generics.ListAPIView):
    queryset = Product.objects.filter(is_available=True)
    serializer_class = ProductSerializer
```

### 4. Middleware Pattern
```python
# Request/Response processing pipeline
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    # ... more middleware
]
```

### 5. Dependency Injection (via Django)
- Settings configuration injection
- Database connection pooling
- Serializer context passing

## Data Flow

### 1. Read Operation (GET Request)
```
┌────────┐      ┌──────┐      ┌────────────┐      ┌───────┐      ┌──────────┐
│ Client │─────>│ View │─────>│ Permission │─────>│ Model │─────>│ Database │
└────────┘      └──────┘      └────────────┘      └───────┘      └──────────┘
                    │                                   │              │
                    │          ┌────────────┐          │              │
                    └─────────>│ Serializer │<─────────┘              │
                               └──────┬─────┘      QuerySet           │
                                      │<─────────────────────────────┘
                                      │
                                   JSON
                                      │
                                      ▼
                               ┌────────┐
                               │ Client │
                               └────────┘
```

### 2. Write Operation (POST/PUT/PATCH Request)
```
┌────────┐      ┌──────┐      ┌────────────┐      ┌────────────┐
│ Client │─────>│ View │─────>│ Permission │─────>│ Serializer │
└────────┘      └──────┘      └────────────┘      └──────┬─────┘
   JSON                                                   │
                                                    Validation
                                                          │
                                                          ▼
                                                   ┌───────────┐
                                              YES  │  Valid?   │  NO
                                         ┌─────────┤           ├────────┐
                                         │         └───────────┘        │
                                         ▼                              ▼
                                   ┌─────────┐                  ┌──────────┐
                                   │  Model  │                  │  400 Bad │
                                   │  .save()│                  │  Request │
                                   └────┬────┘                  └────┬─────┘
                                        │                            │
                                        ▼                            │
                                  ┌──────────┐                       │
                                  │ Database │                       │
                                  └────┬─────┘                       │
                                       │                             │
                                       ▼                             │
                                  201 Created                        │
                                       │                             │
                                       └─────────────┬───────────────┘
                                                     │
                                                     ▼
                                                ┌────────┐
                                                │ Client │
                                                └────────┘
```

### 3. Order Creation Flow (Complex Operation)
```
┌────────┐
│ Client │ POST /api/v1/orders/create/
└───┬────┘
    │
    ▼
┌──────────────┐
│ OrderView    │
└──────┬───────┘
       │
       ├─> 1. Authenticate User (JWT)
       │
       ├─> 2. Get User's Cart
       │      Cart.objects.get(user=user)
       │
       ├─> 3. Get Cart Items
       │      cart.items.all()
       │
       ├─> 4. Validate Cart (not empty)
       │
       ├─> 5. Create Order
       │      order = Order.objects.create(user=user)
       │
       ├─> 6. For each CartItem:
       │      - Create OrderItem with product snapshot
       │      - Copy: product_name, price, quantity
       │
       ├─> 7. Calculate total_price
       │
       ├─> 8. Save Order
       │
       ├─> 9. Clear Cart
       │      cart.items.all().delete()
       │
       └─> 10. Return Order with OrderItems

           Serialized Response (201 Created)
```

## Security Architecture

### Authentication Flow
```
┌─────────────────────────────────────────────────────────────┐
│                    JWT Authentication                        │
└─────────────────────────────────────────────────────────────┘

1. User Login
   ┌────────┐                          ┌──────────┐
   │ Client │──credentials────────────>│   API    │
   └────────┘                          └────┬─────┘
                                            │
                                            ├─> Verify username/password
                                            │
                                            ├─> Generate Access Token (30 min)
                                            │
                                            └─> Generate Refresh Token (7 days)

   ┌────────┐                          ┌──────────┐
   │ Client │<────{access, refresh}────│   API    │
   └────────┘                          └──────────┘

2. Authenticated Request
   ┌────────┐                          ┌──────────┐
   │ Client │──Authorization: Bearer──>│   API    │
   └────────┘    <access_token>        └────┬─────┘
                                            │
                                            ├─> Verify token signature
                                            │
                                            ├─> Check expiration
                                            │
                                            ├─> Extract user from token
                                            │
                                            └─> Process request

   ┌────────┐                          ┌──────────┐
   │ Client │<────Response─────────────│   API    │
   └────────┘                          └──────────┘

3. Token Refresh
   ┌────────┐                          ┌──────────┐
   │ Client │──refresh_token──────────>│   API    │
   └────────┘                          └────┬─────┘
                                            │
                                            ├─> Verify refresh token
                                            │
                                            └─> Generate new access token

   ┌────────┐                          ┌──────────┐
   │ Client │<────{access}─────────────│   API    │
   └────────┘                          └──────────┘
```

### Permission Levels

```
┌─────────────────────────────────────────────────────────────┐
│                    Permission Matrix                         │
├──────────────────┬──────────────┬────────────┬──────────────┤
│    Endpoint      │  Anonymous   │    User    │    Admin     │
├──────────────────┼──────────────┼────────────┼──────────────┤
│ GET /categories  │      ✓       │     ✓      │      ✓       │
│ GET /products    │      ✓       │     ✓      │      ✓       │
│ POST /register   │      ✓       │     ✓      │      ✓       │
│ POST /login      │      ✓       │     ✓      │      ✓       │
├──────────────────┼──────────────┼────────────┼──────────────┤
│ GET /profile     │      ✗       │     ✓      │      ✓       │
│ GET /cart        │      ✗       │     ✓      │      ✓       │
│ POST /cart/add   │      ✗       │     ✓      │      ✓       │
│ POST /orders     │      ✗       │     ✓      │      ✓       │
│ GET /orders      │      ✗       │     ✓      │      ✓       │
├──────────────────┼──────────────┼────────────┼──────────────┤
│ PATCH /orders/   │      ✗       │     ✗      │      ✓       │
│       status     │              │            │              │
└──────────────────┴──────────────┴────────────┴──────────────┘

✓ = Allowed
✗ = Forbidden (401/403)
```

### Data Validation Pipeline
```
Incoming Request
      │
      ▼
┌─────────────────┐
│ Serializer      │
│ Validation      │
└────┬────────────┘
     │
     ├─> Field Type Validation
     ├─> Required Fields Check
     ├─> Custom Validators
     ├─> Business Logic Validation
     │
     ▼
  Valid? ──NO──> 400 Bad Request
     │
    YES
     │
     ▼
┌─────────────────┐
│ Model Layer     │
│ Validation      │
└────┬────────────┘
     │
     ├─> Database Constraints
     ├─> Unique Constraints
     ├─> Foreign Key Validation
     │
     ▼
  Valid? ──NO──> 400 Bad Request
     │
    YES
     │
     ▼
Save to Database
```

## Scalability Considerations

### Current Architecture Limitations
1. **Monolithic Design** - All modules in single application
2. **SQLite Database** - Not suitable for high concurrency
3. **No Caching Layer** - Every request hits database
4. **No Load Balancing** - Single server instance

### Recommended Improvements

```
Current State:
┌────────┐     ┌─────────────────┐     ┌─────────┐
│ Client │────>│ Django (SQLite) │────>│ SQLite  │
└────────┘     └─────────────────┘     └─────────┘

Production-Ready:
┌────────┐     ┌──────────────┐     ┌─────────────┐     ┌────────────┐
│ Client │────>│ Load Balancer│────>│ Django (N)  │────>│ PostgreSQL │
└────────┘     └──────────────┘     └──────┬──────┘     └────────────┘
                                            │
                                            ▼
                                     ┌────────────┐
                                     │   Redis    │
                                     │   Cache    │
                                     └────────────┘
```

## API Versioning Strategy

Current implementation uses **URL path versioning**:

```
/api/v1/products/      <- Version 1
/api/v2/products/      <- Version 2 (future)
```

**Benefits:**
- Clear version identification
- Easy to maintain multiple versions
- Client-friendly
- Cacheable

## Error Handling Architecture

```
Exception Occurs
      │
      ▼
┌─────────────────────┐
│ Django Exception    │
│ Handler             │
└─────┬───────────────┘
      │
      ├─> ValidationError ────────> 400 Bad Request
      ├─> PermissionDenied ───────> 403 Forbidden
      ├─> NotAuthenticated ───────> 401 Unauthorized
      ├─> NotFound ───────────────> 404 Not Found
      ├─> MethodNotAllowed ───────> 405 Method Not Allowed
      └─> Server Error ───────────> 500 Internal Server Error
      │
      ▼
JSON Response:
{
  "detail": "Error message",
  "code": "error_code"
}
```

## Deployment Architecture

```
Development:
┌──────────────────────────────────┐
│ python manage.py runserver       │
│ SQLite Database                  │
│ DEBUG = True                     │
└──────────────────────────────────┘

Production (Recommended):
┌──────────────────────────────────┐
│ Nginx (Reverse Proxy)            │
│   └─> Gunicorn (WSGI Server)     │
│       └─> Django Application     │
│                                  │
│ PostgreSQL Database              │
│ Redis Cache                      │
│ Static Files (S3/CDN)            │
│ DEBUG = False                    │
└──────────────────────────────────┘
```

---

This architecture provides a solid foundation for a restaurant ordering system with clear separation of concerns, security best practices, and room for future scalability.
