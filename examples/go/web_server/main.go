package main

import (
	"fmt"
	"log"
	"net/http"
	"time"

	"./client"
	"./config"
	"./handlers"
	"./middleware"
	"./services"
)

func main() {
	// Create configuration
	cfg := config.DefaultConfig()
	cfg.BaseURL = "https://api.v402.network"
	cfg.PublicKey = "0x1234567890abcdef1234567890abcdef12345678"
	cfg.PrivateKey = "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"

	// Create v402 client
	v402Client, err := client.NewClient(&client.Config{
		BaseURL:         cfg.BaseURL,
		Timeout:         cfg.Timeout,
		RetryCount:      cfg.RetryCount,
		PublicKey:       cfg.PublicKey,
		PrivateKey:      cfg.PrivateKey,
		ChainID:         cfg.ChainID,
		RPCURL:          cfg.RPCURL,
		ContractAddress: cfg.ContractAddress,
	})
	if err != nil {
		log.Fatalf("Failed to create v402 client: %v", err)
	}

	// Create services
	productService := services.NewProductService(v402Client)
	paymentService := services.NewPaymentService(v402Client)
	analyticsService := services.NewAnalyticsService(v402Client)

	// Create handlers
	productHandler := handlers.NewProductHandler(productService)
	paymentHandler := handlers.NewPaymentHandler(paymentService)
	analyticsHandler := handlers.NewAnalyticsHandler(analyticsService)

	// Create middleware
	authMiddleware := middleware.NewAuthMiddleware()
	loggingMiddleware := middleware.NewLoggingMiddleware()
	corsMiddleware := middleware.NewCORSMiddleware()

	// Setup routes
	mux := http.NewServeMux()

	// Product routes
	mux.HandleFunc("/api/v1/products", func(w http.ResponseWriter, r *http.Request) {
		switch r.Method {
		case http.MethodGet:
			productHandler.ListProducts(w, r)
		case http.MethodPost:
			productHandler.CreateProduct(w, r)
		default:
			http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		}
	})

	mux.HandleFunc("/api/v1/products/", func(w http.ResponseWriter, r *http.Request) {
		switch r.Method {
		case http.MethodGet:
			productHandler.GetProduct(w, r)
		case http.MethodPut:
			productHandler.UpdateProduct(w, r)
		case http.MethodDelete:
			productHandler.DeleteProduct(w, r)
		default:
			http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		}
	})

	// Payment routes
	mux.HandleFunc("/api/v1/payments", func(w http.ResponseWriter, r *http.Request) {
		switch r.Method {
		case http.MethodPost:
			paymentHandler.ProcessPayment(w, r)
		default:
			http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		}
	})

	mux.HandleFunc("/api/v1/payments/", func(w http.ResponseWriter, r *http.Request) {
		switch r.Method {
		case http.MethodGet:
			paymentHandler.GetPayment(w, r)
		default:
			http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		}
	})

	// Analytics routes
	mux.HandleFunc("/api/v1/analytics/products/", func(w http.ResponseWriter, r *http.Request) {
		switch r.Method {
		case http.MethodGet:
			analyticsHandler.GetProductAnalytics(w, r)
		default:
			http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		}
	})

	// Health check
	mux.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
		w.Write([]byte("OK"))
	})

	// Apply middleware
	handler := corsMiddleware(loggingMiddleware(authMiddleware(mux)))

	// Start server
	server := &http.Server{
		Addr:         ":8080",
		Handler:      handler,
		ReadTimeout:  15 * time.Second,
		WriteTimeout: 15 * time.Second,
		IdleTimeout:  60 * time.Second,
	}

	fmt.Println("Starting server on :8080")
	log.Fatal(server.ListenAndServe())
}
