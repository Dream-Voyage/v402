package main

import (
	"context"
	"fmt"
	"log"
	"time"

	"./client"
	"./config"
)

func main() {
	// Create configuration
	cfg := &config.ClientConfig{
		BaseURL:         "https://api.v402.network",
		Timeout:         30 * time.Second,
		RetryCount:      3,
		PublicKey:       "0x1234567890abcdef1234567890abcdef12345678",
		PrivateKey:      "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
		ChainID:         1,
		RPCURL:          "https://mainnet.infura.io/v3/your-project-id",
		ContractAddress: "0x1234567890abcdef1234567890abcdef12345678",
		DefaultCurrency: "USDC",
		GasLimit:        100000,
		GasPrice:        "20000000000",
		LogLevel:        "info",
		EnableMetrics:   true,
		MetricsPort:     9090,
		HealthCheck:     true,
	}

	// Validate configuration
	if err := cfg.Validate(); err != nil {
		log.Fatalf("Configuration validation failed: %v", err)
	}

	// Create client
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
		log.Fatalf("Failed to create client: %v", err)
	}

	// Create context with timeout
	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	// Example 1: Create a product
	fmt.Println("=== Creating Product ===")
	product := &client.Product{
		Title:       "Advanced Go Programming",
		Description: "Learn advanced Go programming techniques",
		Price:       "10.00",
		Currency:    "USDC",
		ContentURL:  "https://example.com/content/go-advanced",
		Status:      "active",
	}

	createdProduct, err := v402Client.CreateProduct(ctx, product)
	if err != nil {
		log.Printf("Failed to create product: %v", err)
	} else {
		fmt.Printf("Created product: %+v\n", createdProduct)
	}

	// Example 2: Get a product
	fmt.Println("\n=== Getting Product ===")
	if createdProduct != nil {
		retrievedProduct, err := v402Client.GetProduct(ctx, createdProduct.ID)
		if err != nil {
			log.Printf("Failed to get product: %v", err)
		} else {
			fmt.Printf("Retrieved product: %+v\n", retrievedProduct)
		}
	}

	// Example 3: Process payment
	fmt.Println("\n=== Processing Payment ===")
	paymentReq := &client.PaymentRequest{
		ProductID:   "product-123",
		Amount:      "10.00",
		Currency:    "USDC",
		UserAddress: "0xabcdef1234567890abcdef1234567890abcdef12",
		Nonce:       "nonce-123",
		Signature:   "signature-123",
	}

	paymentResp, err := v402Client.ProcessPayment(ctx, paymentReq)
	if err != nil {
		log.Printf("Failed to process payment: %v", err)
	} else {
		fmt.Printf("Payment response: %+v\n", paymentResp)
	}

	// Example 4: Check access
	fmt.Println("\n=== Checking Access ===")
	accessReq := &client.AccessRequest{
		ProductID:   "product-123",
		UserAddress: "0xabcdef1234567890abcdef1234567890abcdef12",
		Timestamp:   time.Now().Unix(),
		Signature:   "signature-123",
	}

	accessResp, err := v402Client.CheckAccess(ctx, accessReq)
	if err != nil {
		log.Printf("Failed to check access: %v", err)
	} else {
		fmt.Printf("Access response: %+v\n", accessResp)
	}

	fmt.Println("\n=== Example completed successfully ===")
}
