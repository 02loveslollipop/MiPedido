package services

import (
	"context"
	"fmt"
	"log"
	"sync"
	"time"

	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/bson/primitive"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
	"websocketengine.mipedido/pkg/database"
	"websocketengine.mipedido/pkg/models"
	"websocketengine.mipedido/pkg/utils"
)

// Singleton pattern for OrderChangeWatcher
var (
	orderWatcher     *OrderChangeWatcher
	orderWatcherOnce sync.Once
)

// GetOrderWatcher returns the singleton instance of OrderChangeWatcher
func GetOrderWatcher() *OrderChangeWatcher {
	orderWatcherOnce.Do(func() {
		var err error
		orderWatcher, err = NewOrderChangeWatcher("orders")
		if err != nil {
			log.Fatalf("Failed to create order watcher: %v", err)
		}
		err = orderWatcher.Start()
		if err != nil {
			log.Fatalf("Failed to start order watcher: %v", err)
		}
	})
	return orderWatcher
}

type OrderChangeWatcher struct {
	collection     *mongo.Collection
	changeStream   *mongo.ChangeStream
	ctx            context.Context
	cancel         context.CancelFunc
	orderUserCache map[string]string       // Maps order ID to a single user ID
	orderCache     map[string]models.Order // Cache of orders
}

// NewOrderChangeWatcher creates a new order change watcher
func NewOrderChangeWatcher(collectionName string) (*OrderChangeWatcher, error) {
	collection := database.GetCollection(collectionName)
	if collection == nil {
		return nil, fmt.Errorf("collection '%s' not found", collectionName)
	}

	ctx, cancel := context.WithCancel(context.Background())

	watcher := &OrderChangeWatcher{
		collection:     collection,
		ctx:            ctx,
		cancel:         cancel,
		orderUserCache: make(map[string]string),
		orderCache:     make(map[string]models.Order),
	}

	return watcher, nil
}

// Start begins watching for changes in the orders collection
func (w *OrderChangeWatcher) Start() error {
	// Load existing orders for tracking
	w.preloadOrders()

	// Create a pipeline for the change stream
	pipeline := mongo.Pipeline{
		bson.D{
			{Key: "$match", Value: bson.D{
				{Key: "operationType", Value: bson.D{
					{Key: "$in", Value: bson.A{"insert", "update", "replace"}},
				}},
			}},
		},
	}

	opts := options.ChangeStream().SetFullDocument(options.UpdateLookup)
	changeStream, err := w.collection.Watch(w.ctx, pipeline, opts)
	if err != nil {
		return fmt.Errorf("failed to create change stream: %v", err)
	}

	w.changeStream = changeStream

	go w.processChanges()
	log.Println("Order change watcher started")

	return nil
}

// Stop stops watching for changes
func (w *OrderChangeWatcher) Stop() {
	if w.cancel != nil {
		w.cancel()
	}
	if w.changeStream != nil {
		w.changeStream.Close(context.Background())
	}
	log.Println("Order change watcher stopped")
}

// preloadOrders loads existing orders into cache for tracking
func (w *OrderChangeWatcher) preloadOrders() {
	cursor, err := w.collection.Find(w.ctx, bson.M{})
	if err != nil {
		log.Printf("Error preloading orders: %v", err)
		return
	}
	defer cursor.Close(w.ctx)

	var orders []models.Order
	if err := cursor.All(w.ctx, &orders); err != nil {
		log.Printf("Error decoding orders: %v", err)
		return
	}

	for _, order := range orders {
		orderIDHex := order.ID.Hex()
		w.orderCache[orderIDHex] = order
		// We don't set any users in preload since they'll subscribe later
	}

	log.Printf("Preloaded %d orders for tracking", len(orders))
}

// AddOrderToWatch adds an order to watch
func (w *OrderChangeWatcher) AddOrderToWatch(orderID string) {
	// Simply add the order to the watch list
	log.Printf("Added order %s to watch list", orderID)
}

// GetCollection returns the MongoDB collection used by this watcher
func (w *OrderChangeWatcher) GetCollection() *mongo.Collection {
	return w.collection
}

// processChanges processes changes from the change stream
func (w *OrderChangeWatcher) processChanges() {
	for w.changeStream.Next(w.ctx) {
		var changeDoc struct {
			FullDocument models.Order `bson:"fullDocument"`
		}

		if err := w.changeStream.Decode(&changeDoc); err != nil {
			log.Printf("Error decoding change stream document: %v", err)
			continue
		}

		order := changeDoc.FullDocument
		orderIDHex := order.ID.Hex()

		// Get the previous state of the order from cache to detect changes
		oldOrder, exists := w.orderCache[orderIDHex]

		// Check if this is a status change to "fulfilled"
		isFinalized := order.Status == "fulfilled" && (!exists || oldOrder.Status != "fulfilled")

		if isFinalized {
			log.Printf("Order %s has been fulfilled", orderIDHex)

			// Check if the order has already been notified
			notifiedAtTime := order.NotifiedAt.Time()
			zeroDate := time.Date(1970, 1, 1, 0, 0, 0, 0, time.UTC)
			if notifiedAtTime.After(zeroDate) { // Check if the order has been notified
				log.Printf("Order %s has already been notified at %v", orderIDHex, notifiedAtTime)
				continue
			}

			// Create notification payload
			payload := map[string]interface{}{
				"order_id":      orderIDHex,
				"restaurant_id": order.RestaurantID,
				"status":        "fulfilled",
				"timestamp":     time.Now().Format(time.RFC3339),
				"message":       "Your order has been completed",
			}

			// Send notification for the order ID directly
			utils.TriggerEvent(utils.OrderCompleted, "orders", []string{orderIDHex}, payload)
			log.Printf("Sent completion notification for order %s", orderIDHex)

			// Update the MongoDB document to add notifiedAt timestamp
			now := time.Now()
			update := bson.M{
				"$set": bson.M{
					"notifiedAt": now,
				},
			}

			_, err := w.collection.UpdateByID(w.ctx, order.ID, update)
			if err != nil {
				log.Printf("Error updating notifiedAt for order %s: %v", orderIDHex, err)
			} else {
				log.Printf("Updated notifiedAt to %v for order %s", now, orderIDHex)

				// Update our local cache too
				order.NotifiedAt = primitive.NewDateTimeFromTime(now)
				w.orderCache[orderIDHex] = order
			}

			// Find and close the connection for this order
			utils.CloseOrderConnection(orderIDHex)
		}

		// Update our cache with the latest order data
		w.orderCache[orderIDHex] = order
	}

	// Handle any errors in the change stream
	if err := w.changeStream.Err(); err != nil {
		log.Printf("Change stream error: %v", err)
	}
}
