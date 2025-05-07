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

func main() {

	// Load environment variables from .env file if it exists
	if err := godotenv.Load(); err != nil {
		log.Println("No .env file found, using environment variables")
	}

	ctx := context.Background()

	// Load environment variables
	mongoURI := os.Getenv("MONGODB_URL")
	redisHost := os.Getenv("REDIS_HOST")
	redisPort := os.Getenv("REDIS_PORT")
	redisPass := os.Getenv("REDIS_PASSWORD")
	if mongoURI == "" || redisHost == "" || redisPort == "" {
		log.Fatal("Missing required environment variables: MONGODB_URL, REDIS_HOST, REDIS_PORT")
	}

	// Connect to MongoDB
	mongoClient, err := mongo.Connect(ctx, options.Client().ApplyURI(mongoURI))
	if err != nil {
		log.Fatalf("MongoDB connection error: %v", err)
	}
	db := mongoClient.Database("mipedido")

	// Connect to Redis
	rdb := redis.NewClient(&redis.Options{
		Addr:     fmt.Sprintf("%s:%s", redisHost, redisPort),
		Password: redisPass,
		DB:       0,
	})

	// Create RediSearch indices (ignore error if already exists)
	createRediSearchIndices(ctx, rdb)

	// Fetch all restaurants
	restCursor, err := db.Collection("restaurants").Find(ctx, bson.M{})
	if err != nil {
		log.Fatalf("MongoDB restaurant fetch error: %v", err)
	}
	var restaurants []bson.M
	if err = restCursor.All(ctx, &restaurants); err != nil {
		log.Fatalf("MongoDB restaurant decode error: %v", err)
	}

	// Fetch all products
	prodCursor, err := db.Collection("products").Find(ctx, bson.M{})
	if err != nil {
		log.Fatalf("MongoDB product fetch error: %v", err)
	}

	log.Printf("Got %d restaurants from MongoDB", len(restaurants))

	var products []bson.M
	if err = prodCursor.All(ctx, &products); err != nil {
		log.Fatalf("MongoDB product decode error: %v", err)
	}

	log.Printf("Got and decoded %d products from MongoDB", len(products))

	// Build a map of restaurantID -> []products for products_text
	productsByRestaurant := make(map[string][]bson.M)
	for _, prod := range products {
		restID := ""
		if rid, ok := prod["restaurant_id"]; ok {
			switch v := rid.(type) {
			case string:
				restID = v
			case primitive.ObjectID:
				restID = v.Hex()
			}
		}
		if restID != "" {
			productsByRestaurant[restID] = append(productsByRestaurant[restID], prod)
		}
	}

	log.Printf("Indexed %d products by restaurant", len(productsByRestaurant))

	// Index restaurants in Redis
	for _, rest := range restaurants {
		id := ""
		if oid, ok := rest["_id"].(primitive.ObjectID); ok {
			id = oid.Hex()
		} else if s, ok := rest["_id"].(string); ok {
			id = s
		}
		if id == "" {
			continue
		}
		key := fmt.Sprintf("restaurant:%s", id)

		// Build products_text
		products := productsByRestaurant[id]
		var productsTextParts []string
		for _, prod := range products {
			name, _ := prod["name"].(string)
			desc, _ := prod["description"].(string)
			productsTextParts = append(productsTextParts, name+" "+desc)
		}
		productsText := strings.Join(productsTextParts, " ")

		// Prepare restaurant fields
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

	// Index products in Redis
	for _, prod := range products {
		id := ""
		if oid, ok := prod["_id"].(primitive.ObjectID); ok {
			id = oid.Hex()
		} else if s, ok := prod["_id"].(string); ok {
			id = s
		}
		restID := ""
		if rid, ok := prod["restaurant_id"]; ok {
			switch v := rid.(type) {
			case string:
				restID = v
			case primitive.ObjectID:
				restID = v.Hex()
			}
		}
		if id == "" {
			continue
		}
		key := fmt.Sprintf("product:%s", id)

		// Flatten ingredients to a space-separated string
		ingredients := ""
		if arr, ok := prod["ingredients"].(primitive.A); ok {
			var parts []string
			for _, ing := range arr {
				if s, ok := ing.(string); ok {
					parts = append(parts, s)
				}
			}
			ingredients = strings.Join(parts, " ")
		}

		fields := map[string]interface{}{
			"name":          getString(prod["name"]),
			"description":   getString(prod["description"]),
			"ingredients":   ingredients,
			"restaurant_id": restID,
		}
		if err := rdb.HSet(ctx, key, fields).Err(); err != nil {
			log.Printf("Redis HSet error for product %s: %v", id, err)
		}
	}

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
