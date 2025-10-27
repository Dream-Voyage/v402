//! # v402 Rust Client
//! 
//! High-performance, memory-safe Rust client for the v402 protocol with comprehensive
//! multi-chain payment support and enterprise-grade features.
//! 
//! ## Features
//! 
//! - **Multi-chain Support**: Ethereum, Base, Polygon, Solana, BSC, and more
//! - **High Performance**: Built on Tokio with zero-copy operations where possible
//! - **Memory Safety**: Leverages Rust's ownership system for safe concurrent access
//! - **Async/Await**: Full async support with structured concurrency
//! - **Type Safety**: Comprehensive type system preventing runtime errors
//! - **Resilience**: Circuit breaker, retry, and timeout patterns
//! - **Observability**: Structured logging, metrics, and distributed tracing
//! - **Caching**: Intelligent response caching with TTL and size limits
//! - **Middleware**: Composable middleware system for custom logic
//! 
//! ## Quick Start
//! 
//! ```rust
//! use v402_client::{Client, Config, ChainConfig, ChainType};
//! 
//! #[tokio::main]
//! async fn main() -> Result<(), Box<dyn std::error::Error>> {
//!     // Configure client
//!     let config = Config::builder()
//!         .private_key("0x...")
//!         .auto_pay(true)
//!         .add_chain(ChainConfig::ethereum_mainnet())
//!         .add_chain(ChainConfig::base_mainnet())
//!         .build()?;
//! 
//!     // Create client
//!     let client = Client::new(config).await?;
//! 
//!     // Make request with automatic payment
//!     let response = client
//!         .get("https://example.com/premium-content")
//!         .await?;
//! 
//!     if response.payment_made {
//!         println!("Paid {} for content", response.payment_amount.unwrap());
//!     }
//! 
//!     println!("Content: {}", response.text().await?);
//! 
//!     Ok(())
//! }
//! ```
//! 
//! ## Advanced Usage
//! 
//! ### Batch Processing
//! 
//! ```rust
//! use v402_client::Client;
//! 
//! # #[tokio::main]
//! # async fn main() -> Result<(), Box<dyn std::error::Error>> {
//! # let client = Client::builder().build().await?;
//! let urls = vec![
//!     "https://example.com/article1",
//!     "https://example.com/article2", 
//!     "https://example.com/article3",
//! ];
//! 
//! let responses = client
//!     .batch_get(&urls)
//!     .max_concurrent(10)
//!     .execute()
//!     .await?;
//! 
//! for (i, response) in responses.iter().enumerate() {
//!     match response {
//!         Ok(resp) => println!("URL {}: Success ({})", i, resp.status),
//!         Err(e) => println!("URL {}: Error ({})", i, e),
//!     }
//! }
//! # Ok(())
//! # }
//! ```
//! 
//! ### Custom Middleware
//! 
//! ```rust
//! use v402_client::{Client, middleware::Middleware, Request, Response};
//! use async_trait::async_trait;
//! 
//! struct AuthMiddleware {
//!     token: String,
//! }
//! 
//! #[async_trait]
//! impl Middleware for AuthMiddleware {
//!     async fn call(
//!         &self,
//!         req: Request,
//!         next: Box<dyn Fn(Request) -> std::pin::Pin<Box<dyn std::future::Future<Output = Result<Response, v402_client::Error>> + Send>> + Send>,
//!     ) -> Result<Response, v402_client::Error> {
//!         let mut req = req;
//!         req.headers.insert("Authorization", format!("Bearer {}", self.token));
//!         next(req).await
//!     }
//! }
//! 
//! # #[tokio::main]
//! # async fn main() -> Result<(), Box<dyn std::error::Error>> {
//! let client = Client::builder()
//!     .middleware(AuthMiddleware { token: "abc123".to_string() })
//!     .build()
//!     .await?;
//! # Ok(())
//! # }
//! ```

#![cfg_attr(docsrs, feature(doc_cfg))]
#![warn(
    missing_docs,
    rust_2018_idioms,
    unreachable_pub,
    missing_debug_implementations
)]
#![forbid(unsafe_code)]

// Re-export main types
pub use client::{Client, ClientBuilder};
pub use config::{Config, ConfigBuilder, ChainConfig, ChainType};
pub use error::{Error, Result};
pub use types::{PaymentResponse, PaymentHistory, PaymentStatistics, HealthStatus};

// Modules
pub mod client;
pub mod config;
pub mod error;
pub mod types;
pub mod chains;
pub mod payment;
pub mod middleware;
pub mod metrics;
pub mod cache;

// Internal modules
mod http;
mod crypto;
mod utils;

// Feature-gated modules
#[cfg(feature = "ethereum")]
pub mod ethereum;

#[cfg(feature = "solana")]
pub mod solana;

/// Version information
pub const VERSION: &str = env!("CARGO_PKG_VERSION");

/// User agent string for HTTP requests
pub const USER_AGENT: &str = concat!("v402-client-rust/", env!("CARGO_PKG_VERSION"));

/// Default facilitator URL
pub const DEFAULT_FACILITATOR_URL: &str = "https://facilitator.v402.network";

/// Maximum payment amount in wei (10 ETH)
pub const MAX_PAYMENT_AMOUNT: &str = "10000000000000000000";

/// Re-export commonly used external types
pub use reqwest::Method;
pub use serde_json::Value as JsonValue;
pub use tokio;
pub use url::Url;
