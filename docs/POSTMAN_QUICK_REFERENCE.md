# Postman Quick Reference

## 🚀 Quick Start (5 Steps)

1. **Import Files**
   - Import `postman/Restaurant_API.postman_collection.json`
   - Import `postman/Restaurant_API.postman_environment.json`
   - Select "Restaurant API - Local" environment

2. **Start Server**
   ```bash
   python manage.py runserver
   ```

3. **Register & Login**
   - Run: `Authentication > Register User`
   - Run: `Authentication > Login` (tokens auto-saved ✓)

4. **Test API**
   - Browse menu, add to cart, create orders
   - Tokens automatically included in requests

5. **View Results**
   - Check response bodies
   - Variables auto-update after each request

## 📋 Request Execution Order

```
1. Register User
2. Login (saves tokens)
3. List Categories (saves category_id)
4. List Products (saves product_id)
5. Add Item to Cart (saves cart_item_id)
6. Get Cart
7. Create Order (saves order_id)
8. List My Orders
9. Update Order Status
```

## 🔑 Authentication

### Get Tokens
```
POST /auth/login
Body: {"username": "testuser", "password": "SecurePass123!"}
```

### Auto-saved to Environment
- `{{access_token}}` - Expires in 30 min
- `{{refresh_token}}` - Expires in 7 days

### Refresh When Expired
```
POST /auth/refresh
Body: {"refresh": "{{refresh_token}}"}
```

## 📦 Complete User Flow

### 1️⃣ Authentication
```
Register → Login → Get Profile
```

### 2️⃣ Browse Menu
```
List Categories → List Products → Get Product Details
```

### 3️⃣ Shopping
```
Add to Cart → Add More Items → Get Cart
```

### 4️⃣ Checkout
```
Create Order → List Orders → Get Order Details
```

### 5️⃣ Admin
```
Update Order Status (pending → preparing → on_the_way → delivered)
```

## 🎯 Common Requests

### Add Product to Cart
```json
POST /cart/add/
{
    "product_id": 1,
    "quantity": 2
}
```

### Create Order
```json
POST /orders/create/
{}
```

### Update Order Status
```json
PATCH /orders/{id}/status/
{
    "status": "preparing"
}
```

Valid statuses: `pending`, `preparing`, `on_the_way`, `delivered`, `cancelled`

## 🔧 Environment Variables

| Variable | Usage | Example |
|----------|-------|---------|
| `{{base_url}}` | API base URL | `http://localhost:8000/api/v1` |
| `{{access_token}}` | Auth header | Auto in Bearer token |
| `{{product_id}}` | Product endpoint | `/products/{{product_id}}/` |
| `{{order_id}}` | Order endpoint | `/orders/{{order_id}}/` |

## ⚡ Pro Tips

- ✅ Environment dropdown must show "Restaurant API - Local"
- ✅ Run requests in order (top to bottom) for best results
- ✅ Variables auto-save after successful responses
- ✅ Check "Tests" tab to see auto-save scripts
- ✅ Use Collection Runner to test all endpoints at once

## 🐛 Troubleshooting

| Error | Solution |
|-------|----------|
| "Authorization header missing" | Run Login first |
| "Token expired" | Run Refresh Token |
| "Cart is empty" | Add items to cart first |
| "Product not found" | Create products in Django admin |
| Server not responding | Start Django server |

## 📚 Resources

- **Swagger UI**: http://localhost:8000/api/docs/
- **Admin Panel**: http://localhost:8000/admin/
- **Full Guide**: [POSTMAN_GUIDE.md](POSTMAN_GUIDE.md)
- **API Docs**: [API_DOCUMENTATION.md](API_DOCUMENTATION.md)

## 🎨 Sample Request Body Templates

### Register
```json
{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "SecurePass123!",
    "password2": "SecurePass123!",
    "first_name": "John",
    "last_name": "Doe"
}
```

### Login
```json
{
    "username": "john_doe",
    "password": "SecurePass123!"
}
```

### Add to Cart
```json
{
    "product_id": 5,
    "quantity": 3
}
```

### Update Order
```json
{
    "status": "on_the_way"
}
```

---

**Need Help?** Check [POSTMAN_GUIDE.md](POSTMAN_GUIDE.md) for detailed instructions
