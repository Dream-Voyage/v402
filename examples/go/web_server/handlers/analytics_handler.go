package handlers

import (
	"encoding/json"
	"fmt"
	"net/http"
	"strconv"
	"strings"
	"time"

	"./services"
)

// AnalyticsHandler handles analytics-related HTTP requests
type AnalyticsHandler struct {
	analyticsService *services.AnalyticsService
}

// NewAnalyticsHandler creates a new analytics handler
func NewAnalyticsHandler(analyticsService *services.AnalyticsService) *AnalyticsHandler {
	return &AnalyticsHandler{
		analyticsService: analyticsService,
	}
}

// GetProductAnalytics handles product analytics retrieval
func (h *AnalyticsHandler) GetProductAnalytics(w http.ResponseWriter, r *http.Request) {
	productID := extractProductIDFromAnalyticsPath(r.URL.Path)
	if productID == "" {
		http.Error(w, "Product ID required", http.StatusBadRequest)
		return
	}

	// Parse query parameters
	startDate := r.URL.Query().Get("start_date")
	endDate := r.URL.Query().Get("end_date")
	period := r.URL.Query().Get("period")

	if startDate == "" {
		startDate = time.Now().AddDate(0, -1, 0).Format("2006-01-02")
	}
	if endDate == "" {
		endDate = time.Now().Format("2006-01-02")
	}
	if period == "" {
		period = "daily"
	}

	analytics, err := h.analyticsService.GetProductAnalytics(r.Context(), productID, startDate, endDate, period)
	if err != nil {
		http.Error(w, fmt.Sprintf("Failed to get analytics: %v", err), http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(analytics)
}

// GetRevenueAnalytics handles revenue analytics retrieval
func (h *AnalyticsHandler) GetRevenueAnalytics(w http.ResponseWriter, r *http.Request) {
	// Parse query parameters
	startDate := r.URL.Query().Get("start_date")
	endDate := r.URL.Query().Get("end_date")
	period := r.URL.Query().Get("period")
	currency := r.URL.Query().Get("currency")

	if startDate == "" {
		startDate = time.Now().AddDate(0, -1, 0).Format("2006-01-02")
	}
	if endDate == "" {
		endDate = time.Now().Format("2006-01-02")
	}
	if period == "" {
		period = "daily"
	}
	if currency == "" {
		currency = "USDC"
	}

	analytics, err := h.analyticsService.GetRevenueAnalytics(r.Context(), startDate, endDate, period, currency)
	if err != nil {
		http.Error(w, fmt.Sprintf("Failed to get revenue analytics: %v", err), http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(analytics)
}

// GetUserAnalytics handles user analytics retrieval
func (h *AnalyticsHandler) GetUserAnalytics(w http.ResponseWriter, r *http.Request) {
	userAddress := r.URL.Query().Get("user_address")
	if userAddress == "" {
		http.Error(w, "User address required", http.StatusBadRequest)
		return
	}

	// Parse query parameters
	startDate := r.URL.Query().Get("start_date")
	endDate := r.URL.Query().Get("end_date")
	limit, _ := strconv.Atoi(r.URL.Query().Get("limit"))
	if limit <= 0 {
		limit = 10
	}

	if startDate == "" {
		startDate = time.Now().AddDate(0, -1, 0).Format("2006-01-02")
	}
	if endDate == "" {
		endDate = time.Now().Format("2006-01-02")
	}

	analytics, err := h.analyticsService.GetUserAnalytics(r.Context(), userAddress, startDate, endDate, limit)
	if err != nil {
		http.Error(w, fmt.Sprintf("Failed to get user analytics: %v", err), http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(analytics)
}

// extractProductIDFromAnalyticsPath extracts product ID from analytics URL path
func extractProductIDFromAnalyticsPath(path string) string {
	parts := strings.Split(path, "/")
	if len(parts) >= 5 {
		return parts[4]
	}
	return ""
}
