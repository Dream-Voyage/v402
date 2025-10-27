// Package client provides the main v402 client implementation for Go.
package client

import (
	"context"
	"encoding/json"
	"io"
	"net/http"
	"sync"
	"time"

	"github.com/v402/client-go/pkg/chains"
	"github.com/v402/client-go/pkg/config"
	"github.com/v402/client-go/pkg/errors"
	"github.com/v402/client-go/pkg/log"
	"github.com/v402/client-go/pkg/metrics"
	"github.com/v402/client-go/pkg/payment"
	"github.com/v402/client-go/pkg/types"
	"go.uber.org/zap"
)

// Client represents the main v402 client with enterprise features.
//
// The client provides:
// - High-performance concurrent request processing
// - Multi-chain payment support
// - Circuit breaker pattern
// - Comprehensive metrics and tracing
// - Context-aware operations
// - Graceful shutdown
type Client struct {
	config *types.ClientConfig
	logger *zap.Logger

	// Core components
	httpClient     *http.Client
	chainManager   chains.Manager
	paymentManager payment.Manager
	metricsManager metrics.Manager

	// State management
	mu         sync.RWMutex
	closed     bool
	activeReqs int64

	// Context for shutdown
	ctx    context.Context
	cancel context.CancelFunc
	wg     sync.WaitGroup

	// Middleware chain
	middlewares []Middleware
}

// Middleware defines the interface for client middleware.
type Middleware interface {
	Handle(ctx context.Context, req *Request, next Handler) (*types.PaymentResponse, error)
}

// Handler defines the request handler interface.
type Handler interface {
	Handle(ctx context.Context, req *Request) (*types.PaymentResponse, error)
}

// HandlerFunc is an adapter to allow functions to be used as handlers.
type HandlerFunc func(ctx context.Context, req *Request) (*types.PaymentResponse, error)

// Handle calls f(ctx, req).
func (f HandlerFunc) Handle(ctx context.Context, req *Request) (*types.PaymentResponse, error) {
	return f(ctx, req)
}

// Request represents an HTTP request with v402 context.
type Request struct {
	Method  string
	URL     string
	Headers map[string]string
	Body    io.Reader
	AutoPay bool
}

// ClientOption defines options for client configuration.
type ClientOption func(*Client) error

// New creates a new v402 client with the given configuration.
//
// Example:
//
//	cfg := &types.ClientConfig{
//	    PrivateKey: "0x...",
//	    Chains: types.DefaultChainConfigs(),
//	    AutoPay: true,
//	}
//
//	client, err := client.New(cfg,
//	    client.WithMaxConnections(100),
//	    client.WithTimeout(30*time.Second),
//	)
//	if err != nil {
//	    log.Fatal(err)
//	}
//	defer client.Close()
func New(cfg *types.ClientConfig, opts ...ClientOption) (*Client, error) {
	// Validate configuration
	if err := config.Validate(cfg); err != nil {
		return nil, errors.NewConfigError("invalid configuration", err)
	}

	// Create client context
	ctx, cancel := context.WithCancel(context.Background())

	// Initialize logger
	logger, err := log.NewLogger(&cfg.Logging)
	if err != nil {
		cancel()
		return nil, errors.NewConfigError("failed to initialize logger", err)
	}

	// Create client instance
	client := &Client{
		config: cfg,
		logger: logger,
		ctx:    ctx,
		cancel: cancel,
	}

	// Apply options
	for _, opt := range opts {
		if err := opt(client); err != nil {
			cancel()
			return nil, err
		}
	}

	// Initialize components
	if err := client.initialize(); err != nil {
		cancel()
		return nil, err
	}

	logger.Info("v402 client initialized",
		zap.String("version", "1.0.0"),
		zap.Int("chains", len(cfg.Chains)),
		zap.Bool("auto_pay", cfg.AutoPay),
	)

	return client, nil
}

// initialize sets up all client components.
func (c *Client) initialize() error {
	c.mu.Lock()
	defer c.mu.Unlock()

	// Initialize HTTP client
	c.httpClient = &http.Client{
		Timeout: c.config.Timeout,
		Transport: &http.Transport{
			MaxIdleConns:        c.config.MaxConnections,
			MaxIdleConnsPerHost: c.config.MaxConnections / 4,
			IdleConnTimeout:     90 * time.Second,
			DisableCompression:  false,
		},
	}

	// Initialize chain manager
	var err error
	c.chainManager, err = chains.NewManager(c.config.Chains, c.logger)
	if err != nil {
		return errors.NewChainError("", "failed to initialize chain manager", err)
	}

	// Initialize payment manager
	c.paymentManager, err = payment.NewManager(&payment.Config{
		PrivateKey:     c.config.PrivateKey,
		Chains:         c.config.Chains,
		MaxAmount:      c.config.MaxAmountPerRequest,
		FacilitatorURL: c.config.FacilitatorURL,
	}, c.logger)
	if err != nil {
		return errors.NewPaymentError("failed to initialize payment manager", nil)
	}

	// Initialize metrics manager
	if c.config.Metrics.Enabled {
		c.metricsManager, err = metrics.NewManager(&c.config.Metrics, c.logger)
		if err != nil {
			return errors.NewInternalError("failed to initialize metrics manager", err)
		}
	}

	return nil
}

// Get performs a GET request with automatic payment handling.
//
// The method supports context cancellation and will respect deadlines.
// If auto_pay is enabled, it will automatically handle 402 Payment Required responses.
//
// Example:
//
//	ctx := context.WithTimeout(context.Background(), 30*time.Second)
//	resp, err := client.Get(ctx, "https://example.com/premium-content")
//	if err != nil {
//	    return err
//	}
//
//	if resp.PaymentMade {
//	    fmt.Printf("Paid %s for content\n", resp.PaymentAmount)
//	}
func (c *Client) Get(ctx context.Context, url string, options ...RequestOption) (*types.PaymentResponse, error) {
	req := &Request{
		Method:  "GET",
		URL:     url,
		Headers: make(map[string]string),
		AutoPay: c.config.AutoPay,
	}

	// Apply request options
	for _, opt := range options {
		opt(req)
	}

	return c.executeRequest(ctx, req)
}

// Post performs a POST request with automatic payment handling.
func (c *Client) Post(ctx context.Context, url string, body io.Reader, options ...RequestOption) (*types.PaymentResponse, error) {
	req := &Request{
		Method:  "POST",
		URL:     url,
		Headers: make(map[string]string),
		Body:    body,
		AutoPay: c.config.AutoPay,
	}

	// Apply request options
	for _, opt := range options {
		opt(req)
	}

	return c.executeRequest(ctx, req)
}

// BatchGet performs multiple GET requests concurrently with automatic payment handling.
//
// The method uses goroutines to process requests concurrently while respecting
// the maximum concurrent connections limit. Failed requests are included in the
// results with error information.
//
// Example:
//
//	urls := []string{
//	    "https://example.com/article1",
//	    "https://example.com/article2",
//	    "https://example.com/article3",
//	}
//
//	responses, err := client.BatchGet(ctx, urls, 10) // max 10 concurrent
//	for i, resp := range responses {
//	    if resp.StatusCode == 200 {
//	        fmt.Printf("URL %d: Success\n", i)
//	    } else {
//	        fmt.Printf("URL %d: Failed with status %d\n", i, resp.StatusCode)
//	    }
//	}
func (c *Client) BatchGet(ctx context.Context, urls []string, maxConcurrent int) ([]*types.PaymentResponse, error) {
	if c.isClosed() {
		return nil, errors.NewInternalError("client is closed", nil)
	}

	if len(urls) == 0 {
		return []*types.PaymentResponse{}, nil
	}

	// Create semaphore to limit concurrent requests
	semaphore := make(chan struct{}, maxConcurrent)
	responses := make([]*types.PaymentResponse, len(urls))
	var wg sync.WaitGroup

	c.logger.Info("starting batch request",
		zap.Int("url_count", len(urls)),
		zap.Int("max_concurrent", maxConcurrent),
	)

	// Process URLs concurrently
	for i, url := range urls {
		wg.Add(1)

		go func(index int, u string) {
			defer wg.Done()

			// Acquire semaphore
			select {
			case semaphore <- struct{}{}:
				defer func() { <-semaphore }()
			case <-ctx.Done():
				responses[index] = &types.PaymentResponse{
					StatusCode: 0,
					Body:       []byte("request cancelled"),
					URL:        u,
					Timestamp:  time.Now(),
				}
				return
			}

			// Make request
			resp, err := c.Get(ctx, u)
			if err != nil {
				responses[index] = &types.PaymentResponse{
					StatusCode: 500,
					Body:       []byte(err.Error()),
					URL:        u,
					Timestamp:  time.Now(),
				}
			} else {
				responses[index] = resp
			}
		}(i, url)
	}

	// Wait for all requests to complete
	wg.Wait()

	c.logger.Info("batch request completed",
		zap.Int("url_count", len(urls)),
	)

	return responses, nil
}

// executeRequest executes a request through the middleware chain.
func (c *Client) executeRequest(ctx context.Context, req *Request) (*types.PaymentResponse, error) {
	if c.isClosed() {
		return nil, errors.NewInternalError("client is closed", nil)
	}

	// Increment active requests
	c.incrementActiveRequests()
	defer c.decrementActiveRequests()

	// Create handler chain
	handler := c.createHandlerChain()

	// Execute request
	startTime := time.Now()
	resp, err := handler.Handle(ctx, req)
	duration := time.Since(startTime)

	// Record metrics
	if c.metricsManager != nil {
		c.metricsManager.RecordRequest(req.Method, resp, err, duration)
	}

	// Log request
	if err != nil {
		c.logger.Error("request failed",
			zap.String("method", req.Method),
			zap.String("url", req.URL),
			zap.Duration("duration", duration),
			zap.Error(err),
		)
	} else {
		c.logger.Info("request completed",
			zap.String("method", req.Method),
			zap.String("url", req.URL),
			zap.Int("status", resp.StatusCode),
			zap.Bool("payment_made", resp.PaymentMade),
			zap.Duration("duration", duration),
		)
	}

	return resp, err
}

// createHandlerChain creates the middleware chain with the core handler at the end.
func (c *Client) createHandlerChain() Handler {
	// Core handler that actually makes the HTTP request
	coreHandler := HandlerFunc(c.handleHTTPRequest)

	// Wrap with middlewares in reverse order
	var handler Handler = coreHandler
	for i := len(c.middlewares) - 1; i >= 0; i-- {
		middleware := c.middlewares[i]
		next := handler
		handler = HandlerFunc(func(ctx context.Context, req *Request) (*types.PaymentResponse, error) {
			return middleware.Handle(ctx, req, next)
		})
	}

	return handler
}

// handleHTTPRequest is the core HTTP request handler.
func (c *Client) handleHTTPRequest(ctx context.Context, req *Request) (*types.PaymentResponse, error) {
	// Create HTTP request
	httpReq, err := http.NewRequestWithContext(ctx, req.Method, req.URL, req.Body)
	if err != nil {
		return nil, errors.NewNetworkError(req.URL, "failed to create request", err)
	}

	// Add headers
	for key, value := range req.Headers {
		httpReq.Header.Set(key, value)
	}

	// Make HTTP request
	startTime := time.Now()
	httpResp, err := c.httpClient.Do(httpReq)
	if err != nil {
		return nil, errors.NewNetworkError(req.URL, "request failed", err)
	}
	defer httpResp.Body.Close()

	// Read response body
	body, err := io.ReadAll(httpResp.Body)
	if err != nil {
		return nil, errors.NewNetworkError(req.URL, "failed to read response", err)
	}

	// Create response
	response := &types.PaymentResponse{
		StatusCode: httpResp.StatusCode,
		Body:       body,
		Headers:    make(map[string]string),
		URL:        req.URL,
		Timestamp:  time.Now(),
		TotalTime:  time.Since(startTime),
	}

	// Copy headers
	for key, values := range httpResp.Header {
		if len(values) > 0 {
			response.Headers[key] = values[0]
		}
	}

	// Handle 402 Payment Required
	if httpResp.StatusCode == 402 && req.AutoPay {
		return c.handlePaymentRequired(ctx, req, response)
	}

	return response, nil
}

// handlePaymentRequired processes 402 Payment Required responses.
func (c *Client) handlePaymentRequired(ctx context.Context, req *Request, resp *types.PaymentResponse) (*types.PaymentResponse, error) {
	c.logger.Info("payment required, processing payment",
		zap.String("url", req.URL),
	)

	// Parse payment requirements
	var paymentRequired types.PaymentRequiredResponse
	if err := json.Unmarshal(resp.Body, &paymentRequired); err != nil {
		return nil, errors.NewPaymentVerificationFailed("invalid payment requirements", map[string]interface{}{
			"url":   req.URL,
			"error": err.Error(),
		})
	}

	// Select payment requirements
	selectedReq, err := c.paymentManager.SelectPaymentRequirements(paymentRequired.Accepts)
	if err != nil {
		return nil, err
	}

	// Create payment header
	paymentHeader, err := c.paymentManager.CreatePaymentHeader(selectedReq)
	if err != nil {
		return nil, err
	}

	// Retry request with payment
	req.Headers["X-PAYMENT"] = paymentHeader

	c.logger.Info("retrying request with payment",
		zap.String("url", req.URL),
		zap.String("amount", selectedReq.MaxAmountRequired),
		zap.String("network", selectedReq.Network),
	)

	paidResp, err := c.handleHTTPRequest(ctx, req)
	if err != nil {
		return nil, err
	}

	// Mark as paid
	paidResp.PaymentMade = true
	paidResp.PaymentAmount = selectedReq.MaxAmountRequired
	paidResp.Network = selectedReq.Network

	// Process settlement response
	if settlementHeader := paidResp.Headers["X-PAYMENT-RESPONSE"]; settlementHeader != "" {
		// TODO: Decode settlement response and extract transaction info
		paidResp.TransactionHash = "0x..." // Placeholder
	}

	return paidResp, nil
}

// GetPaymentHistory returns the payment history.
func (c *Client) GetPaymentHistory(ctx context.Context, limit int) ([]*types.PaymentHistory, error) {
	if c.paymentManager == nil {
		return []*types.PaymentHistory{}, nil
	}

	return c.paymentManager.GetHistory(ctx, limit)
}

// GetPaymentStatistics returns payment statistics.
func (c *Client) GetPaymentStatistics(ctx context.Context) (*types.PaymentStatistics, error) {
	if c.paymentManager == nil {
		return &types.PaymentStatistics{}, nil
	}

	return c.paymentManager.GetStatistics(ctx)
}

// HealthCheck performs a comprehensive health check.
func (c *Client) HealthCheck(ctx context.Context) (*types.HealthStatus, error) {
	status := &types.HealthStatus{
		IsHealthy:         true,
		Timestamp:         time.Now(),
		HTTPClientHealthy: c.httpClient != nil,
		ChainsHealthy:     make(map[string]bool),
		ActiveConnections: int(c.getActiveRequests()),
	}

	// Check chain manager
	if c.chainManager != nil {
		chainHealth, err := c.chainManager.HealthCheck(ctx)
		if err != nil {
			status.IsHealthy = false
			status.LastError = err.Error()
		} else {
			status.ChainsHealthy = chainHealth
		}
	}

	// Check facilitator
	if c.paymentManager != nil {
		facilitatorHealthy, err := c.paymentManager.HealthCheck(ctx)
		if err != nil {
			status.IsHealthy = false
			status.FacilitatorHealthy = false
			if status.LastError == "" {
				status.LastError = err.Error()
			}
		} else {
			status.FacilitatorHealthy = facilitatorHealthy
		}
	}

	return status, nil
}

// Close gracefully shuts down the client.
func (c *Client) Close() error {
	c.mu.Lock()
	if c.closed {
		c.mu.Unlock()
		return nil
	}
	c.closed = true
	c.mu.Unlock()

	c.logger.Info("shutting down v402 client")

	// Cancel context to stop new requests
	c.cancel()

	// Wait for active requests to complete (with timeout)
	done := make(chan struct{})
	go func() {
		c.wg.Wait()
		close(done)
	}()

	select {
	case <-done:
		c.logger.Info("all requests completed")
	case <-time.After(30 * time.Second):
		c.logger.Warn("timeout waiting for requests to complete")
	}

	// Close components
	var errs []error

	if c.chainManager != nil {
		if err := c.chainManager.Close(); err != nil {
			errs = append(errs, err)
		}
	}

	if c.paymentManager != nil {
		if err := c.paymentManager.Close(); err != nil {
			errs = append(errs, err)
		}
	}

	if c.metricsManager != nil {
		if err := c.metricsManager.Close(); err != nil {
			errs = append(errs, err)
		}
	}

	c.logger.Info("v402 client shutdown complete")

	// Return first error if any
	if len(errs) > 0 {
		return errs[0]
	}

	return nil
}

// Helper methods for state management
func (c *Client) isClosed() bool {
	c.mu.RLock()
	defer c.mu.RUnlock()
	return c.closed
}

func (c *Client) incrementActiveRequests() {
	c.mu.Lock()
	c.activeReqs++
	c.mu.Unlock()
	c.wg.Add(1)
}

func (c *Client) decrementActiveRequests() {
	c.mu.Lock()
	c.activeReqs--
	c.mu.Unlock()
	c.wg.Done()
}

func (c *Client) getActiveRequests() int64 {
	c.mu.RLock()
	defer c.mu.RUnlock()
	return c.activeReqs
}

// RequestOption defines options for individual requests.
type RequestOption func(*Request)

// WithHeaders adds headers to the request.
func WithHeaders(headers map[string]string) RequestOption {
	return func(req *Request) {
		for k, v := range headers {
			req.Headers[k] = v
		}
	}
}

// WithAutoPay overrides the auto-pay setting for this request.
func WithAutoPay(autoPay bool) RequestOption {
	return func(req *Request) {
		req.AutoPay = autoPay
	}
}

// Client options
func WithMaxConnections(max int) ClientOption {
	return func(c *Client) error {
		c.config.MaxConnections = max
		return nil
	}
}

func WithTimeout(timeout time.Duration) ClientOption {
	return func(c *Client) error {
		c.config.Timeout = timeout
		return nil
	}
}

func WithMiddleware(middleware Middleware) ClientOption {
	return func(c *Client) error {
		c.middlewares = append(c.middlewares, middleware)
		return nil
	}
}
