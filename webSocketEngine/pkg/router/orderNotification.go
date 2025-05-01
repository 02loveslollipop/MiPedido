package router

import (
	"log"
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/bson/primitive"
	"go.mongodb.org/mongo-driver/mongo"
	"websocketengine.mipedido/pkg/models"
	"websocketengine.mipedido/pkg/services"
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
	// Get order_id parameter
	orderID := c.Query("order_id")
	if orderID == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Missing order_id parameter"})
		return
	}

	topic := c.DefaultQuery("topic", "orders")

	// Check if order has already been notified
	orderWatcher := services.GetOrderWatcher()
	orderObjID, err := primitive.ObjectIDFromHex(orderID)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid order ID format"})
		return
	}

	// Find the order in MongoDB
	var order models.Order
	err = orderWatcher.GetCollection().FindOne(c, bson.M{"_id": orderObjID}).Decode(&order)
	if err != nil {
		if err == mongo.ErrNoDocuments {
			c.JSON(http.StatusNotFound, gin.H{"error": "Order not found"})
		} else {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to fetch order: " + err.Error()})
		}
		return
	}

	// Check if the order has already been notified
	notifiedAtTime := order.NotifiedAt.Time()
	zeroDate := time.Date(1970, 1, 1, 0, 0, 0, 0, time.UTC)
	if notifiedAtTime.After(zeroDate) { // Check if the order has been notified
		c.JSON(http.StatusConflict, gin.H{
			"error":      "Order has already been notified",
			"notifiedAt": notifiedAtTime,
		})
		
		return
	}

	// Get the Upgrader instance
	upgrader := utils.GetInstance()

	// Upgrade the HTTP connection to a WebSocket connection
	conn, err := upgrader.Upgrade(c.Writer, c.Request, nil)
	if err != nil {
		log.Println("Error during connection upgrade:", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to upgrade connection"})
		return
	}

	// Create a unique connection ID
	connectionID := "conn_" + primitive.NewObjectID().Hex()

	// Create a new client with only the connection ID and order ID
	client := utils.NewClient(conn, connectionID, topic)

	// Associate client with the specific order ID
	client.OrderID = orderID

	// Register the client with the hub
	utils.Hub.Register <- client

	// Register the order for watching in the OrderChangeWatcher
	services.GetOrderWatcher().AddOrderToWatch(orderID)

	// Start client goroutines
	go client.WritePump()
	go client.ReadPump()

	// Send a welcome message to the client
	welcomePayload := map[string]interface{}{
		"message":  "Websocket connection established",
		"order_id": orderID,
		"time":     time.Now().Format(time.RFC3339),
	}

	err = utils.SendToClient(client, "welcome", welcomePayload)
	if err != nil {
		log.Println("Error sending welcome message:", err)
	}
}
