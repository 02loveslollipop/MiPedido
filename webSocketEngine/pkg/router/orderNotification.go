package router

import (
	"log"
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
	"websocketengine.mipedido/pkg/utils"
)

func Routes(route *gin.Engine) {
	// Start the client hub in a goroutine
	go utils.Hub.Run()

	// Create a new router group for the WebSocket routes
	wsGroup := route.Group("/ws")
	{
		// Define the WebSocket endpoint
		wsGroup.GET("/orderNotification", orderNotificationHandler)
	}
}

func orderNotificationHandler(c *gin.Context) {
	// Get query parameters
	userID := c.Query("user_id")
	if userID == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Missing user_id parameter"})
		return
	}

	userType := c.DefaultQuery("user_type", "customer")
	topic := c.DefaultQuery("topic", "orders")

	// Get the Upgrader instance
	upgrader := utils.GetInstance()

	// Upgrade the HTTP connection to a WebSocket connection
	conn, err := upgrader.Upgrade(c.Writer, c.Request, nil)
	if err != nil {
		log.Println("Error during connection upgrade:", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to upgrade connection"})
		return
	}

	// Create a new client
	client := utils.NewClient(conn, userID, userType, topic)

	// Register the client
	utils.Hub.Register <- client

	// Start client goroutines
	go client.WritePump()
	go client.ReadPump()

	// Send a welcome message to the client
	welcomePayload := map[string]string{
		"message": "Welcome to the MiPedido order notification service",
		"user_id": userID,
		"time":    time.Now().Format(time.RFC3339),
	}

	err = utils.SendToClient(client, "welcome", welcomePayload)
	if err != nil {
		log.Println("Error sending welcome message:", err)
	}
}
