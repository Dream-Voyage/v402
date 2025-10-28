package handlers

import (
	"encoding/json"
	"fmt"
	"net/http"
	"strings"

	"./services"
)

// PaymentHandler handles payment-related HTTP requests
type PaymentHandler struct {
	paymentService *services.PaymentService
}

// NewPaymentHandler creates a new payment handler
func NewPaymentHandler(paymentService *services.PaymentService) *PaymentHandler {
	return &PaymentHandler{
		paymentService: paymentService,
	}
}

// ProcessPayment handles payment processing
func (h *PaymentHandler) ProcessPayment(w http.ResponseWriter, r *http.Request) {
	var paymentReq services.PaymentRequest
	if err := json.NewDecoder(r.Body).Decode(&paymentReq); err != nil {
		http.Error(w, "Invalid JSON", http.StatusBadRequest)
		return
	}

	paymentResp, err := h.paymentService.ProcessPayment(r.Context(), &paymentReq)
	if err != nil {
		http.Error(w, fmt.Sprintf("Failed to process payment: %v", err), http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(paymentResp)
}

// GetPayment handles payment retrieval
func (h *PaymentHandler) GetPayment(w http.ResponseWriter, r *http.Request) {
	paymentID := extractPaymentID(r.URL.Path)
	if paymentID == "" {
		http.Error(w, "Payment ID required", http.StatusBadRequest)
		return
	}

	payment, err := h.paymentService.GetPayment(r.Context(), paymentID)
	if err != nil {
		http.Error(w, fmt.Sprintf("Failed to get payment: %v", err), http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(payment)
}

// CheckAccess handles access checking
func (h *PaymentHandler) CheckAccess(w http.ResponseWriter, r *http.Request) {
	var accessReq services.AccessRequest
	if err := json.NewDecoder(r.Body).Decode(&accessReq); err != nil {
		http.Error(w, "Invalid JSON", http.StatusBadRequest)
		return
	}

	accessResp, err := h.paymentService.CheckAccess(r.Context(), &accessReq)
	if err != nil {
		http.Error(w, fmt.Sprintf("Failed to check access: %v", err), http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(accessResp)
}

// extractPaymentID extracts payment ID from URL path
func extractPaymentID(path string) string {
	parts := strings.Split(path, "/")
	if len(parts) >= 4 {
		return parts[3]
	}
	return ""
}
