package model

import (
	"time"

	"go.mongodb.org/mongo-driver/v2/bson"
)

// Review represents an anonymous restaurant review
type Review struct {
	ID           bson.ObjectID `bson:"_id,omitempty" json:"id,omitempty"`
	RestaurantID string        `bson:"restaurant_id" json:"restaurant_id"`
	Rating       int           `bson:"rating" json:"rating"`
	Status       string        `bson:"status" json:"status"`
	CreatedAt    time.Time     `bson:"created_at" json:"created_at"`
}
