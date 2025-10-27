# v402 Java SDK

**Enterprise-grade Java client for v402 multi-chain payment protocol.**

## Features

- 🏢 **Enterprise Ready**: Spring Boot integration, Production patterns
- ⚡ **Reactive**: Project Reactor for async non-blocking operations
- 🌍 **Multi-Chain**: Full support for EVM, Solana, BSC, Polygon
- 📊 **Observable**: Micrometer metrics, distributed tracing
- 🔄 **Resilient**: Resilience4j (Circuit Breaker, Retry, RateLimiter)
- 🎯 **Type-Safe**: Strongly typed APIs, compile-time safety

## Architecture

```
clients/java/
├── v402-client-core/          # Core client library
│   └── src/main/java/org/v402/client/
│       ├── core/              # Core client classes
│       │   ├── V402Client.java
│       │   ├── AsyncV402Client.java
│       │   └── ReactiveV402Client.java
│       ├── chain/             # Chain implementations
│       │   ├── Chain.java     # Chain interface
│       │   ├── evm/           # EVM chains
│       │   ├── solana/        # Solana
│       │   ├── bsc/           # BSC
│       │   └── polygon/       # Polygon
│       ├── payment/           # Payment processing
│       │   ├── Signer.java
│       │   ├── Verifier.java
│       │   ├── PaymentStrategy.java
│       │   └── PaymentHistory.java
│       ├── config/            # Configuration
│       │   ├── V402Config.java
│       │   ├── ChainConfig.java
│       │   └── ClientProperties.java
│       ├── crypto/            # Cryptographic operations
│       │   ├── KeyManager.java
│       │   ├── SignatureService.java
│       │   └── CryptoUtils.java
│       ├── http/              # HTTP client
│       │   ├── HttpClient.java
│       │   ├── ConnectionPool.java
│       │   └── RetryPolicy.java
│       ├── logging/           # Logging
│       │   ├── V402Logger.java
│       │   └── LogContext.java
│       ├── metrics/           # Metrics & monitoring
│       │   ├── MetricsRegistry.java
│       │   ├── PaymentMetrics.java
│       │   └── HealthIndicator.java
│       ├── exception/         # Exception hierarchy
│       │   ├── V402Exception.java
│       │   ├── PaymentException.java
│       │   └── ChainException.java
│       └── model/             # Data models
│           ├── PaymentRequest.java
│           ├── PaymentResponse.java
│           └── Transaction.java
│
├── v402-spring-boot-starter/  # Spring Boot auto-configuration
│   └── src/main/java/org/v402/spring/
│       ├── autoconfigure/
│       │   └── V402AutoConfiguration.java
│       ├── properties/
│       │   └── V402Properties.java
│       └── actuator/
│           └── V402HealthIndicator.java
│
├── v402-resilience/           # Resilience4j integration
│   └── src/main/java/org/v402/resilience/
│       ├── CircuitBreakerConfig.java
│       ├── RetryConfig.java
│       └── RateLimiterConfig.java
│
└── examples/                  # Usage examples
    ├── basic-example/
    ├── spring-boot-example/
    └── reactive-example/
```

## Installation

### Maven

```xml
<dependency>
    <groupId>org.v402</groupId>
    <artifactId>v402-client-core</artifactId>
    <version>1.0.0</version>
</dependency>

<!-- Spring Boot Starter -->
<dependency>
    <groupId>org.v402</groupId>
    <artifactId>v402-spring-boot-starter</artifactId>
    <version>1.0.0</version>
</dependency>
```

### Gradle

```gradle
implementation 'org.v402:v402-client-core:1.0.0'
implementation 'org.v402:v402-spring-boot-starter:1.0.0'
```

## Quick Start

### Basic Usage

```java
import org.v402.client.core.V402Client;
import org.v402.client.config.V402Config;
import org.v402.client.model.PaymentResponse;

public class Example {
    public static void main(String[] args) {
        // Configure client
        V402Config config = V402Config.builder()
            .privateKey("0x...")
            .chains(List.of(
                ChainConfig.ethereum(),
                ChainConfig.base(),
                ChainConfig.polygon()
            ))
            .autoPay(true)
            .maxAmountPerRequest("1000000")
            .build();
        
        // Create client
        V402Client client = new V402Client(config);
        
        // Make request
        PaymentResponse response = client.get("https://example.com/premium");
        
        System.out.println("Status: " + response.getStatusCode());
        System.out.println("Payment Made: " + response.isPaymentMade());
        
        client.close();
    }
}
```

### Reactive Usage (Project Reactor)

```java
import org.v402.client.core.ReactiveV402Client;
import reactor.core.publisher.Mono;
import reactor.core.publisher.Flux;

public class ReactiveExample {
    public static void main(String[] args) {
        ReactiveV402Client client = new ReactiveV402Client(config);
        
        // Single request
        Mono<PaymentResponse> response = client.get("https://example.com/premium");
        
        response.subscribe(
            resp -> System.out.println("Received: " + resp),
            error -> System.err.println("Error: " + error),
            () -> System.out.println("Complete")
        );
        
        // Batch requests
        List<String> urls = Arrays.asList(
            "https://example.com/article1",
            "https://example.com/article2",
            "https://example.com/article3"
        );
        
        Flux.fromIterable(urls)
            .flatMap(client::get)
            .subscribe(resp -> System.out.println("Fetched: " + resp.getUrl()));
    }
}
```

## Spring Boot Integration

### Application Properties

```yaml
v402:
  client:
    private-key: ${V402_PRIVATE_KEY}
    auto-pay: true
    max-amount-per-request: 1000000
    timeout: 30s
    
  chains:
    - name: ethereum
      type: evm
      rpc-url: https://eth-mainnet.g.alchemy.com/v2/...
      chain-id: 1
      
    - name: solana
      type: solana
      rpc-url: https://api.mainnet-beta.solana.com
      
  logging:
    level: INFO
    format: JSON
    
  metrics:
    enabled: true
    
  resilience:
    circuit-breaker:
      enabled: true
      failure-rate-threshold: 50
      wait-duration-in-open-state: 60s
    retry:
      max-attempts: 3
      wait-duration: 1s
```

### Service Integration

```java
import org.v402.client.core.V402Client;
import org.springframework.stereotype.Service;

@Service
public class ContentService {
    private final V402Client v402Client;
    
    public ContentService(V402Client v402Client) {
        this.v402Client = v402Client;
    }
    
    public CompletableFuture<Content> fetchPremiumContent(String url) {
        return v402Client.getAsync(url)
            .thenApply(response -> response.getBody(Content.class));
    }
}
```

### Controller Example

```java
@RestController
@RequestMapping("/api/content")
public class ContentController {
    @Autowired
    private ContentService contentService;
    
    @GetMapping("/premium/{id}")
    public Mono<Content> getPremiumContent(@PathVariable String id) {
        String url = "https://provider.com/content/" + id;
        return Mono.fromFuture(contentService.fetchPremiumContent(url));
    }
}
```

## Advanced Features

### Circuit Breaker Pattern

```java
import io.github.resilience4j.circuitbreaker.CircuitBreaker;
import io.github.resilience4j.circuitbreaker.CircuitBreakerConfig;

CircuitBreakerConfig cbConfig = CircuitBreakerConfig.custom()
    .failureRateThreshold(50)
    .waitDurationInOpenState(Duration.ofSeconds(60))
    .slidingWindowSize(10)
    .build();

V402Config config = V402Config.builder()
    .privateKey("0x...")
    .circuitBreaker(cbConfig)
    .build();

V402Client client = new V402Client(config);
```

### Custom Payment Strategy

```java
public class LowestCostStrategy implements PaymentStrategy {
    @Override
    public PaymentRequirements select(List<PaymentRequirements> options) {
        return options.stream()
            .min(Comparator.comparing(PaymentRequirements::getMaxAmountRequired))
            .orElseThrow(() -> new NoPaymentOptionException());
    }
}

V402Config config = V402Config.builder()
    .privateKey("0x...")
    .paymentStrategy(new LowestCostStrategy())
    .build();
```

### Metrics & Monitoring

```java
import io.micrometer.core.instrument.MeterRegistry;

@Configuration
public class MetricsConfig {
    @Bean
    public MeterRegistry meterRegistry() {
        return new SimpleMeterRegistry();
    }
}

// Metrics are automatically collected:
// - v402.payment.total
// - v402.payment.success
// - v402.payment.failed
// - v402.request.duration
// - v402.chain.requests
```

## Configuration

### Environment Variables

```bash
V402_PRIVATE_KEY=0x...
V402_CHAINS=ethereum,base,polygon
V402_MAX_AMOUNT=1000000
V402_AUTO_PAY=true
V402_LOG_LEVEL=INFO
```

## Development

```bash
# Build
mvn clean install

# Run tests
mvn test

# Run integration tests
mvn verify

# Generate docs
mvn javadoc:javadoc

# Run examples
mvn exec:java -pl examples/basic-example
```

## API Reference

See [JavaDoc](https://javadoc.io/doc/org.v402/v402-client-core)

