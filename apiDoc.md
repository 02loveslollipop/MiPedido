> NOTA: El contenido del QR es el id del pedido.

# Documentación API

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


