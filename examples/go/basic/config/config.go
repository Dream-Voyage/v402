package config

import (
	"time"
)

// ClientConfig represents the configuration for v402 client
type ClientConfig struct {
	// API Configuration
	BaseURL    string        `json:"base_url" yaml:"base_url"`
	Timeout    time.Duration `json:"timeout" yaml:"timeout"`
	RetryCount int           `json:"retry_count" yaml:"retry_count"`

	// Authentication
	PublicKey  string `json:"public_key" yaml:"public_key"`
	PrivateKey string `json:"private_key" yaml:"private_key"`

	// Blockchain Configuration
	ChainID         int64  `json:"chain_id" yaml:"chain_id"`
	RPCURL          string `json:"rpc_url" yaml:"rpc_url"`
	ContractAddress string `json:"contract_address" yaml:"contract_address"`

	// Payment Configuration
	DefaultCurrency string `json:"default_currency" yaml:"default_currency"`
	GasLimit        uint64 `json:"gas_limit" yaml:"gas_limit"`
	GasPrice        string `json:"gas_price" yaml:"gas_price"`

	// Logging
	LogLevel string `json:"log_level" yaml:"log_level"`
	LogFile  string `json:"log_file" yaml:"log_file"`

	// Monitoring
	EnableMetrics bool `json:"enable_metrics" yaml:"enable_metrics"`
	MetricsPort   int  `json:"metrics_port" yaml:"metrics_port"`
	HealthCheck   bool `json:"health_check" yaml:"health_check"`
}

// DefaultConfig returns a default configuration
func DefaultConfig() *ClientConfig {
	return &ClientConfig{
		BaseURL:         "https://api.v402.network",
		Timeout:         30 * time.Second,
		RetryCount:      3,
		ChainID:         1, // Ethereum mainnet
		DefaultCurrency: "USDC",
		GasLimit:        100000,
		GasPrice:        "20000000000", // 20 gwei
		LogLevel:        "info",
		EnableMetrics:   true,
		MetricsPort:     9090,
		HealthCheck:     true,
	}
}

// Validate validates the configuration
func (c *ClientConfig) Validate() error {
	if c.BaseURL == "" {
		return ErrInvalidBaseURL
	}
	if c.PublicKey == "" {
		return ErrMissingPublicKey
	}
	if c.ChainID <= 0 {
		return ErrInvalidChainID
	}
	return nil
}
