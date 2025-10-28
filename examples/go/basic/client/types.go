package client

import (
	"time"
)

// Product represents a content product
type Product struct {
	ID          string    `json:"id"`
	Title       string    `json:"title"`
	Description string    `json:"description"`
	Price       string    `json:"price"`
	Currency    string    `json:"currency"`
	ContentURL  string    `json:"content_url"`
	CreatedAt   time.Time `json:"created_at"`
	UpdatedAt   time.Time `json:"updated_at"`
	Status      string    `json:"status"`
}

// PaymentRequest represents a payment request
type PaymentRequest struct {
	ProductID   string `json:"product_id"`
	Amount      string `json:"amount"`
	Currency    string `json:"currency"`
	UserAddress string `json:"user_address"`
	Nonce       string `json:"nonce"`
	Signature   string `json:"signature"`
}

// PaymentResponse represents a payment response
type PaymentResponse struct {
	TransactionHash string    `json:"transaction_hash"`
	Status          string    `json:"status"`
	Amount          string    `json:"amount"`
	Currency        string    `json:"currency"`
	Timestamp       time.Time `json:"timestamp"`
	BlockNumber     uint64    `json:"block_number"`
	GasUsed         uint64    `json:"gas_used"`
	Error           string    `json:"error,omitempty"`
}

// AccessRequest represents an access request
type AccessRequest struct {
	ProductID   string `json:"product_id"`
	UserAddress string `json:"user_address"`
	Timestamp   int64  `json:"timestamp"`
	Signature   string `json:"signature"`
}

// AccessResponse represents an access response
type AccessResponse struct {
	HasAccess bool   `json:"has_access"`
	Reason    string `json:"reason,omitempty"`
	ExpiresAt int64  `json:"expires_at,omitempty"`
}
