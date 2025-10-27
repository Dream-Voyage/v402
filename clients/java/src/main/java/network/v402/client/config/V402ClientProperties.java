package network.v402.client.config;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.validation.annotation.Validated;

import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.Positive;
import jakarta.validation.constraints.PositiveOrZero;

import java.time.Duration;
import java.util.ArrayList;
import java.util.List;

/**
 * Configuration properties for the v402 client.
 * 
 * This class defines all configurable aspects of the v402 client using Spring Boot's
 * configuration properties mechanism. Properties can be set via application.yml,
 * application.properties, environment variables, or command line arguments.
 * 
 * Example configuration in application.yml:
 * <pre>
 * v402:
 *   client:
 *     private-key: "0x..."
 *     auto-pay-enabled: true
 *     max-amount-per-request: "1000000000000000000"
 *     timeout: PT30S
 *     chains:
 *       - name: ethereum
 *         type: EVM
 *         rpc-url: "https://mainnet.infura.io/v3/..."
 *         chain-id: 1
 *     resilience:
 *       circuit-breaker-enabled: true
 *       failure-threshold: 5
 * </pre>
 * 
 * @author v402 Team
 * @version 1.0.0
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Validated
@ConfigurationProperties(prefix = "v402.client")
public class V402ClientProperties {

    /**
     * Private key for signing transactions (required).
     * Should be a hex string starting with "0x".
     */
    @NotBlank(message = "Private key is required")
    private String privateKey;

    /**
     * List of blockchain chain configurations.
     * At least one chain must be configured.
     */
    @NotEmpty(message = "At least one chain must be configured")
    @Valid
    @Builder.Default
    private List<ChainConfig> chains = new ArrayList<>();

    /**
     * Whether to automatically pay for 402 Payment Required responses.
     */
    @Builder.Default
    private boolean autoPayEnabled = true;

    /**
     * Maximum amount to pay per request in wei/lamports.
     * Default is 1 ETH (1000000000000000000 wei).
     */
    @NotBlank(message = "Max amount per request is required")
    @Builder.Default
    private String maxAmountPerRequest = "1000000000000000000";

    /**
     * Request timeout duration.
     */
    @Builder.Default
    private Duration timeout = Duration.ofSeconds(30);

    /**
     * Maximum number of concurrent HTTP connections.
     */
    @Positive(message = "Max connections must be positive")
    @Builder.Default
    private int maxConnections = 100;

    /**
     * URL of the v402 facilitator service.
     */
    @Builder.Default
    private String facilitatorUrl = "https://facilitator.v402.network";

    /**
     * Resilience configuration for circuit breaker, retry, etc.
     */
    @Valid
    @Builder.Default
    private ResilienceConfig resilience = new ResilienceConfig();

    /**
     * Logging configuration.
     */
    @Valid
    @Builder.Default
    private LoggingConfig logging = new LoggingConfig();

    /**
     * Metrics configuration.
     */
    @Valid
    @Builder.Default
    private MetricsConfig metrics = new MetricsConfig();

    /**
     * Cache configuration.
     */
    @Valid
    @Builder.Default
    private CacheConfig cache = new CacheConfig();

    /**
     * Blockchain chain configuration.
     */
    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    @Validated
    public static class ChainConfig {

        /**
         * Chain name (e.g., "ethereum", "base", "polygon").
         */
        @NotBlank(message = "Chain name is required")
        private String name;

        /**
         * Chain type (EVM, SOLANA, etc.).
         */
        @NotBlank(message = "Chain type is required")
        private String type;

        /**
         * RPC URL for connecting to the blockchain.
         */
        @NotBlank(message = "RPC URL is required")
        private String rpcUrl;

        /**
         * Chain ID (for EVM chains).
         */
        private Long chainId;

        /**
         * Native currency symbol (ETH, MATIC, SOL, etc.).
         */
        @Builder.Default
        private String nativeCurrency = "ETH";

        /**
         * Block explorer URL.
         */
        private String explorerUrl;

        /**
         * Maximum retry attempts for this chain.
         */
        @PositiveOrZero
        @Builder.Default
        private int maxRetries = 3;

        /**
         * Request timeout for this chain.
         */
        @Builder.Default
        private Duration timeout = Duration.ofSeconds(30);

        /**
         * Gas price multiplier for EVM chains.
         */
        @Builder.Default
        private double gasMultiplier = 1.2;
    }

    /**
     * Resilience configuration for fault tolerance patterns.
     */
    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class ResilienceConfig {

        /**
         * Enable circuit breaker pattern.
         */
        @Builder.Default
        private boolean circuitBreakerEnabled = true;

        /**
         * Number of failures to trigger circuit breaker opening.
         */
        @PositiveOrZero
        @Builder.Default
        private int failureThreshold = 5;

        /**
         * Number of successes to close the circuit breaker.
         */
        @PositiveOrZero
        @Builder.Default
        private int successThreshold = 3;

        /**
         * Circuit breaker timeout before trying again.
         */
        @Builder.Default
        private Duration circuitBreakerTimeout = Duration.ofSeconds(60);

        /**
         * Maximum retry attempts.
         */
        @PositiveOrZero
        @Builder.Default
        private int maxRetries = 3;

        /**
         * Base delay for exponential backoff retry.
         */
        @Builder.Default
        private Duration retryBackoff = Duration.ofSeconds(1);

        /**
         * Enable jitter in retry delays.
         */
        @Builder.Default
        private boolean retryJitter = true;
    }

    /**
     * Logging configuration.
     */
    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class LoggingConfig {

        /**
         * Log level (TRACE, DEBUG, INFO, WARN, ERROR).
         */
        @Builder.Default
        private String level = "INFO";

        /**
         * Log format (JSON, TEXT).
         */
        @Builder.Default
        private String format = "JSON";

        /**
         * Log output destination (STDOUT, STDERR, FILE).
         */
        @Builder.Default
        private String output = "STDOUT";

        /**
         * Log file path (if output is FILE).
         */
        private String filePath;

        /**
         * Include request/response bodies in logs (be careful with sensitive data).
         */
        @Builder.Default
        private boolean includeRequestBodies = false;

        /**
         * Include payment information in logs.
         */
        @Builder.Default
        private boolean includePaymentInfo = true;
    }

    /**
     * Metrics configuration.
     */
    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class MetricsConfig {

        /**
         * Enable metrics collection.
         */
        @Builder.Default
        private boolean enabled = true;

        /**
         * Metrics server port.
         */
        @Positive
        @Builder.Default
        private int port = 9090;

        /**
         * Metrics endpoint path.
         */
        @Builder.Default
        private String path = "/metrics";

        /**
         * Enable JVM metrics.
         */
        @Builder.Default
        private boolean jvmMetricsEnabled = true;

        /**
         * Enable system metrics.
         */
        @Builder.Default
        private boolean systemMetricsEnabled = true;
    }

    /**
     * Cache configuration.
     */
    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class CacheConfig {

        /**
         * Enable response caching.
         */
        @Builder.Default
        private boolean enabled = true;

        /**
         * Maximum cache size (number of entries).
         */
        @PositiveOrZero
        @Builder.Default
        private int maxSize = 1000;

        /**
         * Cache TTL (time to live).
         */
        @Builder.Default
        private Duration ttl = Duration.ofMinutes(10);

        /**
         * Cache statistics collection.
         */
        @Builder.Default
        private boolean statisticsEnabled = true;
    }

    /**
     * Creates default configuration suitable for development.
     * 
     * @param privateKey Private key for signing transactions
     * @return Default configuration
     */
    public static V402ClientProperties defaultConfig(String privateKey) {
        return V402ClientProperties.builder()
                .privateKey(privateKey)
                .autoPayEnabled(true)
                .maxAmountPerRequest("1000000000000000000") // 1 ETH
                .timeout(Duration.ofSeconds(30))
                .maxConnections(100)
                .chains(List.of(
                        ChainConfig.builder()
                                .name("ethereum")
                                .type("EVM")
                                .rpcUrl("https://eth-mainnet.g.alchemy.com/v2/demo")
                                .chainId(1L)
                                .nativeCurrency("ETH")
                                .build(),
                        ChainConfig.builder()
                                .name("base")
                                .type("EVM")
                                .rpcUrl("https://mainnet.base.org")
                                .chainId(8453L)
                                .nativeCurrency("ETH")
                                .build()
                ))
                .build();
    }

    /**
     * Creates production-ready configuration.
     * 
     * @param privateKey Private key for signing transactions
     * @param rpcUrls Map of chain names to RPC URLs
     * @return Production configuration
     */
    public static V402ClientProperties productionConfig(String privateKey, 
                                                       java.util.Map<String, String> rpcUrls) {
        List<ChainConfig> chains = rpcUrls.entrySet().stream()
                .map(entry -> ChainConfig.builder()
                        .name(entry.getKey())
                        .type("EVM")
                        .rpcUrl(entry.getValue())
                        .build())
                .toList();

        return V402ClientProperties.builder()
                .privateKey(privateKey)
                .chains(chains)
                .autoPayEnabled(true)
                .maxConnections(200)
                .timeout(Duration.ofSeconds(60))
                .resilience(ResilienceConfig.builder()
                        .circuitBreakerEnabled(true)
                        .failureThreshold(10)
                        .maxRetries(5)
                        .build())
                .logging(LoggingConfig.builder()
                        .level("INFO")
                        .format("JSON")
                        .includeRequestBodies(false)
                        .build())
                .build();
    }
}
