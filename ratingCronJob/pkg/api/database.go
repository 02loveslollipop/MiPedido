package api

import (
	"context"
	"log"
	"os"
	"time"
	"fmt"
	"github.com/joho/godotenv"

	"go.mongodb.org/mongo-driver/v2/mongo"
	"go.mongodb.org/mongo-driver/v2/mongo/options"
)

// ConnectDatabase establishes a connection to MongoDB
func ConnectDatabase() (*mongo.Database, error) {

	// Dump .env file to environment variables

	err := godotenv.Load()

	if err != nil {
		log.Printf("Error loading .env file, if you are running in production, you can ignore this error: %v", err)
		return nil, err
	}

	// Get MongoDB connection string from environment variable or use default
	mongoURI := os.Getenv("MONGODB_URL")
	if mongoURI == "" {
		return nil, fmt.Errorf("MONGODB_URL environment variable is not set")
	}

	// Get database name from environment variable or use default
	dbName := os.Getenv("DATABASE_NAME")
	if dbName == "" {
		dbName = "mipedido"
	}

	// Set connection timeout
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	// Connect to MongoDB
	clientOptions := options.Client().ApplyURI(mongoURI)
	client, err := mongo.Connect(clientOptions)
	if err != nil {
		log.Printf("Failed to connect to MongoDB: %v", err)
		return nil, err
	}

	// Verify connection
	err = client.Ping(ctx, nil)
	if err != nil {
		log.Printf("Failed to ping MongoDB: %v", err)
		return nil, err
	}

	log.Printf("Connected to MongoDB database: %s", dbName)
	return client.Database(dbName), nil
}
