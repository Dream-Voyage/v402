package middleware

import (
	"log"
	"net/http"
	"time"
)

// AuthMiddleware provides authentication middleware
func NewAuthMiddleware() func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			// Check for authentication headers
			publicKey := r.Header.Get("X-Public-Key")
			signature := r.Header.Get("X-Signature")
			timestamp := r.Header.Get("X-Timestamp")

			if publicKey == "" || signature == "" || timestamp == "" {
				http.Error(w, "Missing authentication headers", http.StatusUnauthorized)
				return
			}

			// In a real implementation, you would verify the signature here
			// For now, we'll just log the authentication attempt
			log.Printf("Authentication attempt: publicKey=%s, timestamp=%s", publicKey, timestamp)

			next.ServeHTTP(w, r)
		})
	}
}

// LoggingMiddleware provides request logging
func NewLoggingMiddleware() func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			start := time.Now()

			// Create a response writer wrapper to capture status code
			wrapped := &responseWriter{ResponseWriter: w, statusCode: http.StatusOK}

			next.ServeHTTP(wrapped, r)

			duration := time.Since(start)
			log.Printf("%s %s %d %v", r.Method, r.URL.Path, wrapped.statusCode, duration)
		})
	}
}

// CORSMiddleware provides CORS headers
func NewCORSMiddleware() func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			w.Header().Set("Access-Control-Allow-Origin", "*")
			w.Header().Set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
			w.Header().Set("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Public-Key, X-Signature, X-Timestamp")

			if r.Method == "OPTIONS" {
				w.WriteHeader(http.StatusOK)
				return
			}

			next.ServeHTTP(w, r)
		})
	}
}

// responseWriter wraps http.ResponseWriter to capture status code
type responseWriter struct {
	http.ResponseWriter
	statusCode int
}

func (rw *responseWriter) WriteHeader(code int) {
	rw.statusCode = code
	rw.ResponseWriter.WriteHeader(code)
}
