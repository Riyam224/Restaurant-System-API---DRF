# Restaurant System API

A comprehensive restaurant ordering system built with Django REST Framework that provides a complete backend solution for managing menus, shopping carts, and orders.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)
- [Authentication](#authentication)
- [Documentation](#documentation)
- [System Architecture & Flow Diagrams](#system-architecture--flow-diagrams)
  - [System Architecture Overview](#️-system-architecture-overview)
  - [Database Schema & Relationships](#️-database-schema--relationships)
  - [Authentication & Authorization Flow](#-authentication--authorization-flow)
  - [Shopping Cart Management Flow](#-shopping-cart-management-flow)
  - [Order Lifecycle Flow](#-order-lifecycle-flow)
  - [API Endpoints Map](#-api-endpoints-map)
  - [Request/Response Patterns](#-requestresponse-patterns)
- [Development](#development)
- [Future Enhancements](#future-enhancements)
- [Contributing](#contributing)
- [License](#license)

## Overview

The Restaurant System API is a RESTful backend service designed for restaurant ordering applications. It provides a robust foundation for mobile and web applications that need menu browsing, cart management, and order processing capabilities.

### Key Capabilities

- **User Management**: Secure registration and JWT-based authentication
- **Menu Catalog**: Organized product catalog with categories
- **Shopping Cart**: Real-time cart management with automatic total calculations
- **Order Processing**: Complete order lifecycle from creation to delivery
- **API Documentation**: Interactive Swagger UI for API exploration

### Documentation Quick Links

- **Interactive Docs**: [/api/docs/](http://localhost:8000/api/docs/) (tagged by Accounts, Menu, Cart, Orders with examples and responses)
- **OpenAPI Schema**: [/api/schema/](http://localhost:8000/api/schema/) (downloadable JSON/YAML)
- **Architecture Guide**: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- **API Reference**: [docs/API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md)
- **Database Schema**: [docs/DATABASE_SCHEMA.md](docs/DATABASE_SCHEMA.md)
- **Setup Guide**: [docs/SETUP_GUIDE.md](docs/SETUP_GUIDE.md)
- **Postman Quickstart**: [docs/POSTMAN_QUICK_REFERENCE.md](docs/POSTMAN_QUICK_REFERENCE.md)

## Features

### Authentication & User Management

- User registration with password validation
- JWT token-based authentication (access + refresh tokens)
- Secure user profile management
- Token refresh mechanism

### Menu Management

- Categorized menu items
- Product listings with filtering capabilities
- Product details with descriptions and pricing
- Image support for categories and products

### Shopping Cart

- One cart per authenticated user
- Add/remove items with custom quantities
- Automatic price and item count calculations
- Cart persistence across sessions

### Order Management

- Create orders from cart items
- Order history tracking
- Real-time order status updates
- Historical product data preservation
- Order status workflow: pending → preparing → on_the_way → delivered

### API Performance & Security

- **Pagination**: Automatic pagination for list endpoints (20 items per page)
- **Rate Limiting**: Request throttling at 100 requests per minute per user
- **API Protection**: Built-in safeguards against abuse and excessive usage

## Technology Stack

### Backend Framework

- **Django 6.0** - Web framework
- **Python 3.13** - Programming language
- **Django REST Framework** - RESTful API toolkit
- **djangorestframework-simplejwt** - JWT authentication

### API Documentation

- **drf-spectacular** - OpenAPI 3.0 schema generation
- **Swagger UI** - Interactive API documentation

### Database

- **SQLite3** - Lightweight database (default)

### Additional Integrations

- **CORS Headers** - Cross-origin resource sharing support
- **WhiteNoise** - Static file serving for production
- **OpenAPI 3.0** - API schema specification

## Key Technical Features

### Production-Ready Capabilities

- **Environment-Based Configuration**: Settings controlled via environment variables
- **Security**: PBKDF2 password hashing, JWT token authentication
- **Static Files**: WhiteNoise for efficient static file serving
- **CORS Support**: Cross-origin requests enabled for frontend integration
- **Admin Interface**: Django admin panel for content management
- **Internationalization**: Built-in i18n support (English)
- **Timezone Support**: UTC timezone with full timezone awareness

### API Features

- **Automatic Pagination**: 20 items per page on all list endpoints
- **Rate Limiting**: 100 requests/minute per authenticated user
- **Token Authentication**: JWT with 30-minute access and 7-day refresh tokens
- **Interactive Documentation**: Swagger UI at `/api/docs/` (tagged by domain: Accounts, Menu, Cart, Orders)
- **Schema Export**: OpenAPI 3.0 schema at `/api/schema/` with inlined request/response examples and documented status codes
- **Password Validation**: Django's built-in validators for security
- **Request Throttling**: Protection against API abuse

### Data Management

- **Historical Order Data**: Product snapshots preserved in orders
- **Automatic Calculations**: Cart totals computed automatically
- **One Cart Per User**: Enforced at database level
- **Order Status Workflow**: Structured status transitions
- **Soft Deletes**: Category/Product availability flags instead of deletion

## Quick Start

### Prerequisites

- Python 3.13 or higher
- pip package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd restaurant_system
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install django djangorestframework djangorestframework-simplejwt drf-spectacular django-cors-headers whitenoise
   ```

4. **Run migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Start development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - API Base URL: `http://localhost:8000/api/v1/`
   - Swagger UI: `http://localhost:8000/api/docs/`
   - Admin Panel: `http://localhost:8000/admin/`

## Project Structure

```
restaurant_system/
├── config/                 # Django project configuration
│   ├── settings.py        # Project settings
│   └── urls.py            # Root URL configuration
├── accounts/              # Authentication & user management
│   ├── models.py         # User models (uses Django built-in)
│   ├── serializers.py    # User serializers
│   └── views.py          # Auth endpoints
├── menu/                  # Menu catalog management
│   ├── models.py         # Category & Product models
│   ├── serializers.py    # Menu serializers
│   └── views.py          # Menu endpoints
├── cart/                  # Shopping cart functionality
│   ├── models.py         # Cart & CartItem models
│   ├── serializers.py    # Cart serializers
│   └── views.py          # Cart endpoints
├── orders/                # Order processing
│   ├── models.py         # Order & OrderItem models
│   ├── serializers.py    # Order serializers
│   └── views.py          # Order endpoints
├── core/                  # Core utilities (placeholder)
├── docs/                  # Documentation
│   ├── POSTMAN_GUIDE.md           # Postman collection guide
│   ├── POSTMAN_QUICK_REFERENCE.md # Postman quick reference
│   ├── ARCHITECTURE.md            # System architecture
│   ├── API_DOCUMENTATION.md       # API documentation
│   ├── DATABASE_SCHEMA.md         # Database schema
│   └── SETUP_GUIDE.md             # Setup guide
├── postman/               # Postman collection files
│   ├── Restaurant_API.postman_collection.json
│   └── Restaurant_API.postman_environment.json
├── db.sqlite3            # SQLite database
└── manage.py             # Django management script
```

## API Documentation

### Interactive Documentation

The project includes comprehensive interactive API documentation powered by Swagger UI:

- **Swagger UI**: [http://localhost:8000/api/docs/](http://localhost:8000/api/docs/) (grouped by tags, with request/response examples and documented status codes)
- **OpenAPI Schema**: [http://localhost:8000/api/schema/](http://localhost:8000/api/schema/) (JSON/YAML)
- **Deep Dive**: [API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md) for full endpoint details
- **Architecture & Data**: [ARCHITECTURE.md](docs/ARCHITECTURE.md) and [DATABASE_SCHEMA.md](docs/DATABASE_SCHEMA.md)

Docs generation flow:

```
Views/Serializers → drf-spectacular (schema) → /api/schema/ → Swagger UI (/api/docs/)
```

### Postman Collection

Ready-to-use Postman collection for testing all API endpoints:

- **Collection**: [Restaurant_API.postman_collection.json](postman/Restaurant_API.postman_collection.json)
- **Environment**: [Restaurant_API.postman_environment.json](postman/Restaurant_API.postman_environment.json)
- **Quick Start**: [POSTMAN_QUICK_REFERENCE.md](docs/POSTMAN_QUICK_REFERENCE.md)
- **Complete Guide**: [POSTMAN_GUIDE.md](docs/POSTMAN_GUIDE.md)

Import both files into Postman and start testing immediately with auto-saved tokens and variables.

### API Endpoints Overview

#### Authentication (`/api/v1/auth/`)

- `POST /auth/register` - Create new user account
- `POST /auth/login` - Login and receive JWT tokens
- `POST /auth/refresh` - Refresh access token
- `GET /profile` - Get authenticated user profile

#### Menu (`/api/v1/`)

- `GET /categories/` - List all active categories (paginated)
- `GET /products/` - List all available products (paginated, supports `?category_id=X`)
- `GET /products/<id>/` - Get product details

#### Cart (`/api/v1/cart/`)

- `GET /` - Get current cart with items
- `POST /add/` - Add product to cart
- `DELETE /item/<item_id>/` - Remove item from cart

#### Orders (`/api/v1/orders/`)

- `POST /create/` - Create order from cart
- `GET /` - List user's orders (paginated)
- `GET /<id>/` - Get order details
- `PATCH /<id>/status/` - Update order status (admin only)

For detailed API documentation with request/response examples, see [API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md).

## Authentication

The API uses JWT (JSON Web Token) authentication:

### Token Configuration

- **Access Token Lifetime**: 30 minutes
- **Refresh Token Lifetime**: 7 days
- **Token Type**: Bearer

### Usage

1. **Register/Login** to receive tokens
2. **Include access token** in requests:
   ```
   Authorization: Bearer <access_token>
   ```
3. **Refresh token** when access token expires using the refresh endpoint

### Public vs Protected Endpoints

**Public** (No authentication required):

- Category listings
- Product listings and details

**Protected** (Authentication required):

- User profile
- Cart operations
- Order management

**Admin Only**:

- Order status updates

**Access Matrix**

```
┌────────────┬─────────────────────────────┬──────────────────────────────┐
│ Domain     │ Endpoints                   │ Auth                         │
├────────────┼─────────────────────────────┼──────────────────────────────┤
│ Accounts   │ /auth/*, /profile           │ JWT (Bearer)                 │
│ Menu       │ /categories, /products/*    │ Public (optionally API Key)* │
│ Cart       │ /cart/*                     │ JWT (Bearer)                 │
│ Orders     │ /orders/*                   │ JWT (Bearer)                 │
│ Orders     │ /orders/<id>/status/        │ Admin + JWT (Bearer)         │
└────────────┴─────────────────────────────┴──────────────────────────────┘
*If `djangorestframework-api-key` is installed, Menu reads also accept API Key (`X-API-Key` header).
```

## Documentation

Comprehensive documentation is available in the [docs/](docs/) folder:

### Core Documentation

- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - System architecture and design patterns
- **[API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md)** - Detailed API endpoint documentation
- **[DATABASE_SCHEMA.md](docs/DATABASE_SCHEMA.md)** - Database structure and relationships
- **[SETUP_GUIDE.md](docs/SETUP_GUIDE.md)** - Detailed installation and deployment guide

### Postman Documentation

- **[POSTMAN_GUIDE.md](docs/POSTMAN_GUIDE.md)** - Complete Postman collection guide
- **[POSTMAN_QUICK_REFERENCE.md](docs/POSTMAN_QUICK_REFERENCE.md)** - Quick reference for testing

## System Architecture & Flow Diagrams

### 🏗️ System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         RESTAURANT SYSTEM API                            │
│                        (Django REST Framework)                           │
└─────────────────────────────────────────────────────────────────────────┘
                                     │
                ┌────────────────────┼────────────────────┐
                │                    │                    │
                ▼                    ▼                    ▼
    ┌───────────────────┐ ┌──────────────────┐ ┌─────────────────┐
    │   Authentication  │ │   Core Features  │ │   Integration   │
    │       Layer       │ │      Layer       │ │      Layer      │
    └───────────────────┘ └──────────────────┘ └─────────────────┘
              │                     │                     │
              │                     │                     │
    ┌─────────▼─────────┐          │            ┌────────▼────────┐
    │  JWT Auth (Simple │          │            │  CORS Headers   │
    │  JWT)             │          │            │  WhiteNoise     │
    │  - Access Token   │          │            │  Static Files   │
    │  - Refresh Token  │          │            └─────────────────┘
    │  - 30min/7day     │          │
    └───────────────────┘          │
                                   │
              ┌────────────────────┼────────────────────┐
              │                    │                    │
              ▼                    ▼                    ▼
    ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
    │   📁 Accounts   │  │   🍽️ Menu       │  │   🛒 Cart       │
    │   Module        │  │   Module        │  │   Module        │
    ├─────────────────┤  ├─────────────────┤  ├─────────────────┤
    │ • Registration  │  │ • Categories    │  │ • Add Items     │
    │ • Login         │  │ • Products      │  │ • Update Qty    │
    │ • Profile       │  │ • Filtering     │  │ • Remove Items  │
    │ • Token Refresh │  │ • Pagination    │  │ • Auto Totals   │
    └─────────────────┘  └─────────────────┘  └─────────────────┘
                                   │
                                   ▼
                         ┌─────────────────┐
                         │   📦 Orders     │
                         │   Module        │
                         ├─────────────────┤
                         │ • Create Order  │
                         │ • Order History │
                         │ • Status Update │
                         │ • Order Details │
                         └─────────────────┘
                                   │
              ┌────────────────────┼────────────────────┐
              │                    │                    │
              ▼                    ▼                    ▼
    ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
    │  Pagination     │  │  Rate Limiting  │  │  API Docs       │
    │  (20/page)      │  │  (100 req/min)  │  │  (Swagger UI)   │
    └─────────────────┘  └─────────────────┘  └─────────────────┘
                                   │
                                   ▼
                         ┌─────────────────┐
                         │  SQLite3 DB     │
                         │  (Production:   │
                         │   PostgreSQL)   │
                         └─────────────────┘
```

### 🗄️ Database Schema & Relationships

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          DATABASE SCHEMA                                 │
└─────────────────────────────────────────────────────────────────────────┘

┌──────────────────┐
│   auth_user      │ (Django Built-in)
├──────────────────┤
│ • id (PK)        │
│ • username       │◄────────────────┐
│ • email          │                 │
│ • password       │                 │
│ • is_active      │                 │
│ • date_joined    │                 │
└──────────────────┘                 │
         │                           │
         │ 1                         │ 1
         │                           │
         │ N                         │ N
         ▼                           │
┌──────────────────┐                 │
│   cart_cart      │                 │
├──────────────────┤                 │
│ • id (PK)        │                 │
│ • user_id (FK)   │─────────────────┘
│ • is_active      │
│ • created_at     │
└──────────────────┘
         │
         │ 1
         │
         │ N
         ▼
┌──────────────────┐         ┌──────────────────┐
│  cart_cartitem   │    N    │  menu_product    │
├──────────────────┤────────>├──────────────────┤
│ • id (PK)        │    1    │ • id (PK)        │
│ • cart_id (FK)   │         │ • category_id(FK)│──┐
│ • product_id(FK) │         │ • name           │  │
│ • quantity       │         │ • description    │  │
│ • price          │         │ • price          │  │ N
└──────────────────┘         │ • image          │  │
                             │ • is_available   │  │ 1
                             │ • created_at     │  │
                             └──────────────────┘  │
                                                   │
                                                   ▼
                                          ┌──────────────────┐
                                          │  menu_category   │
                                          ├──────────────────┤
                                          │ • id (PK)        │
                                          │ • name (unique)  │
                                          │ • image          │
                                          │ • is_active      │
                                          │ • created_at     │
                                          └──────────────────┘

┌──────────────────┐
│  orders_order    │
├──────────────────┤         ┌──────────────────┐
│ • id (PK)        │    1    │ orders_orderitem │
│ • user_id (FK)   │<────N───├──────────────────┤
│ • total_price    │         │ • id (PK)        │
│ • status         │         │ • order_id (FK)  │
│ • created_at     │         │ • product_id     │ (Historical)
└──────────────────┘         │ • product_name   │ (Snapshot)
                             │ • price          │ (At time of
                             │ • quantity       │  order)
                             └──────────────────┘

Status Flow: pending → preparing → on_the_way → delivered
            (or cancelled at any point)
```

### 🔐 Authentication & Authorization Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    AUTHENTICATION FLOW (JWT)                             │
└─────────────────────────────────────────────────────────────────────────┘

1️⃣ REGISTRATION
┌─────────┐                        ┌─────────┐                ┌──────────┐
│  Client │                        │   API   │                │    DB    │
└────┬────┘                        └────┬────┘                └────┬─────┘
     │                                  │                          │
     │ POST /api/v1/auth/register/      │                          │
     │ {username, email, password}      │                          │
     │─────────────────────────────────>│                          │
     │                                  │ Validate Password        │
     │                                  │ (Django Validators)      │
     │                                  │                          │
     │                                  │ Hash Password (PBKDF2)   │
     │                                  │                          │
     │                                  │ CREATE User              │
     │                                  │─────────────────────────>│
     │                                  │                          │
     │                                  │ User Created             │
     │                                  │<─────────────────────────┤
     │ 201 Created                      │                          │
     │ {id, username, email}            │                          │
     │<─────────────────────────────────│                          │
     │                                  │                          │

2️⃣ LOGIN & TOKEN GENERATION
     │                                  │                          │
     │ POST /api/v1/auth/login/         │                          │
     │ {username, password}             │                          │
     │─────────────────────────────────>│                          │
     │                                  │ Verify Credentials       │
     │                                  │─────────────────────────>│
     │                                  │                          │
     │                                  │ User Found & Verified    │
     │                                  │<─────────────────────────│
     │                                  │                          │
     │                                  │ Generate JWT Tokens:     │
     │                                  │ • Access (30 min)        │
     │                                  │ • Refresh (7 days)       │
     │                                  │                          │
     │ 200 OK                           │                          │
     │ {                                │                          │
     │   "access": "eyJ0eXAi...",       │                          │
     │   "refresh": "eyJ0eXAi..."       │                          │
     │ }                                │                          │
     │<─────────────────────────────────│                          │
     │                                  │                          │

3️⃣ AUTHENTICATED REQUESTS
     │                                  │                          │
     │ GET /api/v1/cart/                │                          │
     │ Authorization: Bearer <token>    │                          │
     │─────────────────────────────────>│                          │
     │                                  │ Verify JWT Signature     │
     │                                  │ Check Expiration         │
     │                                  │ Extract User ID          │
     │                                  │                          │
     │                                  │ Query User's Cart        │
     │                                  │─────────────────────────>│
     │                                  │ Cart Data                │
     │                                  │<─────────────────────────│
     │ 200 OK {cart_data}               │                          │
     │<─────────────────────────────────│                          │
     │                                  │                          │

4️⃣ TOKEN REFRESH (When Access Token Expires)
     │                                  │                          │
     │ POST /api/v1/auth/refresh/       │                          │
     │ {refresh: "eyJ0eXAi..."}         │                          │
     │─────────────────────────────────>│                          │
     │                                  │ Verify Refresh Token     │
     │                                  │ Check Expiration         │
     │                                  │                          │
     │                                  │ Generate New Access Token│
     │                                  │                          │
     │ 200 OK                           │                          │
     │ {access: "new_token"}            │                          │
     │<─────────────────────────────────│                          │
     │                                  │                          │
```

### 🛒 Shopping Cart Management Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      CART MANAGEMENT FLOW                                │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────┐          ┌─────────┐          ┌──────────┐          ┌─────────┐
│  Client │          │   API   │          │   Cart   │          │ Product │
└────┬────┘          └────┬────┘          └────┬─────┘          └────┬────┘
     │                    │                    │                     │
1️⃣   │ POST /cart/add/     │                    │                     │
     │ {product_id: 5,    │                    │                     │
     │  quantity: 2}      │                    │                     │
     │───────────────────>│                    │                     │
     │                    │ Authenticate User  │                     │
     │                    │                    │                     │
     │                    │ Verify Product ID  │                     │
     │                    │──────────────────────────────────────────>│
     │                    │ Product Details    │                     │
     │                    │<──────────────────────────────────────────│
     │                    │                    │                     │
     │                    │ Get/Create Cart    │                     │
     │                    │───────────────────>│                     │
     │                    │                    │                     │
     │                    │ Check if Product   │                     │
     │                    │ Already in Cart    │                     │
     │                    │───────────────────>│                     │
     │                    │                    │                     │
     │                    │ • If exists:       │                     │
     │                    │   Update quantity  │                     │
     │                    │ • If new:          │                     │
     │                    │   Create CartItem  │                     │
     │                    │───────────────────>│                     │
     │                    │                    │                     │
     │                    │ Calculate:         │                     │
     │                    │ • total_items      │                     │
     │                    │ • total_price      │                     │
     │                    │<───────────────────│                     │
     │ 200 OK             │                    │                     │
     │ {cart_details}     │                    │                     │
     │<───────────────────│                    │                     │
     │                    │                    │                     │
2️⃣   │ GET /cart/         │                    │                     │
     │───────────────────>│                    │                     │
     │                    │ Get User's Cart    │                     │
     │                    │───────────────────>│                     │
     │                    │ Cart + Items[]     │                     │
     │                    │<───────────────────│                     │
     │ 200 OK             │                    │                     │
     │ {                  │                    │                     │
     │   id, user,        │                    │                     │
     │   items: [...]     │                    │                     │
     │   total_items: 5,  │                    │                     │
     │   total_price: $45 │                    │                     │
     │ }                  │                    │                     │
     │<───────────────────│                    │                     │
     │                    │                    │                     │
3️⃣   │ DELETE /cart/item/3/                    │                     │
     │───────────────────>│                    │                     │
     │                    │ Verify Ownership   │                     │
     │                    │───────────────────>│                     │
     │                    │ Delete CartItem    │                     │
     │                    │───────────────────>│                     │
     │                    │ Recalculate Totals │                     │
     │                    │<───────────────────│                     │
     │ 204 No Content     │                    │                     │
     │<───────────────────│                    │                     │
     │                    │                    │                     │
```

### 📦 Order Lifecycle Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        ORDER LIFECYCLE                                   │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────┐      ┌─────────┐      ┌──────────┐      ┌──────────┐
│  Client │      │   API   │      │   Cart   │      │  Orders  │
└────┬────┘      └────┬────┘      └────┬─────┘      └────┬─────┘
     │                │                │                 │
1️⃣   │ POST /orders/create/            │                 │
     │───────────────>│                │                 │
     │                │ Get User Cart  │                 │
     │                │───────────────>│                 │
     │                │                │                 │
     │                │ Validate:      │                 │
     │                │ • Cart exists  │                 │
     │                │ • Has items    │                 │
     │                │ • Items valid  │                 │
     │                │<───────────────│                 │
     │                │                │                 │
     │                │ Create Order:              │
     │                │ • user_id                  │
     │                │ • total_price              │
     │                │ • status="pending"         │
     │                │───────────────────────────>│
     │                │                            │
     │                │ For each CartItem:         │
     │                │ Create OrderItem:          │
     │                │ • order_id                 │
     │                │ • product_id (snapshot)    │
     │                │ • product_name (snapshot)  │
     │                │ • price (at time)          │
     │                │ • quantity                 │
     │                │───────────────────────────>│
     │                │                            │
     │                │ Clear Cart                 │
     │                │───────────────>│           │
     │                │                │           │
     │ 201 Created    │                │           │
     │ {order_id,     │                │           │
     │  items: [...], │                │           │
     │  total,        │                │           │
     │  status}       │                │           │
     │<───────────────│                │           │
     │                │                │           │
     │                                             │
2️⃣   │ GET /orders/                                │
     │───────────────>│                            │
     │                │ Query User Orders          │
     │                │───────────────────────────>│
     │                │ (Paginated, Latest First)  │
     │                │<───────────────────────────│
     │ 200 OK         │                            │
     │ {results: [...],                            │
     │  count, next}  │                            │
     │<───────────────│                            │
     │                │                            │
3️⃣   │ GET /orders/42/ │                           │
     │───────────────>│                            │
     │                │ Get Order + OrderItems     │
     │                │───────────────────────────>│
     │                │ Verify Ownership           │
     │                │<───────────────────────────│
     │ 200 OK         │                            │
     │ {order details,│                            │
     │  items: [...]} │                            │
     │<───────────────│                            │
     │                │                            │

┌─────────────────────────────────────────────────────────────────────────┐
│                    ORDER STATUS WORKFLOW                                 │
└─────────────────────────────────────────────────────────────────────────┘

   ┌─────────┐       ┌───────────┐       ┌─────────────┐       ┌───────────┐
   │ PENDING │──────>│ PREPARING │──────>│ ON_THE_WAY  │──────>│ DELIVERED │
   └─────────┘       └───────────┘       └─────────────┘       └───────────┘
        │                   │                    │
        └───────────────────┴────────────────────┴──────────────┐
                                                                 │
                                                                 ▼
                                                         ┌─────────────┐
                                                         │  CANCELLED  │
                                                         └─────────────┘

Status Updates (Admin Only):
PATCH /orders/{id}/status/
{
  "status": "preparing" | "on_the_way" | "delivered" | "cancelled"
}
```

### 🌐 API Endpoints Map

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          API ENDPOINTS                                   │
│                      Base: /api/v1/                                      │
└─────────────────────────────────────────────────────────────────────────┘

🔐 AUTHENTICATION (/auth/)
├─ POST   /auth/register/          Create new user account
├─ POST   /auth/login/             Login & get JWT tokens
├─ POST   /auth/refresh/           Refresh access token
└─ GET    /profile/                Get user profile (🔒 Auth Required)

🍽️ MENU (/)
├─ GET    /categories/             List categories (✅ Public)
│                                  • Pagination: 20/page
│                                  • Filters: is_active=true
│
└─ GET    /products/               List products (✅ Public)
   ├─ Query: ?category_id=X        Filter by category
   ├─ Query: ?page=N               Pagination
   └─ GET  /products/{id}/         Product details

🛒 CART (/cart/)                    (🔒 Auth Required)
├─ GET    /                        Get current cart
│                                  • Returns: cart + items[] + totals
│
├─ POST   /add/                    Add item to cart
│         Body: {product_id, quantity}
│         • Auto-creates cart if needed
│         • Updates quantity if item exists
│
└─ DELETE /item/{item_id}/         Remove item from cart

📦 ORDERS (/orders/)                (🔒 Auth Required)
├─ POST   /create/                 Create order from cart
│                                  • Snapshots product data
│                                  • Clears cart after creation
│
├─ GET    /                        List user's orders
│                                  • Pagination: 20/page
│                                  • Ordered by: -created_at
│
├─ GET    /{id}/                   Get order details
│                                  • Includes: items, status, total
│
└─ PATCH  /{id}/status/            Update order status (👑 Admin Only)
          Body: {status}

📚 DOCUMENTATION
├─ GET    /api/schema/             OpenAPI 3.0 schema (JSON)
└─ GET    /api/docs/               Swagger UI (Interactive)

⚡ API FEATURES
├─ Pagination: 20 items per page on all list endpoints
├─ Rate Limiting: 100 requests/minute per authenticated user
├─ Authentication: JWT Bearer token in Authorization header
└─ Content-Type: application/json
```

### 🔄 Request/Response Patterns

```
┌─────────────────────────────────────────────────────────────────────────┐
│                   TYPICAL REQUEST/RESPONSE FLOWS                         │
└─────────────────────────────────────────────────────────────────────────┘

📥 STANDARD REQUEST
┌─────────────────────────────────────────────────────────────────┐
│ GET /api/v1/products/?page=1                                    │
│ Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...                 │
│ Content-Type: application/json                                  │
└─────────────────────────────────────────────────────────────────┘

📤 PAGINATED RESPONSE
┌─────────────────────────────────────────────────────────────────┐
│ {                                                               │
│   "count": 45,                                                  │
│   "next": "http://localhost:8000/api/v1/products/?page=2",      │
│   "previous": null,                                             │
│   "results": [                                                  │
│     {                                                           │
│       "id": 1,                                                  │
│       "name": "Burger",                                         │
│       "category": {...},                                        │
│       "price": "12.99",                                         │
│       ...                                                       │
│     },                                                          │
│     ...                                                         │
│   ]                                                             │
│ }                                                               │
└─────────────────────────────────────────────────────────────────┘

⚠️ ERROR RESPONSE (401 Unauthorized)
┌─────────────────────────────────────────────────────────────────┐
│ {                                                               │
│   "detail": "Authentication credentials were not provided."     │
│ }                                                               │
└─────────────────────────────────────────────────────────────────┘

⚠️ ERROR RESPONSE (429 Rate Limited)
┌─────────────────────────────────────────────────────────────────┐
│ {                                                               │
│   "detail": "Request was throttled. Expected available in 42s." │
│ }                                                               │
└─────────────────────────────────────────────────────────────────┘
```

## Development

### Project Settings
- **Debug Mode**: Currently enabled (for development)
- **Allowed Hosts**: `*` (configure for production)
- **Database**: SQLite (consider PostgreSQL for production)
- **Pagination**: Page size set to 20 items
- **Rate Limiting**: 100 requests per minute per authenticated user

### Adding New Features
1. Create Django app: `python manage.py startapp <app_name>`
2. Add to `INSTALLED_APPS` in `config/settings.py`
3. Create models, serializers, and views
4. Register URLs in app's `urls.py` and include in `config/urls.py`
5. Run migrations: `python manage.py makemigrations && python manage.py migrate`

### Testing
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test accounts
python manage.py test menu
python manage.py test cart
python manage.py test orders
```

## Future Enhancements

Potential areas for expansion:

- Payment gateway integration
- Real-time order tracking with WebSockets
- Email notifications
- Restaurant table reservation system
- Reviews and ratings
- Delivery address management
- Multiple restaurant support
- Analytics and reporting

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write/update tests
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For issues, questions, or contributions, please open an issue in the repository.

---

**Built with Django REST Framework** | **Python 3.13** | **API Version 1.0.0**
