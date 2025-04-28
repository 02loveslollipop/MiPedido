package service

import (
	"context"
	"log"

	"go.mongodb.org/mongo-driver/v2/bson"
	"go.mongodb.org/mongo-driver/v2/mongo"

	"review_cron_job.mipedido/pkg/model"
)

type ReviewService struct {
	db             *mongo.Database
	reviewsCol     *mongo.Collection
	restaurantsCol *mongo.Collection
}

func NewReviewService(db *mongo.Database) *ReviewService {
	return &ReviewService{
		db:             db,
		reviewsCol:     db.Collection("reviews"),
		restaurantsCol: db.Collection("restaurants"),
	}
}

func (s *ReviewService) ProcessPendingReviews(ctx context.Context) error {
	log.Println("Starting to process pending reviews...")

	// Only process reviews with "pending" status
	matchStage := bson.M{
		"$match": bson.M{
			"status": "pending",
		},
	}

	// Group by restaurant_id and calculate average rating and review count
	groupStage := bson.M{
		"$group": bson.M{
			"_id": "$restaurant_id",
			"averageRating": bson.M{
				"$avg": "$rating",
			},
			"reviewCount": bson.M{
				"$sum": 1,
			},
			"reviewIDs": bson.M{
				"$push": "$_id",
			},
		},
	}

	pipeline := []bson.M{matchStage, groupStage}

	cursor, err := s.reviewsCol.Aggregate(ctx, pipeline)
	if err != nil {
		return err
	}
	defer cursor.Close(ctx)

	type AggregateResult struct {
		RestaurantID  string          `bson:"_id"`
		AverageRating float64         `bson:"averageRating"`
		ReviewCount   int             `bson:"reviewCount"`
		ReviewIDs     []bson.ObjectID `bson:"reviewIDs"`
	}

	for cursor.Next(ctx) {
		var result AggregateResult
		if err := cursor.Decode(&result); err != nil {
			log.Printf("Error decoding review result: %v", err)
			continue
		}

		restaurantID, err := bson.ObjectIDFromHex(result.RestaurantID)
		if err != nil {
			log.Printf("Invalid restaurant ID: %s - %v", result.RestaurantID, err)
			continue
		}

		restaurant := model.Restaurant{}
		err = s.restaurantsCol.FindOne(ctx, bson.M{"_id": restaurantID}).Decode(&restaurant)
		if err != nil {
			log.Printf("Error fetching restaurant %s: %v", result.RestaurantID, err)
			continue
		}

		// Calculate weighted mean
		var newRating float64
		if restaurant.ReviewCount > 0 {
			existingWeight := float64(restaurant.ReviewCount)
			newWeight := float64(result.ReviewCount)
			newRating = (restaurant.Rating*existingWeight + result.AverageRating*newWeight) / (existingWeight + newWeight)
		} else {
			newRating = result.AverageRating
		}

		// Update restaurant rating and review count
		_, err = s.restaurantsCol.UpdateOne(
			ctx,
			bson.M{"_id": restaurantID},
			bson.M{
				"$set": bson.M{
					"rating":        float64(int(newRating*10)) / 10, // Round to 1 decimal place
					"_review_count": restaurant.ReviewCount + result.ReviewCount,
				},
			},
		)
		if err != nil {
			log.Printf("Error updating restaurant %s: %v", result.RestaurantID, err)
			continue
		}

		// Mark reviews as processed
		_, err = s.reviewsCol.UpdateMany(
			ctx,
			bson.M{
				"_id": bson.M{"$in": result.ReviewIDs},
			},
			bson.M{
				"$set": bson.M{"status": "processed"},
			},
		)
		if err != nil {
			log.Printf("Error marking reviews as processed for restaurant %s: %v", result.RestaurantID, err)
			continue //Continue to the next restaurant even if this fails
		}

		log.Printf("Processed %d reviews for restaurant %s. New rating: %.1f",
			result.ReviewCount, restaurant.Name, newRating)
	}

	if err := cursor.Err(); err != nil {
		return err
	}

	log.Println("Finished processing pending reviews successfully")
	return nil
}
