use axum::{
    extract::{Path, Query, State},
    http::StatusCode,
    response::Json,
    routing::{get, post, put, delete},
    Router,
};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::sync::Arc;
use tokio::sync::RwLock;
use tower::ServiceBuilder;
use tower_http::{cors::CorsLayer, trace::TraceLayer};
use tracing::{info, error};
use uuid::Uuid;
use chrono::{DateTime, Utc};

use crate::models::*;
use crate::services::*;
use crate::config::Config;

// Application state
#[derive(Clone)]
pub struct AppState {
    pub product_service: Arc<RwLock<ProductService>>,
    pub payment_service: Arc<RwLock<PaymentService>>,
    pub access_service: Arc<RwLock<AccessService>>,
    pub analytics_service: Arc<RwLock<AnalyticsService>>,
    pub health_service: Arc<RwLock<HealthService>>,
}

// Query parameters for pagination
#[derive(Debug, Deserialize)]
pub struct PaginationQuery {
    pub page: Option<u32>,
    pub limit: Option<u32>,
}

// Query parameters for product filtering
#[derive(Debug, Deserialize)]
pub struct ProductFilterQuery {
    pub page: Option<u32>,
    pub limit: Option<u32>,
    pub category: Option<String>,
    pub status: Option<String>,
    pub search: Option<String>,
}

// Product handlers
pub async fn create_product(
    State(state): State<AppState>,
    Json(payload): Json<ProductCreate>,
) -> Result<Json<Product>, StatusCode> {
    info!("Creating product: {}", payload.title);
    
    let mut product_service = state.product_service.write().await;
    match product_service.create_product(payload).await {
        Ok(product) => {
            info!("Product created successfully: {}", product.id);
            Ok(Json(product))
        }
        Err(e) => {
            error!("Failed to create product: {}", e);
            Err(StatusCode::INTERNAL_SERVER_ERROR)
        }
    }
}

pub async fn get_product(
    State(state): State<AppState>,
    Path(product_id): Path<Uuid>,
) -> Result<Json<Product>, StatusCode> {
    info!("Getting product: {}", product_id);
    
    let mut product_service = state.product_service.read().await;
    match product_service.get_product(product_id).await {
        Ok(product) => {
            info!("Product retrieved successfully: {}", product_id);
            Ok(Json(product))
        }
        Err(e) => {
            error!("Failed to get product: {}", e);
            Err(StatusCode::NOT_FOUND)
        }
    }
}

pub async fn list_products(
    State(state): State<AppState>,
    Query(params): Query<ProductFilterQuery>,
) -> Result<Json<Vec<Product>>, StatusCode> {
    info!("Listing products - page: {:?}, limit: {:?}", params.page, params.limit);
    
    let product_service = state.product_service.read().await;
    match product_service.list_products(params.page, params.limit).await {
        Ok(products) => {
            info!("Retrieved {} products", products.len());
            Ok(Json(products))
        }
        Err(e) => {
            error!("Failed to list products: {}", e);
            Err(StatusCode::INTERNAL_SERVER_ERROR)
        }
    }
}

pub async fn update_product(
    State(state): State<AppState>,
    Path(product_id): Path<Uuid>,
    Json(payload): Json<ProductUpdate>,
) -> Result<Json<Product>, StatusCode> {
    info!("Updating product: {}", product_id);
    
    let mut product_service = state.product_service.write().await;
    match product_service.update_product(product_id, payload).await {
        Ok(product) => {
            info!("Product updated successfully: {}", product_id);
            Ok(Json(product))
        }
        Err(e) => {
            error!("Failed to update product: {}", e);
            Err(StatusCode::INTERNAL_SERVER_ERROR)
        }
    }
}

pub async fn delete_product(
    State(state): State<AppState>,
    Path(product_id): Path<Uuid>,
) -> Result<StatusCode, StatusCode> {
    info!("Deleting product: {}", product_id);
    
    let mut product_service = state.product_service.write().await;
    match product_service.delete_product(product_id).await {
        Ok(_) => {
            info!("Product deleted successfully: {}", product_id);
            Ok(StatusCode::NO_CONTENT)
        }
        Err(e) => {
            error!("Failed to delete product: {}", e);
            Err(StatusCode::INTERNAL_SERVER_ERROR)
        }
    }
}

// Payment handlers
pub async fn process_payment(
    State(state): State<AppState>,
    Json(payload): Json<PaymentRequest>,
) -> Result<Json<PaymentResponse>, StatusCode> {
    info!("Processing payment for product: {}", payload.product_id);
    
    let mut payment_service = state.payment_service.write().await;
    match payment_service.process_payment(payload).await {
        Ok(payment_response) => {
            info!("Payment processed successfully: {}", payment_response.transaction_hash);
            Ok(Json(payment_response))
        }
        Err(e) => {
            error!("Failed to process payment: {}", e);
            Err(StatusCode::INTERNAL_SERVER_ERROR)
        }
    }
}

pub async fn get_payment(
    State(state): State<AppState>,
    Path(transaction_hash): Path<String>,
) -> Result<Json<PaymentResponse>, StatusCode> {
    info!("Getting payment: {}", transaction_hash);
    
    let payment_service = state.payment_service.read().await;
    match payment_service.get_payment(&transaction_hash).await {
        Ok(payment) => {
            info!("Payment retrieved successfully: {}", transaction_hash);
            Ok(Json(payment))
        }
        Err(e) => {
            error!("Failed to get payment: {}", e);
            Err(StatusCode::NOT_FOUND)
        }
    }
}

// Access handlers
pub async fn check_access(
    State(state): State<AppState>,
    Json(payload): Json<AccessRequest>,
) -> Result<Json<AccessResponse>, StatusCode> {
    info!("Checking access for product: {}, user: {}", payload.product_id, payload.user_address);
    
    let mut access_service = state.access_service.write().await;
    match access_service.check_access(payload).await {
        Ok(access_response) => {
            info!("Access check completed");
            Ok(Json(access_response))
        }
        Err(e) => {
            error!("Failed to check access: {}", e);
            Err(StatusCode::INTERNAL_SERVER_ERROR)
        }
    }
}

// Analytics handlers
pub async fn get_analytics(
    State(state): State<AppState>,
    Json(payload): Json<AnalyticsRequest>,
) -> Result<Json<AnalyticsResponse>, StatusCode> {
    info!("Getting analytics");
    
    let mut analytics_service = state.analytics_service.write().await;
    match analytics_service.get_analytics(payload).await {
        Ok(analytics) => {
            info!("Analytics retrieved successfully");
            Ok(Json(analytics))
        }
        Err(e) => {
            error!("Failed to get analytics: {}", e);
            Err(StatusCode::INTERNAL_SERVER_ERROR)
        }
    }
}

// Health check handler
pub async fn health_check(
    State(state): State<AppState>,
) -> Result<Json<HealthCheck>, StatusCode> {
    info!("Performing health check");
    
    let mut health_service = state.health_service.write().await;
    match health_service.check_health().await {
        Ok(health) => {
            info!("Health check successful: {}", health.status);
            Ok(Json(health))
        }
        Err(e) => {
            error!("Health check failed: {}", e);
            Err(StatusCode::SERVICE_UNAVAILABLE)
        }
    }
}

// Statistics handler
pub async fn get_statistics(
    State(state): State<AppState>,
) -> Result<Json<serde_json::Value>, StatusCode> {
    info!("Getting service statistics");
    
    let product_service = state.product_service.read().await;
    let payment_service = state.payment_service.read().await;
    let access_service = state.access_service.read().await;
    let analytics_service = state.analytics_service.read().await;
    
    let stats = serde_json::json!({
        "cached_products": product_service.cache.len(),
        "payment_history_entries": payment_service.payment_history.len(),
        "cached_access_checks": access_service.access_cache.len(),
        "cached_analytics": analytics_service.analytics_cache.len(),
        "timestamp": Utc::now()
    });
    
    Ok(Json(stats))
}

// Create the application router
pub fn create_app(state: AppState) -> Router {
    Router::new()
        // Product routes
        .route("/api/v1/products", post(create_product))
        .route("/api/v1/products", get(list_products))
        .route("/api/v1/products/:id", get(get_product))
        .route("/api/v1/products/:id", put(update_product))
        .route("/api/v1/products/:id", delete(delete_product))
        
        // Payment routes
        .route("/api/v1/payments", post(process_payment))
        .route("/api/v1/payments/:transaction_hash", get(get_payment))
        
        // Access routes
        .route("/api/v1/access/check", post(check_access))
        
        // Analytics routes
        .route("/api/v1/analytics", post(get_analytics))
        
        // System routes
        .route("/health", get(health_check))
        .route("/statistics", get(get_statistics))
        
        // Add middleware
        .layer(
            ServiceBuilder::new()
                .layer(TraceLayer::new_for_http())
                .layer(CorsLayer::permissive())
        )
        .with_state(state)
}
