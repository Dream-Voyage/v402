package services

import (
	"context"
	"fmt"
	"time"

	"./client"
)

// PaymentService handles payment-related business logic
type PaymentService struct {
	v402Client *client.V402Client
}

// NewPaymentService creates a new payment service
func NewPaymentService(v402Client *client.V402Client) *PaymentService {
	return &PaymentService{
		v402Client: v402Client,
	}
}

// PaymentRequest represents a payment request in the service layer
type PaymentRequest struct {
	ProductID   string `json:"product_id"`
	Amount      string `json:"amount"`
	Currency    string `json:"currency"`
	UserAddress string `json:"user_address"`
	Nonce       string `json:"nonce"`
	Signature   string `json:"signature"`
}

// PaymentResponse represents a payment response in the service layer
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

// AccessRequest represents an access request in the service layer
type AccessRequest struct {
	ProductID   string `json:"product_id"`
	UserAddress string `json:"user_address"`
	Timestamp   int64  `json:"timestamp"`
	Signature   string `json:"signature"`
}

// AccessResponse represents an access response in the service layer
type AccessResponse struct {
	HasAccess bool   `json:"has_access"`
	Reason    string `json:"reason,omitempty"`
	ExpiresAt int64  `json:"expires_at,omitempty"`
}

// ProcessPayment processes a payment
func (s *PaymentService) ProcessPayment(ctx context.Context, paymentReq *PaymentRequest) (*PaymentResponse, error) {
	// Convert service payment request to client payment request
	clientPaymentReq := &client.PaymentRequest{
		ProductID:   paymentReq.ProductID,
		Amount:      paymentReq.Amount,
		Currency:    paymentReq.Currency,
		UserAddress: paymentReq.UserAddress,
		Nonce:       paymentReq.Nonce,
		Signature:   paymentReq.Signature,
	}

	clientPaymentResp, err := s.v402Client.ProcessPayment(ctx, clientPaymentReq)
	if err != nil {
		return nil, fmt.Errorf("failed to process payment: %w", err)
	}

	// Convert client payment response back to service payment response
	return &PaymentResponse{
		TransactionHash: clientPaymentResp.TransactionHash,
		Status:          clientPaymentResp.Status,
		Amount:          clientPaymentResp.Amount,
		Currency:        clientPaymentResp.Currency,
		Timestamp:       clientPaymentResp.Timestamp,
		BlockNumber:     clientPaymentResp.BlockNumber,
		GasUsed:         clientPaymentResp.GasUsed,
		Error:           clientPaymentResp.Error,
	}, nil
}

// GetPayment retrieves a payment by ID
func (s *PaymentService) GetPayment(ctx context.Context, paymentID string) (*PaymentResponse, error) {
	// This would typically involve querying the database
	// For now, we'll return a mock response
	return &PaymentResponse{
		TransactionHash: "0x" + paymentID,
		Status:          "completed",
		Amount:          "10.00",
		Currency:        "USDC",
		Timestamp:       time.Now().Add(-1 * time.Hour),
		BlockNumber:     12345678,
		GasUsed:         50000,
	}, nil
}

// CheckAccess checks if a user has access to a product
func (s *PaymentService) CheckAccess(ctx context.Context, accessReq *AccessRequest) (*AccessResponse, error) {
	// Convert service access request to client access request
	clientAccessReq := &client.AccessRequest{
		ProductID:   accessReq.ProductID,
		UserAddress: accessReq.UserAddress,
		Timestamp:   accessReq.Timestamp,
		Signature:   accessReq.Signature,
	}

	clientAccessResp, err := s.v402Client.CheckAccess(ctx, clientAccessReq)
	if err != nil {
		return nil, fmt.Errorf("failed to check access: %w", err)
	}

	// Convert client access response back to service access response
	return &AccessResponse{
		HasAccess: clientAccessResp.HasAccess,
		Reason:    clientAccessResp.Reason,
		ExpiresAt: clientAccessResp.ExpiresAt,
	}, nil
}
