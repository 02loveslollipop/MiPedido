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

# Restaurant types associated with names
RESTAURANT_TYPES = {
    "Burger Heaven": "Fast Food",
    "Pizza Palace": "Italian",
    "Taco Time": "Mexican",
    "Sushi Supreme": "Japanese",
    "Pasta Paradise": "Italian", 
    "Mediterranean Magic": "Mediterranean",
    "Veggie Delights": "Vegetarian",
    "Steak House": "American",
    "Seafood Sensation": "Seafood",
    "Breakfast Club": "Breakfast"
}

# Restaurant descriptions
RESTAURANT_DESCRIPTIONS = {
    "Burger Heaven": "The best burgers in town with a variety of options for all tastes.",
    "Pizza Palace": "Authentic Italian pizzas with fresh ingredients and crispy crust.",
    "Taco Time": "Authentic Mexican tacos with homemade salsas and fresh toppings.",
    "Sushi Supreme": "Fresh sushi and sashimi prepared by experienced Japanese chefs.",
    "Pasta Paradise": "Homemade pasta dishes with authentic Italian sauces.",
    "Mediterranean Magic": "Delicious Mediterranean cuisine with fresh ingredients.",
    "Veggie Delights": "Healthy vegetarian and vegan options for conscious eaters.",
    "Steak House": "Premium quality steaks cooked to perfection.",
    "Seafood Sensation": "Fresh seafood delivered daily from local fishermen.",
    "Breakfast Club": "Start your day with our delicious breakfast options."
}

# Sample positions for restaurants (latitude, longitude)
RESTAURANT_POSITIONS = {
    "Burger Heaven": {"lat": 40.7128, "lng": -74.0060},
    "Pizza Palace": {"lat": 40.7282, "lng": -73.9942},
    "Taco Time": {"lat": 40.7489, "lng": -73.9680},
    "Sushi Supreme": {"lat": 40.7831, "lng": -73.9712},
    "Pasta Paradise": {"lat": 40.7214, "lng": -74.0052},
    "Mediterranean Magic": {"lat": 40.7551, "lng": -73.9815},
    "Veggie Delights": {"lat": 40.7437, "lng": -73.9873},
    "Steak House": {"lat": 40.7589, "lng": -73.9851},
    "Seafood Sensation": {"lat": 40.7061, "lng": -74.0119},
    "Breakfast Club": {"lat": 40.7411, "lng": -74.0079}
}

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
    db.reviews.delete_many({})  # Clear existing reviews
    
    print("Creating restaurants...")
    restaurant_ids = create_restaurants(db)
    
    # Find the ID of "Burger Heaven" for special handling
    burger_heaven_id = None
    for restaurant_id in restaurant_ids:
        restaurant = db.restaurants.find_one({"_id": ObjectId(restaurant_id)})
        if restaurant and restaurant["name"] == "Burger Heaven":
            burger_heaven_id = str(restaurant_id)
            break
    
    if not burger_heaven_id:
        print("ERROR: Burger Heaven restaurant not found!")
        return client
    
    print("Creating users...")
    create_users(db, restaurant_ids, burger_heaven_id)
    
    print("Creating products for each restaurant...")
    product_ids_by_restaurant = create_products(db, restaurant_ids)
    
    print("Creating sample orders for Burger Heaven...")
    create_orders_for_burger_heaven(db, burger_heaven_id, product_ids_by_restaurant.get(burger_heaven_id, []))
    
    print("Creating anonymous reviews for restaurants...")
    create_reviews(db, restaurant_ids)
    
    print("Database seeded successfully!")
    return client

def create_users(db, restaurant_ids, burger_heaven_id):
    """Create test users with restaurant controls"""
    user_ids = []
    
    # Assign Burger Heaven to the main admin user
    admin_restaurant_assignments = {
        "admin": [burger_heaven_id]
    }
    
    # Assign random restaurants to other admin users
    other_restaurants = [rid for rid in restaurant_ids if rid != burger_heaven_id]
    for restaurant_id in other_restaurants:
        # Randomly assign each restaurant to admin or manager (but not the main admin)
        admin_user = random.choice([user for user in TEST_USERS if user["is_admin"] and user["username"] != "admin"])
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
    """Create dummy restaurants with the new fields"""
    restaurant_ids = []
    
    for i in range(len(RESTAURANT_NAMES)):
        restaurant_name = RESTAURANT_NAMES[i]
        
        restaurant = {
            "name": restaurant_name,
            "img_url": f"{FOOD_IMAGES[i]}?w=400&h=300",
            "rating": round(random.uniform(3.0, 5.0), 1),  # Random rating between 3.0 and 5.0
            "type": RESTAURANT_TYPES.get(restaurant_name, "Other"),
            "description": RESTAURANT_DESCRIPTIONS.get(restaurant_name, f"Delicious food at {restaurant_name}"),
            "position": RESTAURANT_POSITIONS.get(restaurant_name, {"lat": 40.7128, "lng": -74.0060}),  # Default to NYC coords
            "_review_count": 0  # Initialize review count to 0
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

def create_orders_for_burger_heaven(db, burger_heaven_id, burger_heaven_products):
    """Create sample orders for Burger Heaven restaurant only"""
    if not burger_heaven_products:
        print("No products found for Burger Heaven, skipping order creation")
        return
    
    # Get products for this restaurant
    products = list(db.products.find({"restaurant_id": burger_heaven_id}))
    
    # Create 5 sample orders
    for i in range(5):
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
            "restaurant_id": burger_heaven_id,
            "users": users,
            "created_at": datetime.now()
        }
        
        result = db.orders.insert_one(order)
        print(f"Created order {i+1}/5 for Burger Heaven with {user_count} users (Order ID: {result.inserted_id})")

def create_reviews(db, restaurant_ids):
    """Create anonymous reviews for restaurants in the reviews collection"""
    review_count = 0
    
    for restaurant_id in restaurant_ids:
        # Get restaurant info
        restaurant = db.restaurants.find_one({"_id": ObjectId(restaurant_id)})
        restaurant_name = restaurant['name']
        
        # Generate 3-10 reviews per restaurant
        num_reviews = random.randint(3, 10)
        
        for _ in range(num_reviews):
            # Generate random rating between 1 and 5 (whole numbers only)
            rating = random.randint(1, 5)
                
            # Create review (anonymous - only restaurant_id, rating, and status)
            review = {
                "restaurant_id": restaurant_id,
                "rating": rating,
                "status": "pending",  # All new reviews start as pending
                "created_at": datetime.now()
            }
            
            # Insert into reviews collection
            result = db.reviews.insert_one(review)
            review_count += 1
            
            print(f"Created pending review for {restaurant_name}: {rating} stars (ID: {result.inserted_id})")
    
    print(f"Total pending reviews created: {review_count}")

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