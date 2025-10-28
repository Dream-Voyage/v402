use anyhow::Result;
use reqwest::Client;
use serde_json::json;
use std::time::Duration;
use tracing::{info, error};

use crate::models::*;
use crate::config::Config;

pub struct V402Client {
    client: Client,
    config: Config,
}

impl V402Client {
    pub fn new(config: Config) -> Result<Self> {
        let client = Client::builder()
            .timeout(Duration::from_secs(config.timeout))
            .build()?;

        Ok(Self { client, config })
    }

    pub async fn create_product(&self, product: &ProductCreate) -> Result<Product> {
        let url = format!("{}/api/v1/products", self.config.base_url);
        
        let response = self.client
            .post(&url)
            .json(product)
            .send()
            .await?;

        if !response.status().is_success() {
            let error_text = response.text().await?;
            return Err(anyhow::anyhow!("Failed to create product: {}", error_text));
        }

        let product: Product = response.json().await?;
        info!("Created product: {}", product.id);
        Ok(product)
    }

    pub async fn get_product(&self, product_id: &str) -> Result<Product> {
        let url = format!("{}/api/v1/products/{}", self.config.base_url, product_id);
        
        let response = self.client
            .get(&url)
            .send()
            .await?;

        if !response.status().is_success() {
            let error_text = response.text().await?;
            return Err(anyhow::anyhow!("Failed to get product: {}", error_text));
        }

        let product: Product = response.json().await?;
        Ok(product)
    }

    pub async fn list_products(&self, page: Option<u32>, limit: Option<u32>) -> Result<Vec<Product>> {
        let mut url = format!("{}/api/v1/products", self.config.base_url);
        
        if let Some(page) = page {
            url.push_str(&format!("?page={}", page));
        }
        if let Some(limit) = limit {
            let separator = if url.contains('?') { "&" } else { "?" };
            url.push_str(&format!("{}limit={}", separator, limit));
        }

        let response = self.client
            .get(&url)
            .send()
            .await?;

        if !response.status().is_success() {
            let error_text = response.text().await?;
            return Err(anyhow::anyhow!("Failed to list products: {}", error_text));
        }

        let products: Vec<Product> = response.json().await?;
        Ok(products)
    }

    pub async fn update_product(&self, product_id: &str, product: &ProductUpdate) -> Result<Product> {
        let url = format!("{}/api/v1/products/{}", self.config.base_url, product_id);
        
        let response = self.client
            .put(&url)
            .json(product)
            .send()
            .await?;

        if !response.status().is_success() {
            let error_text = response.text().await?;
            return Err(anyhow::anyhow!("Failed to update product: {}", error_text));
        }

        let product: Product = response.json().await?;
        info!("Updated product: {}", product.id);
        Ok(product)
    }

    pub async fn delete_product(&self, product_id: &str) -> Result<()> {
        let url = format!("{}/api/v1/products/{}", self.config.base_url, product_id);
        
        let response = self.client
            .delete(&url)
            .send()
            .await?;

        if !response.status().is_success() {
            let error_text = response.text().await?;
            return Err(anyhow::anyhow!("Failed to delete product: {}", error_text));
        }

        info!("Deleted product: {}", product_id);
        Ok(())
    }

    pub async fn process_payment(&self, payment: &PaymentRequest) -> Result<PaymentResponse> {
        let url = format!("{}/api/v1/payments", self.config.base_url);
        
        let response = self.client
            .post(&url)
            .json(payment)
            .send()
            .await?;

        if !response.status().is_success() {
            let error_text = response.text().await?;
            return Err(anyhow::anyhow!("Failed to process payment: {}", error_text));
        }

        let payment_response: PaymentResponse = response.json().await?;
        info!("Processed payment: {}", payment_response.transaction_hash);
        Ok(payment_response)
    }

    pub async fn get_payment(&self, transaction_hash: &str) -> Result<PaymentResponse> {
        let url = format!("{}/api/v1/payments/{}", self.config.base_url, transaction_hash);
        
        let response = self.client
            .get(&url)
            .send()
            .await?;

        if !response.status().is_success() {
            let error_text = response.text().await?;
            return Err(anyhow::anyhow!("Failed to get payment: {}", error_text));
        }

        let payment: PaymentResponse = response.json().await?;
        Ok(payment)
    }

    pub async fn check_access(&self, access_request: &AccessRequest) -> Result<AccessResponse> {
        let url = format!("{}/api/v1/access/check", self.config.base_url);
        
        let response = self.client
            .post(&url)
            .json(access_request)
            .send()
            .await?;

        if !response.status().is_success() {
            let error_text = response.text().await?;
            return Err(anyhow::anyhow!("Failed to check access: {}", error_text));
        }

        let access_response: AccessResponse = response.json().await?;
        Ok(access_response)
    }

    pub async fn get_analytics(&self, analytics_request: &AnalyticsRequest) -> Result<AnalyticsResponse> {
        let url = format!("{}/api/v1/analytics", self.config.base_url);
        
        let response = self.client
            .post(&url)
            .json(analytics_request)
            .send()
            .await?;

        if !response.status().is_success() {
            let error_text = response.text().await?;
            return Err(anyhow::anyhow!("Failed to get analytics: {}", error_text));
        }

        let analytics: AnalyticsResponse = response.json().await?;
        Ok(analytics)
    }

    pub async fn health_check(&self) -> Result<HealthCheck> {
        let url = format!("{}/health", self.config.base_url);
        
        let response = self.client
            .get(&url)
            .send()
            .await?;

        if !response.status().is_success() {
            let error_text = response.text().await?;
            return Err(anyhow::anyhow!("Failed to check health: {}", error_text));
        }

        let health: HealthCheck = response.json().await?;
        Ok(health)
    }
}
