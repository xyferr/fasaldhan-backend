# Fasaldhan API Documentation

## Overview
Fasaldhan is a contract farming platform that connects farmers with buyers through a comprehensive API system. This API provides endpoints for user management, contract farming, crop listings, and ML-powered analytics.

## Base URL
- **Development**: `http://localhost:8000`
- **API Base**: `/api/`

## Authentication
The API uses JWT (JSON Web Token) authentication. Include the access token in the Authorization header:
```
Authorization: Bearer <access_token>
```

## Postman Setup

### 1. Import Collection
1. Open Postman
2. Click "Import" button
3. Select `Fasaldhan_API_Collection.postman_collection.json`
4. The collection will be imported with all endpoints

### 2. Import Environment
1. Click on "Environments" in Postman
2. Click "Import" 
3. Select `Fasaldhan_Development_Environment.postman_environment.json`
4. Set this as your active environment

### 3. Environment Variables
The environment includes these variables:
- `base_url`: API base URL (default: http://localhost:8000)
- `access_token`: JWT access token (automatically set after login)
- `refresh_token`: JWT refresh token (automatically set after login)
- `listing_id`, `contract_id`, etc.: Sample IDs for testing

## API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/token/refresh/` - Refresh access token

### User Management
- `GET /api/auth/profile/` - Get user profile
- `PUT /api/auth/profile/` - Update user profile
- `GET /api/dashboard/` - Get user dashboard

### Profile Management
- `GET /api/farmer-profile/` - Get farmer profile
- `PUT /api/farmer-profile/` - Create/update farmer profile
- `GET /api/buyer-profile/` - Get buyer profile
- `PUT /api/buyer-profile/` - Create/update buyer profile

### Contract System
#### Categories
- `GET /api/contract/categories/` - List all categories
- `POST /api/contract/categories/` - Create category
- `GET /api/contract/categories/{id}/` - Get category details
- `PUT /api/contract/categories/{id}/` - Update category
- `DELETE /api/contract/categories/{id}/` - Delete category

#### Crops
- `GET /api/contract/crops/` - List all crops
- `POST /api/contract/crops/` - Create crop
- `GET /api/contract/crops/{id}/` - Get crop details
- `PUT /api/contract/crops/{id}/` - Update crop
- `DELETE /api/contract/crops/{id}/` - Delete crop

#### Crop Listings
- `GET /api/contract/listings/` - List all crop listings
- `POST /api/contract/listings/` - Create listing
- `GET /api/contract/listings/{id}/` - Get listing details
- `PUT /api/contract/listings/{id}/` - Update listing
- `DELETE /api/contract/listings/{id}/` - Delete listing

#### Contracts
- `GET /api/contract/contracts/` - List all contracts
- `POST /api/contract/contracts/` - Create contract
- `GET /api/contract/contracts/{id}/` - Get contract details
- `PUT /api/contract/contracts/{id}/` - Update contract
- `DELETE /api/contract/contracts/{id}/` - Delete contract

#### Reviews
- `GET /api/contract/reviews/` - List all reviews
- `POST /api/contract/reviews/` - Create review
- `GET /api/contract/reviews/{id}/` - Get review details
- `PUT /api/contract/reviews/{id}/` - Update review
- `DELETE /api/contract/reviews/{id}/` - Delete review

### Analytics & ML
- `GET /api/contract/dashboard/` - Dashboard analytics
- `GET /api/contract/market-trends/` - Market trends data
- `POST /api/contract/ml/predict-price/` - Price prediction
- `POST /api/contract/ml/assess-quality/` - Quality assessment
- `POST /api/contract/ml/predict-yield/` - Yield prediction

## Sample API Flows

### 1. User Registration and Login
```
1. POST /api/auth/register/ - Register new user
2. POST /api/auth/login/ - Login and get tokens
3. Token is automatically saved in environment
```

### 2. Complete Profile Setup
```
1. Login first
2. PUT /api/farmer-profile/ OR PUT /api/buyer-profile/
3. GET /api/dashboard/ - View dashboard
```

### 3. Create and Manage Listings (Farmer)
```
1. Login as farmer
2. GET /api/contract/categories/ - Get available categories
3. GET /api/contract/crops/ - Get available crops
4. POST /api/contract/listings/ - Create new listing
5. GET /api/contract/listings/ - View all listings
```

### 4. Create Contract (Buyer)
```
1. Login as buyer
2. GET /api/contract/listings/ - Browse available listings
3. POST /api/contract/contracts/ - Create contract for a listing
4. GET /api/contract/contracts/ - View your contracts
```

## Data Models

### User Registration
```json
{
    "username": "farmer123",
    "email": "farmer@example.com",
    "password": "securepassword123",
    "password_confirm": "securepassword123",
    "first_name": "John",
    "last_name": "Doe",
    "user_type": "farmer", // or "buyer"
    "phone_number": "+1234567890",
    "location": "Punjab, India"
}
```

### Farmer Profile
```json
{
    "land_size": 10.5,
    "farming_type": "organic", // organic, traditional, hydroponic, mixed
    "aadhaar_number": "123456789012",
    "farm_address": "Village ABC, District XYZ",
    "pincode": "123456",
    "experience_years": 15,
    "specializations": "Rice, Wheat, Sugarcane",
    "certifications": "Organic Farming Certificate"
}
```

### Buyer Profile
```json
{
    "company_name": "ABC Agriculture Ltd",
    "gst_number": "27AAPFU0939F1ZV",
    "business_type": "wholesaler", // wholesaler, exporter, retailer, processor, restaurant, other
    "business_address": "123 Business Street, Commercial Area",
    "pincode": "110001",
    "website": "https://abcagriculture.com",
    "annual_turnover": 5000000.00,
    "preferred_crops": "Rice, Wheat, Pulses",
    "contact_person_name": "Manager Name",
    "contact_person_designation": "Purchase Manager"
}
```

### Crop Listing
```json
{
    "crop": 1, // crop ID
    "quantity": 1000,
    "unit": "kg",
    "price_per_unit": 45.50,
    "location": "Punjab, India",
    "harvest_date": "2025-10-15",
    "quality_grade": "A",
    "description": "High quality organic basmati rice",
    "is_organic": true
}
```

### Contract
```json
{
    "listing": 1, // listing ID
    "quantity": 500,
    "price_per_unit": 45.50,
    "delivery_date": "2025-11-01",
    "terms_and_conditions": "Standard contract terms apply",
    "payment_terms": "50% advance, 50% on delivery"
}
```

## Error Handling
The API returns standard HTTP status codes:
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `500` - Internal Server Error

Error responses include a message:
```json
{
    "error": "Error description",
    "details": "Additional error details"
}
```

## Rate Limiting
Currently no rate limiting is implemented, but consider implementing it for production.

## Testing Workflow

### 1. Start the Server
```bash
cd c:\ROHIT\CS\python\Projects\fasaldhan-backend
myenv\Scripts\activate
python manage.py runserver
```

### 2. Test Basic Endpoints
1. Use "Root API Overview" to test server connection
2. Register a farmer and a buyer account
3. Login with both accounts and test profile creation
4. Create categories, crops, and listings
5. Test contract creation and ML endpoints

### 3. Environment Setup
- The collection automatically saves tokens after login
- Update the `base_url` variable if deploying to different server
- Use different environments for development, staging, and production

## Notes
- All timestamps are in ISO format
- File uploads (images) should be sent as multipart/form-data
- JWT tokens expire after a certain time, use refresh token to get new access token
- Some endpoints require specific user types (farmer vs buyer)
- ML endpoints return mock data until models are trained

## Support
For API support or questions, contact the development team or check the Django admin panel at `/admin/` for data management.
