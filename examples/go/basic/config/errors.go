package config

import "errors"

// Configuration errors
var (
	ErrInvalidBaseURL    = errors.New("invalid base URL")
	ErrMissingPublicKey  = errors.New("missing public key")
	ErrInvalidChainID    = errors.New("invalid chain ID")
	ErrInvalidTimeout    = errors.New("invalid timeout")
	ErrInvalidRetryCount = errors.New("invalid retry count")
)
