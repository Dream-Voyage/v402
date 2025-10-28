package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"time"

	"github.com/v402/client-go/v402"
)

func main() {
	// Configure v402 client
	config := &v402.Config{
		PrivateKey:  "0x1234567890abcdef1234567890abcdef12345678",
		Facilitator: "https://facilitator.v402.network",
		AutoPay:     true,
		MaxAmount:   "1000000000000000000", // 1 ETH
		Timeout:     30 * time.Second,
	}

	// Create client
	client, err := v402.NewClient(config)
	if err != nil {
		log.Fatalf("Failed to create client: %v", err)
	}
	defer client.Close()

	// Example URLs to fetch
	urls := []string{
		"https://example.com/article-1",
		"https://example.com/article-2",
		"https://example.com/premium-content",
	}

	ctx := context.Background()

	// Process each URL
	for _, url := range urls {
		fmt.Printf("\nFetching: %s\n", url)

		// Make request
		response, err := client.Get(ctx, url)
		if err != nil {
			log.Printf("Failed to fetch %s: %v", url, err)
			continue
		}

		// Check if payment was made
		if response.PaymentMade {
			fmt.Printf("✅ Payment made: %s\n", response.PaymentAmount)
			fmt.Printf("🔗 Transaction: %s\n", response.TransactionHash)
		}

		// Process content
		fmt.Printf("📄 Content length: %d bytes\n", len(response.Body))
	}
}

// Example response structure
type V402Response struct {
	StatusCode      int    `json:"status_code"`
	Body            []byte `json:"body"`
	PaymentMade     bool   `json:"payment_made"`
	PaymentAmount   string `json:"payment_amount"`
	TransactionHash string `json:"transaction_hash"`
}

// Example HTTP client for direct API access
type DirectHTTPClient struct {
	baseURL   string
	publicKey string
	client    *http.Client
}

func NewDirectHTTPClient(baseURL, publicKey string) *DirectHTTPClient {
	return &DirectHTTPClient{
		baseURL:   baseURL,
		publicKey: publicKey,
		client: &http.Client{
			Timeout: 30 * time.Second,
		},
	}
}

func (c *DirectHTTPClient) FetchContent(ctx context.Context, url string) (*V402Response, error) {
	// Create request
	req, err := http.NewRequestWithContext(ctx, "GET", c.baseURL+"/clients/content", nil)
	if err != nil {
		return nil, err
	}

	// Set headers with public key authentication
	req.Header.Set("Authorization", "Bearer "+c.publicKey)
	req.Header.Set("X-Public-Key", c.publicKey)
	req.Header.Set("X-Content-URL", url)

	// Make request
	resp, err := c.client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	// Decode response
	var response V402Response
	if err := json.NewDecoder(resp.Body).Decode(&response); err != nil {
		return nil, err
	}

	return &response, nil
}
