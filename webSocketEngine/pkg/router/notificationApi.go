package router

import (
	"net/http"

	"github.com/gin-gonic/gin"
	"websocketengine.mipedido/pkg/utils"
)

// RegisterNotificationAPI adds notification API routes to the router
func RegisterNotificationAPI(route *gin.Engine) {
	// Create a new router group for the notification API
	apiGroup := route.Group("/api")
	{
		// Define the notification endpoints
		apiGroup.POST("/notify", sendNotificationHandler)
		apiGroup.POST("/notify/order", sendOrderNotificationHandler)
	}
}

// sendNotificationHandler handles general notifications
func sendNotificationHandler(c *gin.Context) {
	var request struct {
		Type      string      `json:"type" binding:"required"`
		Topic     string      `json:"topic" binding:"required"`
		TargetIDs []string    `json:"target_ids"`
		Payload   interface{} `json:"payload" binding:"required"`
	}

	if err := c.ShouldBindJSON(&request); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// Trigger the notification event
	utils.TriggerEvent(utils.EventType(request.Type), request.Topic, request.TargetIDs, request.Payload)

	c.JSON(http.StatusOK, gin.H{"status": "notification sent"})
}

// sendOrderNotificationHandler handles order-specific notifications
func sendOrderNotificationHandler(c *gin.Context) {
	var request struct {
		OrderID      string      `json:"order_id" binding:"required"`
		Status       string      `json:"status" binding:"required"`
		RestaurantID string      `json:"restaurant_id" binding:"required"`
		OrderDetail  interface{} `json:"order_detail"`
	}

	if err := c.ShouldBindJSON(&request); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// Map the status to an event type
	var eventType utils.EventType
	switch request.Status {
	case "created":
		eventType = utils.OrderCreated
	case "updated":
		eventType = utils.OrderUpdated
	case "accepted":
		eventType = utils.OrderAccepted
	case "rejected":
		eventType = utils.OrderRejected
	case "in_process":
		eventType = utils.OrderInProcess
	case "ready":
		eventType = utils.OrderReady
	case "delivered":
		eventType = utils.OrderDelivered
	case "cancelled":
		eventType = utils.OrderCancelled
	default:
		eventType = utils.OrderUpdated
	}

	// Create the payload
	payload := map[string]interface{}{
		"order_id":      request.OrderID,
		"status":        request.Status,
		"restaurant_id": request.RestaurantID,
		"detail":        request.OrderDetail,
	}

	// Send notification for the order ID directly
	utils.TriggerEvent(eventType, "orders", []string{request.OrderID}, payload)

	c.JSON(http.StatusOK, gin.H{
		"status":   "order notification sent",
		"order_id": request.OrderID,
	})
}
