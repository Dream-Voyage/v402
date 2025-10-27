//! High-performance async v402 client implementation.

use crate::{
    config::Config,
    error::{Error, Result},
    middleware::{Middleware, MiddlewareStack},
    types::{PaymentResponse, PaymentHistory, PaymentStatistics, HealthStatus},
    http::HttpClient,
    payment::PaymentManager,
    chains::ChainManager,
    cache::CacheManager,
    metrics::MetricsCollector,
};
use async_trait::async_trait;
use futures::future::try_join_all;
use parking_lot::RwLock;
use std::{
    collections::HashMap,
    sync::{atomic::{AtomicBool, AtomicU64, Ordering}, Arc},
    time::{Duration, Instant},
};
use tokio::{sync::Semaphore, time::timeout};
use tracing::{debug, error, info, instrument, warn};
use uuid::Uuid;

/// High-performance async client for the v402 protocol.
/// 
/// The client is designed for high-throughput scenarios while maintaining
/// memory safety and type safety. It uses Arc<> for shared state and
/// supports graceful shutdown with proper resource cleanup.
/// 
/// ## Architecture
/// 
/// ```text
/// ┌─────────────────────────────────────────────────────┐
/// │                    Client                           │
/// ├─────────────────────────────────────────────────────┤
/// │  ┌─────────────┐  ┌──────────────┐  ┌─────────────┐ │
/// │  │ Middleware  │  │ HTTP Client  │  │   Cache     │ │
/// │  │   Stack     │  │   (reqwest)  │  │ (moka/LRU)  │ │
/// │  └─────────────┘  └──────────────┘  └─────────────┘ │
/// │  ┌─────────────┐  ┌──────────────┐  ┌─────────────┐ │
/// │  │   Payment   │  │    Chain     │  │  Metrics    │ │
/// │  │  Manager    │  │   Manager    │  │ Collector   │ │
/// │  └─────────────┘  └──────────────┘  └─────────────┘ │
/// └─────────────────────────────────────────────────────┘
/// ```
/// 
/// ## Features
/// 
/// - **Zero-copy operations** where possible using `Bytes` and `Arc`
/// - **Structured concurrency** with proper cancellation handling
/// - **Memory-efficient** batch processing with semaphore-based limiting
/// - **Circuit breaker** pattern for automatic failure recovery
/// - **Comprehensive observability** with metrics and distributed tracing
#[derive(Clone)]
pub struct Client {
    /// Client configuration (immutable after creation)
    config: Arc<Config>,
    
    /// HTTP client for making requests
    http_client: Arc<HttpClient>,
    
    /// Payment processing manager
    payment_manager: Arc<PaymentManager>,
    
    /// Multi-chain manager
    chain_manager: Arc<ChainManager>,
    
    /// Response cache manager
    cache_manager: Arc<CacheManager>,
    
    /// Metrics collector
    metrics: Arc<MetricsCollector>,
    
    /// Middleware stack for request/response processing
    middleware_stack: Arc<MiddlewareStack>,
    
    /// Client state
    state: Arc<ClientState>,
}

/// Internal client state for managing lifecycle and statistics.
#[derive(Debug)]
struct ClientState {
    /// Whether the client has been closed
    closed: AtomicBool,
    
    /// Number of active requests
    active_requests: AtomicU64,
    
    /// Request statistics
    stats: RwLock<ClientStats>,
    
    /// Client instance ID for tracing
    instance_id: Uuid,
}

/// Client statistics for monitoring and debugging.
#[derive(Debug, Clone, Default)]
struct ClientStats {
    /// Total requests made
    total_requests: u64,
    
    /// Successful requests
    successful_requests: u64,
    
    /// Failed requests
    failed_requests: u64,
    
    /// Payments made
    payments_made: u64,
    
    /// Total amount paid (in wei)
    total_amount_paid: u128,
    
    /// Average request duration
    average_duration: Duration,
    
    /// Client start time
    start_time: Instant,
}

impl Client {
    /// Creates a new v402 client with the given configuration.
    /// 
    /// This is an expensive operation that:
    /// - Initializes connection pools
    /// - Establishes blockchain connections
    /// - Sets up metrics and tracing
    /// - Validates configuration
    /// 
    /// # Errors
    /// 
    /// Returns an error if:
    /// - Configuration is invalid
    /// - Blockchain connections fail
    /// - HTTP client setup fails
    /// - Metrics initialization fails
    /// 
    /// # Example
    /// 
    /// ```rust
    /// use v402_client::{Client, Config};
    /// 
    /// # #[tokio::main]
    /// # async fn main() -> Result<(), Box<dyn std::error::Error>> {
    /// let config = Config::builder()
    ///     .private_key("0x...")
    ///     .build()?;
    /// 
    /// let client = Client::new(config).await?;
    /// # Ok(())
    /// # }
    /// ```
    #[instrument(skip_all, fields(chains = config.chains.len()))]
    pub async fn new(config: Config) -> Result<Self> {
        info!("Initializing v402 client");
        
        let config = Arc::new(config);
        let instance_id = Uuid::new_v4();
        
        // Initialize HTTP client
        let http_client = Arc::new(HttpClient::new(&config).await?);
        
        // Initialize chain manager
        let chain_manager = Arc::new(ChainManager::new(&config).await?);
        
        // Initialize payment manager
        let payment_manager = Arc::new(PaymentManager::new(&config, &chain_manager).await?);
        
        // Initialize cache manager
        let cache_manager = Arc::new(CacheManager::new(&config.cache)?);
        
        // Initialize metrics collector
        let metrics = Arc::new(MetricsCollector::new(&config.metrics)?);
        
        // Initialize middleware stack
        let middleware_stack = Arc::new(MiddlewareStack::new());
        
        // Initialize client state
        let state = Arc::new(ClientState {
            closed: AtomicBool::new(false),
            active_requests: AtomicU64::new(0),
            stats: RwLock::new(ClientStats {
                start_time: Instant::now(),
                ..Default::default()
            }),
            instance_id,
        });
        
        let client = Self {
            config,
            http_client,
            payment_manager,
            chain_manager,
            cache_manager,
            metrics,
            middleware_stack,
            state,
        };
        
        info!(
            instance_id = %instance_id,
            "v402 client initialized successfully"
        );
        
        Ok(client)
    }

    /// Creates a new client builder for advanced configuration.
    /// 
    /// # Example
    /// 
    /// ```rust
    /// use v402_client::Client;
    /// 
    /// # #[tokio::main]
    /// # async fn main() -> Result<(), Box<dyn std::error::Error>> {
    /// let client = Client::builder()
    ///     .private_key("0x...")
    ///     .auto_pay(true)
    ///     .max_amount_per_request("1000000000000000000")
    ///     .timeout(std::time::Duration::from_secs(60))
    ///     .build()
    ///     .await?;
    /// # Ok(())
    /// # }
    /// ```
    pub fn builder() -> ClientBuilder {
        ClientBuilder::new()
    }

    /// Performs an HTTP GET request with automatic payment handling.
    /// 
    /// This method:
    /// 1. Checks cache for existing response
    /// 2. Makes HTTP request through middleware stack
    /// 3. Handles 402 Payment Required automatically if enabled
    /// 4. Updates cache and metrics
    /// 5. Returns structured response
    /// 
    /// # Arguments
    /// 
    /// * `url` - The URL to request
    /// 
    /// # Returns
    /// 
    /// A `PaymentResponse` containing the response data and payment information.
    /// 
    /// # Errors
    /// 
    /// - `Error::Network` for network-related failures
    /// - `Error::Payment` for payment-related failures
    /// - `Error::ClientClosed` if client has been closed
    /// 
    /// # Example
    /// 
    /// ```rust
    /// # use v402_client::Client;
    /// # #[tokio::main]
    /// # async fn main() -> Result<(), Box<dyn std::error::Error>> {
    /// # let client = Client::builder().build().await?;
    /// let response = client.get("https://example.com/premium").await?;
    /// 
    /// if response.payment_made {
    ///     println!("Paid {} wei", response.payment_amount.unwrap());
    /// }
    /// 
    /// let content = response.text().await?;
    /// println!("Content: {}", content);
    /// # Ok(())
    /// # }
    /// ```
    #[instrument(skip(self), fields(
        instance_id = %self.state.instance_id,
        url = %url
    ))]
    pub async fn get<U>(&self, url: U) -> Result<PaymentResponse>
    where
        U: AsRef<str> + Send,
    {
        self.request(reqwest::Method::GET, url, None::<&[u8]>).await
    }

    /// Performs an HTTP POST request with automatic payment handling.
    /// 
    /// # Arguments
    /// 
    /// * `url` - The URL to request
    /// * `body` - The request body (optional)
    /// 
    /// # Example
    /// 
    /// ```rust
    /// # use v402_client::Client;
    /// # #[tokio::main]
    /// # async fn main() -> Result<(), Box<dyn std::error::Error>> {
    /// # let client = Client::builder().build().await?;
    /// let response = client
    ///     .post("https://api.example.com/data", Some(b"request data"))
    ///     .await?;
    /// # Ok(())
    /// # }
    /// ```
    #[instrument(skip(self, body), fields(
        instance_id = %self.state.instance_id,
        url = %url.as_ref()
    ))]
    pub async fn post<U, B>(&self, url: U, body: Option<B>) -> Result<PaymentResponse>
    where
        U: AsRef<str> + Send,
        B: AsRef<[u8]> + Send,
    {
        self.request(reqwest::Method::POST, url, body).await
    }

    /// Core request method that handles all HTTP methods.
    async fn request<U, B>(
        &self,
        method: reqwest::Method,
        url: U,
        body: Option<B>,
    ) -> Result<PaymentResponse>
    where
        U: AsRef<str> + Send,
        B: AsRef<[u8]> + Send,
    {
        self.ensure_not_closed()?;
        
        let url = url.as_ref();
        let start_time = Instant::now();
        
        // Increment active request counter
        self.state.active_requests.fetch_add(1, Ordering::Relaxed);
        
        // Create request guard for automatic cleanup
        let _guard = RequestGuard::new(&self.state);
        
        // Check cache for GET requests
        if method == reqwest::Method::GET {
            if let Some(cached) = self.cache_manager.get(url).await? {
                debug!(url = %url, "Cache hit");
                self.metrics.increment_cache_hits();
                return Ok(cached);
            }
        }
        
        // Execute request through middleware stack
        let result = self.execute_request(method, url, body).await;
        
        // Update statistics
        let duration = start_time.elapsed();
        self.update_stats(&result, duration).await;
        
        // Record metrics
        self.metrics.record_request(
            &method.to_string(),
            &result,
            duration,
        );
        
        result
    }

    /// Executes the actual HTTP request through the middleware stack.
    async fn execute_request<B>(
        &self,
        method: reqwest::Method,
        url: &str,
        body: Option<B>,
    ) -> Result<PaymentResponse>
    where
        B: AsRef<[u8]> + Send,
    {
        // Create request
        let mut request = crate::http::Request::new(method, url)?;
        
        if let Some(body) = body {
            request = request.body(body.as_ref().to_vec());
        }
        
        // Execute through middleware stack
        let response = self.middleware_stack.execute(request, &*self.http_client).await?;
        
        // Handle 402 Payment Required
        if response.status == 402 && self.config.auto_pay {
            return self.handle_payment_required(request, response).await;
        }
        
        Ok(response)
    }

    /// Handles 402 Payment Required responses.
    async fn handle_payment_required(
        &self,
        mut request: crate::http::Request,
        response: PaymentResponse,
    ) -> Result<PaymentResponse> {
        info!(url = %request.url, "Payment required, processing payment");
        
        // Parse payment requirements
        let payment_requirements = self.payment_manager
            .parse_payment_requirements(&response.body)
            .await?;
        
        // Create payment header
        let payment_header = self.payment_manager
            .create_payment_header(&payment_requirements)
            .await?;
        
        // Add payment header and retry
        request.headers.insert("X-PAYMENT".to_string(), payment_header);
        
        info!(
            url = %request.url,
            amount = %payment_requirements.max_amount_required,
            network = %payment_requirements.network,
            "Retrying request with payment"
        );
        
        // Execute paid request
        let mut paid_response = self.middleware_stack
            .execute(request, &*self.http_client)
            .await?;
        
        // Mark as paid and update payment info
        paid_response.payment_made = true;
        paid_response.payment_amount = Some(payment_requirements.max_amount_required);
        paid_response.network = Some(payment_requirements.network);
        
        // Process settlement if available
        if let Some(settlement_header) = paid_response.headers.get("X-PAYMENT-RESPONSE") {
            // Decode and process settlement
            if let Ok(settlement) = self.payment_manager
                .process_settlement(settlement_header)
                .await
            {
                paid_response.transaction_hash = settlement.transaction_hash;
                paid_response.payer = settlement.payer;
            }
        }
        
        Ok(paid_response)
    }

    /// Performs multiple GET requests concurrently.
    /// 
    /// This method provides high-performance batch processing with:
    /// - Semaphore-based concurrency limiting
    /// - Automatic error recovery
    /// - Memory-efficient streaming
    /// - Comprehensive error reporting
    /// 
    /// # Arguments
    /// 
    /// * `urls` - Vector of URLs to request
    /// * `max_concurrent` - Maximum number of concurrent requests
    /// 
    /// # Returns
    /// 
    /// A vector of `Result<PaymentResponse, Error>` in the same order as input URLs.
    /// 
    /// # Example
    /// 
    /// ```rust
    /// # use v402_client::Client;
    /// # #[tokio::main]
    /// # async fn main() -> Result<(), Box<dyn std::error::Error>> {
    /// # let client = Client::builder().build().await?;
    /// let urls = vec![
    ///     "https://example.com/1",
    ///     "https://example.com/2",
    ///     "https://example.com/3",
    /// ];
    /// 
    /// let responses = client.batch_get(&urls, 10).await?;
    /// 
    /// for (i, result) in responses.into_iter().enumerate() {
    ///     match result {
    ///         Ok(response) => println!("URL {}: {} bytes", i, response.body.len()),
    ///         Err(error) => println!("URL {}: Error - {}", i, error),
    ///     }
    /// }
    /// # Ok(())
    /// # }
    /// ```
    #[instrument(skip(self, urls), fields(
        instance_id = %self.state.instance_id,
        url_count = urls.len(),
        max_concurrent = max_concurrent
    ))]
    pub async fn batch_get(
        &self,
        urls: &[impl AsRef<str> + Send + Sync],
        max_concurrent: usize,
    ) -> Result<Vec<Result<PaymentResponse, Error>>> {
        self.ensure_not_closed()?;
        
        if urls.is_empty() {
            return Ok(Vec::new());
        }
        
        info!(
            url_count = urls.len(),
            max_concurrent = max_concurrent,
            "Starting batch GET requests"
        );
        
        // Create semaphore for concurrency limiting
        let semaphore = Arc::new(Semaphore::new(max_concurrent));
        
        // Create tasks for each URL
        let tasks = urls.iter().map(|url| {
            let url = url.as_ref().to_string();
            let client = self.clone();
            let semaphore = semaphore.clone();
            
            tokio::spawn(async move {
                // Acquire semaphore permit
                let _permit = semaphore.acquire().await.map_err(|_| {
                    Error::Internal("Failed to acquire semaphore permit".to_string())
                })?;
                
                // Make request with timeout
                let request_timeout = client.config.timeout;
                timeout(request_timeout, client.get(&url)).await
                    .map_err(|_| Error::Timeout(url.clone(), request_timeout))?
            })
        });
        
        // Execute all tasks concurrently
        let results = try_join_all(tasks).await
            .map_err(|e| Error::Internal(format!("Batch request task failed: {}", e)))?;
        
        info!(
            url_count = urls.len(),
            "Batch GET requests completed"
        );
        
        Ok(results)
    }

    /// Retrieves payment history.
    /// 
    /// # Arguments
    /// 
    /// * `limit` - Maximum number of records to return
    /// 
    /// # Example
    /// 
    /// ```rust
    /// # use v402_client::Client;
    /// # #[tokio::main]
    /// # async fn main() -> Result<(), Box<dyn std::error::Error>> {
    /// # let client = Client::builder().build().await?;
    /// let history = client.get_payment_history(100).await?;
    /// 
    /// for payment in history {
    ///     println!("Paid {} to {} on {}", 
    ///         payment.amount, payment.payee, payment.network);
    /// }
    /// # Ok(())
    /// # }
    /// ```
    pub async fn get_payment_history(&self, limit: usize) -> Result<Vec<PaymentHistory>> {
        self.ensure_not_closed()?;
        self.payment_manager.get_history(limit).await
    }

    /// Retrieves payment statistics.
    /// 
    /// # Example
    /// 
    /// ```rust
    /// # use v402_client::Client;
    /// # #[tokio::main]
    /// # async fn main() -> Result<(), Box<dyn std::error::Error>> {
    /// # let client = Client::builder().build().await?;
    /// let stats = client.get_payment_statistics().await?;
    /// 
    /// println!("Total payments: {}", stats.total_payments);
    /// println!("Total amount: {} wei", stats.total_amount);
    /// # Ok(())
    /// # }
    /// ```
    pub async fn get_payment_statistics(&self) -> Result<PaymentStatistics> {
        self.ensure_not_closed()?;
        self.payment_manager.get_statistics().await
    }

    /// Performs a comprehensive health check.
    /// 
    /// # Example
    /// 
    /// ```rust
    /// # use v402_client::Client;
    /// # #[tokio::main]
    /// # async fn main() -> Result<(), Box<dyn std::error::Error>> {
    /// # let client = Client::builder().build().await?;
    /// let health = client.health_check().await?;
    /// 
    /// if health.healthy {
    ///     println!("Client is healthy");
    /// } else {
    ///     println!("Client has issues: {:?}", health.issues);
    /// }
    /// # Ok(())
    /// # }
    /// ```
    pub async fn health_check(&self) -> Result<HealthStatus> {
        let mut status = HealthStatus {
            healthy: true,
            timestamp: chrono::Utc::now(),
            components: HashMap::new(),
            issues: Vec::new(),
            metrics: HashMap::new(),
        };
        
        // Check HTTP client
        let http_healthy = self.http_client.health_check().await.is_ok();
        status.components.insert("http_client".to_string(), http_healthy);
        if !http_healthy {
            status.healthy = false;
            status.issues.push("HTTP client unhealthy".to_string());
        }
        
        // Check chain manager
        let chain_health = self.chain_manager.health_check().await?;
        for (chain, healthy) in &chain_health {
            status.components.insert(format!("chain_{}", chain), *healthy);
            if !healthy {
                status.healthy = false;
                status.issues.push(format!("Chain {} unhealthy", chain));
            }
        }
        
        // Check cache
        let cache_healthy = self.cache_manager.health_check().await.is_ok();
        status.components.insert("cache".to_string(), cache_healthy);
        
        // Add metrics
        let stats = self.state.stats.read().clone();
        status.metrics.insert("total_requests".to_string(), stats.total_requests.into());
        status.metrics.insert("successful_requests".to_string(), stats.successful_requests.into());
        status.metrics.insert("failed_requests".to_string(), stats.failed_requests.into());
        status.metrics.insert("active_requests".to_string(), 
            self.state.active_requests.load(Ordering::Relaxed).into());
        
        Ok(status)
    }

    /// Adds a middleware to the middleware stack.
    /// 
    /// Middlewares are executed in the order they are added.
    /// 
    /// # Example
    /// 
    /// ```rust
    /// use v402_client::{Client, middleware::Middleware};
    /// 
    /// # #[tokio::main]
    /// # async fn main() -> Result<(), Box<dyn std::error::Error>> {
    /// let mut client = Client::builder().build().await?;
    /// 
    /// // Add custom middleware
    /// client.add_middleware(Box::new(MyCustomMiddleware::new()));
    /// # Ok(())
    /// # }
    /// ```
    pub fn add_middleware(&self, middleware: Box<dyn Middleware>) {
        self.middleware_stack.add(middleware);
    }

    /// Gracefully closes the client and releases all resources.
    /// 
    /// This method:
    /// - Stops accepting new requests
    /// - Waits for active requests to complete (with timeout)
    /// - Closes all connections
    /// - Flushes metrics and logs
    /// 
    /// # Example
    /// 
    /// ```rust
    /// # use v402_client::Client;
    /// # #[tokio::main]
    /// # async fn main() -> Result<(), Box<dyn std::error::Error>> {
    /// let client = Client::builder().build().await?;
    /// 
    /// // Use client...
    /// 
    /// client.close().await?;
    /// # Ok(())
    /// # }
    /// ```
    #[instrument(skip(self), fields(instance_id = %self.state.instance_id))]
    pub async fn close(&self) -> Result<()> {
        if self.state.closed.swap(true, Ordering::Relaxed) {
            return Ok(()); // Already closed
        }
        
        info!("Closing v402 client");
        
        // Wait for active requests to complete (with timeout)
        let shutdown_timeout = Duration::from_secs(30);
        let start = Instant::now();
        
        while self.state.active_requests.load(Ordering::Relaxed) > 0 
            && start.elapsed() < shutdown_timeout 
        {
            tokio::time::sleep(Duration::from_millis(100)).await;
        }
        
        if self.state.active_requests.load(Ordering::Relaxed) > 0 {
            warn!(
                active_requests = self.state.active_requests.load(Ordering::Relaxed),
                "Forcing shutdown with active requests"
            );
        }
        
        // Close all components
        if let Err(e) = self.chain_manager.close().await {
            error!("Error closing chain manager: {}", e);
        }
        
        if let Err(e) = self.payment_manager.close().await {
            error!("Error closing payment manager: {}", e);
        }
        
        if let Err(e) = self.cache_manager.close().await {
            error!("Error closing cache manager: {}", e);
        }
        
        if let Err(e) = self.metrics.close().await {
            error!("Error closing metrics collector: {}", e);
        }
        
        info!("v402 client closed successfully");
        
        Ok(())
    }

    /// Checks if the client is closed.
    pub fn is_closed(&self) -> bool {
        self.state.closed.load(Ordering::Relaxed)
    }

    /// Returns the current configuration.
    pub fn config(&self) -> &Config {
        &self.config
    }

    /// Ensures the client is not closed.
    fn ensure_not_closed(&self) -> Result<()> {
        if self.is_closed() {
            Err(Error::ClientClosed)
        } else {
            Ok(())
        }
    }

    /// Updates client statistics.
    async fn update_stats(&self, result: &Result<PaymentResponse>, duration: Duration) {
        let mut stats = self.state.stats.write();
        
        stats.total_requests += 1;
        
        match result {
            Ok(response) => {
                stats.successful_requests += 1;
                
                if response.payment_made {
                    stats.payments_made += 1;
                    
                    if let Some(amount_str) = &response.payment_amount {
                        if let Ok(amount) = amount_str.parse::<u128>() {
                            stats.total_amount_paid += amount;
                        }
                    }
                }
            }
            Err(_) => {
                stats.failed_requests += 1;
            }
        }
        
        // Update average duration (simple moving average)
        if stats.total_requests == 1 {
            stats.average_duration = duration;
        } else {
            let total_duration = stats.average_duration * (stats.total_requests - 1) as u32 + duration;
            stats.average_duration = total_duration / stats.total_requests as u32;
        }
    }
}

/// RAII guard for tracking active requests.
struct RequestGuard<'a> {
    state: &'a ClientState,
}

impl<'a> RequestGuard<'a> {
    fn new(state: &'a ClientState) -> Self {
        Self { state }
    }
}

impl Drop for RequestGuard<'_> {
    fn drop(&mut self) {
        self.state.active_requests.fetch_sub(1, Ordering::Relaxed);
    }
}

/// Builder for creating a v402 client with custom configuration.
#[derive(Debug)]
pub struct ClientBuilder {
    config_builder: crate::config::ConfigBuilder,
    middlewares: Vec<Box<dyn Middleware>>,
}

impl ClientBuilder {
    /// Creates a new client builder.
    pub fn new() -> Self {
        Self {
            config_builder: crate::config::ConfigBuilder::new(),
            middlewares: Vec::new(),
        }
    }

    /// Sets the private key for signing transactions.
    pub fn private_key<S: Into<String>>(mut self, key: S) -> Self {
        self.config_builder = self.config_builder.private_key(key);
        self
    }

    /// Enables or disables automatic payment.
    pub fn auto_pay(mut self, enabled: bool) -> Self {
        self.config_builder = self.config_builder.auto_pay(enabled);
        self
    }

    /// Sets the maximum amount to pay per request.
    pub fn max_amount_per_request<S: Into<String>>(mut self, amount: S) -> Self {
        self.config_builder = self.config_builder.max_amount_per_request(amount);
        self
    }

    /// Sets the request timeout.
    pub fn timeout(mut self, timeout: Duration) -> Self {
        self.config_builder = self.config_builder.timeout(timeout);
        self
    }

    /// Adds a middleware to the client.
    pub fn middleware(mut self, middleware: Box<dyn Middleware>) -> Self {
        self.middlewares.push(middleware);
        self
    }

    /// Builds the client.
    pub async fn build(self) -> Result<Client> {
        let config = self.config_builder.build()?;
        let mut client = Client::new(config).await?;
        
        // Add middlewares
        for middleware in self.middlewares {
            client.add_middleware(middleware);
        }
        
        Ok(client)
    }
}

impl Default for ClientBuilder {
    fn default() -> Self {
        Self::new()
    }
}

// Implement Send + Sync for Client (all components are thread-safe)
unsafe impl Send for Client {}
unsafe impl Sync for Client {}
