package utils

import (
	"log"
	"sync"
)

// EventType defines the type of event that occurred
type EventType string

// Define various event types
const (
	OrderCreated     EventType = "order_created"
	OrderUpdated     EventType = "order_updated"
	OrderAccepted    EventType = "order_accepted"
	OrderRejected    EventType = "order_rejected"
	OrderInProcess   EventType = "order_in_process"
	OrderReady       EventType = "order_ready"
	OrderDelivered   EventType = "order_delivered"
	OrderCancelled   EventType = "order_cancelled"
	PaymentConfirmed EventType = "payment_confirmed"
)

// NotificationEvent represents an event that will trigger notifications
type NotificationEvent struct {
	Type      EventType   `json:"type"`
	Topic     string      `json:"topic"`
	TargetIDs []string    `json:"target_ids"` // User IDs who should receive this notification
	Payload   interface{} `json:"payload"`
}

// NotificationManager handles the event processing and notification dispatch
type NotificationManager struct {
	// Channels for receiving events
	Events chan NotificationEvent

	// Stop channel to gracefully shutdown
	Stop chan struct{}

	mu sync.Mutex
}

// Global notification manager
var notificationManager *NotificationManager
var notifierOnce sync.Once

// GetNotifier returns the singleton notification manager instance
func GetNotifier() *NotificationManager {
	notifierOnce.Do(func() {
		notificationManager = &NotificationManager{
			Events: make(chan NotificationEvent, 100),
			Stop:   make(chan struct{}),
		}
		go notificationManager.Start()
	})
	return notificationManager
}

// Start begins processing events from the event channel
func (nm *NotificationManager) Start() {
	log.Println("Starting notification manager")
	for {
		select {
		case event := <-nm.Events:
			nm.processEvent(event)
		case <-nm.Stop:
			log.Println("Stopping notification manager")
			return
		}
	}
}

// Stop the notification manager
func (nm *NotificationManager) Shutdown() {
	close(nm.Stop)
}

// Process an event and send notifications
func (nm *NotificationManager) processEvent(event NotificationEvent) {
	log.Printf("Processing notification event: %s for topic: %s", event.Type, event.Topic)

	if event.Topic == "orders" && len(event.TargetIDs) > 0 {
		// For orders topic with specific target IDs, treat them as order IDs
		for _, orderID := range event.TargetIDs {
			BroadcastToOrder(orderID, string(event.Type), event.Payload)
		}
	} else if len(event.TargetIDs) > 0 {
		// For other topics, send to specific users
		nm.sendToUsers(event)
	} else {
		// Broadcast to all clients subscribed to the topic
		BroadcastToTopic(event.Topic, string(event.Type), event.Payload)
	}
}

// Send notifications to specific users
func (nm *NotificationManager) sendToUsers(event NotificationEvent) {
	for _, id := range event.TargetIDs {
		Hub.mu.Lock()
		for client := range Hub.Clients {
			if client.ID == id && client.Topic == event.Topic {
				err := SendToClient(client, string(event.Type), event.Payload)
				if err != nil {
					log.Printf("Error sending notification to client %s: %v", client.ID, err)
				}
			}
		}
		Hub.mu.Unlock()
	}
}

// Create a function to easily trigger an event from other parts of the application
func TriggerEvent(eventType EventType, topic string, targetIDs []string, payload interface{}) {
	notifier := GetNotifier()
	event := NotificationEvent{
		Type:      eventType,
		Topic:     topic,
		TargetIDs: targetIDs,
		Payload:   payload,
	}
	notifier.Events <- event
}
