package network.v402.example.controller;

import network.v402.example.model.Product;
import network.v402.example.model.Payment;
import network.v402.example.service.ProductService;
import network.v402.example.service.PaymentService;
import network.v402.example.dto.*;
import network.v402.example.exception.ProductNotFoundException;
import network.v402.example.exception.PaymentProcessingException;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.validation.annotation.Validated;

import jakarta.validation.Valid;
import java.util.List;
import java.util.UUID;

/**
 * REST controller for v402 protocol operations
 */
@RestController
@RequestMapping("/api/v1")
@Validated
@CrossOrigin(origins = "*")
public class V402Controller {
    
    private final ProductService productService;
    private final PaymentService paymentService;
    
    @Autowired
    public V402Controller(ProductService productService, PaymentService paymentService) {
        this.productService = productService;
        this.paymentService = paymentService;
    }
    
    // Product endpoints
    
    /**
     * Create a new product
     */
    @PostMapping("/products")
    public ResponseEntity<ProductResponse> createProduct(@Valid @RequestBody ProductCreateRequest request) {
        try {
            ProductResponse product = productService.createProduct(request);
            return ResponseEntity.status(HttpStatus.CREATED).body(product);
        } catch (Exception e) {
            throw new RuntimeException("Failed to create product: " + e.getMessage(), e);
        }
    }
    
    /**
     * Get a product by ID
     */
    @GetMapping("/products/{id}")
    public ResponseEntity<ProductResponse> getProduct(@PathVariable UUID id) {
        try {
            ProductResponse product = productService.getProduct(id);
            return ResponseEntity.ok(product);
        } catch (ProductNotFoundException e) {
            return ResponseEntity.notFound().build();
        } catch (Exception e) {
            throw new RuntimeException("Failed to get product: " + e.getMessage(), e);
        }
    }
    
    /**
     * List products with pagination and filtering
     */
    @GetMapping("/products")
    public ResponseEntity<Page<ProductResponse>> listProducts(
            @RequestParam(required = false) String category,
            @RequestParam(required = false) String status,
            @RequestParam(required = false) String search,
            Pageable pageable) {
        try {
            Page<ProductResponse> products = productService.listProducts(category, status, search, pageable);
            return ResponseEntity.ok(products);
        } catch (Exception e) {
            throw new RuntimeException("Failed to list products: " + e.getMessage(), e);
        }
    }
    
    /**
     * Update a product
     */
    @PutMapping("/products/{id}")
    public ResponseEntity<ProductResponse> updateProduct(
            @PathVariable UUID id, 
            @Valid @RequestBody ProductUpdateRequest request) {
        try {
            ProductResponse product = productService.updateProduct(id, request);
            return ResponseEntity.ok(product);
        } catch (ProductNotFoundException e) {
            return ResponseEntity.notFound().build();
        } catch (Exception e) {
            throw new RuntimeException("Failed to update product: " + e.getMessage(), e);
        }
    }
    
    /**
     * Delete a product
     */
    @DeleteMapping("/products/{id}")
    public ResponseEntity<Void> deleteProduct(@PathVariable UUID id) {
        try {
            productService.deleteProduct(id);
            return ResponseEntity.noContent().build();
        } catch (ProductNotFoundException e) {
            return ResponseEntity.notFound().build();
        } catch (Exception e) {
            throw new RuntimeException("Failed to delete product: " + e.getMessage(), e);
        }
    }
    
    // Payment endpoints
    
    /**
     * Process a payment
     */
    @PostMapping("/payments")
    public ResponseEntity<PaymentResponse> processPayment(@Valid @RequestBody PaymentRequest request) {
        try {
            PaymentResponse payment = paymentService.processPayment(request);
            return ResponseEntity.status(HttpStatus.CREATED).body(payment);
        } catch (PaymentProcessingException e) {
            return ResponseEntity.badRequest().body(
                PaymentResponse.builder()
                    .error(e.getMessage())
                    .status("failed")
                    .build()
            );
        } catch (Exception e) {
            throw new RuntimeException("Failed to process payment: " + e.getMessage(), e);
        }
    }
    
    /**
     * Get payment by transaction hash
     */
    @GetMapping("/payments/{transactionHash}")
    public ResponseEntity<PaymentResponse> getPayment(@PathVariable String transactionHash) {
        try {
            return paymentService.getPayment(transactionHash)
                    .map(ResponseEntity::ok)
                    .orElse(ResponseEntity.notFound().build());
        } catch (Exception e) {
            throw new RuntimeException("Failed to get payment: " + e.getMessage(), e);
        }
    }
    
    /**
     * Get payment history for a user
     */
    @GetMapping("/payments/user/{userAddress}")
    public ResponseEntity<List<PaymentResponse>> getPaymentHistory(
            @PathVariable String userAddress,
            @RequestParam(defaultValue = "10") int limit) {
        try {
            List<PaymentResponse> payments = paymentService.getPaymentHistory(userAddress, limit);
            return ResponseEntity.ok(payments);
        } catch (Exception e) {
            throw new RuntimeException("Failed to get payment history: " + e.getMessage(), e);
        }
    }
    
    // Access endpoints
    
    /**
     * Check access to a product
     */
    @PostMapping("/access/check")
    public ResponseEntity<AccessResponse> checkAccess(@Valid @RequestBody AccessRequest request) {
        try {
            AccessResponse access = paymentService.checkAccess(request);
            return ResponseEntity.ok(access);
        } catch (Exception e) {
            throw new RuntimeException("Failed to check access: " + e.getMessage(), e);
        }
    }
    
    // Analytics endpoints
    
    /**
     * Get payment statistics for a product
     */
    @GetMapping("/analytics/products/{productId}/payments")
    public ResponseEntity<PaymentService.PaymentStatistics> getPaymentStatistics(@PathVariable UUID productId) {
        try {
            PaymentService.PaymentStatistics stats = paymentService.getPaymentStatistics(productId);
            return ResponseEntity.ok(stats);
        } catch (Exception e) {
            throw new RuntimeException("Failed to get payment statistics: " + e.getMessage(), e);
        }
    }
    
    /**
     * Get product analytics
     */
    @GetMapping("/analytics/products/{productId}")
    public ResponseEntity<ProductAnalyticsResponse> getProductAnalytics(@PathVariable UUID productId) {
        try {
            ProductAnalyticsResponse analytics = productService.getProductAnalytics(productId);
            return ResponseEntity.ok(analytics);
        } catch (Exception e) {
            throw new RuntimeException("Failed to get product analytics: " + e.getMessage(), e);
        }
    }
    
    // Webhook endpoints
    
    /**
     * Handle payment status updates from blockchain
     */
    @PostMapping("/webhooks/payment-status")
    public ResponseEntity<Void> updatePaymentStatus(@RequestBody PaymentStatusUpdateRequest request) {
        try {
            paymentService.updatePaymentStatus(
                request.getTransactionHash(),
                request.getStatus(),
                request.getBlockNumber(),
                request.getGasUsed(),
                request.getErrorMessage()
            );
            return ResponseEntity.ok().build();
        } catch (Exception e) {
            throw new RuntimeException("Failed to update payment status: " + e.getMessage(), e);
        }
    }
    
    // Health check endpoint
    
    /**
     * Health check endpoint
     */
    @GetMapping("/health")
    public ResponseEntity<HealthResponse> healthCheck() {
        try {
            HealthResponse health = HealthResponse.builder()
                    .status("healthy")
                    .timestamp(java.time.LocalDateTime.now())
                    .version("1.0.0")
                    .build();
            return ResponseEntity.ok(health);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE)
                    .body(HealthResponse.builder()
                            .status("unhealthy")
                            .timestamp(java.time.LocalDateTime.now())
                            .version("1.0.0")
                            .error(e.getMessage())
                            .build());
        }
    }
    
    // Exception handlers
    
    @ExceptionHandler(ProductNotFoundException.class)
    public ResponseEntity<ErrorResponse> handleProductNotFound(ProductNotFoundException e) {
        ErrorResponse error = ErrorResponse.builder()
                .error("Product not found")
                .message(e.getMessage())
                .timestamp(java.time.LocalDateTime.now())
                .build();
        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(error);
    }
    
    @ExceptionHandler(PaymentProcessingException.class)
    public ResponseEntity<ErrorResponse> handlePaymentProcessing(PaymentProcessingException e) {
        ErrorResponse error = ErrorResponse.builder()
                .error("Payment processing failed")
                .message(e.getMessage())
                .timestamp(java.time.LocalDateTime.now())
                .build();
        return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(error);
    }
    
    @ExceptionHandler(Exception.class)
    public ResponseEntity<ErrorResponse> handleGenericException(Exception e) {
        ErrorResponse error = ErrorResponse.builder()
                .error("Internal server error")
                .message(e.getMessage())
                .timestamp(java.time.LocalDateTime.now())
                .build();
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(error);
    }
}
