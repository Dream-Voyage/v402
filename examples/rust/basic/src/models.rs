use serde::{Deserialize, Serialize};
use uuid::Uuid;
use chrono::{DateTime, Utc};
use validator::Validate;

#[derive(Debug, Clone, Serialize, Deserialize, Validate)]
pub struct Product {
    pub id: Uuid,
    #[validate(length(min = 1, max = 200))]
    pub title: String,
    #[validate(length(min = 1, max = 1000))]
    pub description: String,
    #[validate(regex = "PRICE_REGEX")]
    pub price: String,
    #[validate(length(max = 10))]
    pub currency: String,
    #[validate(url)]
    pub content_url: String,
    #[validate(length(max = 50))]
    pub category: Option<String>,
    pub tags: Vec<String>,
    #[validate(length(max = 100))]
    pub author: Option<String>,
    pub status: ProductStatus,
    pub view_count: u64,
    pub purchase_count: u64,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ProductStatus {
    Active,
    Inactive,
    Draft,
}

#[derive(Debug, Clone, Serialize, Deserialize, Validate)]
pub struct ProductCreate {
    #[validate(length(min = 1, max = 200))]
    pub title: String,
    #[validate(length(min = 1, max = 1000))]
    pub description: String,
    #[validate(regex = "PRICE_REGEX")]
    pub price: String,
    #[validate(length(max = 10))]
    pub currency: String,
    #[validate(url)]
    pub content_url: String,
    #[validate(length(max = 50))]
    pub category: Option<String>,
    pub tags: Vec<String>,
    #[validate(length(max = 100))]
    pub author: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, Validate)]
pub struct ProductUpdate {
    #[validate(length(min = 1, max = 200))]
    pub title: Option<String>,
    #[validate(length(min = 1, max = 1000))]
    pub description: Option<String>,
    #[validate(regex = "PRICE_REGEX")]
    pub price: Option<String>,
    #[validate(length(max = 10))]
    pub currency: Option<String>,
    #[validate(url)]
    pub content_url: Option<String>,
    #[validate(length(max = 50))]
    pub category: Option<String>,
    pub tags: Option<Vec<String>>,
    #[validate(length(max = 100))]
    pub author: Option<String>,
    pub status: Option<ProductStatus>,
}

#[derive(Debug, Clone, Serialize, Deserialize, Validate)]
pub struct PaymentRequest {
    pub product_id: Uuid,
    #[validate(regex = "PRICE_REGEX")]
    pub amount: String,
    #[validate(length(max = 10))]
    pub currency: String,
    #[validate(regex = "ETH_ADDRESS_REGEX")]
    pub user_address: String,
    #[validate(length(min = 1, max = 100))]
    pub nonce: String,
    #[validate(length(min = 1, max = 200))]
    pub signature: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PaymentResponse {
    pub transaction_hash: String,
    pub status: PaymentStatus,
    pub amount: String,
    pub currency: String,
    pub timestamp: DateTime<Utc>,
    pub block_number: Option<u64>,
    pub gas_used: Option<u64>,
    pub error: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum PaymentStatus {
    Pending,
    Completed,
    Failed,
    Refunded,
}

#[derive(Debug, Clone, Serialize, Deserialize, Validate)]
pub struct AccessRequest {
    pub product_id: Uuid,
    #[validate(regex = "ETH_ADDRESS_REGEX")]
    pub user_address: String,
    pub timestamp: i64,
    #[validate(length(min = 1, max = 200))]
    pub signature: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AccessResponse {
    pub has_access: bool,
    pub reason: Option<String>,
    pub expires_at: Option<i64>,
}

#[derive(Debug, Clone, Serialize, Deserialize, Validate)]
pub struct AnalyticsRequest {
    pub product_id: Option<Uuid>,
    pub start_date: Option<DateTime<Utc>>,
    pub end_date: Option<DateTime<Utc>>,
    pub period: PeriodType,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AnalyticsResponse {
    pub product_id: Option<Uuid>,
    pub views: u64,
    pub purchases: u64,
    pub revenue: String,
    pub currency: String,
    pub period: PeriodType,
    pub generated_at: DateTime<Utc>,
    pub conversion_rate: f64,
    pub top_countries: Vec<CountryData>,
    pub top_referrers: Vec<ReferrerData>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum PeriodType {
    Hourly,
    Daily,
    Weekly,
    Monthly,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CountryData {
    pub code: String,
    pub name: String,
    pub count: u64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ReferrerData {
    pub domain: String,
    pub count: u64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct User {
    pub id: Uuid,
    pub public_key: String,
    pub username: Option<String>,
    pub email: Option<String>,
    pub is_verified: bool,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize, Validate)]
pub struct AccessLog {
    pub id: Uuid,
    pub product_id: Uuid,
    pub user_address: String,
    pub access_type: AccessType,
    pub ip_address: Option<String>,
    pub user_agent: Option<String>,
    pub referrer: Option<String>,
    pub country: Option<String>,
    pub created_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum AccessType {
    View,
    Purchase,
    Access,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ErrorResponse {
    pub error: String,
    pub detail: Option<String>,
    pub timestamp: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HealthCheck {
    pub status: String,
    pub timestamp: DateTime<Utc>,
    pub version: String,
    pub uptime: Option<f64>,
    pub database_status: Option<String>,
}

// Validation regex constants
lazy_static::lazy_static! {
    static ref PRICE_REGEX: regex::Regex = regex::Regex::new(r"^\d+\.\d{2}$").unwrap();
    static ref ETH_ADDRESS_REGEX: regex::Regex = regex::Regex::new(r"^0x[a-fA-F0-9]{40}$").unwrap();
}
