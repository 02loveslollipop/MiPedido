package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"os"
	"strings"

	"github.com/go-redis/redis/v8"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/bson/primitive"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
	"github.com/joho/godotenv"
)

func resolveID(val interface{}) string {
	switch v := val.(type) {
	case primitive.ObjectID:
		return v.Hex()
	case string:
		return v
	default:
		return ""
	}
}

func fetchCollection(ctx context.Context, db *mongo.Database, collectionName string) []bson.M {
	cursor, err := db.Collection(collectionName).Find(ctx, bson.M{})
	if err != nil {
		log.Fatalf("MongoDB %s fetch error: %v", collectionName, err)
	}
	var docs []bson.M
	if err = cursor.All(ctx, &docs); err != nil {
		log.Fatalf("MongoDB %s decode error: %v", collectionName, err)
	}
	return docs
}

func groupProductsByRestaurant(products []bson.M) map[string][]bson.M {
	productsByRestaurant := make(map[string][]bson.M)
	for _, prod := range products {
		restID := resolveID(prod["restaurant_id"])
		if restID != "" {
			productsByRestaurant[restID] = append(productsByRestaurant[restID], prod)
		}
	}
	return productsByRestaurant
}

func buildProductsText(products []bson.M) string {
	var productsTextParts []string
	for _, prod := range products {
		name, _ := prod["name"].(string)
		desc, _ := prod["description"].(string)
		productsTextParts = append(productsTextParts, name+" "+desc)
	}
	return strings.Join(productsTextParts, " ")
}

func indexRestaurants(ctx context.Context, rdb *redis.Client, restaurants []bson.M, productsByRestaurant map[string][]bson.M) {
	for _, rest := range restaurants {
		id := resolveID(rest["_id"])
		if id == "" {
			continue
		}
		key := fmt.Sprintf("restaurant:%s", id)
		productsText := buildProductsText(productsByRestaurant[id])

		fields := map[string]interface{}{
			"name":          getString(rest["name"]),
			"description":   getString(rest["description"]),
			"type":          getString(rest["type"]),
			"products_text": productsText,
		}
		if err := rdb.HSet(ctx, key, fields).Err(); err != nil {
			log.Printf("Redis HSet error for restaurant %s: %v", id, err)
		}
	}
	log.Printf("Indexed %d restaurants in Redis", len(restaurants))
}

func flattenIngredients(val interface{}) string {
	arr, ok := val.(primitive.A)
	if !ok {
		return ""
	}
	var parts []string
	for _, ing := range arr {
		if s, ok := ing.(string); ok {
			parts = append(parts, s)
		}
	}
	return strings.Join(parts, " ")
}

func indexProducts(ctx context.Context, rdb *redis.Client, products []bson.M) {
	for _, prod := range products {
		id := resolveID(prod["_id"])
		if id == "" {
			continue
		}
		key := fmt.Sprintf("product:%s", id)
		restID := resolveID(prod["restaurant_id"])

		fields := map[string]interface{}{
			"name":          getString(prod["name"]),
			"description":   getString(prod["description"]),
			"ingredients":   flattenIngredients(prod["ingredients"]),
			"restaurant_id": restID,
		}
		if err := rdb.HSet(ctx, key, fields).Err(); err != nil {
			log.Printf("Redis HSet error for product %s: %v", id, err)
		}
	}
}

func main() {
	if err := godotenv.Load(); err != nil {
		log.Println("No .env file found, using environment variables")
	}

	ctx := context.Background()

	mongoURI := os.Getenv("MONGODB_URL")
	redisHost := os.Getenv("REDIS_HOST")
	redisPort := os.Getenv("REDIS_PORT")
	redisPass := os.Getenv("REDIS_PASSWORD")
	if mongoURI == "" || redisHost == "" || redisPort == "" {
		log.Fatal("Missing required environment variables: MONGODB_URL, REDIS_HOST, REDIS_PORT")
	}

	mongoClient, err := mongo.Connect(ctx, options.Client().ApplyURI(mongoURI))
	if err != nil {
		log.Fatalf("MongoDB connection error: %v", err)
	}
	db := mongoClient.Database("mipedido")

	rdb := redis.NewClient(&redis.Options{
		Addr:     fmt.Sprintf("%s:%s", redisHost, redisPort),
		Password: redisPass,
		DB:       0,
	})

	createRediSearchIndices(ctx, rdb)

	restaurants := fetchCollection(ctx, db, "restaurants")
	products := fetchCollection(ctx, db, "products")

	log.Printf("Got %d restaurants from MongoDB", len(restaurants))
	log.Printf("Got and decoded %d products from MongoDB", len(products))

	productsByRestaurant := groupProductsByRestaurant(products)
	log.Printf("Indexed %d products by restaurant", len(productsByRestaurant))

	indexRestaurants(ctx, rdb, restaurants, productsByRestaurant)
	indexProducts(ctx, rdb, products)

	log.Println("MongoDB data dumped to Redis and indexed successfully.")
}

func getString(val interface{}) string {
	if val == nil {
		return ""
	}
	switch v := val.(type) {
	case string:
		return v
	case []byte:
		return string(v)
	default:
		b, _ := json.Marshal(v)
		return string(b)
	}
}

func createRediSearchIndices(ctx context.Context, rdb *redis.Client) {
	// Restaurant index
	restaurantIdx := []interface{}{
		"restaurant-idx", "ON", "HASH", "PREFIX", "1", "restaurant:",
		"SCHEMA",
		"name", "TEXT", "WEIGHT", "5.0",
		"description", "TEXT", "WEIGHT", "1.0",
		"type", "TEXT", "WEIGHT", "2.0",
		"products_text", "TEXT", "WEIGHT", "1.0",
	}
	if err := rdb.Do(ctx, append([]interface{}{"FT.CREATE"}, restaurantIdx...)...).Err(); err != nil {
		if !strings.Contains(err.Error(), "Index already exists") {
			log.Printf("Error creating restaurant-idx: %v", err)
		}
	}

	// Product index
	productIdx := []interface{}{
		"product-idx", "ON", "HASH", "PREFIX", "1", "product:",
		"SCHEMA",
		"name", "TEXT", "WEIGHT", "5.0",
		"description", "TEXT", "WEIGHT", "1.0",
		"ingredients", "TEXT", "WEIGHT", "2.0",
		"restaurant_id", "TEXT", "WEIGHT", "1.0",
	}
	if err := rdb.Do(ctx, append([]interface{}{"FT.CREATE"}, productIdx...)...).Err(); err != nil {
		if !strings.Contains(err.Error(), "Index already exists") {
			log.Printf("Error creating product-idx: %v", err)
		}
	}
}
