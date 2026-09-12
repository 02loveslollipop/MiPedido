package utils

import (
	"bytes"
	"log"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"

	"github.com/gin-gonic/gin"
)

func TestSanitizeLog(t *testing.T) {
	tests := []struct {
		name     string
		input    string
		expected string
	}{
		{
			name:     "plain string",
			input:    "normal log text",
			expected: "normal log text",
		},
		{
			name:     "string with newline",
			input:    "line1\nline2",
			expected: "line1\\nline2",
		},
		{
			name:     "string with CRLF",
			input:    "line1\r\nline2",
			expected: "line1\\r\\nline2",
		},
		{
			name:     "string with malicious log injection payload",
			input:    "200 OK\r\n2026-09-12 [CRITICAL] Fake Admin Log",
			expected: "200 OK\\r\\n2026-09-12 [CRITICAL] Fake Admin Log",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := SanitizeLog(tt.input)
			if got != tt.expected {
				t.Errorf("SanitizeLog(%q) = %q, want %q", tt.input, got, tt.expected)
			}
		})
	}
}

func TestLogRequest(t *testing.T) {
	gin.SetMode(gin.TestMode)
	var logBuf bytes.Buffer
	log.SetOutput(&logBuf)
	defer log.SetOutput(nil)

	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	req, err := http.NewRequest(http.MethodGet, "/test/path", nil)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	req.URL.Path = "/test/path\r\ninjected"
	c.Request = req

	LogRequest(c, "test message\nwith newline", "arg1\r\nwithCRLF")

	output := logBuf.String()
	if strings.Contains(output, "\r") {
		t.Errorf("Log output contains raw carriage return: %q", output)
	}
	if !strings.Contains(output, "\\r\\ninjected") {
		t.Errorf("Log output should contain sanitized path: %q", output)
	}
}

func TestLogNon2xxResponses(t *testing.T) {
	gin.SetMode(gin.TestMode)
	var logBuf bytes.Buffer
	log.SetOutput(&logBuf)
	defer log.SetOutput(nil)

	router := gin.New()
	router.Use(LogNon2xxResponses())
	router.POST("/error-endpoint", func(c *gin.Context) {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": "bad request\r\nfake log",
		})
	})

	body := strings.NewReader(`{"query":"test\r\ninjection"}`)
	req, err := http.NewRequest(http.MethodPost, "/error-endpoint", body)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	req.URL.RawQuery = "search=foo\r\nbar"
	req.Header.Set("Content-Type", "application/json")

	w := httptest.NewRecorder()
	router.ServeHTTP(w, req)

	if w.Code != http.StatusBadRequest {
		t.Fatalf("expected status 400, got %d", w.Code)
	}

	output := logBuf.String()
	// Ensure no unescaped carriage returns or newlines in log payload fields
	if strings.Contains(output, "\r") {
		t.Errorf("Log output contains unescaped CR: %q", output)
	}
	if !strings.Contains(output, "HTTP Error [400]") {
		t.Errorf("Log output should record status 400, got: %q", output)
	}
}
