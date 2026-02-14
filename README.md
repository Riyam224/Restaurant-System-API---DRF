# Restaurant System API

**Version 2.0** - Production-Ready Backend for Restaurant Ordering Applications

A comprehensive, enterprise-grade restaurant ordering system built with Django REST Framework. Features include authentication, menu management, shopping cart, orders, coupons, reviews, analytics with AI-powered insights, and complete mobile app integration support.

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-4.2.11-green.svg)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.15.2-red.svg)](https://www.django-rest-framework.org/)
[![Production Ready](https://img.shields.io/badge/Production-Ready-success.svg)](/)

---

## 📚 Documentation

### For Developers

- **[API Documentation](docs/API_DOCUMENTATION.md)** - Complete API reference with all endpoints, authentication, request/response examples
- **[Analytics Guide](docs/ANALYTICS_GUIDE.md)** - Analytics system, AI insights, predictions, and anomaly detection
- **[Flutter Integration](docs/FLUTTER_INTEGRATION.md)** - Mobile app integration guide with code examples
- **[Admin Panel Guide](docs/ADMIN_PANEL.md)** - Modern admin interface customization and usage

### For Arabic Speakers

- **[التوثيق العربي](docs/README_AR.md)** - الدليل الكامل باللغة العربية

---

## ⚡ Quick Start

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

# 4. Configure environment variables
cp .env.example .env
# Edit .env and add your configuration

# 5. Run migrations
python manage.py migrate

# 6. Create superuser
python manage.py createsuperuser

# 7. (Optional) Load sample data
python seed_test_data.py

# 8. Start server
python manage.py runserver
```

### Access Points

- **API Base**: http://localhost:8000/api/v1/
- **Interactive API Docs**: http://localhost:8000/api/schema/swagger-ui/
- **Admin Panel**: http://localhost:8000/admin/
- **ReDoc**: http://localhost:8000/api/schema/redoc/

---

## 🎯 What This API Does

This is a **complete backend solution** for restaurant ordering applications. It provides:

### Core Features

✅ **Authentication & User Management**
- JWT token-based authentication (Google OAuth supported)
- User registration, login, and profile management
- Secure password hashing and session management

✅ **Menu Management**
- Categorized product catalog with images
- Advanced search and filtering
- Product availability and inventory tracking
- Real-time stock management

✅ **Shopping Cart**
- Persistent cart across sessions
- Snapshot pricing (prices locked when added to cart)
- Stock validation before adding items
- Automatic total calculations

✅ **Order Management**
- Create orders from cart with atomic transactions
- Order status workflow (pending → preparing → on_the_way → delivered)
- Order history and tracking
- Coupon/discount integration
- Automatic inventory deduction

✅ **Coupon & Discount System**
- Percentage and fixed-amount discounts
- User-specific and public coupons
- Usage limits and expiration dates
- Minimum order requirements
- Validation and preview API

✅ **Reviews & Ratings**
- Product reviews with 1-5 star ratings
- Verified purchase tracking
- Helpfulness voting
- Admin moderation
- Rating statistics and distribution

✅ **Address Management**
- Multiple delivery addresses per user
- Geolocation support (latitude/longitude)
- Label-based organization (Home, Work, etc.)

### Advanced Features

⚡ **Analytics & Business Intelligence**
- Real-time dashboard KPIs (revenue, orders, users)
- Revenue and sales analytics
- Product performance metrics
- User behavior analytics
- **AI-Powered Insights** (Claude Sonnet 4.5)
  - Natural language business summaries
  - Anomaly detection with AI explanations
  - Predictive analytics for revenue forecasting
  - Intelligent recommendations

🎨 **Modern Admin Panel**
- Beautiful, customizable interface (Jazzmin)
- Dashboard with live statistics and charts
- Custom theming and branding
- Quick actions and shortcuts
- Color-coded status indicators
- Mobile-responsive design

🔐 **Security & Performance**
- Rate limiting (100/hr anonymous, 2000/day authenticated)
- CORS support for frontend integration
- Input validation and sanitization
- Query optimization with caching
- Comprehensive error handling
- Rotating logs with error tracking

🧪 **Quality Assurance**
- 80%+ test coverage
- Service layer architecture (SOLID principles)
- Comprehensive test suite (32+ tests)
- Factory Boy for test data generation

📱 **Mobile-Ready**
- RESTful API design
- Complete Flutter integration guide
- Detailed code examples
- Best practices for mobile development

---

## 🏗️ Architecture

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
│ • API Views     │ │ • CartService   │ │ • Product       │
│ • Serializers   │ │ • OrderService  │ │ • Cart          │
│ • Permissions   │ │ • CouponService │ │ • Order         │
│ • Validators    │ │ • Analytics     │ │ • Coupon        │
└─────────────────┘ └─────────────────┘ └─────────────────┘
         │                  │                  │
         └──────────────────┴──────────────────┘
                            │
                ┌───────────┴───────────┐
                │                       │
                ▼                       ▼
       ┌─────────────────┐    ┌─────────────────┐
       │  Cache Layer    │    │  AI Services    │
       ├─────────────────┤    ├─────────────────┤
       │ • Redis/Memory  │    │ • Claude AI     │
       │ • Invalidation  │    │ • Insights      │
       └─────────────────┘    └─────────────────┘
```

---

## 🛠️ Technology Stack

### Backend Core
- **Python 3.13** - Programming language
- **Django 4.2.11** - Web framework
- **Django REST Framework 3.15.2** - RESTful API toolkit
- **PostgreSQL** - Production database (SQLite for development)

### Authentication & Security
- **djangorestframework-simplejwt** - JWT authentication
- **Firebase Admin SDK** - Google OAuth integration
- **django-cors-headers** - CORS handling

### API Documentation
- **drf-spectacular** - OpenAPI 3.0 schema generation
- **Swagger UI** - Interactive API documentation
- **ReDoc** - Alternative API documentation

### Analytics & AI
- **Anthropic Claude API** - AI-powered business insights
- **Claude Sonnet 4.5** - Latest AI model for analytics

### Admin Interface
- **django-jazzmin** - Modern, customizable admin interface

### Deployment
- **gunicorn** - WSGI HTTP server
- **whitenoise** - Static file serving
- **dj-database-url** - Database URL parsing
- **Railway** - Cloud deployment platform

### Testing & Quality
- **coverage** - Code coverage reporting
- **factory-boy** - Test data factories
- **pytest** - Advanced testing framework

---

## 📂 Project Structure

```
restaurant_system/
├── config/                      # Django configuration
│   ├── settings.py             # Main settings
│   ├── urls.py                 # Root URL configuration
│   └── wsgi.py                 # WSGI application
│
├── accounts/                    # Authentication & users
│   ├── models.py               # User model
│   ├── serializers.py          # User serializers
│   ├── views.py                # Auth endpoints
│   └── urls.py                 # Auth routes
│
├── menu/                        # Menu & products
│   ├── models.py               # Category, Product, Inventory
│   ├── serializers.py          # Menu serializers
│   ├── views.py                # Menu endpoints
│   └── admin.py                # Product admin
│
├── cart/                        # Shopping cart
│   ├── models.py               # Cart, CartItem
│   ├── serializers.py          # Cart serializers
│   ├── views.py                # Cart endpoints
│   ├── services.py             # Business logic
│   └── tests.py                # Cart tests
│
├── orders/                      # Order management
│   ├── models.py               # Order, OrderItem
│   ├── serializers.py          # Order serializers
│   ├── views.py                # Order endpoints
│   ├── services.py             # Business logic
│   └── tests.py                # Order tests
│
├── coupons/                     # Discount system
│   ├── models.py               # Coupon, CouponUsage
│   ├── serializers.py          # Coupon serializers
│   ├── views.py                # Coupon endpoints
│   └── services.py             # Business logic
│
├── reviews/                     # Review system
│   ├── models.py               # Review, Helpfulness
│   ├── serializers.py          # Review serializers
│   └── views.py                # Review endpoints
│
├── addresses/                   # Address management
│   ├── models.py               # Address model
│   ├── serializers.py          # Address serializers
│   └── views.py                # Address endpoints
│
├── analytics/                   # Analytics & AI
│   ├── views.py                # Analytics endpoints
│   ├── queries.py              # Analytics queries
│   ├── claude_insights.py      # AI integration
│   ├── anomaly_detection.py    # Anomaly detection
│   └── predictions.py          # Predictive analytics
│
├── core/                        # Core utilities
│   ├── permissions.py          # Custom permissions
│   ├── cache.py                # Caching utilities
│   └── admin_dashboard.py      # Admin dashboard
│
├── docs/                        # Documentation
│   ├── API_DOCUMENTATION.md    # Complete API reference
│   ├── ANALYTICS_GUIDE.md      # Analytics & AI guide
│   ├── FLUTTER_INTEGRATION.md  # Mobile integration
│   ├── ADMIN_PANEL.md          # Admin panel guide
│   └── README_AR.md            # Arabic documentation
│
├── static/                      # Static files
│   └── admin/                  # Admin panel assets
│
├── templates/                   # HTML templates
│   └── admin/                  # Admin templates
│
├── logs/                        # Application logs
│   ├── restaurant.log          # General logs
│   └── errors.log              # Error logs
│
├── requirements.txt             # Python dependencies
├── manage.py                    # Django management
├── .env.example                 # Environment template
└── README.md                    # This file
```

---

## 🔌 API Endpoints Overview

### Authentication
```
POST   /api/v1/auth/register/      # Register new user
POST   /api/v1/auth/login/         # Login (get JWT tokens)
POST   /api/v1/auth/refresh/       # Refresh access token
POST   /api/v1/auth/google/        # Google OAuth login
GET    /api/v1/profile/            # Get user profile
```

### Menu
```
GET    /api/v1/categories/                # List categories
GET    /api/v1/products/                  # List products (with filters)
GET    /api/v1/products/{id}/             # Product details
GET    /api/v1/products/{id}/ratings/     # Product ratings
```

### Cart (Authenticated)
```
GET    /api/v1/cart/                # Get user's cart
POST   /api/v1/cart/add/            # Add item to cart
PATCH  /api/v1/cart/item/{id}/      # Update item quantity
DELETE /api/v1/cart/item/{id}/      # Remove item
DELETE /api/v1/cart/clear/          # Clear cart
```

### Orders (Authenticated)
```
POST   /api/v1/orders/create/       # Create order from cart
GET    /api/v1/orders/              # List my orders
GET    /api/v1/orders/{id}/         # Order details
GET    /api/v1/orders/{id}/status/  # Get order status
PATCH  /api/v1/orders/{id}/status/  # Update status (Admin)
POST   /api/v1/orders/{id}/cancel/  # Cancel order
```

### Coupons
```
GET    /api/v1/coupons/             # List available coupons
POST   /api/v1/coupons/validate/    # Validate coupon
GET    /api/v1/coupons/{code}/      # Coupon details
GET    /api/v1/coupons/my-usage/    # My usage history
```

### Reviews (Authenticated)
```
POST   /api/v1/reviews/create/         # Create review
GET    /api/v1/reviews/                # List reviews (filtered)
PUT    /api/v1/reviews/{id}/           # Update review
DELETE /api/v1/reviews/{id}/           # Delete review
POST   /api/v1/reviews/helpful/        # Vote helpfulness
```

### Analytics (Admin Only)
```
GET    /api/v1/analytics/dashboard/              # Dashboard KPIs
GET    /api/v1/analytics/revenue/metrics/        # Revenue analytics
GET    /api/v1/analytics/revenue/daily/          # Daily revenue
GET    /api/v1/analytics/orders/status/          # Order analytics
GET    /api/v1/analytics/users/metrics/          # User analytics
GET    /api/v1/analytics/products/performance/   # Product performance
GET    /api/v1/analytics/coupons/performance/    # Coupon analytics
GET    /api/v1/analytics/reviews/metrics/        # Review metrics
GET    /api/v1/analytics/insights/business/      # AI business insights
GET    /api/v1/analytics/anomalies/detect/       # Anomaly detection
GET    /api/v1/analytics/predictions/tomorrow/   # Revenue prediction
```

**For detailed API documentation with examples, see [docs/API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md)**

---

## 🧪 Testing

### Run Tests

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test cart
python manage.py test orders
python manage.py test analytics

# Run with coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Generate HTML report

# Open coverage report
open htmlcov/index.html
```

### Test Coverage
- **Cart Service**: 17 test cases ✅
- **Order Service**: 15 test cases ✅
- **Analytics**: 16 test cases ✅
- **Total Coverage**: 80%+ ✅

---

## 🚀 Deployment

### Environment Variables

Create a `.env` file with:

```bash
# Django
DEBUG=False
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DATABASE_URL=postgresql://user:password@host:port/dbname

# CORS
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com

# AI Features (Optional)
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Google OAuth (Optional)
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
```

### Production Checklist

- ✅ Set `DEBUG=False`
- ✅ Configure strong `SECRET_KEY`
- ✅ Set up PostgreSQL database
- ✅ Configure `ALLOWED_HOSTS`
- ✅ Set up CORS origins
- ✅ Run migrations: `python manage.py migrate`
- ✅ Collect static files: `python manage.py collectstatic`
- ✅ Set up SSL certificate
- ✅ Configure logging
- ✅ Set up Redis for caching (recommended)
- ✅ Configure backup strategy

### Deploy to Railway

This project is configured for Railway deployment:

1. Push code to GitHub
2. Import repository in Railway
3. Add environment variables
4. Railway will auto-deploy

---

## 📖 How to Use This API

### For Frontend Developers

1. **Start here**: Read [docs/API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md)
2. **Test endpoints**: Use Swagger UI at http://localhost:8000/api/schema/swagger-ui/
3. **Authentication**: Implement JWT token handling
4. **Error handling**: Follow the error response formats in the docs

### For Mobile App Developers

1. **Flutter guide**: See [docs/FLUTTER_INTEGRATION.md](docs/FLUTTER_INTEGRATION.md)
2. **Code examples**: Ready-to-use Dart code included
3. **Best practices**: Token management, caching, error handling

### For Business/Analytics Users

1. **Admin panel**: Access http://localhost:8000/admin/
2. **Analytics**: See [docs/ANALYTICS_GUIDE.md](docs/ANALYTICS_GUIDE.md)
3. **Dashboard**: View real-time KPIs and AI insights
4. **Reports**: Export data via API or admin panel

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is open source and available under the MIT License.

---

## 🆘 Support & Resources

### Documentation
- **API Reference**: [docs/API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md)
- **Analytics Guide**: [docs/ANALYTICS_GUIDE.md](docs/ANALYTICS_GUIDE.md)
- **Flutter Integration**: [docs/FLUTTER_INTEGRATION.md](docs/FLUTTER_INTEGRATION.md)
- **Admin Panel**: [docs/ADMIN_PANEL.md](docs/ADMIN_PANEL.md)

### Interactive Tools
- **Swagger UI**: http://localhost:8000/api/schema/swagger-ui/
- **ReDoc**: http://localhost:8000/api/schema/redoc/
- **Admin Panel**: http://localhost:8000/admin/

### Logs & Debugging
- **Application Logs**: `logs/restaurant.log`
- **Error Logs**: `logs/errors.log`
- **Django Debug**: Set `DEBUG=True` in `.env`

---

## ✨ What's New in v2.0

- ✅ Service layer architecture (SOLID principles)
- ✅ Inventory management with stock tracking
- ✅ AI-powered analytics (Claude Sonnet 4.5)
- ✅ Anomaly detection with explanations
- ✅ Predictive analytics
- ✅ Modern admin panel with custom theming
- ✅ Google OAuth authentication
- ✅ 80%+ test coverage
- ✅ Comprehensive documentation
- ✅ Flutter integration guide
- ✅ Production-ready deployment configuration

---

**Built with ❤️ using Django REST Framework**

**Version**: 2.0.0
**Status**: Production Ready ✅
**Last Updated**: February 14, 2026
