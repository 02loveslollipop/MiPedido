package database

import (
	"context"
	"fmt"
	"log"
	"os"
	"sync"
	"time"

	"github.com/joho/godotenv"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

var (
	client      *mongo.Client
	database    *mongo.Database
	once        sync.Once
	isConnected bool = false
)

// ConnectMongoDB establishes a connection to MongoDB
func ConnectMongoDB() error {
	var err error

	once.Do(func() {
		// Try to load .env file
		err = godotenv.Load()
		if err != nil {
			log.Printf("Warning: Error loading .env file: %v (this is normal in production)", err)
		}

		// Get MongoDB connection string from environment variable or use default
		mongoURI := os.Getenv("MONGODB_URL")
		if mongoURI == "" {
			mongoURI = "mongodb://localhost:27017"
			log.Printf("MONGODB_URL not set, using default: %s", mongoURI)
		}

		// Get database name from environment variable or use default
		dbName := os.Getenv("DATABASE_NAME")
		if dbName == "" {
			dbName = "mipedido"
			log.Printf("DATABASE_NAME not set, using default: %s", dbName)
		}

		// Set connection timeout
		ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
		defer cancel()

		// Connect to MongoDB
		clientOptions := options.Client().ApplyURI(mongoURI)
		client, err = mongo.Connect(ctx, clientOptions)
		if err != nil {
			log.Printf("Failed to connect to MongoDB: %v", err)
			return
		}

		// Verify connection
		err = client.Ping(ctx, nil)
		if err != nil {
			log.Printf("Failed to ping MongoDB: %v", err)
			return
		}

		database = client.Database(dbName)
		isConnected = true
		log.Printf("Connected to MongoDB database: %s", dbName)
	})

	if !isConnected {
		return fmt.Errorf("failed to connect to MongoDB: %v", err)
	}

	return nil
}

// GetCollection returns a MongoDB collection
func GetCollection(collectionName string) *mongo.Collection {
	if !isConnected || database == nil {
		log.Fatal("MongoDB not connected. Call ConnectMongoDB first")
		return nil
	}
	return database.Collection(collectionName)
}

// DisconnectMongoDB closes the MongoDB connection
func DisconnectMongoDB() {
	if client != nil {
		ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
		defer cancel()

		if err := client.Disconnect(ctx); err != nil {
			log.Printf("Error disconnecting from MongoDB: %v", err)
		} else {
			log.Println("MongoDB connection closed")
			isConnected = false
		}
	}
}
