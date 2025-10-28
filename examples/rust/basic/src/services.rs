use anyhow::Result;
use tracing::{info, error, warn};
use std::collections::HashMap;
use uuid::Uuid;
use chrono::{DateTime, Utc};

use crate::models::*;
use crate::client::V402Client;

pub struct ProductService {
    client: V402Client,
    cache: HashMap<Uuid, Product>,
}

impl ProductService {
    pub fn new(client: V402Client) -> Self {
        Self {
            client,
            cache: HashMap::new(),
        }
    }

    pub async fn create_product(&mut self, product_data: ProductCreate) -> Result<Product> {
        info!("Creating product: {}", product_data.title);
        
        let product = self.client.create_product(&product_data).await?;
        
        // Cache the product
        self.cache.insert(product.id, product.clone());
        
        info!("Product created successfully: {}", product.id);
        Ok(product)
    }

    pub async fn get_product(&mut self, product_id: Uuid) -> Result<Product> {
        // Check cache first
        if let Some(product) = self.cache.get(&product_id) {
            info!("Product found in cache: {}", product_id);
            return Ok(product.clone());
        }

        info!("Fetching product from API: {}", product_id);
        let product = self.client.get_product(&product_id.to_string()).await?;
        
        // Cache the product
        self.cache.insert(product.id, product.clone());
        
        Ok(product)
    }

    pub async fn list_products(&self, page: Option<u32>, limit: Option<u32>) -> Result<Vec<Product>> {
        info!("Listing products - page: {:?}, limit: {:?}", page, limit);
        
        let products = self.client.list_products(page, limit).await?;
        
        info!("Retrieved {} products", products.len());
        Ok(products)
    }

    pub async fn update_product(&mut self, product_id: Uuid, product_data: ProductUpdate) -> Result<Product> {
        info!("Updating product: {}", product_id);
        
        let product = self.client.update_product(&product_id.to_string(), &product_data).await?;
        
        // Update cache
        self.cache.insert(product.id, product.clone());
        
        info!("Product updated successfully: {}", product_id);
        Ok(product)
    }

    pub async fn delete_product(&mut self, product_id: Uuid) -> Result<()> {
        info!("Deleting product: {}", product_id);
        
        self.client.delete_product(&product_id.to_string()).await?;
        
        // Remove from cache
        self.cache.remove(&product_id);
        
        info!("Product deleted successfully: {}", product_id);
        Ok(())
    }

    pub fn get_cached_product(&self, product_id: Uuid) -> Option<&Product> {
        self.cache.get(&product_id)
    }

    pub fn clear_cache(&mut self) {
        self.cache.clear();
        info!("Product cache cleared");
    }
}

pub struct PaymentService {
    client: V402Client,
    payment_history: HashMap<String, PaymentResponse>,
}

impl PaymentService {
    pub fn new(client: V402Client) -> Self {
        Self {
            client,
            payment_history: HashMap::new(),
        }
    }

    pub async fn process_payment(&mut self, payment_request: PaymentRequest) -> Result<PaymentResponse> {
        info!("Processing payment for product: {}", payment_request.product_id);
        
        let payment_response = self.client.process_payment(&payment_request).await?;
        
        // Store in history
        self.payment_history.insert(
            payment_response.transaction_hash.clone(),
            payment_response.clone()
        );
        
        info!("Payment processed successfully: {}", payment_response.transaction_hash);
        Ok(payment_response)
    }

    pub async fn get_payment(&self, transaction_hash: &str) -> Result<PaymentResponse> {
        // Check history first
        if let Some(payment) = self.payment_history.get(transaction_hash) {
            info!("Payment found in history: {}", transaction_hash);
            return Ok(payment.clone());
        }

        info!("Fetching payment from API: {}", transaction_hash);
        let payment = self.client.get_payment(transaction_hash).await?;
        
        Ok(payment)
    }

    pub fn get_payment_history(&self) -> Vec<PaymentResponse> {
        self.payment_history.values().cloned().collect()
    }

    pub fn clear_history(&mut self) {
        self.payment_history.clear();
        info!("Payment history cleared");
    }
}

pub struct AccessService {
    client: V402Client,
    access_cache: HashMap<(Uuid, String), AccessResponse>,
}

impl AccessService {
    pub fn new(client: V402Client) -> Self {
        Self {
            client,
            access_cache: HashMap::new(),
        }
    }

    pub async fn check_access(&mut self, access_request: AccessRequest) -> Result<AccessResponse> {
        let cache_key = (access_request.product_id, access_request.user_address.clone());
        
        // Check cache first
        if let Some(access_response) = self.access_cache.get(&cache_key) {
            info!("Access check found in cache for product: {}, user: {}", 
                  access_request.product_id, access_request.user_address);
            return Ok(access_response.clone());
        }

        info!("Checking access for product: {}, user: {}", 
              access_request.product_id, access_request.user_address);
        
        let access_response = self.client.check_access(&access_request).await?;
        
        // Cache the response
        self.access_cache.insert(cache_key, access_response.clone());
        
        Ok(access_response)
    }

    pub fn clear_cache(&mut self) {
        self.access_cache.clear();
        info!("Access cache cleared");
    }
}

pub struct AnalyticsService {
    client: V402Client,
    analytics_cache: HashMap<String, AnalyticsResponse>,
}

impl AnalyticsService {
    pub fn new(client: V402Client) -> Self {
        Self {
            client,
            analytics_cache: HashMap::new(),
        }
    }

    pub async fn get_analytics(&mut self, analytics_request: AnalyticsRequest) -> Result<AnalyticsResponse> {
        let cache_key = format!("{:?}", analytics_request);
        
        // Check cache first
        if let Some(analytics) = self.analytics_cache.get(&cache_key) {
            info!("Analytics found in cache");
            return Ok(analytics.clone());
        }

        info!("Fetching analytics from API");
        let analytics = self.client.get_analytics(&analytics_request).await?;
        
        // Cache the response
        self.analytics_cache.insert(cache_key, analytics.clone());
        
        Ok(analytics)
    }

    pub fn clear_cache(&mut self) {
        self.analytics_cache.clear();
        info!("Analytics cache cleared");
    }
}

pub struct HealthService {
    client: V402Client,
    last_check: Option<DateTime<Utc>>,
    health_status: Option<HealthCheck>,
}

impl HealthService {
    pub fn new(client: V402Client) -> Self {
        Self {
            client,
            last_check: None,
            health_status: None,
        }
    }

    pub async fn check_health(&mut self) -> Result<HealthCheck> {
        info!("Performing health check");
        
        let health = self.client.health_check().await?;
        
        self.last_check = Some(Utc::now());
        self.health_status = Some(health.clone());
        
        info!("Health check completed: {}", health.status);
        Ok(health)
    }

    pub fn get_last_health_status(&self) -> Option<&HealthCheck> {
        self.health_status.as_ref()
    }

    pub fn get_last_check_time(&self) -> Option<DateTime<Utc>> {
        self.last_check
    }
}
