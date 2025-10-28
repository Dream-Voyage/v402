package services

import (
	"context"
	"fmt"
	"time"

	"./client"
)

// ProductService handles product-related business logic
type ProductService struct {
	v402Client *client.V402Client
}

// NewProductService creates a new product service
func NewProductService(v402Client *client.V402Client) *ProductService {
	return &ProductService{
		v402Client: v402Client,
	}
}

// Product represents a product in the service layer
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
	Category    string    `json:"category"`
	Tags        []string  `json:"tags"`
	Author      string    `json:"author"`
}

// CreateProduct creates a new product
func (s *ProductService) CreateProduct(ctx context.Context, product *Product) (*Product, error) {
	// Convert service product to client product
	clientProduct := &client.Product{
		Title:       product.Title,
		Description: product.Description,
		Price:       product.Price,
		Currency:    product.Currency,
		ContentURL:  product.ContentURL,
		Status:      product.Status,
	}

	createdProduct, err := s.v402Client.CreateProduct(ctx, clientProduct)
	if err != nil {
		return nil, fmt.Errorf("failed to create product: %w", err)
	}

	// Convert client product back to service product
	return &Product{
		ID:          createdProduct.ID,
		Title:       createdProduct.Title,
		Description: createdProduct.Description,
		Price:       createdProduct.Price,
		Currency:    createdProduct.Currency,
		ContentURL:  createdProduct.ContentURL,
		CreatedAt:   createdProduct.CreatedAt,
		UpdatedAt:   createdProduct.UpdatedAt,
		Status:      createdProduct.Status,
	}, nil
}

// GetProduct retrieves a product by ID
func (s *ProductService) GetProduct(ctx context.Context, productID string) (*Product, error) {
	clientProduct, err := s.v402Client.GetProduct(ctx, productID)
	if err != nil {
		return nil, fmt.Errorf("failed to get product: %w", err)
	}

	return &Product{
		ID:          clientProduct.ID,
		Title:       clientProduct.Title,
		Description: clientProduct.Description,
		Price:       clientProduct.Price,
		Currency:    clientProduct.Currency,
		ContentURL:  clientProduct.ContentURL,
		CreatedAt:   clientProduct.CreatedAt,
		UpdatedAt:   clientProduct.UpdatedAt,
		Status:      clientProduct.Status,
	}, nil
}

// ListProducts lists products with pagination and filtering
func (s *ProductService) ListProducts(ctx context.Context, page, limit int, category, status string) ([]*Product, error) {
	// This would typically involve database queries
	// For now, we'll return a mock response
	products := []*Product{
		{
			ID:          "product-1",
			Title:       "Sample Product 1",
			Description: "This is a sample product",
			Price:       "10.00",
			Currency:    "USDC",
			ContentURL:  "https://example.com/content/1",
			CreatedAt:   time.Now().Add(-24 * time.Hour),
			UpdatedAt:   time.Now().Add(-1 * time.Hour),
			Status:      "active",
			Category:    "education",
		},
		{
			ID:          "product-2",
			Title:       "Sample Product 2",
			Description: "This is another sample product",
			Price:       "20.00",
			Currency:    "USDC",
			ContentURL:  "https://example.com/content/2",
			CreatedAt:   time.Now().Add(-48 * time.Hour),
			UpdatedAt:   time.Now().Add(-2 * time.Hour),
			Status:      "active",
			Category:    "technology",
		},
	}

	return products, nil
}

// UpdateProduct updates an existing product
func (s *ProductService) UpdateProduct(ctx context.Context, product *Product) (*Product, error) {
	// This would typically involve updating the product in the database
	// For now, we'll return the product as-is
	product.UpdatedAt = time.Now()
	return product, nil
}

// DeleteProduct deletes a product
func (s *ProductService) DeleteProduct(ctx context.Context, productID string) error {
	// This would typically involve deleting the product from the database
	// For now, we'll just return nil
	return nil
}
