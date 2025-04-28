package model

import "go.mongodb.org/mongo-driver/v2/bson"

// Position represents geographic coordinates
type Position struct {
	Lat float64 `bson:"lat" json:"lat"`
	Lng float64 `bson:"lng" json:"lng"`
}

// Restaurant represents a restaurant entity
type Restaurant struct {
	ID          bson.ObjectID	   `bson:"_id,omitempty" json:"id,omitempty"`
	Name        string             `bson:"name" json:"name"`
	ImgURL      string             `bson:"img_url" json:"img_url"`
	Rating      float64            `bson:"rating" json:"rating"`
	Type        string             `bson:"type,omitempty" json:"type,omitempty"`
	Description string             `bson:"description,omitempty" json:"description,omitempty"`
	Position    *Position          `bson:"position,omitempty" json:"position,omitempty"`
	ReviewCount int                `bson:"_review_count" json:"_review_count"`
}

