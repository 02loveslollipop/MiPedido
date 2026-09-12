package utils

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"strings"
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
			sanitizedPath := SanitizeLog(c.Request.URL.Path)
			sanitizedQuery := SanitizeLog(fmt.Sprintf("%v", c.Request.URL.Query()))

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

				sanitizedReqBody := SanitizeLog(requestBodyFormatted)
				sanitizedRespBody := SanitizeLog(prettyJSON.String())

				log.Printf("HTTP Error [%d] - %s %s - Duration: %v\nRequest: %s\nResponse: %s\nQuery Params: %s",
					writer.statusCode,
					c.Request.Method,
					sanitizedPath,
					duration,
					sanitizedReqBody,
					sanitizedRespBody,
					sanitizedQuery)
			} else {
				// If JSON formatting fails, log the raw response
				sanitizedReqBody := SanitizeLog(requestBody)
				sanitizedRespBody := SanitizeLog(writer.body.String())

				log.Printf("HTTP Error [%d] - %s %s - Duration: %v\nRequest: %s\nResponse: %s\nQuery Params: %s",
					writer.statusCode,
					c.Request.Method,
					sanitizedPath,
					duration,
					sanitizedReqBody,
					sanitizedRespBody,
					sanitizedQuery)
			}
		}
	}
}

// SanitizeLog removes CR and LF characters to prevent log injection (CWE-117).
func SanitizeLog(s string) string {
	s = strings.ReplaceAll(s, "\r", "\\r")
	s = strings.ReplaceAll(s, "\n", "\\n")
	return s
}

// LogRequest is a helper function to log request data
func LogRequest(c *gin.Context, message string, data ...interface{}) {
	method := ""
	path := ""
	if c != nil && c.Request != nil {
		method = c.Request.Method
		if c.Request.URL != nil {
			path = c.Request.URL.Path
		}
	}
	sanitizedPath := SanitizeLog(path)
	sanitizedMessage := SanitizeLog(message)
	requestInfo := fmt.Sprintf("[%s %s] %s", method, sanitizedPath, sanitizedMessage)
	if len(data) > 0 {
		sanitizedData := make([]interface{}, len(data))
		for i, d := range data {
			sanitizedData[i] = SanitizeLog(fmt.Sprintf("%v", d))
		}
		log.Printf("%s - %v", requestInfo, sanitizedData)
	} else {
		log.Printf("%s", requestInfo)
	}
}
