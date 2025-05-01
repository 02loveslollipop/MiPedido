package utils

import (
	"encoding/json"
	"log"
	"sync"
	"time"

	"github.com/gorilla/websocket"
)

var (
	writeWait = 10 * time.Second // Time allowed to write a message to the peer.

	pongWait = 60 * time.Second // Time allowed to read the next pong message from the peer.

	pingPeriod = (pongWait * 9) / 10 // Send pings to peer with this period. Must be less than pongWait.

	maxMessageSize = 512 // Maximum message size allowed from peer.
)

// Client represents a single WebSocket connection
type Client struct {
	ID      string // Connection identifier
	Topic   string // What kind of notifications this client wants
	OrderID string // ID of the order this client is watching
	Conn    *websocket.Conn
	Send    chan []byte
	mu      sync.Mutex
}

// ClientHub maintains the set of active clients and broadcasts messages to clients
type ClientHub struct {
	// Registered clients
	Clients map[*Client]bool

	// Register requests from clients
	Register chan *Client

	// Unregister requests from clients
	Unregister chan *Client

	// Lock to protect concurrent map access
	mu sync.Mutex
}

// Create a new hub instance
var Hub = NewHub()

// NewHub creates a new client hub
func NewHub() *ClientHub {
	return &ClientHub{
		Clients:    make(map[*Client]bool),
		Register:   make(chan *Client),
		Unregister: make(chan *Client),
	}
}

// Run starts the hub
func (h *ClientHub) Run() {
	for {
		select {
		case client := <-h.Register:
			h.mu.Lock()

			// If this client is watching an order, unregister any existing clients for the same order
			if client.OrderID != "" {
				for existingClient := range h.Clients {
					if existingClient.OrderID == client.OrderID {
						// Remove existing client watching this order
						delete(h.Clients, existingClient)
						close(existingClient.Send)
						log.Printf("Disconnected previous client %s for order %s", existingClient.ID, existingClient.OrderID)
					}
				}
			}

			// Register the new client
			h.Clients[client] = true
			log.Printf("Client connected: %s, Order: %s, Topic: %s", client.ID, client.OrderID, client.Topic)

			h.mu.Unlock()

		case client := <-h.Unregister:
			h.mu.Lock()
			if _, ok := h.Clients[client]; ok {
				delete(h.Clients, client)
				close(client.Send)
				log.Printf("Client disconnected: %s, Order: %s", client.ID, client.OrderID)
			}
			h.mu.Unlock()
		}
	}
}

// NewClient creates a new client instance
func NewClient(conn *websocket.Conn, connectionID string, topic string) *Client {
	return &Client{
		ID:      connectionID,
		Topic:   topic,
		OrderID: "",
		Conn:    conn,
		Send:    make(chan []byte, 256),
	}
}

// ReadPump pumps messages from the WebSocket connection to the hub
func (c *Client) ReadPump() {
	defer func() {
		Hub.Unregister <- c
		c.Conn.Close()
	}()

	c.Conn.SetReadLimit(int64(maxMessageSize))
	c.Conn.SetReadDeadline(time.Now().Add(pongWait))
	c.Conn.SetPongHandler(func(string) error {
		c.Conn.SetReadDeadline(time.Now().Add(pongWait))
		return nil
	})

	for {
		_, _, err := c.Conn.ReadMessage()
		if err != nil {
			if websocket.IsUnexpectedCloseError(err, websocket.CloseGoingAway, websocket.CloseAbnormalClosure) {
				log.Printf("error: %v", err)
			}
			break
		}
	}
}

// WritePump pumps messages from the hub to the WebSocket connection
func (c *Client) WritePump() {
	ticker := time.NewTicker(pingPeriod)
	defer func() {
		ticker.Stop()
		c.Conn.Close()
	}()

	for {
		select {
		case message, ok := <-c.Send:
			c.Conn.SetWriteDeadline(time.Now().Add(writeWait))
			if !ok {
				// The hub closed the channel
				c.Conn.WriteMessage(websocket.CloseMessage, []byte{})
				return
			}

			w, err := c.Conn.NextWriter(websocket.TextMessage)
			if err != nil {
				return
			}
			w.Write(message)

			if err := w.Close(); err != nil {
				return
			}

		case <-ticker.C:
			c.Conn.SetWriteDeadline(time.Now().Add(writeWait))
			if err := c.Conn.WriteMessage(websocket.PingMessage, nil); err != nil {
				return
			}
		}
	}
}

// Message represents a notification message
type Message struct {
	Type    string      `json:"type"`
	Topic   string      `json:"topic"`
	Payload interface{} `json:"payload"`
}

// SendToClient sends a message to a specific client
func SendToClient(client *Client, msgType string, payload interface{}) error {
	client.mu.Lock()
	defer client.mu.Unlock()

	message := Message{
		Type:    msgType,
		Topic:   client.Topic,
		Payload: payload,
	}

	data, err := json.Marshal(message)
	if err != nil {
		return err
	}

	select {
	case client.Send <- data:
		return nil
	default:
		return WebSocketClosedError{"Failed to send message: client channel full or closed"}
	}
}

// BroadcastToTopic sends a message to all clients subscribed to a specific topic
func BroadcastToTopic(topic string, msgType string, payload interface{}) {
	message := Message{
		Type:    msgType,
		Topic:   topic,
		Payload: payload,
	}

	data, err := json.Marshal(message)
	if err != nil {
		log.Printf("Error marshaling message: %v", err)
		return
	}

	Hub.mu.Lock()
	for client := range Hub.Clients {
		if client.Topic == topic {
			select {
			case client.Send <- data:
			default:
				close(client.Send)
				delete(Hub.Clients, client)
			}
		}
	}
	Hub.mu.Unlock()
}

// BroadcastToOrder sends a message to the single client subscribed to this order ID
func BroadcastToOrder(orderID string, msgType string, payload interface{}) {
	message := Message{
		Type:    msgType,
		Topic:   "orders", // Orders is the standard topic for order notifications
		Payload: payload,
	}

	data, err := json.Marshal(message)
	if err != nil {
		log.Printf("Error marshaling message: %v", err)
		return
	}

	Hub.mu.Lock()
	defer Hub.mu.Unlock()

	// Find the single client for this order
	for client := range Hub.Clients {
		if client.OrderID == orderID {
			select {
			case client.Send <- data:
				log.Printf("Sent notification to user %s for order %s", client.ID, orderID)
			default:
				close(client.Send)
				delete(Hub.Clients, client)
				log.Printf("Failed to send notification, removed client %s", client.ID)
			}
			return // Exit after finding the first client, since we only expect one per order
		}
	}

	log.Printf("No active clients found for order %s", orderID)
}

// CloseOrderConnection finds and closes a client connection for a specific order ID
func CloseOrderConnection(orderID string) {
	Hub.mu.Lock()
	defer Hub.mu.Unlock()

	for client := range Hub.Clients {
		if client.OrderID == orderID {
			// Send a closing message to the client
			closePayload := map[string]interface{}{
				"message":   "Order has been finalized. Connection will now close.",
				"order_id":  orderID,
				"timestamp": time.Now().Format(time.RFC3339),
			}

			// Try to send a closing message
			message := Message{
				Type:    "order_completed",
				Topic:   "orders",
				Payload: closePayload,
			}

			data, err := json.Marshal(message)
			if err == nil {
				// Try to send the closing message, but don't block if it fails
				select {
				case client.Send <- data:
					log.Printf("Sent closing message to client %s for order %s", client.ID, orderID)
				default:
					log.Printf("Failed to send closing message to client %s for order %s", client.ID, orderID)
				}
			}

			// Close the client connection
			close(client.Send)
			delete(Hub.Clients, client)
			log.Printf("Closed connection for client %s with order %s after notification", client.ID, orderID)
			return // Only one client per order, so we can return after finding it
		}
	}

	log.Printf("No active clients found for order %s to close", orderID)
}

// WebSocketClosedError is an error type for closed websocket connections
type WebSocketClosedError struct {
	Message string
}

func (e WebSocketClosedError) Error() string {
	return e.Message
}
