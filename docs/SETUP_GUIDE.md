# Setup and Installation Guide

Complete guide to set up, configure, and deploy the Restaurant System API.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Development Setup](#development-setup)
- [Configuration](#configuration)
- [Database Setup](#database-setup)
- [Creating Sample Data](#creating-sample-data)
- [Running the Application](#running-the-application)
- [Testing](#testing)
- [Production Deployment](#production-deployment)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Software

| Software | Minimum Version | Purpose |
|----------|----------------|---------|
| Python | 3.13 | Programming language |
| pip | Latest | Package manager |
| Git | 2.0+ | Version control |
| SQLite | 3.0+ | Database (included with Python) |

### Optional Software (Production)

| Software | Purpose |
|----------|---------|
| PostgreSQL 15+ | Production database |
| Nginx | Reverse proxy |
| Gunicorn | WSGI server |
| Redis | Caching layer |
| Docker | Containerization |

### System Requirements

**Development:**
- OS: macOS, Linux, or Windows
- RAM: 2GB minimum
- Disk Space: 500MB

**Production:**
- OS: Linux (Ubuntu 22.04 LTS recommended)
- RAM: 4GB minimum
- Disk Space: 10GB minimum
- CPU: 2 cores minimum

## Development Setup

### 1. Clone the Repository

```bash
# Clone the repository
git clone <repository-url>
cd restaurant_system

# Or if starting from existing directory
cd restaurant_system
```

### 2. Create Virtual Environment

**macOS/Linux:**
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Verify activation (should show venv path)
which python
```

**Windows:**
```cmd
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Verify activation
where python
```

### 3. Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install Django and required packages
pip install django
pip install djangorestframework
pip install djangorestframework-simplejwt
pip install drf-spectacular

# Verify installations
pip list
```

**Expected output:**
```
Package                       Version
----------------------------- -------
Django                        6.0
djangorestframework           3.14.0
djangorestframework-simplejwt 5.3.0
drf-spectacular              0.27.0
```

### 4. Create requirements.txt (Optional)

```bash
# Generate requirements file
pip freeze > requirements.txt
```

**Sample requirements.txt:**
```
Django==6.0
djangorestframework==3.14.0
djangorestframework-simplejwt==5.3.0
drf-spectacular==0.27.0
```

**Install from requirements:**
```bash
pip install -r requirements.txt
```

## Configuration

### Environment Variables

Create a `.env` file in the project root (optional for development):

```bash
# .env
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (for production)
DB_NAME=restaurant_db
DB_USER=restaurant_user
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432

# JWT Settings
JWT_ACCESS_TOKEN_LIFETIME=30
JWT_REFRESH_TOKEN_LIFETIME=10080
```

### Django Settings Configuration

The main settings are in [config/settings.py](config/settings.py). Key configurations:

**Security (Development):**
```python
DEBUG = True
SECRET_KEY = 'your-secret-key'  # Change in production
ALLOWED_HOSTS = ['*']  # Restrict in production
```

**Database (Development):**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

**Installed Apps:**
```python
INSTALLED_APPS = [
    # Django defaults
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party
    'rest_framework',
    'rest_framework_simplejwt',
    'drf_spectacular',

    # Custom apps
    'accounts',
    'menu',
    'cart',
    'orders',
    'core',
]
```

**JWT Configuration:**
```python
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
}
```

## Database Setup

### 1. Run Migrations

```bash
# Create migration files (if needed)
python manage.py makemigrations

# Apply migrations to database
python manage.py migrate

# Expected output:
# Running migrations:
#   Applying contenttypes.0001_initial... OK
#   Applying auth.0001_initial... OK
#   Applying accounts.0001_initial... OK
#   Applying menu.0001_initial... OK
#   Applying cart.0001_initial... OK
#   Applying orders.0001_initial... OK
```

### 2. Create Superuser

```bash
# Create admin account
python manage.py createsuperuser

# You'll be prompted for:
# Username: admin
# Email: admin@example.com
# Password: ********
# Password (again): ********
```

### 3. Verify Database

```bash
# Check database structure
python manage.py dbshell

# Inside SQLite shell:
.tables
.schema menu_product
.exit
```

## Creating Sample Data

### Option 1: Django Admin Interface

1. Start the server:
   ```bash
   python manage.py runserver
   ```

2. Access admin panel:
   ```
   http://localhost:8000/admin/
   ```

3. Login with superuser credentials

4. Create data:
   - Add Categories (Appetizers, Main Courses, Desserts, Beverages)
   - Add Products for each category
   - View created data

### Option 2: Django Shell

```bash
python manage.py shell
```

```python
from menu.models import Category, Product

# Create categories
appetizers = Category.objects.create(
    name="Appetizers",
    image_url="https://example.com/appetizers.jpg",
    is_active=True
)

main_courses = Category.objects.create(
    name="Main Courses",
    image_url="https://example.com/main.jpg",
    is_active=True
)

desserts = Category.objects.create(
    name="Desserts",
    image_url="https://example.com/desserts.jpg",
    is_active=True
)

# Create products
Product.objects.create(
    category=appetizers,
    name="Caesar Salad",
    description="Fresh romaine lettuce with Caesar dressing",
    price=8.99,
    image_url="https://example.com/salad.jpg",
    is_available=True
)

Product.objects.create(
    category=main_courses,
    name="Margherita Pizza",
    description="Classic pizza with tomato sauce and mozzarella",
    price=12.99,
    image_url="https://example.com/pizza.jpg",
    is_available=True
)

Product.objects.create(
    category=desserts,
    name="Tiramisu",
    description="Italian coffee-flavored dessert",
    price=6.99,
    image_url="https://example.com/tiramisu.jpg",
    is_available=True
)

# Verify
print(f"Categories: {Category.objects.count()}")
print(f"Products: {Product.objects.count()}")

# Exit shell
exit()
```

### Option 3: Management Command (Create Custom)

Create `menu/management/commands/load_sample_data.py`:

```python
from django.core.management.base import BaseCommand
from menu.models import Category, Product

class Command(BaseCommand):
    help = 'Load sample data into database'

    def handle(self, *args, **kwargs):
        # Clear existing data
        Category.objects.all().delete()

        # Create categories
        categories_data = [
            {"name": "Appetizers", "image_url": "https://example.com/appetizers.jpg"},
            {"name": "Main Courses", "image_url": "https://example.com/main.jpg"},
            {"name": "Desserts", "image_url": "https://example.com/desserts.jpg"},
            {"name": "Beverages", "image_url": "https://example.com/beverages.jpg"},
        ]

        for cat_data in categories_data:
            Category.objects.create(**cat_data, is_active=True)

        self.stdout.write(self.style.SUCCESS('Sample data loaded successfully!'))
```

Run it:
```bash
python manage.py load_sample_data
```

## Running the Application

### Development Server

```bash
# Start development server
python manage.py runserver

# Start on specific port
python manage.py runserver 8080

# Start on specific host
python manage.py runserver 0.0.0.0:8000
```

**Access points:**
- API Base: http://localhost:8000/api/v1/
- Swagger UI: http://localhost:8000/api/docs/
- Admin Panel: http://localhost:8000/admin/
- OpenAPI Schema: http://localhost:8000/api/schema/

### Useful Development Commands

```bash
# Check for issues
python manage.py check

# Run Django shell
python manage.py shell

# Show migrations
python manage.py showmigrations

# Create new app
python manage.py startapp app_name

# Collect static files
python manage.py collectstatic
```

## Testing

### Manual API Testing

**Using cURL:**

```bash
# Test registration
curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123",
    "password2": "testpass123"
  }'

# Test login
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123"
  }'

# Save the access token from response
export TOKEN="your_access_token_here"

# Test authenticated endpoint
curl http://localhost:8000/api/v1/cart/ \
  -H "Authorization: Bearer $TOKEN"
```

**Using Swagger UI:**

1. Navigate to http://localhost:8000/api/docs/ (endpoints grouped by tags: Accounts, Menu, Cart, Orders).
2. Click "Authorize" and enter `Bearer <your_access_token>` (JWT). If you install `djangorestframework-api-key`, you can also authorize with an API key for the read-only Menu endpoints.
3. Expand an endpoint to see the built-in request/response examples and documented status codes.
4. Execute requests directly from the UI.

### Automated Testing

Create test files (example: `menu/tests.py`):

```python
from django.test import TestCase
from rest_framework.test import APIClient
from menu.models import Category, Product

class MenuAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.category = Category.objects.create(
            name="Test Category",
            is_active=True
        )

    def test_list_categories(self):
        response = self.client.get('/api/v1/categories/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_create_product(self):
        product = Product.objects.create(
            category=self.category,
            name="Test Product",
            price=9.99,
            is_available=True
        )
        self.assertEqual(product.name, "Test Product")
```

**Run tests:**
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test menu

# Run with verbosity
python manage.py test --verbosity=2

# Keep test database
python manage.py test --keepdb
```

## Production Deployment

### 1. Update Settings for Production

Create `config/settings_prod.py`:

```python
from .settings import *

DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']

# Use environment variables
import os
SECRET_KEY = os.environ.get('SECRET_KEY')

# PostgreSQL Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# Security Settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Static files
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'
```

### 2. Install Production Dependencies

```bash
pip install gunicorn psycopg2-binary python-decouple
```

### 3. Configure Gunicorn

Create `gunicorn_config.py`:

```python
bind = "0.0.0.0:8000"
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
errorlog = "/var/log/gunicorn/error.log"
accesslog = "/var/log/gunicorn/access.log"
loglevel = "info"
```

### 4. Setup Nginx

Create `/etc/nginx/sites-available/restaurant_system`:

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location = /favicon.ico { access_log off; log_not_found off; }

    location /static/ {
        alias /path/to/restaurant_system/staticfiles/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/restaurant_system /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 5. Setup Systemd Service

Create `/etc/systemd/system/restaurant_system.service`:

```ini
[Unit]
Description=Restaurant System Gunicorn
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/restaurant_system
Environment="PATH=/path/to/restaurant_system/venv/bin"
ExecStart=/path/to/restaurant_system/venv/bin/gunicorn \
          --config gunicorn_config.py \
          config.wsgi:application

[Install]
WantedBy=multi-user.target
```

Start service:
```bash
sudo systemctl start restaurant_system
sudo systemctl enable restaurant_system
sudo systemctl status restaurant_system
```

### 6. SSL with Let's Encrypt

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal
sudo systemctl status certbot.timer
```

### 7. Database Migration (Production)

```bash
# Backup existing data
python manage.py dumpdata > backup.json

# Run migrations
python manage.py migrate --settings=config.settings_prod

# Collect static files
python manage.py collectstatic --settings=config.settings_prod

# Create superuser
python manage.py createsuperuser --settings=config.settings_prod
```

## Docker Deployment (Optional)

### Dockerfile

```dockerfile
FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "--config", "gunicorn_config.py", "config.wsgi:application"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: restaurant_db
      POSTGRES_USER: restaurant_user
      POSTGRES_PASSWORD: your_password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  web:
    build: .
    command: gunicorn config.wsgi:application --bind 0.0.0.0:8000
    volumes:
      - .:/app
      - static_volume:/app/staticfiles
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
      - SECRET_KEY=your-secret-key
      - DB_NAME=restaurant_db
      - DB_USER=restaurant_user
      - DB_PASSWORD=your_password
      - DB_HOST=db
      - DB_PORT=5432
    depends_on:
      - db

  nginx:
    image: nginx:latest
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - static_volume:/app/staticfiles
    ports:
      - "80:80"
    depends_on:
      - web

volumes:
  postgres_data:
  static_volume:
```

**Run with Docker:**
```bash
docker-compose up -d
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

## Troubleshooting

### Common Issues

#### 1. Module Not Found Error

**Error:**
```
ModuleNotFoundError: No module named 'rest_framework'
```

**Solution:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Install missing package
pip install djangorestframework
```

#### 2. Database Migration Issues

**Error:**
```
django.db.utils.OperationalError: no such table: menu_product
```

**Solution:**
```bash
# Delete database and migrations
rm db.sqlite3
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete

# Recreate
python manage.py makemigrations
python manage.py migrate
```

#### 3. Port Already in Use

**Error:**
```
Error: That port is already in use.
```

**Solution:**
```bash
# Find process using port 8000
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill process
kill -9 <PID>  # macOS/Linux
taskkill /PID <PID> /F  # Windows

# Or use different port
python manage.py runserver 8080
```

#### 4. CORS Issues

**Error:**
```
Access to XMLHttpRequest blocked by CORS policy
```

**Solution:**
```bash
# Install django-cors-headers
pip install django-cors-headers
```

Add to `settings.py`:
```python
INSTALLED_APPS = [
    ...
    'corsheaders',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    ...
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8080",
]
```

#### 5. Static Files Not Loading

**Solution:**
```bash
# Collect static files
python manage.py collectstatic

# Check STATIC_URL in settings.py
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
```

### Debug Mode

Enable detailed error messages:

```python
# settings.py
DEBUG = True
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
}
```

### Check System

```bash
# Django system check
python manage.py check

# Check specific deployment settings
python manage.py check --deploy

# Show installed packages
pip list

# Show Django version
python -m django --version
```

## Monitoring and Maintenance

### Log Files

```bash
# Application logs
tail -f /var/log/gunicorn/error.log
tail -f /var/log/gunicorn/access.log

# Nginx logs
tail -f /var/log/nginx/error.log
tail -f /var/log/nginx/access.log
```

### Database Backup

```bash
# SQLite backup
sqlite3 db.sqlite3 ".backup backup_$(date +%Y%m%d).db"

# PostgreSQL backup
pg_dump restaurant_db > backup_$(date +%Y%m%d).sql
```

### Performance Monitoring

Consider using:
- Django Debug Toolbar (development)
- Sentry (error tracking)
- New Relic (APM)
- Prometheus + Grafana (metrics)

---

**Setup Guide Version:** 1.0 | **Last Updated:** January 2025

For additional help, refer to:
- [README.md](README.md) - Project overview
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture
- [API_DOCUMENTATION.md](API_DOCUMENTATION.md) - API reference
- [DATABASE_SCHEMA.md](DATABASE_SCHEMA.md) - Database structure
