package main

import (
	"context"
	"log"

	"review_cron_job.mipedido/pkg/api"
	"review_cron_job.mipedido/pkg/service"
)

func main() {
	// Set up logging
	log.SetFlags(log.Ldate | log.Ltime | log.Lshortfile)
	log.Println("Starting MiPedido Rating Cron Job (single run)...")

	// Connect to database
	db, err := api.ConnectDatabase()
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}

	// Initialize review service
	reviewService := service.NewReviewService(db)

	// Run the processing once
	log.Printf("Running review processing...")
	ctx := context.Background()
	if err := reviewService.ProcessPendingReviews(ctx); err != nil {
		log.Printf("Processing error: %v", err)
		// Decide if the program should exit with an error code
		// os.Exit(1) // Uncomment if you want to exit with error status
	} else {
		log.Println("Review processing completed successfully.")
	}

	log.Println("Exiting MiPedido Rating Cron Job.")
}
