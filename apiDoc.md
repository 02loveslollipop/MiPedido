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
            "id": String
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

***Description**: Adds a user to an existing order. Returns the user id (for the specific order). If the order does not exist, it returns an error.

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
    "user_id": String
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

### Close Order (Get final order)

**URL**: `/v1/order/{order_id}`
**Method**: `PUT`
**Auth required**: `Yes`
**Auth type**: `JWT`
**Content-Type**: `application/json`
**Description**: Closes the order and returns the final order with all the products and ingredients agregated by product and ingredients (So if two users have the same product with the same ingredients, it will be agregated. But if at least one ingredient is different, it will be considered a different product). If the order does not exist, it returns an error. If the bearer token is not valid, it returns an error. If the user exist, but the in the users collection the given user id is not related to the restaurant of the order, it returns an error. (The users collection must have a `controls` field in the user object with the restaurant id).

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
- Order found.

***HTTP** 200: OK

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
    date_completed: String,
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

## User

### Login

**URL**: `/v1/login`

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


