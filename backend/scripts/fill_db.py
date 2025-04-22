import random
import os
import sys
from pymongo import MongoClient
from bson import ObjectId
import dotenv
from datetime import datetime
import hashlib

# Load environment variables from .env file
dotenv.load_dotenv()

# MongoDB connection details
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "mipedido")

# Sample data
RESTAURANT_NAMES = [
    "Burger Heaven", "Pizza Palace", "Taco Time", "Sushi Supreme", "Pasta Paradise",
    "Mediterranean Magic", "Veggie Delights", "Steak House", "Seafood Sensation", "Breakfast Club"
]

FOOD_IMAGES = [
    "https://images.unsplash.com/photo-1571091718767-18b5b1457add",
    "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38",
    "https://images.unsplash.com/photo-1565299507177-b0ac66763828",
    "https://images.unsplash.com/photo-1563379926898-05f4575a45d8",
    "https://images.unsplash.com/photo-1559847844-5315695dadae",
    "https://images.unsplash.com/photo-1512621776951-a57141f2eefd",
    "https://images.unsplash.com/photo-1544025162-d76694265947",
    "https://images.unsplash.com/photo-1561758033-d89a9ad46330",
    "https://images.unsplash.com/photo-1529042410759-befb1204b468",
    "https://images.unsplash.com/photo-1504674900247-0877df9cc836"
]

PRODUCT_TYPES = {
    "Burger": {
        "names": ["Classic Burger", "Cheese Burger", "Bacon Burger", "Veggie Burger", "Double Cheeseburger"],
        "ingredients": ["Beef patty", "Cheese", "Lettuce", "Tomato", "Onion", "Pickles", "Bacon", "Special sauce", "Mushrooms"],
        "price_range": (8.99, 15.99)
    },
    "Pizza": {
        "names": ["Margherita", "Pepperoni", "Hawaiian", "Vegetarian", "Meat Lovers"],
        "ingredients": ["Mozzarella", "Tomato sauce", "Pepperoni", "Ham", "Pineapple", "Mushrooms", "Bell peppers", "Olives", "Onion"],
        "price_range": (10.99, 18.99)
    },
    "Taco": {
        "names": ["Beef Taco", "Chicken Taco", "Fish Taco", "Veggie Taco", "Steak Taco"],
        "ingredients": ["Tortilla", "Beef", "Chicken", "Fish", "Lettuce", "Tomato", "Cheese", "Sour cream", "Guacamole", "Salsa"],
        "price_range": (7.99, 12.99)
    },
    "Sushi": {
        "names": ["California Roll", "Spicy Tuna Roll", "Dragon Roll", "Vegetable Roll", "Salmon Nigiri"],
        "ingredients": ["Rice", "Nori", "Crab", "Avocado", "Cucumber", "Tuna", "Salmon", "Eel", "Tempura", "Spicy mayo"],
        "price_range": (12.99, 24.99)
    },
    "Pasta": {
        "names": ["Spaghetti Bolognese", "Fettuccine Alfredo", "Penne Arrabbiata", "Lasagna", "Carbonara"],
        "ingredients": ["Pasta", "Tomato sauce", "Cream sauce", "Ground beef", "Parmesan", "Garlic", "Basil", "Bacon", "Egg", "Chili flakes"],
        "price_range": (9.99, 16.99)
    }
}

# Sample user data - admin users will control restaurants
TEST_USERS = [
    {"username": "admin", "password": "admin123", "is_admin": True},
    {"username": "user1", "password": "pass1234", "is_admin": False},
    {"username": "user2", "password": "securepass", "is_admin": False},
    {"username": "manager", "password": "test123", "is_admin": True},
    {"username": "customer", "password": "customer456", "is_admin": False}
]

def seed_database():
    """Seed the database with dummy data"""
    # Connect to MongoDB
    client = MongoClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    
    # Clear existing data
    print("Clearing existing data...")
    db.restaurants.delete_many({})
    db.products.delete_many({})
    db.orders.delete_many({})
    db.users.delete_many({})
    
    print("Creating restaurants...")
    restaurant_ids = create_restaurants(db)
    
    print("Creating users...")
    create_users(db, restaurant_ids)
    
    print("Creating products for each restaurant...")
    create_products(db, restaurant_ids)
    
    print("Creating sample orders...")
    create_orders(db, restaurant_ids)
    
    print("Database seeded successfully!")
    return client

def create_users(db, restaurant_ids):
    """Create test users with restaurant controls"""
    user_ids = []
    
    # Assign random restaurants to admin users
    admin_restaurant_assignments = {}
    for restaurant_id in restaurant_ids:
        # Randomly assign each restaurant to admin or manager
        admin_user = random.choice([user for user in TEST_USERS if user["is_admin"]])
        if admin_user["username"] not in admin_restaurant_assignments:
            admin_restaurant_assignments[admin_user["username"]] = []
        admin_restaurant_assignments[admin_user["username"]].append(restaurant_id)
    
    for user_data in TEST_USERS:
        # Hash the password (simple SHA-256 hash for demonstration purposes)
        hashed_password = hashlib.sha256(user_data["password"].encode()).hexdigest()
        
        # Assign restaurant controls for admin users
        controls = []
        if user_data["is_admin"]:
            controls = admin_restaurant_assignments.get(user_data["username"], [])
        
        user = {
            "username": user_data["username"],
            "hashed_password": hashed_password,
            "controls": controls
        }
        
        # Check if user already exists
        existing_user = db.users.find_one({"username": user_data["username"]})
        if existing_user:
            print(f"User {user_data['username']} already exists, skipping...")
            user_ids.append(str(existing_user["_id"]))
            continue
        
        # Insert the new user
        result = db.users.insert_one(user)
        user_ids.append(str(result.inserted_id))
        
        controls_info = f" (Controls {len(controls)} restaurants)" if controls else ""
        print(f"Created user: {user['username']}{controls_info} (ID: {result.inserted_id})")
    
    return user_ids

def create_restaurants(db):
    """Create dummy restaurants"""
    restaurant_ids = []
    
    for i in range(len(RESTAURANT_NAMES)):
        restaurant = {
            "name": RESTAURANT_NAMES[i],
            "img_url": f"{FOOD_IMAGES[i]}?w=400&h=300",
        }
        
        result = db.restaurants.insert_one(restaurant)
        restaurant_ids.append(str(result.inserted_id))
        print(f"Created restaurant: {restaurant['name']} (ID: {result.inserted_id})")
    
    return restaurant_ids

def create_products(db, restaurant_ids):
    """Create dummy products for each restaurant"""
    product_ids_by_restaurant = {}
    
    for restaurant_id in restaurant_ids:
        product_ids_by_restaurant[restaurant_id] = []
        restaurant = db.restaurants.find_one({"_id": ObjectId(restaurant_id)})
        restaurant_name = restaurant['name']
        
        # Determine which product types fit this restaurant's theme
        if "Burger" in restaurant_name:
            product_types = ["Burger"]
        elif "Pizza" in restaurant_name:
            product_types = ["Pizza"]
        elif "Taco" in restaurant_name:
            product_types = ["Taco"]
        elif "Sushi" in restaurant_name:
            product_types = ["Sushi"]
        elif "Pasta" in restaurant_name:
            product_types = ["Pasta"]
        else:
            # For other restaurants, pick 2-3 random product types
            product_types = random.sample(list(PRODUCT_TYPES.keys()), random.randint(2, 3))
        
        # Create products for this restaurant
        for product_type in product_types:
            for name in PRODUCT_TYPES[product_type]["names"]:
                # Choose 3-5 random ingredients
                available_ingredients = PRODUCT_TYPES[product_type]["ingredients"]
                ingredients = random.sample(available_ingredients, random.randint(3, min(5, len(available_ingredients))))
                
                # Generate a random price within the range for this product type
                min_price, max_price = PRODUCT_TYPES[product_type]["price_range"]
                price = round(random.uniform(min_price, max_price), 2)
                
                # Select a random image
                img_index = random.randint(0, len(FOOD_IMAGES) - 1)
                
                # Set active status (90% chance of being active)
                is_active = random.random() < 0.9
                
                product = {
                    "restaurant_id": restaurant_id,
                    "name": name,
                    "description": f"Delicious {name.lower()} made with premium ingredients",
                    "price": price,
                    "img_url": f"{FOOD_IMAGES[img_index]}?w=300&h=200",
                    "ingredients": ingredients,
                    "active": is_active
                }
                
                result = db.products.insert_one(product)
                product_id = str(result.inserted_id)
                product_ids_by_restaurant[restaurant_id].append(product_id)
                active_status = "active" if is_active else "inactive"
                print(f"Created product: {product['name']} ({active_status}) for {restaurant_name} (ID: {result.inserted_id})")
    
    return product_ids_by_restaurant

def create_orders(db, restaurant_ids):
    """Create sample orders with users and products"""
    # Create 5 sample orders
    for i in range(5):
        # Select a random restaurant
        restaurant_id = random.choice(restaurant_ids)
        
        # Get products for this restaurant
        products = list(db.products.find({"restaurant_id": restaurant_id}))
        
        if not products:
            continue
        
        # Generate 1-3 users for this order
        user_count = random.randint(1, 3)
        users = {}
        
        for j in range(user_count):
            user_id = str(ObjectId())
            
            # Each user orders 1-4 products
            user_products = []
            product_count = random.randint(1, 4)
            selected_products = random.sample(products, min(product_count, len(products)))
            
            for product in selected_products:
                # Select a random subset of ingredients
                selected_ingredients = random.sample(
                    product["ingredients"], 
                    random.randint(1, len(product["ingredients"]))
                )
                
                # Add product to user's order with quantity 1-3
                user_products.append({
                    "id": str(product["_id"]),
                    "name": product["name"],
                    "price": product["price"],
                    "img_url": product["img_url"],
                    "quantity": random.randint(1, 3),
                    "ingredients": selected_ingredients
                })
            
            users[user_id] = {"products": user_products}
        
        # Create the order
        order = {
            "restaurant_id": restaurant_id,
            "users": users,
            "created_at": datetime.now()
        }
        
        result = db.orders.insert_one(order)
        print(f"Created order {i+1}/5 with {user_count} users for restaurant ID: {restaurant_id} (Order ID: {result.inserted_id})")

def main():
    print(f"Connecting to MongoDB at {MONGODB_URL}")
    print(f"Using database: {DATABASE_NAME}")
    
    try:
        client = seed_database()
        client.close()
        print("Database connection closed")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()