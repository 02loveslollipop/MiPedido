> NOTA: El contenido del QR es el id del pedido.

# Documentación API publica de MiPedido

## Restaurant

### List Restaurants

**URL**: `/v1/restaurants`

**Method**: `GET`

**Auth required**: `No`

**Content-Type**: `application/json`

**Description**: Returns a list of restaurants available for the users.

#### Input: `None`

#### Output:

- List available restaurants.

**HTTP** 200: OK

```json
{
    [
        {
            "name": String,
            "img_url": String,
            "id": String,
            "rating": Number,
            "type": String,
            "description": String,
            "position": {
                "lat": Number,
                "lng": Number
            }
        },
        ...
    ]
}

```

- Internal error.

**HTTP** 500: Internal Server Error

```json
{
    "error": String
}
```

## Order

### Create Order

**URL**: `/v1/order`

**Method**: `POST`

**Auth required**: `No`

**Content-Type**: `application/json`

**Description**: Creates an empty order in a restaurant and returns the order id and the user id (for the specific order). If the restaurant does not exist, it returns an error. 

#### input: JSON
```json
{
    "restaurant_id": String,
}
```

#### Output:  

- Order created.

**HTTP** 201: Created

```json
{
    "order_id": String,
    "user_id": String
}

```

- Restaurant not found.

**HTTP** 404: Not Found

```json
{
    "error": "Restaurant not found"
}
```

- Internal error.

**HTTP** 500: Internal Server Error

```json
{
    "error": String
}
```



### Join Order

**URL**: `/v1/order/{order_id}`

**Method**: `PUT`

**Auth required**: `No`

**Content-Type**: `application/json`

***Description**: Adds a user to an existing order. Returns the user id (for the specific order) and the restaurant id. If the order does not exist, it returns an error.

#### Input: Path variable
```json
{
    "order_id": String,
}
```

#### Output:

- User added.

**HTTP** 201: Created

```json
{
    "user_id": String,
    "restaurant_id": String
}
```

- Order not found.

**HTTP** 404: Not Found

```json
{
    "error": "Order not found"
}
```

- Internal error.

**HTTP** 500: Internal Server Error

```json
{
    "error": String
}
```

### Modify order for user

**URL**: `/v1/order/{order_id}/{user_id}`

**Method**: `PUT`

**Auth required**: `No`

**Content-Type**: `application/json`

**Description**: Modify the order of a user. If the product does not exist, it is created. If it exists, it is updated. If the given quantity is 0, it is deleted. If the product id does not exist, it returns an error. If one of the ingredients is not valid for the product, it returns an error. If the user does not exist for the order, it returns an error.

#### Input: Path variable
```json
{
    "order_id": String,
    "user_id": String,
}
```

#### Input: JSON
```json
{
    "product_id": String,
    "quantity": Number,
    "ingredients": [
        String,
    ]
}
```

#### Output:

- Product Added.

**HTTP** 201: Created

```json
{
    "status": "Created"
}
```

- Product Updated.
**HTTP** 200: OK

```json
{
    "status": "Updated"
}
```

- Product Deleted.
**HTTP** 200: OK

```json
{
    "status": "Deleted"
}
```

- Product not found.

**HTTP** 404: Not Found

```json
{
    "error": "Product not found in the restaurant"
}
```

- Ingredient not found for product.
**HTTP** 404: Not Found

```json
{
    "error": "Ingredient not found for product"
}
```

- User not found for order.
**HTTP** 404: Not Found

```json
{
    "error": "User not found for order"
}
```

- Order not found.
**HTTP** 404: Not Found

```json
{
    "error": "Order not found"
}
```

- Internal error.
**HTTP** 500: Internal Server Error

```json
{
    "error": String
}
```

### Get User Order

**URL**: `/v1/order/{order_id}/{user_id}`

**Method**: `GET`

**Auth required**: `No`

**Content-Type**: `application/json`

**Description**: Returns the order of a user. If the order does not exist, it returns an error. If the user does not exist for the order, it returns an error. Else, it returns a list of products with the quantity and ingredients for the user.

#### Input: Path variable
```json
{
    "order_id": String,
    "user_id": String,
}
```

#### Output:

- Order found.

**HTTP** 200: OK

```json
{
    [
        {
            "name": String,
            "price": Number,
            "img_url": String,
            "id": String,
            "quantity": Number,
            "ingredients": [
                String,
            ]
        },
    ]
}
```

- Order not found.

**HTTP** 404: Not Found

```json
{
    "error": "Order not found"
}
```

- User not found for order.

**HTTP** 404: Not Found

```json
{
    "error": "User not found for order"
}
```

- Internal error.

**HTTP** 500: Internal Server Error

```json
{
    "error": String
}
```

### Finalize Order (Get final order)

**URL**: `/v1/order/{order_id}/finalize`
**Method**: `POST`
**Auth required**: `Yes`
**Auth type**: `JWT`
**Content-Type**: `application/json`
**Description**: Finalizes the order and returns it with all products aggregated by product and ingredients (if two users have the same product with the same ingredients, it will be aggregated; if ingredients differ, they are considered different products). 

This endpoint marks the order as ready for fulfillment, but it doesn't mark it as fulfilled yet. An order can be finalized multiple times as long as it hasn't been fulfilled. This allows reviewing and refreshing the final order details.

If the order is already fulfilled, it returns a 409 Conflict error. The user must control the restaurant to access this endpoint.

#### Input: Path variable
```json
{
    "order_id": String,
}
```

#### Input: JSON
```json
{
    "access_token": String
}
```

#### Output:
- Order finalized.

***HTTP** 201: Created

```json
{
    products: [
        {
            "name": String,
            "price_per_unit": Number,
            "total_price": Number,
            "img_url": String,
            "id": String,
            "quantity": Number,
            "ingredients": [
                String,
            ]
        },
    ]
    total_price: Number,
    total_quantity: Number,
    date_completed: String, // Placeholder - actual value set on fulfillment
}
```

- Order not found.

**HTTP** 404: Not Found

```json
{
    "error": "Order not found"
}
```

- Order already fulfilled.

**HTTP** 409: Conflict

```json
{
    "error": "Order already fulfilled"
}
```

- User not found for order.

**HTTP** 404: Not Found

```json
{
    "error": "User not found for order"
}
```

- Internal error.

**HTTP** 500: Internal Server Error

```json
{
    "error": String
}
```

- Invalid token.

**HTTP** 401: Unauthorized

```json
{
    "error": "Invalid token"
}
```

- Restaurant not found in the user controls.

**HTTP** 401: Unauthorized

```json
{
    "error": "This user cannot finalize this order"
}
```

### Fulfill Order

**URL**: `/v1/order/{order_id}/fulfill`
**Method**: `POST`
**Auth required**: `Yes`
**Auth type**: `JWT`
**Content-Type**: `application/json`
**Description**: Marks an order as fulfilled by a business user. The order must be finalized before it can be fulfilled. 

This endpoint sets the date_completed field in the database and marks the order as "fulfilled", which prevents further finalization or fulfillment.

If the order is already fulfilled, it returns an error. If the order hasn't been finalized yet, it returns an error. The user must control the restaurant to access this endpoint.

#### Input: Path variable
```json
{
    "order_id": String,
}
```

#### Input: JSON
```json
{
    "access_token": String
}
```

#### Output:

- Order fulfilled.

**HTTP** 200: OK

```json
{
    "status": "Fulfilled",
    "fulfilled_at": String  // ISO DateTime - also sets date_completed in database
}
```

- Order not found.

**HTTP** 404: Not Found

```json
{
    "error": "Order not found"
}
```

- Order already fulfilled.

**HTTP** 400: Bad Request

```json
{
    "error": "Order already fulfilled"
}
```

- Order not finalized yet.

**HTTP** 400: Bad Request

```json
{
    "error": "Order must be finalized before fulfillment"
}
```

- Internal error.

**HTTP** 500: Internal Server Error

```json
{
    "error": String
}
```

- Invalid token.

**HTTP** 401: Unauthorized

```json
{
    "error": "Invalid token"
}
```

- Restaurant not found in the user controls.

**HTTP** 401: Unauthorized

```json
{
    "error": "This user cannot fulfill this order"
}
```

## Product

### List Products of a Restaurant

**URL**: `/v1/products/{restaurant_id}`

**Method**: `GET`

**Auth required**: `No`

**Content-Type**: `application/json`

**Description**: Returns a list of products available for the user in a restaurant. If the restaurant does not exist, it returns an error.


#### Input: Path variable
```json
{
    "restaurant_id": String,
}
```

#### Output:

- Products found.

**HTTP** 200: OK

```json
{
    [
        {
            "name": String,
            "description": String,
            "price": Number,
            "img_url": String,
            "id": String,
            "ingredients": [
                String,
            ]
        },
    ]
}

```

- Restaurant not found.

**HTTP** 404: Not Found

```json
{
    "error": String
}
```

- Internal error.

**HTTP** 500: Internal Server Error

```json
{
    "error": String
}
```

### List All Products of a Restaurant (Including Disabled)

**URL**: `/v1/products/{restaurant_id}/all`

**Method**: `GET`

**Auth required**: `Yes`

**Auth type**: `JWT Bearer Token`

**Content-Type**: `application/json`

**Description**: Returns a list of all products (both enabled and disabled) for a specific restaurant. This endpoint is intended for business users who need to manage all products. If the restaurant does not exist, it returns an error. The user must control the restaurant to access this endpoint.

#### Input: Path variable
```json
{
    "restaurant_id": String,
}
```

#### Input: Header
```
Authorization: Bearer {access_token}
```

#### Output:

- Products found.

**HTTP** 200: OK

```json
{
    [
        {
            "name": String,
            "description": String,
            "price": Number,
            "img_url": String,
            "id": String,
            "ingredients": [
                String,
            ],
            "isEnabled": Boolean
        },
    ]
}
```

- Restaurant not found.

**HTTP** 404: Not Found

```json
{
    "error": "Restaurant not found"
}
```

- Unauthorized access.

**HTTP** 401: Unauthorized

```json
{
    "error": "This user cannot access this restaurant's products"
}
```

- Invalid authentication.

**HTTP** 401: Unauthorized

```json
{
    "error": "Invalid authentication credentials"
}
```

- Internal error.

**HTTP** 500: Internal Server Error

```json
{
    "error": String
}
```

### Get Product Details

**URL**: `/v1/products/{restaurant_id}/{product_id}`

**Method**: `GET`

**Auth required**: `No` (Optional)

**Content-Type**: `application/json`

**Description**: Returns detailed information about a specific product in a restaurant. If the product does not exist, it returns an error. If the restaurant does not exist, it returns an error.

#### Input: Path variable
```json
{
    "restaurant_id": String,
    "product_id": String
}
```

#### Output:

- Product found.

**HTTP** 200: OK

```json
{
    "name": String,
    "description": String,
    "price": Number,
    "img_url": String,
    "id": String,
    "ingredients": [
        String,
    ],
    "isEnabled": Boolean
}
```

- Product not found.

**HTTP** 404: Not Found

```json
{
    "error": "Product not found"
}
```

- Restaurant not found.

**HTTP** 404: Not Found

```json
{
    "error": "Restaurant not found"
}
```

- Internal error.

**HTTP** 500: Internal Server Error

```json
{
    "error": String
}
```

### Disable Product

**URL**: `/v1/products/{restaurant_id}/{product_id}`
**Method**: `DELETE`
**Auth required**: `Yes`
**Auth type**: `JWT`
**Content-Type**: `application/json`
***Description**: Disables a product in a restaurant. If the product does not exist, it returns an error. If the restaurant does not exist, it returns an error. If the bearer token is not valid, it returns an error. If the user exist, but the in the users collection the given user id is not related to the restaurant of the order, it returns an error. (The users collection must have a `controls` field in the user object with the restaurant id).

#### Input: Path variable
```json
{
    "restaurant_id": String,
    "product_id": String,
}
```

#### Input: JSON
```json
{
    "access_token": String
}
```

#### Output:

- Product disabled.

**HTTP** 200: OK

```json
{
    "status": "Disabled"
}
```

- Product not found.

**HTTP** 404: Not Found

```json
{
    "error": "Product not found"
}
```

- Restaurant not found.

**HTTP** 404: Not Found

```json
{
    "error": "Restaurant not found"
}
```

- Internal error.

**HTTP** 500: Internal Server Error

```json
{
    "error": String
}
```

- Invalid token.

**HTTP** 401: Unauthorized

```json
{
    "error": "Invalid token"
}
```

- Restaurant not found in the user controls.

***HTTP** 401: Unauthorized

```json
{
    "error": "This user cannot fulfill this request"
}
```

### Enable Product

**URL**: `/v1/products/{restaurant_id}/{product_id}/enable`

**Method**: `PUT`

**Auth required**: `Yes`

**Auth type**: `JWT`

**Content-Type**: `application/json`

**Description**: Enables a previously disabled product in a restaurant. If the product does not exist, it returns an error. If the restaurant does not exist, it returns an error. If the bearer token is not valid, it returns an error. If the user exists, but in the users collection the given user id is not related to the restaurant of the order, it returns an error. (The users collection must have a `controls` field in the user object with the restaurant id).

#### Input: Path variable
```json
{
    "restaurant_id": String,
    "product_id": String
}
```

#### Input: JSON
```json
{
    "access_token": String
}
```

#### Output:

- Product enabled.

**HTTP** 200: OK

```json
{
    "status": "Enabled"
}
```

- Product not found.

**HTTP** 404: Not Found

```json
{
    "error": "Product not found"
}
```

- Restaurant not found.

**HTTP** 404: Not Found

```json
{
    "error": "Restaurant not found"
}
```

- Internal error.

**HTTP** 500: Internal Server Error

```json
{
    "error": String
}
```

- Invalid token.

**HTTP** 401: Unauthorized

```json
{
    "error": "Invalid token"
}
```

- Restaurant not found in the user controls.

**HTTP** 401: Unauthorized

```json
{
    "error": "This user cannot fulfill this request"
}
```

## User

### Login

**URL**: `/v1/user/login`

**Method**: `POST`

**Auth required**: `No`

**Content-Type**: `application/json`

**Description**: Sign in in the server. Returns an access token and the user id. If the user does not exist, it returns an error.

#### Input: JSON
```json
{
    "username": String,
    "password": String,
}
```

#### Output:
- User found.
**HTTP** 200: OK

```json
{
    "access_token": String,
    "user_id": String,
}
```

- User not found.
**HTTP** 404: Not Found

```json
{
    "error": "User not found"
}
```

### Get User Restaurant

**URL**: `/v1/user/restaurant`

**Method**: `GET`

**Auth required**: `Yes`

**Auth type**: `JWT Bearer Token`

**Content-Type**: `application/json`

**Description**: Returns the primary restaurant ID associated with the authenticated user. Only returns one restaurant ID even if the user controls multiple restaurants.

#### Input: Header
```
Authorization: Bearer {access_token}
```

#### Output:
- Restaurant found.
**HTTP** 200: OK

```json
{
    "restaurant_id": String
}
```

- No restaurant found for user.
**HTTP** 404: Not Found

```json
{
    "detail": "No restaurant found for this user"
}
```

- Invalid authentication.
**HTTP** 401: Unauthorized

```json
{
    "detail": "Invalid authentication credentials"
}
```

## Review

### Create Review

**URL**: `/v1/review/`

**Method**: `POST`

**Auth required**: `No`

**Content-Type**: `application/json`

**Description**: Create an anonymous review for a restaurant. The review starts with "pending" status and will be processed by a background job to update the restaurant's rating. Rating must be between 1 and 5 stars.

#### Input: JSON
```json
{
    "restaurant_id": String,
    "rating": Number  // 1-5
}
```

#### Output:

- Review created.

**HTTP** 201: Created

```json
{
    "id": String,
    "restaurant_id": String,
    "rating": Number,
    "status": "pending",
    "created_at": String  // ISO DateTime
}
```

- Invalid rating.

**HTTP** 400: Bad Request

```json
{
    "detail": "Rating must be between 1 and 5"
}
```

- Restaurant not found.

**HTTP** 404: Not Found

```json
{
    "detail": "Restaurant not found"
}
```

- Internal error.

**HTTP** 500: Internal Server Error

```json
{
    "detail": String
}
```

## Shortener

### Get full Order ID from Short Code

**URL**: `/v1/shortener/{short_code}` // Corrected path parameter

**Method**: `GET`

**Auth required**: `No`

**Content-Type**: `application/json`

**Description**: Returns the full Order ID from a short code. The short code is a 6-character Base36 string. If the short code does not correspond to an existing order, it returns an error.

#### Input: Path variable
```json
{
    "short_code": String, // The 6-character Base36 short code
}
```

#### Output:

- Order found.

**HTTP** 200: OK

```json
{
    "object_id": String // The full 24-character hexadecimal Order ID
}
```

- Short code not found. // Corrected error description

**HTTP** 404: Not Found

```json
{
    "error": "Short code not found" // Corrected error message
}
```

- Internal error.

**HTTP** 500: Internal Server Error

```json
{
    "error": String
}
```

## Search

### Search Restaurants

**URL**: `/v1/search/restaurants`

**Method**: `GET`

**Auth required**: `No`

**Content-Type**: `application/json`

**Description**: Search for restaurants by name, description, type, or associated products. Returns restaurants that match the search query.

#### Input: Query Parameters
- `q` (string, required): Search query for restaurants, products, or cuisines
- `limit` (integer, optional, default: 10): Maximum number of results to return
- `offset` (integer, optional, default: 0): Number of results to skip

#### Output:

- Restaurants found.

**HTTP** 200: OK

```json
{
  "count": Number,
  "results": [
    {
      "id": String,
      "name": String,
      "type": String,
      "img_url": String,
      "rating": Number,
      "description": String,
      "position": {
        "lat": Number,
        "lng": Number
      }
    },
    ...
  ]
}
```

- Internal error.

**HTTP** 500: Internal Server Error

```json
{
  "detail": String
}
```

### Search Products

**URL**: `/v1/search/products`

**Method**: `GET`

**Auth required**: `No`

**Content-Type**: `application/json`

**Description**: Search for products by name, description, or ingredients. Returns products that match the search query, including basic restaurant info for each product.

#### Input: Query Parameters
- `q` (string, required): Search query for products, ingredients, or descriptions
- `limit` (integer, optional, default: 10): Maximum number of results to return
- `offset` (integer, optional, default: 0): Number of results to skip

#### Output:

- Products found.

**HTTP** 200: OK

```json
{
  "count": Number,
  "results": [
    {
      "id": String,
      "name": String,
      "description": String,
      "price": Number,
      "img_url": String,
      "ingredients": [String],
      "restaurant": {
        "id": String,
        "name": String
      }
    },
    ...
  ]
}
```

- Internal error.

**HTTP** 500: Internal Server Error

```json
{
  "detail": String
}
```

# MiPedido Admin API Documentation

This document outlines the administrative endpoints available in the MiPedido API system.

## Authentication

All admin endpoints require authentication using a bearer token. To get a token, administrators must first login using the authentication endpoint.

### Admin Login

```
POST /v1/admin/login
```

Authenticates an admin user and returns an access token.

**Request:**

```json
{
  "username": "admin",
  "password": "adminpassword"
}
```

**Response:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "admin_id": "612e4c8212ab3f4e10d9ef4a",
  "username": "admin"
}
```

### Get Current Admin

```
GET /v1/admin/me
```

Returns information about the currently authenticated admin.

**Response:**

```json
{
  "id": "612e4c8212ab3f4e10d9ef4a",
  "username": "admin"
}
```

## Admin Management

### List All Admins

```
GET /v1/admin/
```

Lists all admin users in the system.

**Response:**

```json
[
  {
    "id": "612e4c8212ab3f4e10d9ef4a",
    "username": "admin"
  },
  {
    "id": "612e4c8212ab3f4e10d9ef4b",
    "username": "manager"
  }
]
```

### Create Admin

```
POST /v1/admin/
```

Creates a new admin user. Only existing admins can create new admins.

**Request:**

```json
{
  "username": "newadmin",
  "password": "securepassword"
}
```

**Response:**

```json
{
  "id": "612e4c8212ab3f4e10d9ef4c",
  "username": "newadmin"
}
```

### Update Admin

```
PUT /v1/admin/{admin_id}
```

Updates an existing admin's details.

**Request:**

```json
{
  "username": "updatedname",
  "password": "newpassword"  // Optional
}
```

**Response:**

```json
{
  "id": "612e4c8212ab3f4e10d9ef4c",
  "username": "updatedname"
}
```

## Restaurant Management

### List All Restaurants

```
GET /v1/admin/restaurants/
```

Lists all restaurants in the system.

**Response:**

```json
[
  {
    "id": "612e4c8212ab3f4e10d9ef60",
    "name": "Burger Heaven",
    "type": "Fast Food",
    "img_url": "https://example.com/image.jpg",
    "rating": 4.5,
    "description": "Best burgers in town"
  }
]
```

### Get Restaurant

```
GET /v1/admin/restaurants/{restaurant_id}
```

Get details of a specific restaurant.

**Response:**

```json
{
  "id": "612e4c8212ab3f4e10d9ef60",
  "name": "Burger Heaven",
  "type": "Fast Food",
  "img_url": "https://example.com/image.jpg",
  "rating": 4.5,
  "description": "Best burgers in town",
  "position": {
    "lat": 40.7128,
    "lng": -74.0060
  }
}
```

### Create Restaurant

```
POST /v1/admin/restaurants/
```

Creates a new restaurant.

**Request:**

```json
{
  "name": "New Restaurant",
  "type": "Italian",
  "img_url": "https://example.com/img.jpg",
  "description": "Authentic Italian cuisine",
  "position": {
    "lat": 40.7128,
    "lng": -74.0060
  }
}
```

**Response:**

```json
{
  "id": "612e4c8212ab3f4e10d9ef61",
  "name": "New Restaurant",
  "type": "Italian",
  "img_url": "https://example.com/img.jpg",
  "description": "Authentic Italian cuisine",
  "rating": 0,
  "position": {
    "lat": 40.7128,
    "lng": -74.0060
  }
}
```

### Update Restaurant

```
PUT /v1/admin/restaurants/{restaurant_id}
```

Updates a restaurant's details.

**Request:**

```json
{
  "name": "Updated Name",
  "description": "Updated description",
  "img_url": "https://example.com/new-image.jpg",
  "type": "Fusion"
}
```

**Response:** Returns the updated restaurant object.

### Delete Restaurant

```
DELETE /v1/admin/restaurants/{restaurant_id}
```

Deletes a restaurant.

**Response:** HTTP 204 No Content

### Update Restaurant Rating

```
PUT /v1/admin/restaurants/{restaurant_id}/update-rating
```

Manually updates a restaurant's rating.

**Request:**

```json
{
  "rating": 4.7
}
```

**Response:**

```json
{
  "message": "Rating updated successfully"
}
```

## Product Management

### List Products by Restaurant

```
GET /v1/admin/products/restaurant/{restaurant_id}
```

Lists all products for a specific restaurant, including disabled ones.

**Response:**

```json
[
  {
    "id": "612e4c8212ab3f4e10d9ef70",
    "name": "Classic Burger",
    "description": "Our signature burger with beef patty",
    "price": 12.99,
    "img_url": "https://example.com/burger.jpg",
    "ingredients": ["Beef patty", "Lettuce", "Tomato", "Special sauce"],
    "restaurant_id": "612e4c8212ab3f4e10d9ef60",
    "active": true
  }
]
```

### Get Product

```
GET /v1/admin/products/{product_id}
```

Get details of a specific product.

**Response:**

```json
{
  "id": "612e4c8212ab3f4e10d9ef70",
  "name": "Classic Burger",
  "description": "Our signature burger with beef patty",
  "price": 12.99,
  "img_url": "https://example.com/burger.jpg",
  "ingredients": ["Beef patty", "Lettuce", "Tomato", "Special sauce"],
  "restaurant_id": "612e4c8212ab3f4e10d9ef60",
  "active": true
}
```

### Create Product

```
POST /v1/admin/products/
```

Creates a new product.

**Request:**

```json
{
  "restaurant_id": "612e4c8212ab3f4e10d9ef60",
  "name": "Veggie Burger",
  "description": "Plant-based burger",
  "price": 10.99,
  "img_url": "https://example.com/veggie-burger.jpg",
  "ingredients": ["Plant-based patty", "Lettuce", "Tomato"]
}
```

**Response:** Returns the created product object.

### Update Product

```
PUT /v1/admin/products/{product_id}
```

Updates a product's details.

**Request:**

```json
{
  "name": "Super Veggie Burger",
  "price": 11.99,
  "ingredients": ["Plant-based patty", "Lettuce", "Tomato", "Vegan mayo"]
}
```

**Response:** Returns the updated product object.

### Delete Product

```
DELETE /v1/admin/products/{product_id}
```

Permanently deletes a product.

**Response:** HTTP 204 No Content

### Enable Product

```
PUT /v1/admin/products/{product_id}/enable
```

Enables a disabled product.

**Response:**

```json
{
  "message": "Product enabled successfully"
}
```

### Disable Product

```
PUT /v1/admin/products/{product_id}/disable
```

Disables a product, making it unavailable for ordering.

**Response:**

```json
{
  "message": "Product disabled successfully"
}
```

## User Management

### List All Users

```
GET /v1/admin/users/
```

Lists all users in the system.

**Response:**

```json
[
  {
    "id": "612e4c8212ab3f4e10d9ef80",
    "username": "user1",
    "controls": ["612e4c8212ab3f4e10d9ef60"]
  }
]
```

### Get User

```
GET /v1/admin/users/{user_id}
```

Get details of a specific user, including which restaurants they control.

**Response:**

```json
{
  "id": "612e4c8212ab3f4e10d9ef80",
  "username": "user1",
  "controls": ["612e4c8212ab3f4e10d9ef60"],
  "restaurants": [
    {
      "id": "612e4c8212ab3f4e10d9ef60",
      "name": "Burger Heaven"
    }
  ]
}
```

### Create User

```
POST /v1/admin/users/
```

Creates a new user.

**Request:**

```json
{
  "username": "newuser",
  "password": "userpassword"
}
```

**Response:** Returns the created user object.

### Update User

```
PUT /v1/admin/users/{user_id}
```

Updates a user's details.

**Request:**

```json
{
  "username": "updateduser",
  "password": "newpassword"  // Optional
}
```

**Response:**

```json
{
  "message": "User updated successfully"
}
```

## Blob Storage

The Blob Storage API provides endpoints for uploading and deleting files such as images and PDFs.

### Upload File to Blob Storage

**URL**: `/v1/blob/upload`

**Method**: `POST`

**Auth required**: `Yes`

**Auth type**: `JWT Bearer Token`

**Content-Type**: `multipart/form-data`

**Description**: Uploads a file to blob storage. Currently supports JPEG, PNG, and PDF files with a maximum size of 5MB.

#### Input: Form Data
```
file: File  // The file to upload
```

#### Input: Header
```
Authorization: Bearer {access_token}
```

#### Output:

- File uploaded successfully.

**HTTP** 201: Created

```json
{
  "name": String,  // Original filename
  "url": String    // Accessible URL of the uploaded file
}
```

- Invalid file type.

**HTTP** 400: Bad Request

```json
{
  "detail": "Invalid file type. Only JPEG, PNG, and PDF files are allowed."
}
```

- File size too large.

**HTTP** 400: Bad Request

```json
{
  "detail": "File size exceeds the limit of 5MB."
}
```

- Invalid authentication.

**HTTP** 401: Unauthorized

```json
{
  "detail": "Not authenticated"
}
```

- Internal error.

**HTTP** 500: Internal Server Error

```json
{
  "detail": String
}
```

### Delete File from Blob Storage

**URL**: `/v1/blob/delete/`

**Method**: `DELETE`

**Auth required**: `Yes`

**Auth type**: `JWT Bearer Token`

**Description**: Deletes a file from blob storage based on its URL.

#### Input: Query Parameter
```
blob_url: String  // The full URL of the file to delete
```

#### Input: Header
```
Authorization: Bearer {access_token}
```

#### Output:

- File deleted successfully.

**HTTP** 200: OK

```json
{
  "message": "Blob deleted successfully"
}
```

- Missing blob URL.

**HTTP** 400: Bad Request

```json
{
  "detail": "Blob URL is required"
}
```

- Invalid blob URL format.

**HTTP** 400: Bad Request

```json
{
  "detail": "Invalid blob URL format"
}
```

- Invalid authentication.

**HTTP** 401: Unauthorized

```json
{
  "detail": "Not authenticated"
}
```

- Internal error.

**HTTP** 500: Internal Server Error

```json
{
  "detail": String
}
```

## Admin Activity Logs

The system automatically logs all admin operations to an audit trail.

### List Admin Logs

```
GET /v1/admin/logs/
```

Lists admin operation logs with optional filtering.

**Query Parameters:**
- `admin_id`: Filter logs by admin ID
- `admin_username`: Filter logs by admin username
- `operation`: Filter by operation type (create, update, delete, etc.)
- `target_type`: Filter by target resource type (restaurant, product, user, etc.)
- `target_id`: Filter by target resource ID
- `from_date`: Filter logs from this date/time (ISO format)
- `to_date`: Filter logs until this date/time (ISO format)
- `skip`: Number of records to skip for pagination
- `limit`: Maximum number of records to return

**Response:**

```json
{
  "logs": [
    {
      "id": "612e4c8212ab3f4e10d9ef90",
      "admin_id": "612e4c8212ab3f4e10d9ef4a",
      "admin_username": "admin",
      "operation": "create",
      "target_type": "restaurant",
      "target_id": "612e4c8212ab3f4e10d9ef60",
      "details": {
        "name": "Burger Heaven"
      },
      "timestamp": "2025-04-28T10:30:15.123Z"
    }
  ],
  "total": 42,
  "skip": 0,
  "limit": 100
}
```

### Get Specific Log Entry

```
GET /v1/admin/logs/{log_id}
```

Get details of a specific log entry.

**Response:**

```json
{
  "id": "612e4c8212ab3f4e10d9ef90",
  "admin_id": "612e4c8212ab3f4e10d9ef4a",
  "admin_username": "admin",
  "operation": "create",
  "target_type": "restaurant",
  "target_id": "612e4c8212ab3f4e10d9ef60",
  "details": {
    "name": "Burger Heaven"
  },
  "timestamp": "2025-04-28T10:30:15.123Z"
}
```

## Error Responses

All endpoints may return the following error responses:

- `400 Bad Request` - Invalid request parameters
- `401 Unauthorized` - Missing or invalid authentication token
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `409 Conflict` - Resource conflict (e.g., duplicate username)
- `500 Internal Server Error` - Server error

Error response format:

```json
{
  "detail": "Error message describing the issue"
}
```

# Documentación otros

## Reduced OrderID

The order ID is reduced to a shorter, more user-friendly format using Base36 encoding of parts of the original MongoDB ObjectId. This is primarily used for display and manual input (like the 6-character code).

**Encoding Process (Conceptual - Actual implementation might vary slightly):**
1. **Extract Data from ObjectId**: A MongoDB ObjectId consists of:
    * 4 bytes: timestamp
    * 3 bytes: machine identifier
    * 2 bytes: process ID
    * 3 bytes: counter
2. **Select Bits**: To create a short code, specific bits are selected (e.g., from timestamp and counter). The exact selection determines the uniqueness and collision probability. *Note: The previous description mentioning 22 bits of timestamp and 16 bits of counter might be inaccurate or outdated based on the `/v1/shortener` endpoint's behavior.* A common approach is to use a dedicated shortener mapping in the database.
3. **Base36 Encode**: The selected data (or a generated unique sequence) is encoded into a Base36 string (0-9, A-Z), typically padded to a fixed length (e.g., 6 characters).

**Retrieval Process (Using `/v1/shortener/{short_code}`):**
1. **Input**: Provide the 6-character Base36 `short_code`.
2. **Lookup**: The server looks up this `short_code` in its shortener mapping table or collection.
3. **Return**: If found, the server returns the corresponding full 24-character hexadecimal `object_id` (the original Order ID).

This `/v1/shortener` endpoint simplifies retrieving the full ID from the short code without needing client-side decoding logic.

## WebSocket API

The WebSocket API provides real-time notifications for order status changes, particularly when orders are fulfilled.

### Order Notification WebSocket

**URL**: `ws://<host>:8080/ws/orderNotification`

**Method**: `WebSocket`

**Auth required**: `No`

**Description**: Establishes a WebSocket connection to receive real-time notifications for a specific order. The WebSocket remains open until the order is marked as fulfilled, at which point the server will send a notification and close the connection.

#### Connection Parameters (Query String):

```
order_id: String  // Required - The MongoDB ObjectID of the order to monitor
topic: String     // Optional - The topic to subscribe to (default: "orders")
```

#### Response Messages:

Messages sent from the server are JSON objects with the following structure:

```json
{
  "type": String,     // Message type (e.g., "welcome", "order_completed")
  "topic": String,    // The topic (usually "orders")
  "payload": Object   // Message content, varies by message type
}
```

**Message Types:**

1. **`welcome` message**:
   - Sent immediately after connection is established
   - Payload format:

```json
{
  "message": "Websocket connection established",
  "order_id": String,
  "time": String      // ISO DateTime format
}
```

2. **`order_completed` message**:
   - Sent when the order status changes to "fulfilled"
   - After this message, the connection will be closed by the server
   - Payload format:

```json
{
  "order_id": String,
  "restaurant_id": String,
  "status": "fulfilled",
  "timestamp": String,    // ISO DateTime format
  "message": "Your order has been completed"
}
```

#### Error Responses:

- **Invalid order format**:

**HTTP** 400: Bad Request
```json
{
  "error": "Invalid order ID format"
}
```

- **Missing order ID**:

**HTTP** 400: Bad Request
```json
{
  "error": "Missing order_id parameter"
}
```

- **Order not found**:

**HTTP** 404: Not Found
```json
{
  "error": "Order not found"
}
```

- **Order already notified**:

**HTTP** 409: Conflict
```json
{
  "error": "Order has already been notified",
  "notifiedAt": String  // ISO DateTime when the order was notified
}
```

### Notification API (For admin/backend use)

These endpoints allow other services to trigger notifications through the WebSocket system.

#### Send General Notification

**URL**: `/api/notify`

**Method**: `POST`

**Auth required**: `No` (Internal API, should be secured in production)

**Content-Type**: `application/json`

**Description**: Sends a notification to clients subscribed to a specific topic.

**Request Body**:
```json
{
  "type": String,        // Notification type
  "topic": String,       // Topic to broadcast to
  "target_ids": [        // Optional array of user IDs to target
    String
  ],
  "payload": Object      // Any JSON payload to send to clients
}
```

**Response**:
```json
{
  "status": "notification sent"
}
```

#### Send Order Notification

**URL**: `/api/notify/order`

**Method**: `POST`

**Auth required**: `No` (Internal API, should be secured in production)

**Content-Type**: `application/json`

**Description**: Sends a notification specifically for an order.

**Request Body**:
```json
{
  "order_id": String,        // Order ID to notify
  "status": String,          // Order status (e.g., "completed", "delivered")
  "restaurant_id": String,   // Restaurant ID
  "order_detail": Object     // Optional order details
}
```

**Response**:
```json
{
  "status": "order notification sent",
  "order_id": String
}
```

### Test Client

A test client for WebSocket connections is available at `http://<host>:8080/test`. This web page allows you to test WebSocket connections and observe real-time notifications.