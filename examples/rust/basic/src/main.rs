use anyhow::Result;
use tracing::{info, error};
use uuid::Uuid;
use chrono::Utc;

use crate::models::*;
use crate::config::Config;
use crate::client::V402Client;
use crate::services::*;

#[tokio::main]
async fn main() -> Result<()> {
    // Initialize tracing
    tracing_subscriber::fmt::init();

    info!("Starting v402 Rust client example");

    // Load configuration
    let config = Config::from_env().unwrap_or_default();
    
    // Validate configuration
    if let Err(e) = config.validate() {
        error!("Configuration validation failed: {}", e);
        return Err(anyhow::anyhow!("Invalid configuration: {}", e));
    }

    info!("Configuration loaded successfully");

    // Create v402 client
    let client = V402Client::new(config)?;
    
    // Create services
    let mut product_service = ProductService::new(client.clone());
    let mut payment_service = PaymentService::new(client.clone());
    let mut access_service = AccessService::new(client.clone());
    let mut analytics_service = AnalyticsService::new(client.clone());
    let mut health_service = HealthService::new(client);

    // Example 1: Health Check
    info!("=== Health Check ===");
    match health_service.check_health().await {
        Ok(health) => {
            info!("Health check successful: {}", health.status);
            info!("Version: {}", health.version);
            info!("Timestamp: {}", health.timestamp);
        }
        Err(e) => {
            error!("Health check failed: {}", e);
        }
    }

    // Example 2: Create a product
    info!("=== Creating Product ===");
    let product_data = ProductCreate {
        title: "Advanced Rust Programming".to_string(),
        description: "Learn advanced Rust programming techniques and best practices".to_string(),
        price: "15.00".to_string(),
        currency: "USDC".to_string(),
        content_url: "https://example.com/content/rust-advanced".to_string(),
        category: Some("programming".to_string()),
        tags: vec!["rust".to_string(), "programming".to_string(), "advanced".to_string()],
        author: Some("Rust Expert".to_string()),
    };

    match product_service.create_product(product_data).await {
        Ok(product) => {
            info!("Product created successfully: {}", product.id);
            info!("Title: {}", product.title);
            info!("Price: {} {}", product.price, product.currency);
        }
        Err(e) => {
            error!("Failed to create product: {}", e);
        }
    }

    // Example 3: List products
    info!("=== Listing Products ===");
    match product_service.list_products(Some(1), Some(10)).await {
        Ok(products) => {
            info!("Retrieved {} products", products.len());
            for product in products {
                info!("Product: {} - {} ({})", product.id, product.title, product.status);
            }
        }
        Err(e) => {
            error!("Failed to list products: {}", e);
        }
    }

    // Example 4: Process payment
    info!("=== Processing Payment ===");
    let payment_request = PaymentRequest {
        product_id: Uuid::new_v4(), // In real usage, this would be the actual product ID
        amount: "15.00".to_string(),
        currency: "USDC".to_string(),
        user_address: "0xabcdef1234567890abcdef1234567890abcdef12".to_string(),
        nonce: "nonce-123".to_string(),
        signature: "signature-123".to_string(),
    };

    match payment_service.process_payment(payment_request).await {
        Ok(payment_response) => {
            info!("Payment processed successfully");
            info!("Transaction hash: {}", payment_response.transaction_hash);
            info!("Status: {:?}", payment_response.status);
            info!("Amount: {} {}", payment_response.amount, payment_response.currency);
        }
        Err(e) => {
            error!("Failed to process payment: {}", e);
        }
    }

    // Example 5: Check access
    info!("=== Checking Access ===");
    let access_request = AccessRequest {
        product_id: Uuid::new_v4(), // In real usage, this would be the actual product ID
        user_address: "0xabcdef1234567890abcdef1234567890abcdef12".to_string(),
        timestamp: Utc::now().timestamp(),
        signature: "signature-123".to_string(),
    };

    match access_service.check_access(access_request).await {
        Ok(access_response) => {
            info!("Access check completed");
            info!("Has access: {}", access_response.has_access);
            if let Some(reason) = access_response.reason {
                info!("Reason: {}", reason);
            }
            if let Some(expires_at) = access_response.expires_at {
                info!("Expires at: {}", expires_at);
            }
        }
        Err(e) => {
            error!("Failed to check access: {}", e);
        }
    }

    // Example 6: Get analytics
    info!("=== Getting Analytics ===");
    let analytics_request = AnalyticsRequest {
        product_id: None, // Get analytics for all products
        start_date: None,
        end_date: None,
        period: PeriodType::Daily,
    };

    match analytics_service.get_analytics(analytics_request).await {
        Ok(analytics) => {
            info!("Analytics retrieved successfully");
            info!("Views: {}", analytics.views);
            info!("Purchases: {}", analytics.purchases);
            info!("Revenue: {} {}", analytics.revenue, analytics.currency);
            info!("Conversion rate: {:.2}%", analytics.conversion_rate);
            info!("Top countries: {}", analytics.top_countries.len());
            info!("Top referrers: {}", analytics.top_referrers.len());
        }
        Err(e) => {
            error!("Failed to get analytics: {}", e);
        }
    }

    // Example 7: Service statistics
    info!("=== Service Statistics ===");
    info!("Cached products: {}", product_service.cache.len());
    info!("Payment history entries: {}", payment_service.payment_history.len());
    info!("Cached access checks: {}", access_service.access_cache.len());
    info!("Cached analytics: {}", analytics_service.analytics_cache.len());

    // Example 8: Clear caches
    info!("=== Clearing Caches ===");
    product_service.clear_cache();
    payment_service.clear_history();
    access_service.clear_cache();
    analytics_service.clear_cache();
    info!("All caches cleared");

    info!("v402 Rust client example completed successfully");
    Ok(())
}
