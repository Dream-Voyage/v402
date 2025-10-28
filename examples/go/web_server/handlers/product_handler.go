package handlers

import (
	"encoding/json"
	"fmt"
	"net/http"
	"strconv"
	"strings"

	"./services"
)

// ProductHandler handles product-related HTTP requests
type ProductHandler struct {
	productService *services.ProductService
}

// NewProductHandler creates a new product handler
func NewProductHandler(productService *services.ProductService) *ProductHandler {
	return &ProductHandler{
		productService: productService,
	}
}

// CreateProduct handles product creation
func (h *ProductHandler) CreateProduct(w http.ResponseWriter, r *http.Request) {
	var product services.Product
	if err := json.NewDecoder(r.Body).Decode(&product); err != nil {
		http.Error(w, "Invalid JSON", http.StatusBadRequest)
		return
	}

	createdProduct, err := h.productService.CreateProduct(r.Context(), &product)
	if err != nil {
		http.Error(w, fmt.Sprintf("Failed to create product: %v", err), http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(createdProduct)
}

// GetProduct handles product retrieval
func (h *ProductHandler) GetProduct(w http.ResponseWriter, r *http.Request) {
	productID := extractProductID(r.URL.Path)
	if productID == "" {
		http.Error(w, "Product ID required", http.StatusBadRequest)
		return
	}

	product, err := h.productService.GetProduct(r.Context(), productID)
	if err != nil {
		http.Error(w, fmt.Sprintf("Failed to get product: %v", err), http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(product)
}

// ListProducts handles product listing
func (h *ProductHandler) ListProducts(w http.ResponseWriter, r *http.Request) {
	// Parse query parameters
	page, _ := strconv.Atoi(r.URL.Query().Get("page"))
	if page <= 0 {
		page = 1
	}

	limit, _ := strconv.Atoi(r.URL.Query().Get("limit"))
	if limit <= 0 {
		limit = 10
	}

	category := r.URL.Query().Get("category")
	status := r.URL.Query().Get("status")

	products, err := h.productService.ListProducts(r.Context(), page, limit, category, status)
	if err != nil {
		http.Error(w, fmt.Sprintf("Failed to list products: %v", err), http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(products)
}

// UpdateProduct handles product updates
func (h *ProductHandler) UpdateProduct(w http.ResponseWriter, r *http.Request) {
	productID := extractProductID(r.URL.Path)
	if productID == "" {
		http.Error(w, "Product ID required", http.StatusBadRequest)
		return
	}

	var product services.Product
	if err := json.NewDecoder(r.Body).Decode(&product); err != nil {
		http.Error(w, "Invalid JSON", http.StatusBadRequest)
		return
	}

	product.ID = productID
	updatedProduct, err := h.productService.UpdateProduct(r.Context(), &product)
	if err != nil {
		http.Error(w, fmt.Sprintf("Failed to update product: %v", err), http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(updatedProduct)
}

// DeleteProduct handles product deletion
func (h *ProductHandler) DeleteProduct(w http.ResponseWriter, r *http.Request) {
	productID := extractProductID(r.URL.Path)
	if productID == "" {
		http.Error(w, "Product ID required", http.StatusBadRequest)
		return
	}

	err := h.productService.DeleteProduct(r.Context(), productID)
	if err != nil {
		http.Error(w, fmt.Sprintf("Failed to delete product: %v", err), http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusNoContent)
}

// extractProductID extracts product ID from URL path
func extractProductID(path string) string {
	parts := strings.Split(path, "/")
	if len(parts) >= 4 {
		return parts[3]
	}
	return ""
}
