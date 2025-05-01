package utils

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
)

// LoggingResponseWriter is a custom response writer that captures the response status code and body
type LoggingResponseWriter struct {
	gin.ResponseWriter
	body       *bytes.Buffer
	statusCode int
}

// Write captures the response body
func (w *LoggingResponseWriter) Write(b []byte) (int, error) {
	w.body.Write(b)
	return w.ResponseWriter.Write(b)
}

// WriteHeader captures the response status code
func (w *LoggingResponseWriter) WriteHeader(code int) {
	w.statusCode = code
	w.ResponseWriter.WriteHeader(code)
}

// LogNon2xxResponses is a middleware that logs all non-2xx HTTP responses
func LogNon2xxResponses() gin.HandlerFunc {
	return func(c *gin.Context) {
		// Create a custom response writer to capture the response
		writer := &LoggingResponseWriter{
			ResponseWriter: c.Writer,
			body:           bytes.NewBufferString(""),
			statusCode:     http.StatusOK, // Default status code
		}
		c.Writer = writer

		// Get the request body for logging if needed
		requestBody := ""
		if c.Request.Method == "POST" || c.Request.Method == "PUT" {
			var bodyBytes []byte
			if c.Request.Body != nil {
				bodyBytes, _ = io.ReadAll(c.Request.Body)
				// Restore the body for further processing
				c.Request.Body = io.NopCloser(bytes.NewBuffer(bodyBytes))
				requestBody = string(bodyBytes)
			}
		}

		// Process request
		startTime := time.Now()
		c.Next()
		duration := time.Since(startTime)

		// Log non-2xx responses
		if writer.statusCode < 200 || writer.statusCode >= 300 {
			// Format the response body as JSON if possible
			var prettyJSON bytes.Buffer
			if err := json.Indent(&prettyJSON, writer.body.Bytes(), "", "  "); err == nil {
				// Try to format the request body as well if it's not empty
				requestBodyFormatted := requestBody
				if requestBody != "" {
					var prettyRequest bytes.Buffer
					if err := json.Indent(&prettyRequest, []byte(requestBody), "", "  "); err == nil {
						requestBodyFormatted = prettyRequest.String()
					}
				}

				log.Printf("HTTP Error [%d] - %s %s - Duration: %v\nRequest: %s\nResponse: %s\nQuery Params: %v",
					writer.statusCode,
					c.Request.Method,
					c.Request.URL.Path,
					duration,
					requestBodyFormatted,
					prettyJSON.String(),
					c.Request.URL.Query())
			} else {
				// If JSON formatting fails, log the raw response
				log.Printf("HTTP Error [%d] - %s %s - Duration: %v\nRequest: %s\nResponse: %s\nQuery Params: %v",
					writer.statusCode,
					c.Request.Method,
					c.Request.URL.Path,
					duration,
					requestBody,
					writer.body.String(),
					c.Request.URL.Query())
			}
		}
	}
}

// LogRequest is a helper function to log request data
func LogRequest(c *gin.Context, message string, data ...interface{}) {
	requestInfo := fmt.Sprintf("[%s %s] %s", c.Request.Method, c.Request.URL.Path, message)
	if len(data) > 0 {
		log.Printf("%s - %v", requestInfo, data)
	} else {
		log.Printf("%s", requestInfo)
	}
}
