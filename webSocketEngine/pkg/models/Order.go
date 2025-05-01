package models

import (
	"go.mongodb.org/mongo-driver/bson/primitive"
)

// Product represents a product in an order
type Product struct {
	ID          string   `bson:"id"`
	Name        string   `bson:"name"`
	Price       float64  `bson:"price"`
	ImgURL      string   `bson:"img_url"`
	Quantity    int      `bson:"quantity"`
	Ingredients []string `bson:"ingredients"`
}

// UserOrder represents the products ordered by a specific user
type UserOrder struct {
	Products []Product `bson:"products"`
}

// Order represents the order document in the database
type Order struct {
	ID           primitive.ObjectID   `bson:"_id,omitempty"`
	RestaurantID string               `bson:"restaurant_id"`
	Users        map[string]UserOrder `bson:"users"`
	Status       string               `bson:"status"`
	CreatedAt    primitive.DateTime   `bson:"created_at"`
	NotifiedAt   primitive.DateTime   `bson:"notifiedAt,omitempty"`
}
