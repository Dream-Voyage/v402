// Package types defines the core data structures for the v402 Go client.
package types

import (
	"time"
)

// ChainType represents the type of blockchain network.
type ChainType string

const (
	ChainTypeEVM     ChainType = "evm"
	ChainTypeSolana  ChainType = "solana"
	ChainTypeBSC     ChainType = "bsc"
	ChainTypePolygon ChainType = "polygon"
)

// PaymentStatus represents the status of a payment transaction.
type PaymentStatus string

const (
	PaymentStatusPending   PaymentStatus = "pending"
	PaymentStatusConfirmed PaymentStatus = "confirmed"
	PaymentStatusFailed    PaymentStatus = "failed"
	PaymentStatusExpired   PaymentStatus = "expired"
)

// PaymentScheme represents the payment scheme type.
type PaymentScheme string

const (
	PaymentSchemeExact   PaymentScheme = "exact"
	PaymentSchemeUpto    PaymentScheme = "upto"
	PaymentSchemeDynamic PaymentScheme = "dynamic"
)

// ChainConfig holds configuration for a blockchain network.
type ChainConfig struct {
	Name           string    `yaml:"name" json:"name"`
	Type           ChainType `yaml:"type" json:"type"`
	RPCURL         string    `yaml:"rpc_url" json:"rpc_url"`
	ChainID        *int64    `yaml:"chain_id,omitempty" json:"chain_id,omitempty"`
	NativeCurrency string    `yaml:"native_currency" json:"native_currency"`
	ExplorerURL    string    `yaml:"explorer_url,omitempty" json:"explorer_url,omitempty"`
	MaxRetries     int       `yaml:"max_retries" json:"max_retries"`
	Timeout        int       `yaml:"timeout" json:"timeout"`
	GasMultiplier  float64   `yaml:"gas_multiplier" json:"gas_multiplier"`
}

// ClientConfig holds the main client configuration.
type ClientConfig struct {
	PrivateKey          string        `yaml:"private_key" json:"private_key"`
	Chains              []ChainConfig `yaml:"chains" json:"chains"`
	AutoPay             bool          `yaml:"auto_pay" json:"auto_pay"`
	MaxAmountPerRequest string        `yaml:"max_amount_per_request" json:"max_amount_per_request"`
	Timeout             time.Duration `yaml:"timeout" json:"timeout"`
	MaxConnections      int           `yaml:"max_connections" json:"max_connections"`
	FacilitatorURL      string        `yaml:"facilitator_url" json:"facilitator_url"`

	// Resilience configuration
	Resilience ResilienceConfig `yaml:"resilience" json:"resilience"`

	// Logging configuration
	Logging LoggingConfig `yaml:"logging" json:"logging"`

	// Metrics configuration
	Metrics MetricsConfig `yaml:"metrics" json:"metrics"`
}

// ResilienceConfig holds resilience pattern configuration.
type ResilienceConfig struct {
	EnableCircuitBreaker bool          `yaml:"enable_circuit_breaker" json:"enable_circuit_breaker"`
	FailureThreshold     int           `yaml:"failure_threshold" json:"failure_threshold"`
	SuccessThreshold     int           `yaml:"success_threshold" json:"success_threshold"`
	Timeout              time.Duration `yaml:"timeout" json:"timeout"`
	MaxRetries           int           `yaml:"max_retries" json:"max_retries"`
	RetryBackoff         time.Duration `yaml:"retry_backoff" json:"retry_backoff"`
	RetryJitter          bool          `yaml:"retry_jitter" json:"retry_jitter"`
}

// LoggingConfig holds logging configuration.
type LoggingConfig struct {
	Level    string `yaml:"level" json:"level"`
	Format   string `yaml:"format" json:"format"`
	Output   string `yaml:"output" json:"output"`
	FilePath string `yaml:"file_path,omitempty" json:"file_path,omitempty"`
}

// MetricsConfig holds metrics configuration.
type MetricsConfig struct {
	Enabled bool   `yaml:"enabled" json:"enabled"`
	Port    int    `yaml:"port" json:"port"`
	Path    string `yaml:"path" json:"path"`
}

// PaymentRequirements represents payment requirements from server.
type PaymentRequirements struct {
	Scheme            PaymentScheme `json:"scheme"`
	Network           string        `json:"network"`
	MaxAmountRequired string        `json:"maxAmountRequired"`
	Resource          string        `json:"resource"`
	Description       string        `json:"description"`
	MimeType          string        `json:"mimeType"`
	PayTo             string        `json:"payTo"`
	MaxTimeoutSeconds int           `json:"maxTimeoutSeconds"`
	Asset             string        `json:"asset"`
	Extra             interface{}   `json:"extra,omitempty"`
}

// PaymentRequiredResponse represents a 402 Payment Required response.
type PaymentRequiredResponse struct {
	X402Version int                   `json:"x402Version"`
	Accepts     []PaymentRequirements `json:"accepts"`
	Error       string                `json:"error,omitempty"`
}

// PaymentResponse represents the response from a paid request.
type PaymentResponse struct {
	StatusCode      int               `json:"status_code"`
	Body            []byte            `json:"body"`
	Headers         map[string]string `json:"headers"`
	URL             string            `json:"url"`
	PaymentMade     bool              `json:"payment_made"`
	PaymentAmount   string            `json:"payment_amount,omitempty"`
	TransactionHash string            `json:"transaction_hash,omitempty"`
	Network         string            `json:"network,omitempty"`
	Payer           string            `json:"payer,omitempty"`
	Timestamp       time.Time         `json:"timestamp"`
	TotalTime       time.Duration     `json:"total_time"`
	DNSTime         time.Duration     `json:"dns_time,omitempty"`
	ConnectTime     time.Duration     `json:"connect_time,omitempty"`
}

// PaymentHistory represents a record of a payment transaction.
type PaymentHistory struct {
	PaymentID       string        `json:"payment_id"`
	URL             string        `json:"url"`
	Amount          string        `json:"amount"`
	TransactionHash string        `json:"transaction_hash"`
	Network         string        `json:"network"`
	ChainType       ChainType     `json:"chain_type"`
	Payer           string        `json:"payer"`
	Payee           string        `json:"payee"`
	Timestamp       time.Time     `json:"timestamp"`
	Status          PaymentStatus `json:"status"`
	Description     string        `json:"description"`
	Scheme          PaymentScheme `json:"scheme"`
	BlockNumber     *int64        `json:"block_number,omitempty"`
	GasUsed         string        `json:"gas_used,omitempty"`
	GasPrice        string        `json:"gas_price,omitempty"`
	Metadata        interface{}   `json:"metadata,omitempty"`
}

// PaymentStatistics represents statistics about payments made.
type PaymentStatistics struct {
	TotalPayments      int                    `json:"total_payments"`
	SuccessfulPayments int                    `json:"successful_payments"`
	FailedPayments     int                    `json:"failed_payments"`
	TotalAmount        string                 `json:"total_amount"`
	AverageAmount      string                 `json:"average_amount"`
	MinAmount          string                 `json:"min_amount"`
	MaxAmount          string                 `json:"max_amount"`
	UniqueResources    int                    `json:"unique_resources"`
	UniqueNetworks     int                    `json:"unique_networks"`
	TimePeriodStart    time.Time              `json:"time_period_start"`
	TimePeriodEnd      time.Time              `json:"time_period_end"`
	NetworkBreakdown   map[string]interface{} `json:"network_breakdown"`
}

// HealthStatus represents the health status of the client.
type HealthStatus struct {
	IsHealthy          bool            `json:"is_healthy"`
	Timestamp          time.Time       `json:"timestamp"`
	HTTPClientHealthy  bool            `json:"http_client_healthy"`
	ChainsHealthy      map[string]bool `json:"chains_healthy"`
	FacilitatorHealthy bool            `json:"facilitator_healthy"`
	CacheHealthy       bool            `json:"cache_healthy"`
	ActiveConnections  int             `json:"active_connections"`
	CacheSize          int             `json:"cache_size"`
	MemoryUsageMB      float64         `json:"memory_usage_mb,omitempty"`
	LastError          string          `json:"last_error,omitempty"`
	ErrorCount         int             `json:"error_count"`
}

// CircuitBreakerState represents the state of a circuit breaker.
type CircuitBreakerState struct {
	IsOpen          bool       `json:"is_open"`
	FailureCount    int        `json:"failure_count"`
	SuccessCount    int        `json:"success_count"`
	LastFailureTime *time.Time `json:"last_failure_time,omitempty"`
	LastSuccessTime *time.Time `json:"last_success_time,omitempty"`
	NextRetryTime   *time.Time `json:"next_retry_time,omitempty"`
}

// DefaultChainConfigs returns default configurations for supported chains.
func DefaultChainConfigs() []ChainConfig {
	return []ChainConfig{
		{
			Name:           "ethereum",
			Type:           ChainTypeEVM,
			RPCURL:         "https://eth-mainnet.g.alchemy.com/v2/demo",
			ChainID:        int64Ptr(1),
			NativeCurrency: "ETH",
			ExplorerURL:    "https://etherscan.io",
			MaxRetries:     3,
			Timeout:        30,
			GasMultiplier:  1.2,
		},
		{
			Name:           "base",
			Type:           ChainTypeEVM,
			RPCURL:         "https://mainnet.base.org",
			ChainID:        int64Ptr(8453),
			NativeCurrency: "ETH",
			ExplorerURL:    "https://basescan.org",
			MaxRetries:     3,
			Timeout:        30,
			GasMultiplier:  1.2,
		},
		{
			Name:           "polygon",
			Type:           ChainTypePolygon,
			RPCURL:         "https://polygon-rpc.com",
			ChainID:        int64Ptr(137),
			NativeCurrency: "MATIC",
			ExplorerURL:    "https://polygonscan.com",
			MaxRetries:     3,
			Timeout:        30,
			GasMultiplier:  1.2,
		},
		{
			Name:           "solana",
			Type:           ChainTypeSolana,
			RPCURL:         "https://api.mainnet-beta.solana.com",
			NativeCurrency: "SOL",
			ExplorerURL:    "https://explorer.solana.com",
			MaxRetries:     3,
			Timeout:        30,
		},
	}
}

// Helper function to create int64 pointer
func int64Ptr(i int64) *int64 {
	return &i
}

// JSON returns the response body as JSON
func (pr *PaymentResponse) JSON() (interface{}, error) {
	// Implementation would parse JSON from Body
	return nil, nil
}

// Text returns the response body as text
func (pr *PaymentResponse) Text() string {
	return string(pr.Body)
}
