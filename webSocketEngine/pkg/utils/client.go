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
	ID       string
	UserType string // "customer", "vendor", etc.
	Topic    string // What kind of notifications this client wants
	Conn     *websocket.Conn
	Send     chan []byte
	mu       sync.Mutex
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
			h.Clients[client] = true
			h.mu.Unlock()
			log.Printf("Client connected: %s, Topic: %s", client.ID, client.Topic)

		case client := <-h.Unregister:
			h.mu.Lock()
			if _, ok := h.Clients[client]; ok {
				delete(h.Clients, client)
				close(client.Send)
				log.Printf("Client disconnected: %s", client.ID)
			}
			h.mu.Unlock()
		}
	}
}

// NewClient creates a new client instance
func NewClient(conn *websocket.Conn, id string, userType string, topic string) *Client {
	return &Client{
		ID:       id,
		UserType: userType,
		Topic:    topic,
		Conn:     conn,
		Send:     make(chan []byte, 256),
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

// WebSocketClosedError is an error type for closed websocket connections
type WebSocketClosedError struct {
	Message string
}

func (e WebSocketClosedError) Error() string {
	return e.Message
}
