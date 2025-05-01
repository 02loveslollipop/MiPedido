package router

import (
	"path/filepath"

	"github.com/gin-gonic/gin"
)

// RegisterStaticRoutes registers routes for serving static content
func RegisterStaticRoutes(r *gin.Engine) {
	// Serve the test client HTML page at /test endpoint
	r.GET("/test", func(c *gin.Context) {
		// Get the absolute path to the test HTML file
		testFilePath := filepath.Join("assets", "index.html")

		// Serve the file
		c.File(testFilePath)
	})
}
