# Reviews & Ratings Module

## Overview

A complete reviews and ratings system for the restaurant delivery API, following clean architecture principles and SOLID design patterns.

## Features

### Core Functionality
- ⭐ **Product Reviews**: Users can rate products 1-5 stars with optional comments
- 🔒 **One Review Per Product**: Users can only review each product once
- ✏️ **Edit Window**: Reviews can be edited within 7 days of creation
- ✅ **Verified Purchase Badge**: Automatically marked if linked to an order
- 👍 **Helpfulness Voting**: Users can mark reviews as helpful/not helpful
- 🛡️ **Moderation**: Admin can approve/reject reviews with moderation notes

### Business Rules
1. Users must be authenticated to create reviews
2. One review per user per product (enforced at database level)
3. Reviews can be edited within 7 days of creation
4. Users cannot vote on their own reviews
5. Users can only vote once per review
6. All reviews are auto-approved by default (can be changed)

## Architecture

### Models

#### `Review`
- **Purpose**: Store customer reviews for products
- **Key Fields**:
  - `user`: Foreign key to User
  - `product_id`: ID of reviewed product
  - `order_id`: Optional link to purchase order
  - `rating`: 1-5 stars
  - `comment`: Optional text review
  - `is_verified_purchase`: Auto-set if order_id provided
  - `is_approved`: Moderation status
  - `moderation_note`: Internal admin notes

- **Constraints**:
  - Unique together: (user, product_id)
  - Rating validators: MinValueValidator(1), MaxValueValidator(5)

- **Indexes**:
  - (product_id, -created_at)
  - (user, -created_at)
  - (is_approved, -created_at)

#### `ReviewHelpfulness`
- **Purpose**: Track helpful/not helpful votes
- **Key Fields**:
  - `review`: Foreign key to Review
  - `user`: Foreign key to User
  - `is_helpful`: Boolean (True=helpful, False=not helpful)

- **Constraints**:
  - Unique together: (review, user)

### Serializers

#### `ReviewSerializer`
- **Purpose**: List and retrieve reviews
- **Features**:
  - Displays username (not full user object)
  - Calculates helpful/not helpful counts
  - Shows if user can edit (within 7 days)
  - Includes rating display text

#### `ReviewCreateSerializer`
- **Purpose**: Create new reviews
- **Validation**:
  - Rating must be 1-5
  - Comment min 10 chars, max 1000 chars
  - Prevents duplicate reviews
  - Auto-sets user from request

#### `ReviewUpdateSerializer`
- **Purpose**: Update existing reviews
- **Validation**:
  - Same as create
  - Enforces 7-day edit window

#### `ReviewHelpfulnessSerializer`
- **Purpose**: Vote on review helpfulness
- **Validation**:
  - Prevents voting on own reviews
  - Prevents duplicate votes

#### `ProductRatingStatsSerializer`
- **Purpose**: Aggregate rating statistics
- **Returns**:
  - Average rating (rounded to 2 decimals)
  - Total review count
  - Rating distribution (5★ to 1★)

### Views

All views follow REST principles and include OpenAPI documentation.

#### `ReviewListAPIView` (Public)
- **Endpoint**: `GET /api/v1/reviews/?product_id={id}`
- **Purpose**: List all approved reviews for a product
- **Filters**:
  - `product_id` (required)
  - `rating` (optional, 1-5)
- **Permissions**: Public (no authentication)
- **Optimizations**: select_related("user"), prefetch_related("helpfulness_votes")

#### `ReviewCreateAPIView` (Authenticated)
- **Endpoint**: `POST /api/v1/reviews/create/`
- **Purpose**: Create a new review
- **Permissions**: IsAuthenticatedJWT
- **Returns**: Full review details with ReviewSerializer

#### `ReviewDetailAPIView` (Owner Only)
- **Endpoint**: `GET/PATCH/DELETE /api/v1/reviews/{id}/`
- **Purpose**: Retrieve, update, or delete user's own review
- **Permissions**: IsAuthenticatedJWT + owner check
- **Edit Restriction**: Can only update within 7 days

#### `MyReviewsAPIView` (Authenticated)
- **Endpoint**: `GET /api/v1/reviews/my/`
- **Purpose**: List all reviews by authenticated user
- **Permissions**: IsAuthenticatedJWT

#### `ProductRatingStatsAPIView` (Public)
- **Endpoint**: `GET /api/v1/products/{product_id}/ratings/`
- **Purpose**: Get aggregate rating statistics
- **Permissions**: Public
- **Returns**: Average rating, total count, distribution

#### `ReviewHelpfulnessAPIView` (Authenticated)
- **Endpoint**: `POST /api/v1/reviews/helpful/`
- **Purpose**: Vote on review helpfulness
- **Permissions**: IsAuthenticatedJWT
- **Payload**: `{review_id: int, is_helpful: bool}`

## API Endpoints

### Review CRUD
```
GET    /api/v1/reviews/?product_id={id}&rating={1-5}   # List reviews
POST   /api/v1/reviews/create/                         # Create review
GET    /api/v1/reviews/{id}/                           # Get review
PATCH  /api/v1/reviews/{id}/                           # Update review
DELETE /api/v1/reviews/{id}/                           # Delete review
GET    /api/v1/reviews/my/                             # My reviews
```

### Statistics
```
GET    /api/v1/products/{id}/ratings/                  # Product stats
```

### Helpfulness
```
POST   /api/v1/reviews/helpful/                        # Vote helpful
```

## Request/Response Examples

### Create Review
```json
POST /api/v1/reviews/create/
{
    "product_id": 5,
    "order_id": 123,
    "rating": 5,
    "comment": "Amazing pizza! Fresh ingredients and fast delivery."
}

Response: 201 Created
{
    "id": 42,
    "user": 7,
    "username": "john_doe",
    "product_id": 5,
    "order_id": 123,
    "rating": 5,
    "rating_display": "5 - Excellent",
    "comment": "Amazing pizza! Fresh ingredients and fast delivery.",
    "is_verified_purchase": true,
    "is_approved": true,
    "helpful_count": 0,
    "not_helpful_count": 0,
    "can_edit": true,
    "created_at": "2026-01-15T10:30:00Z",
    "updated_at": "2026-01-15T10:30:00Z"
}
```

### Get Product Statistics
```json
GET /api/v1/products/5/ratings/

Response: 200 OK
{
    "average_rating": 4.35,
    "total_reviews": 127,
    "rating_distribution": {
        "5": 65,
        "4": 40,
        "3": 15,
        "2": 5,
        "1": 2,
        "total": 127
    }
}
```

### Vote Helpful
```json
POST /api/v1/reviews/helpful/
{
    "review_id": 42,
    "is_helpful": true
}

Response: 201 Created
{
    "message": "Your vote has been recorded"
}
```

## Admin Interface

### Review Admin
- **List Display**: ID, User, Product ID, Rating, Verified, Approved, Created
- **Filters**: Rating, Verified Purchase, Approval Status, Date
- **Search**: Username, Email, Product ID, Comment
- **Fieldsets**: Review Info, Moderation, Timestamps

### Helpfulness Admin
- **List Display**: ID, Review, User, Helpful, Created
- **Filters**: Is Helpful, Date
- **Search**: Review ID, Username

## Design Patterns Used

### SOLID Principles

#### Single Responsibility Principle (SRP)
- Each serializer has one responsibility (create, update, list)
- Models contain only data logic and aggregations
- Views handle only HTTP request/response

#### Open/Closed Principle (OCP)
- Serializers can be extended without modification
- Views use mixins for extensibility
- Model methods are static for easy extension

#### Liskov Substitution Principle (LSP)
- All views inherit from DRF generic views
- Serializers properly extend ModelSerializer

#### Interface Segregation Principle (ISP)
- Separate serializers for different operations
- Public vs authenticated endpoints
- Read vs write permissions

#### Dependency Inversion Principle (DIP)
- Views depend on abstract serializers
- Permissions are injected via permission_classes
- Database queries abstracted through ORM

### Clean Architecture

#### Layers
1. **Models (Domain Layer)**: Business logic and rules
2. **Serializers (Application Layer)**: Input validation and transformation
3. **Views (Presentation Layer)**: HTTP handling and routing
4. **URLs (Infrastructure Layer)**: Routing configuration

#### Benefits
- Testable (each layer can be tested independently)
- Maintainable (clear separation of concerns)
- Extensible (easy to add features)
- Independent of frameworks (business logic is pure)

## Database Optimizations

### Indexes
- Composite index on (product_id, -created_at) for fast product queries
- Index on (user, -created_at) for user review history
- Index on (is_approved, -created_at) for moderation

### Query Optimizations
- `select_related("user")` to prevent N+1 queries
- `prefetch_related("helpfulness_votes")` for vote counts
- Aggregation queries for statistics

### Constraints
- Unique constraint on (user, product_id) prevents duplicates at DB level
- Rating validators ensure data integrity
- Foreign keys with proper on_delete behavior

## Security Features

### Authentication
- JWT-based authentication via IsAuthenticatedJWT
- Public endpoints (list, stats) don't require auth
- Write operations require authentication

### Authorization
- Users can only edit/delete own reviews
- 7-day edit window prevents abuse
- Cannot vote on own reviews
- Cannot vote twice on same review

### Input Validation
- Comment length validation (10-1000 chars)
- Rating range validation (1-5)
- Duplicate review prevention
- SQL injection protection via ORM

## Testing Recommendations

### Unit Tests
- Model methods (get_product_average_rating, get_product_rating_distribution)
- Serializer validation
- Business rule enforcement

### Integration Tests
- Create review flow
- Edit within/outside 7-day window
- Duplicate review prevention
- Helpfulness voting restrictions

### API Tests
- All endpoints with various auth states
- Error responses
- Pagination
- Filtering

## Future Enhancements

### Possible Features
1. **Review Images**: Allow users to upload photos
2. **Review Responses**: Restaurant can respond to reviews
3. **Report Abuse**: Flag inappropriate reviews
4. **Sort Options**: Sort by helpful, rating, date
5. **Review Replies**: Users can reply to reviews
6. **Verified Purchase Check**: Actually verify user purchased the product
7. **Email Notifications**: Notify on new reviews/votes
8. **Review Summary**: AI-generated summary of all reviews

### Performance Improvements
1. Caching for product statistics
2. Materialized views for aggregations
3. Elasticsearch for full-text search
4. Redis for vote counts

## Integration with Existing System

### Menu App
- Can display average rating on product list
- Add `rating_stats` field to ProductSerializer
- Filter/sort products by rating

### Orders App
- Mark reviews as verified if order_id matches user's orders
- Show "Review this product" prompt after order delivery
- Link to review from order detail

### Accounts App
- Show user's review count on profile
- Display review history
- Reputation system based on helpful votes

## Deployment Checklist

- [x] Models created and migrated
- [x] Serializers implemented with validation
- [x] Views with proper permissions
- [x] URLs configured
- [x] Admin interface registered
- [x] OpenAPI documentation complete
- [ ] Write unit tests
- [ ] Write integration tests
- [ ] Add to CI/CD pipeline
- [ ] Update API documentation
- [ ] Train admin users on moderation

## License

Part of Restaurant Delivery System API
