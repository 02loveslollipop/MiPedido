package main

import (
	"log"
	"os"
	"os/signal"
	"syscall"

	"github.com/gin-gonic/gin"
	"websocketengine.mipedido/pkg/database"
	"websocketengine.mipedido/pkg/router"
	"websocketengine.mipedido/pkg/services"
	"websocketengine.mipedido/pkg/utils"
)

func main() {
	// Initialize the MongoDB connection
	log.Println("Connecting to MongoDB...")
	if err := database.ConnectMongoDB(); err != nil {
		log.Fatalf("Failed to connect to MongoDB: %v", err)
	}
	defer database.DisconnectMongoDB()

	// Initialize the order watcher service
	orderWatcher := services.GetOrderWatcher()
	if orderWatcher == nil {
		log.Fatalf("Failed to initialize order watcher service")
	}

	// Initialize the notification manager
	notifier := utils.GetNotifier()
	defer notifier.Shutdown()

	// Create a new Gin router
	r := gin.Default()

	// Add our custom middleware for logging non-2xx responses
	r.Use(utils.LogNon2xxResponses())

	// Add CORS middleware
	r.Use(func(c *gin.Context) {
		c.Writer.Header().Set("Access-Control-Allow-Origin", "*")
		c.Writer.Header().Set("Access-Control-Allow-Credentials", "true")
		c.Writer.Header().Set("Access-Control-Allow-Headers", "Content-Type, Content-Length, Accept-Encoding, X-CSRF-Token, Authorization, accept, origin, Cache-Control, X-Requested-With")
		c.Writer.Header().Set("Access-Control-Allow-Methods", "POST, OPTIONS, GET, PUT, DELETE")

		if c.Request.Method == "OPTIONS" {
			c.AbortWithStatus(204)
			return
		}

		c.Next()
	})

	// Root route for health check
	r.GET("/", func(c *gin.Context) {
		c.JSON(200, gin.H{
			"status": "MiPedido WebSocket Engine is running",
		})
	})

	// Register WebSocket routes
	router.Routes(r)

	// Register notification API routes
	router.RegisterNotificationAPI(r)

	// Register static file routes
	router.RegisterStaticRoutes(r)

	// Get the port from environment variable or use default
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	// Setup graceful shutdown
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)

	go func() {
		<-quit
		log.Println("Shutting down server...")
		notifier.Shutdown()
		os.Exit(0)
	}()

	// Start server
	log.Printf("MiPedido WebSocket Engine is starting on port %s", port)
	err := r.Run(":" + port)
	if err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}
