package models

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
	Metadata    Metadata  `json:"metadata"`
}

// Metadata contains additional product information
type Metadata struct {
	Category   string            `json:"category"`
	Tags       []string          `json:"tags"`
	Author     string            `json:"author"`
	Language   string            `json:"language"`
	Difficulty string            `json:"difficulty"`
	Duration   int               `json:"duration"` // in minutes
	Custom     map[string]string `json:"custom"`
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

// AnalyticsData represents analytics data
type AnalyticsData struct {
	ProductID    string     `json:"product_id"`
	Views        int64      `json:"views"`
	Purchases    int64      `json:"purchases"`
	Revenue      string     `json:"revenue"`
	Currency     string     `json:"currency"`
	Period       string     `json:"period"`
	GeneratedAt  time.Time  `json:"generated_at"`
	TopCountries []Country  `json:"top_countries"`
	TopReferrers []Referrer `json:"top_referrers"`
}

// Country represents country analytics
type Country struct {
	Code  string `json:"code"`
	Name  string `json:"name"`
	Count int64  `json:"count"`
}

// Referrer represents referrer analytics
type Referrer struct {
	Domain string `json:"domain"`
	Count  int64  `json:"count"`
}
