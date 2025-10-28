package client

import (
	"bytes"
	"context"
	"crypto/ecdsa"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"time"

	"github.com/ethereum/go-ethereum/common/hexutil"
	"github.com/ethereum/go-ethereum/crypto"
)

// V402Client represents the main client for v402 protocol
type V402Client struct {
	config     *Config
	httpClient *http.Client
	privateKey *ecdsa.PrivateKey
}

// Config represents client configuration
type Config struct {
	BaseURL         string
	Timeout         time.Duration
	RetryCount      int
	PublicKey       string
	PrivateKey      string
	ChainID         int64
	RPCURL          string
	ContractAddress string
}

// NewClient creates a new v402 client
func NewClient(config *Config) (*V402Client, error) {
	if config == nil {
		return nil, fmt.Errorf("config cannot be nil")
	}

	// Parse private key
	privateKey, err := crypto.HexToECDSA(config.PrivateKey)
	if err != nil {
		return nil, fmt.Errorf("invalid private key: %w", err)
	}

	// Create HTTP client
	httpClient := &http.Client{
		Timeout: config.Timeout,
	}

	return &V402Client{
		config:     config,
		httpClient: httpClient,
		privateKey: privateKey,
	}, nil
}

// CreateProduct creates a new product
func (c *V402Client) CreateProduct(ctx context.Context, product *Product) (*Product, error) {
	url := fmt.Sprintf("%s/api/v1/products", c.config.BaseURL)

	reqBody, err := json.Marshal(product)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal product: %w", err)
	}

	req, err := http.NewRequestWithContext(ctx, "POST", url, bytes.NewBuffer(reqBody))
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %w", err)
	}

	// Add authentication headers
	if err := c.addAuthHeaders(req, reqBody); err != nil {
		return nil, fmt.Errorf("failed to add auth headers: %w", err)
	}

	resp, err := c.httpClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("failed to execute request: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusCreated {
		body, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("request failed with status %d: %s", resp.StatusCode, string(body))
	}

	var createdProduct Product
	if err := json.NewDecoder(resp.Body).Decode(&createdProduct); err != nil {
		return nil, fmt.Errorf("failed to decode response: %w", err)
	}

	return &createdProduct, nil
}

// GetProduct retrieves a product by ID
func (c *V402Client) GetProduct(ctx context.Context, productID string) (*Product, error) {
	url := fmt.Sprintf("%s/api/v1/products/%s", c.config.BaseURL, productID)

	req, err := http.NewRequestWithContext(ctx, "GET", url, nil)
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %w", err)
	}

	// Add authentication headers
	if err := c.addAuthHeaders(req, nil); err != nil {
		return nil, fmt.Errorf("failed to add auth headers: %w", err)
	}

	resp, err := c.httpClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("failed to execute request: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("request failed with status %d: %s", resp.StatusCode, string(body))
	}

	var product Product
	if err := json.NewDecoder(resp.Body).Decode(&product); err != nil {
		return nil, fmt.Errorf("failed to decode response: %w", err)
	}

	return &product, nil
}

// ProcessPayment processes a payment for a product
func (c *V402Client) ProcessPayment(ctx context.Context, paymentReq *PaymentRequest) (*PaymentResponse, error) {
	url := fmt.Sprintf("%s/api/v1/payments", c.config.BaseURL)

	reqBody, err := json.Marshal(paymentReq)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal payment request: %w", err)
	}

	req, err := http.NewRequestWithContext(ctx, "POST", url, bytes.NewBuffer(reqBody))
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %w", err)
	}

	// Add authentication headers
	if err := c.addAuthHeaders(req, reqBody); err != nil {
		return nil, fmt.Errorf("failed to add auth headers: %w", err)
	}

	resp, err := c.httpClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("failed to execute request: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("request failed with status %d: %s", resp.StatusCode, string(body))
	}

	var paymentResp PaymentResponse
	if err := json.NewDecoder(resp.Body).Decode(&paymentResp); err != nil {
		return nil, fmt.Errorf("failed to decode response: %w", err)
	}

	return &paymentResp, nil
}

// CheckAccess checks if a user has access to a product
func (c *V402Client) CheckAccess(ctx context.Context, accessReq *AccessRequest) (*AccessResponse, error) {
	url := fmt.Sprintf("%s/api/v1/access/check", c.config.BaseURL)

	reqBody, err := json.Marshal(accessReq)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal access request: %w", err)
	}

	req, err := http.NewRequestWithContext(ctx, "POST", url, bytes.NewBuffer(reqBody))
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %w", err)
	}

	// Add authentication headers
	if err := c.addAuthHeaders(req, reqBody); err != nil {
		return nil, fmt.Errorf("failed to add auth headers: %w", err)
	}

	resp, err := c.httpClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("failed to execute request: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("request failed with status %d: %s", resp.StatusCode, string(body))
	}

	var accessResp AccessResponse
	if err := json.NewDecoder(resp.Body).Decode(&accessResp); err != nil {
		return nil, fmt.Errorf("failed to decode response: %w", err)
	}

	return &accessResp, nil
}

// addAuthHeaders adds authentication headers to the request
func (c *V402Client) addAuthHeaders(req *http.Request, body []byte) error {
	// Create signature
	timestamp := time.Now().Unix()
	message := fmt.Sprintf("%s:%d", req.URL.Path, timestamp)
	if body != nil {
		message += fmt.Sprintf(":%s", string(body))
	}

	hash := crypto.Keccak256Hash([]byte(message))
	signature, err := crypto.Sign(hash.Bytes(), c.privateKey)
	if err != nil {
		return fmt.Errorf("failed to sign message: %w", err)
	}

	// Add headers
	req.Header.Set("X-Public-Key", c.config.PublicKey)
	req.Header.Set("X-Timestamp", fmt.Sprintf("%d", timestamp))
	req.Header.Set("X-Signature", hexutil.Encode(signature))
	req.Header.Set("Content-Type", "application/json")

	return nil
}
