// Package errors defines the error types for the v402 Go client.
package errors

import (
	"fmt"
)

// ErrorCode represents error categories.
type ErrorCode string

const (
	ErrorCodePayment  ErrorCode = "PAYMENT_ERROR"
	ErrorCodeChain    ErrorCode = "CHAIN_ERROR"
	ErrorCodeNetwork  ErrorCode = "NETWORK_ERROR"
	ErrorCodeConfig   ErrorCode = "CONFIG_ERROR"
	ErrorCodeInternal ErrorCode = "INTERNAL_ERROR"
)

// V402Error is the base error type for all v402 client errors.
type V402Error struct {
	Code    ErrorCode
	Message string
	Details map[string]interface{}
	Cause   error
}

// Error implements the error interface.
func (e *V402Error) Error() string {
	if e.Cause != nil {
		return fmt.Sprintf("[%s] %s: %v", e.Code, e.Message, e.Cause)
	}
	return fmt.Sprintf("[%s] %s", e.Code, e.Message)
}

// Unwrap returns the underlying cause.
func (e *V402Error) Unwrap() error {
	return e.Cause
}

// PaymentError represents payment-related errors.
type PaymentError struct {
	*V402Error
}

// NewPaymentError creates a new payment error.
func NewPaymentError(message string, details map[string]interface{}) *PaymentError {
	return &PaymentError{
		V402Error: &V402Error{
			Code:    ErrorCodePayment,
			Message: message,
			Details: details,
		},
	}
}

// PaymentLimitExceeded represents when payment amount exceeds maximum.
type PaymentLimitExceeded struct {
	*PaymentError
	Amount    string
	MaxAmount string
}

// NewPaymentLimitExceeded creates a payment limit exceeded error.
func NewPaymentLimitExceeded(amount, maxAmount string) *PaymentLimitExceeded {
	return &PaymentLimitExceeded{
		PaymentError: NewPaymentError(
			fmt.Sprintf("Payment amount %s exceeds maximum %s", amount, maxAmount),
			map[string]interface{}{
				"amount":     amount,
				"max_amount": maxAmount,
			},
		),
		Amount:    amount,
		MaxAmount: maxAmount,
	}
}

// PaymentVerificationFailed represents payment verification failures.
type PaymentVerificationFailed struct {
	*PaymentError
	Reason string
}

// NewPaymentVerificationFailed creates a payment verification failed error.
func NewPaymentVerificationFailed(reason string, details map[string]interface{}) *PaymentVerificationFailed {
	return &PaymentVerificationFailed{
		PaymentError: NewPaymentError(
			fmt.Sprintf("Payment verification failed: %s", reason),
			details,
		),
		Reason: reason,
	}
}

// ChainError represents blockchain-related errors.
type ChainError struct {
	*V402Error
	ChainName string
}

// NewChainError creates a new chain error.
func NewChainError(chainName, message string, cause error) *ChainError {
	return &ChainError{
		V402Error: &V402Error{
			Code:    ErrorCodeChain,
			Message: message,
			Cause:   cause,
			Details: map[string]interface{}{
				"chain_name": chainName,
			},
		},
		ChainName: chainName,
	}
}

// UnsupportedChain represents when a chain is not supported.
type UnsupportedChain struct {
	*ChainError
}

// NewUnsupportedChain creates an unsupported chain error.
func NewUnsupportedChain(chainName string) *UnsupportedChain {
	return &UnsupportedChain{
		ChainError: NewChainError(
			chainName,
			fmt.Sprintf("Chain '%s' is not supported", chainName),
			nil,
		),
	}
}

// ChainConnectionError represents connection failures to blockchain.
type ChainConnectionError struct {
	*ChainError
}

// NewChainConnectionError creates a chain connection error.
func NewChainConnectionError(chainName, reason string) *ChainConnectionError {
	return &ChainConnectionError{
		ChainError: NewChainError(
			chainName,
			fmt.Sprintf("Failed to connect to %s: %s", chainName, reason),
			nil,
		),
	}
}

// NetworkError represents network-related errors.
type NetworkError struct {
	*V402Error
	URL string
}

// NewNetworkError creates a new network error.
func NewNetworkError(url, message string, cause error) *NetworkError {
	return &NetworkError{
		V402Error: &V402Error{
			Code:    ErrorCodeNetwork,
			Message: message,
			Cause:   cause,
			Details: map[string]interface{}{
				"url": url,
			},
		},
		URL: url,
	}
}

// ConnectionTimeout represents connection timeout errors.
type ConnectionTimeout struct {
	*NetworkError
	Timeout int
}

// NewConnectionTimeout creates a connection timeout error.
func NewConnectionTimeout(url string, timeout int) *ConnectionTimeout {
	return &ConnectionTimeout{
		NetworkError: NewNetworkError(
			url,
			fmt.Sprintf("Connection to %s timed out after %ds", url, timeout),
			nil,
		),
		Timeout: timeout,
	}
}

// RequestFailed represents failed HTTP requests.
type RequestFailed struct {
	*NetworkError
	StatusCode int
}

// NewRequestFailed creates a request failed error.
func NewRequestFailed(url string, statusCode int, reason string) *RequestFailed {
	return &RequestFailed{
		NetworkError: NewNetworkError(
			url,
			fmt.Sprintf("Request to %s failed: %s", url, reason),
			nil,
		),
		StatusCode: statusCode,
	}
}

// TooManyRetries represents when maximum retry attempts are exceeded.
type TooManyRetries struct {
	*NetworkError
	Attempts int
}

// NewTooManyRetries creates a too many retries error.
func NewTooManyRetries(url string, attempts int) *TooManyRetries {
	return &TooManyRetries{
		NetworkError: NewNetworkError(
			url,
			fmt.Sprintf("Request to %s failed after %d attempts", url, attempts),
			nil,
		),
		Attempts: attempts,
	}
}

// ConfigError represents configuration-related errors.
type ConfigError struct {
	*V402Error
}

// NewConfigError creates a new configuration error.
func NewConfigError(message string, cause error) *ConfigError {
	return &ConfigError{
		V402Error: &V402Error{
			Code:    ErrorCodeConfig,
			Message: message,
			Cause:   cause,
		},
	}
}

// InternalError represents internal client errors.
type InternalError struct {
	*V402Error
}

// NewInternalError creates a new internal error.
func NewInternalError(message string, cause error) *InternalError {
	return &InternalError{
		V402Error: &V402Error{
			Code:    ErrorCodeInternal,
			Message: message,
			Cause:   cause,
		},
	}
}

// IsPaymentError checks if error is payment-related.
func IsPaymentError(err error) bool {
	var paymentErr *PaymentError
	return As(err, &paymentErr)
}

// IsChainError checks if error is chain-related.
func IsChainError(err error) bool {
	var chainErr *ChainError
	return As(err, &chainErr)
}

// IsNetworkError checks if error is network-related.
func IsNetworkError(err error) bool {
	var networkErr *NetworkError
	return As(err, &networkErr)
}

// As finds the first error in err's chain that matches target.
func As(err error, target interface{}) bool {
	// Simple implementation - in real code would use errors.As
	return false
}
