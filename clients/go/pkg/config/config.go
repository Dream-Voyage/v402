// Package config provides configuration management for the v402 Go client.
package config

import (
	"fmt"
	"os"
	"path/filepath"
	"time"

	"github.com/v402/client-go/pkg/types"
)

// Validate validates the client configuration.
func Validate(cfg *types.ClientConfig) error {
	if cfg.PrivateKey == "" {
		return fmt.Errorf("private_key is required")
	}

	if len(cfg.Chains) == 0 {
		return fmt.Errorf("at least one chain must be configured")
	}

	for _, chain := range cfg.Chains {
		if chain.Name == "" {
			return fmt.Errorf("chain name is required")
		}
		if chain.RPCURL == "" {
			return fmt.Errorf("chain rpc_url is required for %s", chain.Name)
		}
	}

	if cfg.Timeout == 0 {
		cfg.Timeout = 30 * time.Second
	}

	if cfg.MaxConnections == 0 {
		cfg.MaxConnections = 100
	}

	return nil
}

// LoadFromFile loads configuration from a YAML file.
func LoadFromFile(path string) (*types.ClientConfig, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, fmt.Errorf("failed to read config file: %w", err)
	}

	var cfg types.ClientConfig
	if err := yaml.Unmarshal(data, &cfg); err != nil {
		return nil, fmt.Errorf("failed to parse config: %w", err)
	}

	return &cfg, nil
}

// SaveToFile saves configuration to a YAML file.
func SaveToFile(cfg *types.ClientConfig, path string) error {
	// Create directory if it doesn't exist
	dir := filepath.Dir(path)
	if err := os.MkdirAll(dir, 0755); err != nil {
		return fmt.Errorf("failed to create config directory: %w", err)
	}

	data, err := yaml.Marshal(cfg)
	if err != nil {
		return fmt.Errorf("failed to marshal config: %w", err)
	}

	if err := os.WriteFile(path, data, 0644); err != nil {
		return fmt.Errorf("failed to write config file: %w", err)
	}

	return nil
}

// Default returns a default configuration.
func Default() *types.ClientConfig {
	return &types.ClientConfig{
		Chains:              types.DefaultChainConfigs(),
		AutoPay:             true,
		MaxAmountPerRequest: "1000000000000000000", // 1 ETH in wei
		Timeout:             30 * time.Second,
		MaxConnections:      100,
		FacilitatorURL:      "https://facilitator.v402.network",
		Resilience: types.ResilienceConfig{
			EnableCircuitBreaker: true,
			FailureThreshold:     5,
			SuccessThreshold:     3,
			Timeout:              30 * time.Second,
			MaxRetries:           3,
			RetryBackoff:         time.Second,
			RetryJitter:          true,
		},
		Logging: types.LoggingConfig{
			Level:  "info",
			Format: "json",
			Output: "stdout",
		},
		Metrics: types.MetricsConfig{
			Enabled: true,
			Port:    9090,
			Path:    "/metrics",
		},
	}
}
