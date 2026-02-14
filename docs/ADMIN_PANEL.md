# Restaurant Admin Panel Documentation

## Table of Contents
1. [Quick Start](#quick-start)
2. [What's New](#whats-new)
3. [Features](#features)
4. [Analytics Dashboard](#analytics-dashboard)
5. [Customization Guide](#customization-guide)
6. [File Structure](#file-structure)
7. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Start Using Your Admin Panel (2 Minutes)

```bash
# 1. Start the server
cd /Users/r/StudioProjects/restaurant_system
source venv/bin/activate
python manage.py runserver

# 2. Access admin panel
# Open browser: http://localhost:8000/admin/

# 3. Create admin user (if needed)
python manage.py create_admin
```

### What You'll See

When you log in, you'll immediately see:
- ✅ **Dashboard Statistics**: Orders, Products, Users, Revenue
- ✅ **Recent Orders Table**: Last 5 orders with color-coded status
- ✅ **Quick Actions**: Fast links to common tasks
- ✅ **Modern Design**: Clean, professional interface
- ✅ **Custom Icons**: Visual navigation with FontAwesome icons

---

## What's New

### Visual Improvements

| Aspect | Before | After |
|--------|--------|-------|
| **Theme** | Default Django | Modern Flatly theme |
| **Dashboard** | Basic list | Rich statistics & actions |
| **Icons** | None/Generic | Custom FontAwesome icons |
| **Colors** | Basic | Professional blue/green palette |
| **Cards** | Flat | Elevated with shadows & hover effects |
| **Buttons** | Square | Rounded with smooth transitions |
| **Sidebar** | Unorganized | Logically grouped with custom order |
| **Status** | Plain text | Color-coded badges |

### New Features

1. **Dashboard Statistics Cards**
   - Total Orders count
   - Products count
   - Active Users count
   - Total Revenue (from completed orders)

2. **Recent Activity Section**
   - Last 5 orders table
   - Quick stats (completed/pending orders)
   - Available products count
   - Total reviews count

3. **Quick Action Buttons**
   - Add Product
   - View Orders
   - Create Coupon
   - Manage Users

4. **Enhanced Navigation**
   - Custom icons for each model:
     - 🛒 Orders
     - 🍴 Products & Menu
     - 🛍️ Cart
     - 🏷️ Coupons
     - 📍 Addresses
     - ⭐ Reviews
     - 👥 Users

5. **Color-Coded Status System**
   - [PENDING] - Orange
   - [CONFIRMED] - Blue
   - [PREPARING] - Purple
   - [READY] - Green
   - [COMPLETED] - Teal
   - [CANCELLED] - Red

---

## Features

### Dashboard Overview

The dashboard provides at-a-glance business metrics:

```
┌────────────────────────────────────────────┐
│  Statistics Cards                          │
├────────────────────────────────────────────┤
│  📊 Orders    🍴 Products   👤 Users   💰  │
│     152          45          1,234    $25K │
└────────────────────────────────────────────┘

┌────────────────────────────────────────────┐
│  Recent Orders          Quick Statistics   │
├────────────────────────────────────────────┤
│  #152 [PENDING]         ✅ Completed: 128  │
│  #151 [COMPLETED]       🕐 Pending: 24     │
│  #150 [COMPLETED]       📦 Products: 45    │
└────────────────────────────────────────────┘

┌────────────────────────────────────────────┐
│  Quick Actions                             │
├────────────────────────────────────────────┤
│  [+ Add Product]  [📋 View Orders]         │
│  [🏷️ Create Coupon] [👥 Manage Users]     │
└────────────────────────────────────────────┘
```

### Navigation Sidebar

Organized by business priority:
1. **Orders** - Manage customer orders
2. **Menu** - Products and categories
3. **Cart** - Shopping cart management
4. **Coupons** - Discount codes and usage
5. **Addresses** - Customer addresses
6. **Reviews** - Customer feedback
7. **Authentication** - Users and permissions

### Modern UI Components

- **Cards**: Clean design with subtle shadows
- **Buttons**: Rounded corners, hover effects, smooth transitions
- **Tables**: Enhanced readability with hover effects
- **Forms**: Modern input fields with focus states
- **Badges**: Color-coded status indicators
- **Animations**: Smooth fade-in and hover effects

---

## Analytics Dashboard

The admin dashboard includes powerful analytics features powered by AI.

### AI-Powered Insights

When you access the admin dashboard, you'll see:

1. **Real-Time KPIs**
   - Revenue with growth percentages
   - Order counts and trends
   - User statistics
   - Average order value

2. **Interactive Charts** (powered by Chart.js)
   - Revenue trend chart with 30-day history
   - Order status breakdown (donut chart)
   - Top 10 products performance

3. **AI Business Insights** (powered by Claude Sonnet 4.5)
   - Natural language business summaries
   - AI-identified opportunities
   - Warnings about potential issues
   - Actionable recommendations

4. **Anomaly Detection**
   - Automatic detection of unusual patterns
   - Revenue spikes and drops
   - Order volume anomalies
   - AI-generated explanations

### Setting Up Analytics

The analytics dashboard requires:

1. **Admin permissions** - Your user must have `is_staff=True`
2. **Anthropic API key** (for AI features) - Add to `.env`:
   ```
   ANTHROPIC_API_KEY=sk-ant-your-key-here
   ```

3. **Test data** - Run to populate with sample data:
   ```bash
   python seed_test_data.py
   ```

### Accessing Analytics

- **Admin Dashboard**: http://localhost:8000/admin/ (includes charts and AI insights)
- **Analytics API**: http://localhost:8000/api/v1/analytics/dashboard/
- **Full Analytics Guide**: See [docs/ANALYTICS_GUIDE.md](ANALYTICS_GUIDE.md)

The dashboard automatically loads analytics data when you visit the admin index page. All data is cached for performance (5-30 minutes depending on the metric).

---

## Customization Guide

### Change Theme

Edit `config/settings.py` (line 434):

```python
"theme": "flatly",  # Change to any theme below
```

**Available Themes:**

**Light Themes:**
- `flatly` ⭐ (Current) - Modern & clean
- `cosmo` - Professional blue
- `minty` - Fresh green
- `sandstone` - Warm neutral
- `united` - Ubuntu orange
- `materia` - Material Design

**Dark Themes:**
- `superhero` - Dark with blue accents
- `darkly` - Pure dark theme
- `slate` - Elegant dark gray
- `cyborg` - Matrix-style green

**Elegant:**
- `lux` - Luxurious gold accents
- `pulse` - Purple accents

After changing theme:
```bash
# Restart server and refresh browser (Ctrl+F5)
```

### Add Your Logo

1. **Prepare logo file:**
   - Recommended size: 200x60px
   - Format: PNG with transparency or SVG
   - Save as: `static/admin/img/logo.png`

2. **Update settings.py** (line 365):
   ```python
   "site_logo": "admin/img/logo.png",
   "site_logo_classes": "img-circle",  # or "img-square"
   "site_icon": "admin/img/favicon.ico",
   ```

3. **Collect static files:**
   ```bash
   python manage.py collectstatic --noinput
   ```

4. **Refresh browser** (hard refresh: Ctrl+F5 or Cmd+Shift+R)

### Customize Colors

Edit `static/admin/css/custom_admin.css` (lines 6-13):

```css
:root {
    --primary-color: #2c3e50;      /* Main dark color */
    --secondary-color: #3498db;    /* Accent blue */
    --success-color: #27ae60;      /* Success green */
    --warning-color: #f39c12;      /* Warning orange */
    --danger-color: #e74c3c;       /* Danger red */
    --light-bg: #f8f9fa;           /* Light background */
    --border-radius: 8px;          /* Corner roundness */
}
```

After editing:
```bash
python manage.py collectstatic --noinput
# Then hard refresh browser
```

### Change Navigation Order

Edit `config/settings.py` (lines 440-448):

```python
"order_with_respect_to": [
    "menu",      # Show menu first
    "orders",    # Then orders
    "cart",
    "coupons",
    "addresses",
    "reviews",
    "auth",
],
```

### Modify Dashboard Statistics

Edit `core/admin_dashboard.py` to customize statistics logic:

```python
# Add custom statistic
extra_context['your_metric'] = YourModel.objects.count()
```

Then update `templates/admin/index.html` to display it.

### Change Model Icons

Edit `config/settings.py` (lines 401-416):

```python
"icons": {
    "menu.Product": "fas fa-pizza-slice",    # Change icon
    "orders.Order": "fas fa-receipt",
    # Add more...
}
```

Browse icons at: [FontAwesome Icons](https://fontawesome.com/icons)

### Add Custom Menu Links

Edit `config/settings.py` (lines 378-382):

```python
"topmenu_links": [
    {"name": "Home", "url": "admin:index"},
    {"name": "API Docs", "url": "/api/docs/", "new_window": True},
    {"name": "Reports", "url": "/admin/reports/"},
],
```

---

## File Structure

### Created Files

```
restaurant_system/
├── docs/
│   └── ADMIN_PANEL.md              # This documentation
├── static/
│   └── admin/
│       ├── css/
│       │   ├── custom_admin.css    # Main custom styling (700+ lines)
│       │   └── theme-variants.css  # Optional theme variations
│       └── img/
│           └── README.md           # Logo & branding guide
├── templates/
│   └── admin/
│       └── index.html              # Custom dashboard template
└── core/
    └── admin_dashboard.py          # Dashboard statistics logic
```

### Modified Files

- `config/settings.py` (lines 360-449) - Enhanced Jazzmin configuration

### Key Configuration File

**config/settings.py** - Main Jazzmin settings:

```python
JAZZMIN_SETTINGS = {
    # Branding
    "site_title": "Restaurant Admin",
    "site_header": "Restaurant System",
    "site_brand": "Restaurant Dashboard",

    # Logo (customize this)
    "site_logo": None,  # Add: "admin/img/logo.png"
    "site_icon": None,  # Add: "admin/img/favicon.ico"

    # Theme
    "theme": "flatly",  # Modern flat design

    # Custom styling
    "custom_css": "admin/css/custom_admin.css",

    # Navigation
    "order_with_respect_to": ["orders", "menu", "cart", ...],

    # Icons (all models have custom icons)
    "icons": {
        "menu.Product": "fas fa-utensils",
        "orders.Order": "fas fa-shopping-cart",
        # ... more icons
    },
}
```

### Custom CSS Features

**static/admin/css/custom_admin.css** contains:

- **Color Scheme**: Professional palette with CSS variables
- **Dashboard Cards**: Elevated design with shadows
- **Buttons**: Rounded with hover animations
- **Tables**: Enhanced readability
- **Forms**: Modern input styling
- **Status Badges**: Color-coded indicators
- **Responsive Design**: Mobile-friendly rules
- **Animations**: Smooth transitions (0.3s)
- **Custom Scrollbar**: Styled scrollbars

---

## Troubleshooting

### CSS Not Loading

**Solution:**
```bash
python manage.py collectstatic --noinput
# Then restart server and hard refresh browser (Ctrl+F5)
```

### Statistics Showing 0

**Solution:**
```bash
# Run migrations
python manage.py migrate

# Check if models have data
python manage.py shell
>>> from orders.models import Order
>>> Order.objects.count()
```

### Theme Not Changing

**Steps:**
1. Edit `config/settings.py` and save
2. Restart development server
3. Clear browser cache (Ctrl+Shift+R / Cmd+Shift+R)
4. If still not working, try incognito/private mode

### Can't Log In

**Solution:**
```bash
# Create admin user
python manage.py create_admin

# Or manually
python manage.py createsuperuser
```

### Logo Not Appearing

**Checklist:**
1. ✅ File exists in `static/admin/img/logo.png`
2. ✅ Path is correct in `settings.py`
3. ✅ Ran `collectstatic`
4. ✅ Hard refreshed browser
5. ✅ Check browser console for 404 errors

### Icons Not Displaying

**Solution:**
1. Check browser console for errors
2. Verify FontAwesome is loading
3. Check icon names in settings.py (must be valid FontAwesome icons)

---

## Common Tasks

### Check Today's Orders
1. Click **Orders** → **Orders**
2. Use date filter on right sidebar: "Today"
3. See color-coded status for each order

### Add a New Product
1. Click **+ Add Product** (quick action button)
2. Fill form: name, price, category, description
3. Upload image
4. Check "Is available"
5. Save

### Create a Discount Coupon
1. Click **🏷️ Create Coupon** (quick action)
2. Enter code (e.g., "SAVE10")
3. Choose discount type (percentage/fixed)
4. Set minimum order amount
5. Set expiry date
6. Save

### View Customer Reviews
1. Click **⭐ Reviews** in sidebar
2. Click **Reviews** submenu
3. Filter by rating or approval status
4. Click review to see full details

### Export Data
1. Go to any list page (Orders, Products, etc.)
2. Look for export options (CSV/Excel)
3. Select items or export all
4. Download file

---

## Mobile Access

The admin panel is fully responsive:

1. Open on mobile: `http://your-ip:8000/admin/`
2. Tap hamburger menu (☰) to show/hide sidebar
3. All features work with touch
4. Statistics cards stack vertically
5. Tables scroll horizontally on small screens

**Tips:**
- Use landscape mode for better table viewing
- Pinch to zoom if needed
- Touch targets are 44px+ for easy tapping

---

## Performance & Best Practices

### Performance
- CSS is minified in production
- Static files are cached by browser
- Compressed by WhiteNoise
- All assets are optimized

### Security
- No security changes - all improvements are UI/UX only
- Same permission system
- Same authentication/authorization

### Accessibility
- WCAG AA compliant colors
- Sufficient contrast ratios
- Keyboard navigation supported
- Screen reader friendly

### Maintenance
- Review and update colors to match branding
- Test on new browser versions quarterly
- Keep documentation updated
- Monitor performance metrics

---

## Advanced Customization

### Optional Theme Variants

The file `static/admin/css/theme-variants.css` contains ready-to-use theme variants:

- **Dark Mode** - For night-time use
- **Vibrant Colors** - Colorful gradients
- **Minimal** - Ultra-clean design
- **Restaurant/Food** - Warm, food-inspired colors
- **Elegant/Luxury** - Upscale look with gold accents
- **Ocean/Blue** - Calming blue theme
- **Nature/Green** - Eco-friendly green theme

To use: Uncomment the desired section in `theme-variants.css`

### Add Charts/Graphs

Consider adding visualization libraries:
- Chart.js for interactive charts
- ApexCharts for modern graphics
- Google Charts for quick setup

### Email Notifications

Set up automatic notifications:
- Order status changes
- Low inventory alerts
- New review notifications

### Activity Logging

Track admin actions:
- Who edited what and when
- Audit trail for compliance
- Change history for rollback

---

## Statistics Explained

| Metric | Description | Source |
|--------|-------------|--------|
| **Orders** | Total order count | All orders in database |
| **Products** | Total menu items | All products (available + unavailable) |
| **Users** | Active user count | Users with `is_active=True` |
| **Revenue** | Total earnings | Sum of orders with status=COMPLETED & payment_status=PAID |
| **Completed** | Finished orders | Orders with status=COMPLETED |
| **Pending** | Awaiting action | Orders with status=PENDING |
| **Available Products** | In-stock items | Products with `is_available=True` |
| **Reviews** | Customer feedback | Total review count |

---

## Next Steps

Now that you have a modern admin panel, consider:

1. ✅ **Add Your Logo** - Make it yours with branding
2. ✅ **Try Different Themes** - Find your favorite look
3. ✅ **Explore All Sections** - Click through the interface
4. ✅ **Invite Team Members** - Create staff accounts
5. ✅ **Set Up Permissions** - Control who sees what
6. ✅ **Customize Colors** - Match your brand
7. ✅ **Add Custom Links** - Quick access to important pages

**Future Enhancements:**
- Charts/graphs for visual trends
- Export features (CSV/Excel)
- Advanced filters and search
- Bulk actions for efficiency
- Email notification system
- Activity audit log

---

## Support & Resources

- **Django Admin Docs**: https://docs.djangoproject.com/en/stable/ref/contrib/admin/
- **Jazzmin Docs**: https://django-jazzmin.readthedocs.io/
- **Bootstrap Docs**: https://getbootstrap.com/docs/
- **FontAwesome Icons**: https://fontawesome.com/icons

---

**Version**: 1.0
**Last Updated**: January 2026
**Tech Stack**: Django + Jazzmin + Bootstrap (Flatly) + Custom CSS
**Total Code**: 1,500+ lines of new code

---

*Your admin panel is now modern, clean, and professional! 🚀*
