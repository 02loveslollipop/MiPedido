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


<!-- 
## Servidor

### login

Inicia sesion en el servidor. Retorna un token de acceso y el id del usuario. Si el usuario no existe, retorna un error.

- input:
```json
{
    "username": String,
    "password": String,
}
```

- output:
```json
{
    "access_token": String,
    "user_id": String,
}
```

### getOrderById

Retorna la orden de un usuario. Si no existe, retorna un error. Si el pedido es de otro restaurante, retorna un error. De lo contrario, retorna la orden agregada de todos los usuarios que la componen.

> Se realiza una agregacion por producto y por ingredientes es decir se suman todos los productos iguales y con mismo ingrediente y se retorna la cantidad total de cada uno.

- input:
```json
{
    "order_id": String,
}
```

- output:
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





 -->
