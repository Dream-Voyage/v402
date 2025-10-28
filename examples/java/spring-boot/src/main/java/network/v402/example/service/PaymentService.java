package network.v402.example.service;

import network.v402.example.model.Product;
import network.v402.example.model.Payment;
import network.v402.example.model.PaymentStatus;
import network.v402.example.repository.ProductRepository;
import network.v402.example.repository.PaymentRepository;
import network.v402.example.dto.PaymentRequest;
import network.v402.example.dto.PaymentResponse;
import network.v402.example.dto.AccessRequest;
import network.v402.example.dto.AccessResponse;
import network.v402.example.exception.PaymentProcessingException;
import network.v402.example.exception.ProductNotFoundException;
import network.v402.example.exception.AccessDeniedException;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.cache.annotation.CacheEvict;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;
import java.util.Optional;

/**
 * Service for handling payment operations in the v402 protocol
 */
@Service
@Transactional
public class PaymentService {
    
    private final PaymentRepository paymentRepository;
    private final ProductRepository productRepository;
    private final V402ClientService v402ClientService;
    private final AccessService accessService;
    
    @Autowired
    public PaymentService(PaymentRepository paymentRepository,
                         ProductRepository productRepository,
                         V402ClientService v402ClientService,
                         AccessService accessService) {
        this.paymentRepository = paymentRepository;
        this.productRepository = productRepository;
        this.v402ClientService = v402ClientService;
        this.accessService = accessService;
    }
    
    /**
     * Process a payment for a product
     */
    public PaymentResponse processPayment(PaymentRequest request) {
        // Validate product exists
        Product product = productRepository.findById(request.getProductId())
                .orElseThrow(() -> new ProductNotFoundException("Product not found: " + request.getProductId()));
        
        // Validate payment amount matches product price
        if (!request.getAmount().equals(product.getPrice())) {
            throw new PaymentProcessingException("Payment amount does not match product price");
        }
        
        // Validate currency matches product currency
        if (!request.getCurrency().equals(product.getCurrency())) {
            throw new PaymentProcessingException("Payment currency does not match product currency");
        }
        
        try {
            // Process payment through v402 client
            PaymentResponse v402Response = v402ClientService.processPayment(request);
            
            // Create payment record
            Payment payment = new Payment();
            payment.setTransactionHash(v402Response.getTransactionHash());
            payment.setProduct(product);
            payment.setUserAddress(request.getUserAddress());
            payment.setAmount(request.getAmount());
            payment.setCurrency(request.getCurrency());
            payment.setStatus(PaymentStatus.valueOf(v402Response.getStatus().toUpperCase()));
            payment.setBlockNumber(v402Response.getBlockNumber());
            payment.setGasUsed(v402Response.getGasUsed());
            payment.setErrorMessage(v402Response.getError());
            
            // Save payment
            payment = paymentRepository.save(payment);
            
            // Update product purchase count if payment is completed
            if (payment.isCompleted()) {
                product.incrementPurchaseCount();
                productRepository.save(product);
            }
            
            // Convert to response DTO
            return convertToResponse(payment);
            
        } catch (Exception e) {
            // Create failed payment record
            Payment failedPayment = new Payment();
            failedPayment.setTransactionHash("failed-" + UUID.randomUUID().toString());
            failedPayment.setProduct(product);
            failedPayment.setUserAddress(request.getUserAddress());
            failedPayment.setAmount(request.getAmount());
            failedPayment.setCurrency(request.getCurrency());
            failedPayment.setStatus(PaymentStatus.FAILED);
            failedPayment.setErrorMessage(e.getMessage());
            
            paymentRepository.save(failedPayment);
            
            throw new PaymentProcessingException("Payment processing failed: " + e.getMessage(), e);
        }
    }
    
    /**
     * Get payment by transaction hash
     */
    @Cacheable(value = "payments", key = "#transactionHash")
    public Optional<PaymentResponse> getPayment(String transactionHash) {
        return paymentRepository.findByTransactionHash(transactionHash)
                .map(this::convertToResponse);
    }
    
    /**
     * Get payment history for a user
     */
    public List<PaymentResponse> getPaymentHistory(String userAddress, int limit) {
        return paymentRepository.findByUserAddressOrderByCreatedAtDesc(userAddress)
                .stream()
                .limit(limit)
                .map(this::convertToResponse)
                .toList();
    }
    
    /**
     * Check if user has access to a product
     */
    @Cacheable(value = "access", key = "#request.productId + '_' + #request.userAddress")
    public AccessResponse checkAccess(AccessRequest request) {
        // Check if user has completed payment for this product
        boolean hasPayment = paymentRepository.existsByProductIdAndUserAddressAndStatus(
                request.getProductId(), 
                request.getUserAddress(), 
                PaymentStatus.COMPLETED
        );
        
        if (hasPayment) {
            return AccessResponse.builder()
                    .hasAccess(true)
                    .reason("Payment verified")
                    .expiresAt(System.currentTimeMillis() + (30L * 24 * 60 * 60 * 1000)) // 30 days
                    .build();
        }
        
        return AccessResponse.builder()
                .hasAccess(false)
                .reason("No payment found")
                .build();
    }
    
    /**
     * Get payment statistics for a product
     */
    public PaymentStatistics getPaymentStatistics(UUID productId) {
        List<Payment> payments = paymentRepository.findByProductId(productId);
        
        long totalPayments = payments.size();
        long completedPayments = payments.stream()
                .mapToLong(p -> p.isCompleted() ? 1 : 0)
                .sum();
        long failedPayments = payments.stream()
                .mapToLong(p -> p.isFailed() ? 1 : 0)
                .sum();
        
        BigDecimal totalRevenue = payments.stream()
                .filter(Payment::isCompleted)
                .map(Payment::getAmount)
                .reduce(BigDecimal.ZERO, BigDecimal::add);
        
        return PaymentStatistics.builder()
                .totalPayments(totalPayments)
                .completedPayments(completedPayments)
                .failedPayments(failedPayments)
                .totalRevenue(totalRevenue)
                .successRate(totalPayments > 0 ? (double) completedPayments / totalPayments * 100 : 0.0)
                .build();
    }
    
    /**
     * Update payment status (for webhook processing)
     */
    @CacheEvict(value = "payments", key = "#transactionHash")
    public void updatePaymentStatus(String transactionHash, PaymentStatus status, 
                                   Long blockNumber, Long gasUsed, String errorMessage) {
        Optional<Payment> paymentOpt = paymentRepository.findByTransactionHash(transactionHash);
        if (paymentOpt.isPresent()) {
            Payment payment = paymentOpt.get();
            payment.setStatus(status);
            payment.setBlockNumber(blockNumber);
            payment.setGasUsed(gasUsed);
            payment.setErrorMessage(errorMessage);
            paymentRepository.save(payment);
            
            // Update product purchase count if payment is now completed
            if (status == PaymentStatus.COMPLETED) {
                Product product = payment.getProduct();
                product.incrementPurchaseCount();
                productRepository.save(product);
            }
        }
    }
    
    /**
     * Convert Payment entity to PaymentResponse DTO
     */
    private PaymentResponse convertToResponse(Payment payment) {
        return PaymentResponse.builder()
                .id(payment.getId())
                .transactionHash(payment.getTransactionHash())
                .productId(payment.getProduct().getId())
                .userAddress(payment.getUserAddress())
                .amount(payment.getAmount())
                .currency(payment.getCurrency())
                .status(payment.getStatus().name().toLowerCase())
                .blockNumber(payment.getBlockNumber())
                .gasUsed(payment.getGasUsed())
                .error(payment.getErrorMessage())
                .createdAt(payment.getCreatedAt())
                .updatedAt(payment.getUpdatedAt())
                .build();
    }
    
    /**
     * Inner class for payment statistics
     */
    public static class PaymentStatistics {
        private final long totalPayments;
        private final long completedPayments;
        private final long failedPayments;
        private final BigDecimal totalRevenue;
        private final double successRate;
        
        private PaymentStatistics(Builder builder) {
            this.totalPayments = builder.totalPayments;
            this.completedPayments = builder.completedPayments;
            this.failedPayments = builder.failedPayments;
            this.totalRevenue = builder.totalRevenue;
            this.successRate = builder.successRate;
        }
        
        public static Builder builder() {
            return new Builder();
        }
        
        public long getTotalPayments() { return totalPayments; }
        public long getCompletedPayments() { return completedPayments; }
        public long getFailedPayments() { return failedPayments; }
        public BigDecimal getTotalRevenue() { return totalRevenue; }
        public double getSuccessRate() { return successRate; }
        
        public static class Builder {
            private long totalPayments;
            private long completedPayments;
            private long failedPayments;
            private BigDecimal totalRevenue;
            private double successRate;
            
            public Builder totalPayments(long totalPayments) {
                this.totalPayments = totalPayments;
                return this;
            }
            
            public Builder completedPayments(long completedPayments) {
                this.completedPayments = completedPayments;
                return this;
            }
            
            public Builder failedPayments(long failedPayments) {
                this.failedPayments = failedPayments;
                return this;
            }
            
            public Builder totalRevenue(BigDecimal totalRevenue) {
                this.totalRevenue = totalRevenue;
                return this;
            }
            
            public Builder successRate(double successRate) {
                this.successRate = successRate;
                return this;
            }
            
            public PaymentStatistics build() {
                return new PaymentStatistics(this);
            }
        }
    }
}
