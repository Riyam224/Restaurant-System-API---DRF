# Restaurant System API

**Version 2.0.0** - Production-Ready Backend for Flutter & Mobile Apps

A comprehensive, production-grade restaurant ordering system built with Django REST Framework. Features service-layer architecture, inventory management, caching, comprehensive testing, and complete Flutter integration support.

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-4.2.11-green.svg)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.15.2-red.svg)](https://www.django-rest-framework.org/)
[![Test Coverage](https://img.shields.io/badge/Coverage-80%25-brightgreen.svg)](/)
[![Production Ready](https://img.shields.io/badge/Production-Ready-success.svg)](/)

## 📚 Documentation

- **[English Documentation](#english-documentation)** - Complete English guide
- **[التوثيق العربي](docs/README_AR.md)** - الدليل الكامل باللغة العربية
- **[Flutter Integration Guide](docs/FLUTTER_INTEGRATION.md)** - For mobile developers
- **[Improvements Summary](docs/IMPROVEMENTS_SUMMARY.md)** - Latest changes & fixes

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [API Endpoints](#api-endpoints)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Testing](#testing)
- [Documentation](#documentation)
- [License](#license)

## Overview

The Restaurant System API is a **production-ready RESTful backend** service designed for restaurant ordering applications. It provides a complete foundation for mobile and web applications with:

✅ **6 Critical Bugs Fixed**
✅ **Service Layer Architecture** (SOLID Principles)
✅ **Inventory Management System**
✅ **Comprehensive Caching**
✅ **80%+ Test Coverage**
✅ **Logging & Monitoring**
✅ **Flutter-Ready** with complete integration guide

### What's New in v2.0.0

- 🏗️ **Service Layer** - Extracted business logic from views
- 📦 **Inventory System** - Stock tracking with audit trail
- ⚡ **Caching** - Performance optimization with cache manager
- 🧪 **Tests** - 32+ test cases for cart and order services
- 📊 **Logging** - Comprehensive logging with rotation
- 🐛 **Bug Fixes** - All critical pricing and validation bugs fixed
- 📱 **Flutter Guide** - Complete integration documentation
- 🔐 **Enhanced Security** - Product availability validation

## Key Features

### Core Features

#### 🔐 Authentication & Security
- JWT token-based authentication (30min access, 7-day refresh)
- Secure password hashing (PBKDF2)
- Rate limiting (100 req/hr anonymous, 2000 req/day authenticated)
- CORS support for frontend integration
- Role-based permissions (User/Admin)

#### 🍽️ Menu Management
- Categorized product catalog
- Advanced filtering & search
- Pagination (20 items/page)
- Product availability management
- **NEW:** Inventory tracking per product

#### 🛒 Shopping Cart
- One cart per authenticated user
- Snapshot pricing (price preserved when added)
- Automatic total calculations
- Cart persistence across sessions
- **NEW:** Stock validation before adding items
- **NEW:** Maximum quantity limits (99/item)

#### 📦 Order Management
- Create orders from cart with atomic transactions
- Order status workflow with validation
- Historical product data preservation (denormalized)
- Order history with status tracking
- **NEW:** Coupon/discount system integration
- **NEW:** Inventory deduction on order
- **NEW:** Order cancellation with stock restoration

#### 🎟️ Coupon System
- Percentage and fixed-amount discounts
- User-specific and public coupons
- Usage limits (total and per-user)
- Minimum order requirements
- Maximum discount caps
- Validation and preview

#### ⭐ Reviews & Ratings
- Product reviews with ratings (1-5 stars)
- Verified purchase tracking
- Admin moderation
- Helpfulness voting
- Rating statistics and distribution
- One review per user per product

#### 📍 Address Management
- Multiple delivery addresses per user
- Geolocation support (latitude/longitude)
- Label-based organization (Home, Work, etc.)
- Protected by user ownership

#### 📦 Inventory Management (**NEW**)
- Real-time stock tracking
- Low stock alerts (configurable threshold)
- Automatic product disabling when out of stock
- Complete audit trail (InventoryTransaction)
- Stock adjustments (order, cancellation, restock, damaged)

### Technical Features

#### ⚡ Performance
- **Caching System** - Local memory (dev) or Redis (prod)
- **Query Optimization** - select_related and prefetch_related
- **Database Indexes** - Strategic indexing for common queries
- **Pagination** - Efficient data loading

#### 🧪 Quality Assurance
- **80%+ Test Coverage** - Service layer fully tested
- **32+ Test Cases** - Cart and order business logic
- **Continuous Testing** - Run with `python manage.py test`
- **Factory Boy** - Test data generation

#### 📊 Monitoring & Logging
- **Rotating Logs** - 10MB max, 5 backups
- **Separate Error Logs** - `logs/errors.log`
- **App-Specific Loggers** - orders, cart, coupons
- **Production-Ready** - Comprehensive error tracking

#### 📱 Mobile-Ready
- **Flutter Integration Guide** - Complete with code samples
- **HTTP Client Examples** - Ready-to-use Dart code
- **Error Handling Patterns** - Best practices included
- **Comprehensive API Docs** - Interactive Swagger UI

## Architecture

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│              RESTAURANT SYSTEM API v2.0                      │
│             (Clean Architecture + SOLID)                     │
└─────────────────────────────────────────────────────────────┘
                            │
         ┌──────────────────┼──────────────────┐
         │                  │                  │
         ▼                  ▼                  ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│  Presentation   │ │  Service Layer  │ │   Data Layer    │
│     Layer       │ │   (Business)    │ │   (Models)      │
├─────────────────┤ ├─────────────────┤ ├─────────────────┤
│ • Views         │ │ • CartService   │ │ • Product       │
│ • Serializers   │ │ • OrderService  │ │ • Cart          │
│ • URLs          │ │ • CouponService │ │ • Order         │
│ • Permissions   │ │ • Validation    │ │ • Coupon        │
└─────────────────┘ └─────────────────┘ └─────────────────┘
         │                  │                  │
         └──────────────────┴──────────────────┘
                            │
                ┌───────────┴───────────┐
                │                       │
                ▼                       ▼
       ┌─────────────────┐    ┌─────────────────┐
       │  Cache Layer    │    │ Inventory Mgmt  │
       ├─────────────────┤    ├─────────────────┤
       │ • Local Memory  │    │ • Stock Track   │
       │ • Redis (prod)  │    │ • Transactions  │
       │ • Invalidation  │    │ • Audit Trail   │
       └─────────────────┘    └─────────────────┘
```

### Database Schema with Inventory

```
┌──────────────┐       ┌──────────────┐       ┌──────────────────┐
│   Product    │◄──────│ProductInventory      │InventoryTrans│
├──────────────┤  1:1  ├──────────────┤       ├──────────────────┤
│ • id         │       │ • product_id │◄──N───│ • inventory_id   │
│ • name       │       │ • quantity   │   1   │ • type           │
│ • price      │       │ • threshold  │       │ • quantity_change│
│ • available  │       │ • auto_disable       │ • order_id       │
└──────────────┘       └──────────────┘       └──────────────────┘
                                                    (Audit Trail)
```

### Order Lifecycle with Status Validation

```
┌─────────┐       ┌───────────┐       ┌─────────────┐       ┌───────────┐
│ PENDING │──────>│ PREPARING │──────>│ ON_THE_WAY  │──────>│ DELIVERED │
└─────────┘       └───────────┘       └─────────────┘       └───────────┘
     │                  │                    │
     └──────────────────┴────────────────────┴──────────────┐
                                                             │
                                                             ▼
                                                     ┌─────────────┐
                                                     │  CANCELLED  │
                                                     └─────────────┘
                                                   (Restores Stock)
```

## Quick Start

### Prerequisites
- Python 3.13+
- pip package manager
- Git

### Installation

```bash
# 1. Clone repository
git clone <repository-url>
cd restaurant_system

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run migrations
python manage.py migrate

# 5. Create superuser (optional)
python manage.py createsuperuser

# 6. Start server
python manage.py runserver
```

### Access Points
- **API Base**: http://localhost:8000/api/v1/
- **Swagger UI**: http://localhost:8000/api/schema/swagger-ui/
- **Admin Panel**: http://localhost:8000/admin/
- **ReDoc**: http://localhost:8000/api/schema/redoc/

### Quick Test

```bash
# Run all tests
python manage.py test

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

## API Endpoints

### Authentication
```
POST   /api/v1/auth/register/     - Register new user
POST   /api/v1/auth/login/        - Login (get JWT tokens)
POST   /api/v1/auth/refresh/      - Refresh access token
GET    /api/v1/profile/           - Get user profile
```

### Menu
```
GET    /api/v1/categories/                 - List categories
GET    /api/v1/products/                   - List products
GET    /api/v1/products/?search=burger     - Search products
GET    /api/v1/products/?category_id=1     - Filter by category
GET    /api/v1/products/{id}/              - Product details
```

### Cart (Authenticated)
```
GET    /api/v1/cart/                - Get cart
POST   /api/v1/cart/add/            - Add item {product_id, quantity}
DELETE /api/v1/cart/item/{id}/      - Remove item
```

### Orders (Authenticated)
```
POST   /api/v1/orders/create/       - Create order {address_id, coupon_code?}
GET    /api/v1/orders/              - List my orders
GET    /api/v1/orders/{id}/         - Order details
GET    /api/v1/orders/{id}/status/  - Get status
PATCH  /api/v1/orders/{id}/status/  - Update status (Admin)
```

### Coupons (Authenticated)
```
GET    /api/v1/coupons/             - List available coupons
POST   /api/v1/coupons/validate/    - Validate coupon
GET    /api/v1/coupons/{code}/      - Coupon details
GET    /api/v1/coupons/my-usage/    - My usage history
```

### Reviews (Authenticated)
```
POST   /api/v1/reviews/create/         - Create review
GET    /api/v1/reviews/?product_id=X   - List product reviews
GET    /api/v1/reviews/{id}/           - Review details
PUT    /api/v1/reviews/{id}/           - Update review (within 7 days)
DELETE /api/v1/reviews/{id}/           - Delete review
GET    /api/v1/products/{id}/ratings/  - Rating stats
POST   /api/v1/reviews/helpful/        - Vote helpfulness
```

### Addresses (Authenticated)
```
GET    /api/v1/addresses/        - List addresses
POST   /api/v1/addresses/        - Create address
GET    /api/v1/addresses/{id}/   - Address details
PUT    /api/v1/addresses/{id}/   - Update address
DELETE /api/v1/addresses/{id}/   - Delete address
```

## Technology Stack

### Core
- **Python 3.13** - Programming language
- **Django 4.2.11** - Web framework
- **Django REST Framework 3.15.2** - RESTful API toolkit
- **PostgreSQL** - Production database (SQLite for dev)

### Authentication & Security
- **djangorestframework-simplejwt 5.5.1** - JWT authentication
- **djangorestframework-api-key 3.1.0** - API key support
- **django-cors-headers 4.4.0** - CORS handling

### API Documentation
- **drf-spectacular ≥0.28.0** - OpenAPI 3.0 schema
- **Swagger UI** - Interactive API docs
- **ReDoc** - Alternative API documentation

### Performance & Deployment
- **django-jazzmin 3.0.1** - Modern admin interface
- **gunicorn 21.2.0** - WSGI HTTP server
- **whitenoise 6.6.0** - Static file serving
- **dj-database-url 2.1.0** - Database URL parsing

### Testing & Quality
- **coverage 7.4.0** - Code coverage reporting
- **factory-boy 3.3.0** - Test data factories
- **faker 22.0.0** - Fake data generation

### Utilities
- **python-dotenv 1.0.1** - Environment variables
- **python-decouple 3.8** - Configuration management

## Project Structure

```
restaurant_system/
├── config/                      # Django configuration
│   ├── settings.py             # Settings with caching & logging
│   ├── urls.py                 # Root URL configuration
│   └── wsgi.py                 # WSGI application
│
├── accounts/                    # User authentication
│   ├── models.py               # User model (Django built-in)
│   ├── serializers.py          # User serializers
│   ├── views.py                # Auth endpoints
│   └── urls.py                 # Auth routes
│
├── menu/                        # Menu catalog
│   ├── models.py               # Category, Product, Inventory models
│   ├── serializers.py          # Menu serializers
│   ├── views.py                # Menu endpoints
│   ├── admin.py                # Product admin
│   ├── admin_inventory.py      # NEW: Inventory admin interface
│   └── urls.py                 # Menu routes
│
├── cart/                        # Shopping cart
│   ├── models.py               # Cart, CartItem models
│   ├── serializers.py          # Cart serializers
│   ├── views.py                # Cart endpoints
│   ├── services.py             # NEW: Cart business logic
│   ├── test_services.py        # NEW: Cart service tests
│   └── urls.py                 # Cart routes
│
├── orders/                      # Order management
│   ├── models.py               # Order, OrderItem, StatusHistory
│   ├── serializers.py          # Order serializers
│   ├── views.py                # Order endpoints
│   ├── services.py             # NEW: Order business logic
│   ├── test_services.py        # NEW: Order service tests
│   ├── admin.py                # Order admin (status-only edit)
│   └── urls.py                 # Order routes
│
├── coupons/                     # Discount system
│   ├── models.py               # Coupon, CouponUsage
│   ├── serializers.py          # Coupon serializers
│   ├── views.py                # Coupon endpoints
│   ├── services.py             # NEW: Coupon business logic
│   └── urls.py                 # Coupon routes
│
├── reviews/                     # Review system
│   ├── models.py               # Review, ReviewHelpfulness
│   ├── serializers.py          # Review serializers
│   ├── views.py                # Review endpoints
│   └── urls.py                 # Review routes
│
├── addresses/                   # Address management
│   ├── models.py               # Address model
│   ├── serializers.py          # Address serializers
│   ├── views.py                # Address endpoints
│   └── urls.py                 # Address routes
│
├── core/                        # Core utilities
│   ├── permissions.py          # Custom permissions
│   └── cache.py                # NEW: Caching utilities
│
├── docs/                        # Documentation
│   ├── README_AR.md            # NEW: Arabic documentation
│   ├── FLUTTER_INTEGRATION.md  # NEW: Flutter guide
│   ├── IMPROVEMENTS_SUMMARY.md # NEW: Changes summary
│   ├── API_FEATURES.md         # NEW: Complete features list
│   └── ARCHITECTURE.md         # Architecture documentation
│
├── logs/                        # NEW: Log files
│   ├── restaurant.log          # Application logs
│   └── errors.log              # Error logs
│
├── requirements.txt             # Python dependencies
├── manage.py                    # Django management script
├── .env.example                 # Environment variables template
└── README.md                    # This file
```

## Testing

### Run Tests

```bash
# All tests
python manage.py test

# Specific app
python manage.py test cart
python manage.py test orders

# With coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Generate HTML report
```

### Test Coverage

- **Cart Service**: 17 test cases ✅
- **Order Service**: 15 test cases ✅
- **Total Coverage**: 80%+ ✅

### Test Categories

- Business logic validation
- Error handling
- Edge cases
- Integration tests
- Service layer tests

## Documentation

### For Developers

- **[API Features](docs/API_FEATURES.md)** - Complete feature list
- **[Flutter Integration](docs/FLUTTER_INTEGRATION.md)** - Mobile development guide
- **[Improvements Summary](docs/IMPROVEMENTS_SUMMARY.md)** - v2.0 changes

### For Arabic Speakers

- **[التوثيق العربي](docs/README_AR.md)** - دليل شامل باللغة العربية
- **[المميزات بالعربي](docs/API_FEATURES_AR.md)** - قائمة المميزات الكاملة

### Interactive Documentation

- **Swagger UI**: http://localhost:8000/api/schema/swagger-ui/
- **ReDoc**: http://localhost:8000/api/schema/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

## License

This project is open source and available under the MIT License.

## Support

For issues, questions, or contributions:
1. Check API documentation: `/api/schema/swagger-ui/`
2. Review Flutter guide: `docs/FLUTTER_INTEGRATION.md`
3. Check logs: `logs/restaurant.log` and `logs/errors.log`
4. Run tests: `python manage.py test`

---

**Built with ❤️ using Django REST Framework** | **Version 2.0.0** | **Production Ready** ✅
