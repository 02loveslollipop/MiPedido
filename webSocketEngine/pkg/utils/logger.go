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

func extractRequestBody(c *gin.Context) string {
	if (c.Request.Method != "POST" && c.Request.Method != "PUT") || c.Request.Body == nil {
		return ""
	}
	bodyBytes, err := io.ReadAll(c.Request.Body)
	if err != nil {
		return ""
	}
	c.Request.Body = io.NopCloser(bytes.NewBuffer(bodyBytes))
	return string(bodyBytes)
}

func formatJSONOrRaw(raw []byte) string {
	var pretty bytes.Buffer
	if err := json.Indent(&pretty, raw, "", "  "); err == nil {
		return pretty.String()
	}
	return string(raw)
}

func logNon2xxResponse(c *gin.Context, writer *LoggingResponseWriter, requestBody string, duration time.Duration) {
	if writer.statusCode >= 200 && writer.statusCode < 300 {
		return
	}

	sanitizedPath := SanitizeLog(c.Request.URL.Path)
	sanitizedQuery := SanitizeLog(fmt.Sprintf("%v", c.Request.URL.Query()))

	reqFormatted := requestBody
	if requestBody != "" {
		reqFormatted = formatJSONOrRaw([]byte(requestBody))
	}

	respFormatted := formatJSONOrRaw(writer.body.Bytes())

	log.Printf("HTTP Error [%d] - %s %s - Duration: %v\nRequest: %s\nResponse: %s\nQuery Params: %s",
		writer.statusCode,
		c.Request.Method,
		sanitizedPath,
		duration,
		SanitizeLog(reqFormatted),
		SanitizeLog(respFormatted),
		sanitizedQuery)
}

// LogNon2xxResponses is a middleware that logs all non-2xx HTTP responses
func LogNon2xxResponses() gin.HandlerFunc {
	return func(c *gin.Context) {
		writer := &LoggingResponseWriter{
			ResponseWriter: c.Writer,
			body:           bytes.NewBufferString(""),
			statusCode:     http.StatusOK,
		}
		c.Writer = writer

		requestBody := extractRequestBody(c)

		startTime := time.Now()
		c.Next()
		duration := time.Since(startTime)

		logNon2xxResponse(c, writer, requestBody, duration)
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
