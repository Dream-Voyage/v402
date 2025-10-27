package network.v402.client;

import lombok.extern.slf4j.Slf4j;
import network.v402.client.config.V402ClientProperties;
import network.v402.client.core.AsyncV402Client;
import network.v402.client.core.RequestOptions;
import network.v402.client.model.PaymentResponse;
import network.v402.client.model.PaymentHistory;
import network.v402.client.model.PaymentStatistics;
import network.v402.client.model.HealthStatus;
import org.springframework.stereotype.Component;

import java.util.List;
import java.util.Map;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.TimeUnit;

/**
 * Main synchronous v402 client for Java applications.
 * 
 * This client provides a synchronous interface that wraps the async client implementation.
 * It's designed for traditional Java applications and provides enterprise-grade features:
 * 
 * <ul>
 *   <li>Multi-chain payment processing (Ethereum, Base, Polygon, Solana, BSC)</li>
 *   <li>Automatic payment handling for 402 Payment Required responses</li>
 *   <li>Connection pooling and HTTP/2 support</li>
 *   <li>Circuit breaker pattern for resilience</li>
 *   <li>Comprehensive metrics via Micrometer</li>
 *   <li>Structured logging with correlation IDs</li>
 *   <li>Spring Boot auto-configuration</li>
 * </ul>
 * 
 * <h3>Basic Usage:</h3>
 * <pre>{@code
 * // Configure client
 * V402ClientProperties properties = V402ClientProperties.builder()
 *     .privateKey("0x...")
 *     .autoPayEnabled(true)
 *     .maxAmountPerRequest("1000000000000000000") // 1 ETH
 *     .build();
 * 
 * // Create client
 * V402Client client = new V402Client(properties);
 * 
 * // Make requests
 * try {
 *     PaymentResponse response = client.get("https://example.com/premium-content");
 *     
 *     if (response.isPaymentMade()) {
 *         System.out.println("Paid " + response.getPaymentAmount() + " for content");
 *     }
 *     
 *     String content = response.getBodyAsString();
 *     System.out.println(content);
 * } finally {
 *     client.close();
 * }
 * }</pre>
 * 
 * <h3>Spring Integration:</h3>
 * <pre>{@code
 * @Service
 * public class ContentService {
 *     
 *     @Autowired
 *     private V402Client v402Client;
 *     
 *     public String getPremiumContent(String url) {
 *         PaymentResponse response = v402Client.get(url);
 *         return response.getBodyAsString();
 *     }
 * }
 * }</pre>
 * 
 * <h3>Batch Processing:</h3>
 * <pre>{@code
 * List<String> urls = Arrays.asList(
 *     "https://example.com/article1",
 *     "https://example.com/article2",
 *     "https://example.com/article3"
 * );
 * 
 * List<PaymentResponse> responses = client.batchGet(urls, 10); // max 10 concurrent
 * 
 * for (PaymentResponse response : responses) {
 *     if (response.getStatusCode() == 200) {
 *         System.out.println("Success: " + response.getUrl());
 *     }
 * }
 * }</pre>
 * 
 * @author v402 Team
 * @version 1.0.0
 * @since 1.0.0
 */
@Slf4j
@Component
public class V402Client {
    
    private final AsyncV402Client asyncClient;
    private final V402ClientProperties properties;
    private volatile boolean closed = false;

    /**
     * Creates a new v402 client with the specified properties.
     * 
     * @param properties Client configuration properties
     * @throws IllegalArgumentException if properties are invalid
     */
    public V402Client(V402ClientProperties properties) {
        if (properties == null) {
            throw new IllegalArgumentException("Properties cannot be null");
        }
        
        this.properties = properties;
        this.asyncClient = new AsyncV402Client(properties);
        
        log.info("V402Client initialized with {} chains, auto-pay: {}", 
                properties.getChains().size(), 
                properties.isAutoPayEnabled());
    }

    /**
     * Performs a synchronous GET request with automatic payment handling.
     * 
     * This method will automatically handle 402 Payment Required responses by:
     * <ol>
     *   <li>Parsing payment requirements from the server</li>
     *   <li>Selecting the most suitable payment method</li>
     *   <li>Creating and signing the payment authorization</li>
     *   <li>Retrying the request with payment header</li>
     *   <li>Processing the settlement response</li>
     * </ol>
     * 
     * @param url The URL to request
     * @return PaymentResponse containing the response data and payment information
     * @throws IllegalStateException if client is closed
     * @throws network.v402.client.exception.PaymentException if payment processing fails
     * @throws network.v402.client.exception.NetworkException if network request fails
     * @throws InterruptedException if the request is interrupted
     */
    public PaymentResponse get(String url) throws InterruptedException {
        return get(url, RequestOptions.DEFAULT);
    }

    /**
     * Performs a synchronous GET request with custom options.
     * 
     * @param url The URL to request
     * @param options Request options (headers, timeout, auto-pay override, etc.)
     * @return PaymentResponse containing the response data and payment information
     * @throws IllegalStateException if client is closed
     * @throws InterruptedException if the request is interrupted
     */
    public PaymentResponse get(String url, RequestOptions options) throws InterruptedException {
        checkNotClosed();
        
        try {
            CompletableFuture<PaymentResponse> future = asyncClient.get(url, options);
            return future.get(properties.getTimeout().toMillis(), TimeUnit.MILLISECONDS);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw e;
        } catch (Exception e) {
            log.error("GET request failed for URL: {}", url, e);
            throw new RuntimeException("Request failed", e);
        }
    }

    /**
     * Performs a synchronous POST request with automatic payment handling.
     * 
     * @param url The URL to request
     * @param body The request body content
     * @return PaymentResponse containing the response data and payment information
     * @throws IllegalStateException if client is closed
     * @throws InterruptedException if the request is interrupted
     */
    public PaymentResponse post(String url, String body) throws InterruptedException {
        return post(url, body, RequestOptions.DEFAULT);
    }

    /**
     * Performs a synchronous POST request with custom options.
     * 
     * @param url The URL to request
     * @param body The request body content
     * @param options Request options
     * @return PaymentResponse containing the response data and payment information
     * @throws IllegalStateException if client is closed
     * @throws InterruptedException if the request is interrupted
     */
    public PaymentResponse post(String url, String body, RequestOptions options) throws InterruptedException {
        checkNotClosed();
        
        try {
            CompletableFuture<PaymentResponse> future = asyncClient.post(url, body, options);
            return future.get(properties.getTimeout().toMillis(), TimeUnit.MILLISECONDS);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw e;
        } catch (Exception e) {
            log.error("POST request failed for URL: {}", url, e);
            throw new RuntimeException("Request failed", e);
        }
    }

    /**
     * Performs multiple GET requests concurrently with automatic payment handling.
     * 
     * This method processes multiple URLs concurrently while respecting the maximum
     * concurrent requests limit. Failed requests are included in the results with
     * error information in the response body.
     * 
     * <h4>Performance Characteristics:</h4>
     * <ul>
     *   <li>Uses virtual threads (Project Loom) when available</li>
     *   <li>Implements semaphore-based concurrency control</li>
     *   <li>Automatic retry with exponential backoff</li>
     *   <li>Circuit breaker prevents cascade failures</li>
     * </ul>
     * 
     * @param urls List of URLs to request
     * @param maxConcurrent Maximum number of concurrent requests (1-100)
     * @return List of PaymentResponse objects in the same order as input URLs
     * @throws IllegalArgumentException if maxConcurrent is out of range
     * @throws IllegalStateException if client is closed
     * @throws InterruptedException if the batch operation is interrupted
     */
    public List<PaymentResponse> batchGet(List<String> urls, int maxConcurrent) throws InterruptedException {
        checkNotClosed();
        
        if (maxConcurrent < 1 || maxConcurrent > 100) {
            throw new IllegalArgumentException("maxConcurrent must be between 1 and 100");
        }
        
        if (urls.isEmpty()) {
            return List.of();
        }
        
        try {
            CompletableFuture<List<PaymentResponse>> future = asyncClient.batchGet(urls, maxConcurrent);
            return future.get(properties.getTimeout().toMillis() * urls.size(), TimeUnit.MILLISECONDS);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw e;
        } catch (Exception e) {
            log.error("Batch GET request failed for {} URLs", urls.size(), e);
            throw new RuntimeException("Batch request failed", e);
        }
    }

    /**
     * Retrieves the payment history for this client.
     * 
     * The history includes all successful and failed payment attempts with
     * detailed information about amounts, networks, transaction hashes, and timestamps.
     * 
     * @param limit Maximum number of records to return (1-1000)
     * @return List of payment history records, most recent first
     * @throws IllegalArgumentException if limit is out of range
     * @throws InterruptedException if the operation is interrupted
     */
    public List<PaymentHistory> getPaymentHistory(int limit) throws InterruptedException {
        checkNotClosed();
        
        if (limit < 1 || limit > 1000) {
            throw new IllegalArgumentException("limit must be between 1 and 1000");
        }
        
        try {
            CompletableFuture<List<PaymentHistory>> future = asyncClient.getPaymentHistory(limit);
            return future.get(10, TimeUnit.SECONDS);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw e;
        } catch (Exception e) {
            log.error("Failed to get payment history", e);
            throw new RuntimeException("Failed to get payment history", e);
        }
    }

    /**
     * Retrieves comprehensive payment statistics for this client.
     * 
     * Statistics include:
     * <ul>
     *   <li>Total number of payments made</li>
     *   <li>Success/failure rates</li>
     *   <li>Amount distributions (total, average, min, max)</li>
     *   <li>Network breakdown</li>
     *   <li>Time series data</li>
     * </ul>
     * 
     * @return PaymentStatistics object with comprehensive metrics
     * @throws InterruptedException if the operation is interrupted
     */
    public PaymentStatistics getPaymentStatistics() throws InterruptedException {
        checkNotClosed();
        
        try {
            CompletableFuture<PaymentStatistics> future = asyncClient.getPaymentStatistics();
            return future.get(10, TimeUnit.SECONDS);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw e;
        } catch (Exception e) {
            log.error("Failed to get payment statistics", e);
            throw new RuntimeException("Failed to get payment statistics", e);
        }
    }

    /**
     * Performs a comprehensive health check of the client and all its components.
     * 
     * The health check includes:
     * <ul>
     *   <li>HTTP client connection pool status</li>
     *   <li>Blockchain network connectivity</li>
     *   <li>Payment facilitator availability</li>
     *   <li>Cache performance metrics</li>
     *   <li>Memory usage and GC pressure</li>
     * </ul>
     * 
     * @return HealthStatus with detailed component health information
     * @throws InterruptedException if the health check is interrupted
     */
    public HealthStatus healthCheck() throws InterruptedException {
        try {
            CompletableFuture<HealthStatus> future = asyncClient.healthCheck();
            return future.get(30, TimeUnit.SECONDS);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw e;
        } catch (Exception e) {
            log.warn("Health check failed", e);
            
            // Return degraded health status
            return HealthStatus.builder()
                    .healthy(false)
                    .error(e.getMessage())
                    .build();
        }
    }

    /**
     * Returns the current client configuration.
     * 
     * @return V402ClientProperties configuration object
     */
    public V402ClientProperties getProperties() {
        return properties;
    }

    /**
     * Checks if the client is closed.
     * 
     * @return true if the client is closed, false otherwise
     */
    public boolean isClosed() {
        return closed;
    }

    /**
     * Gracefully shuts down the client and releases all resources.
     * 
     * This method:
     * <ul>
     *   <li>Stops accepting new requests</li>
     *   <li>Waits for active requests to complete (up to 30 seconds)</li>
     *   <li>Closes connection pools</li>
     *   <li>Shuts down thread pools</li>
     *   <li>Releases blockchain connections</li>
     *   <li>Flushes metrics and logs</li>
     * </ul>
     * 
     * After calling this method, the client cannot be reused.
     * 
     * @throws InterruptedException if shutdown is interrupted
     */
    public void close() throws InterruptedException {
        if (closed) {
            return;
        }
        
        log.info("Shutting down V402Client");
        closed = true;
        
        try {
            CompletableFuture<Void> future = asyncClient.close();
            future.get(30, TimeUnit.SECONDS);
            log.info("V402Client shutdown complete");
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw e;
        } catch (Exception e) {
            log.error("Error during client shutdown", e);
            throw new RuntimeException("Shutdown failed", e);
        }
    }

    /**
     * Ensures the client is not closed.
     * 
     * @throws IllegalStateException if the client is closed
     */
    private void checkNotClosed() {
        if (closed) {
            throw new IllegalStateException("Client is closed");
        }
    }

    @Override
    public String toString() {
        return String.format("V402Client{chains=%d, autoPay=%s, closed=%s}", 
                properties.getChains().size(), 
                properties.isAutoPayEnabled(), 
                closed);
    }
}
