use serde::{Deserialize, Serialize};
use std::time::Duration;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Config {
    pub base_url: String,
    pub timeout: u64,
    pub retry_count: u32,
    pub public_key: String,
    pub private_key: String,
    pub chain_id: u64,
    pub rpc_url: String,
    pub contract_address: String,
    pub default_currency: String,
    pub gas_limit: u64,
    pub gas_price: String,
    pub log_level: String,
    pub enable_metrics: bool,
    pub metrics_port: u16,
    pub health_check: bool,
    pub server_port: u16,
}

impl Default for Config {
    fn default() -> Self {
        Self {
            base_url: "https://api.v402.network".to_string(),
            timeout: 30,
            retry_count: 3,
            public_key: "0x1234567890abcdef1234567890abcdef12345678".to_string(),
            private_key: "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890".to_string(),
            chain_id: 1, // Ethereum mainnet
            rpc_url: "https://mainnet.infura.io/v3/your-project-id".to_string(),
            contract_address: "0x1234567890abcdef1234567890abcdef12345678".to_string(),
            default_currency: "USDC".to_string(),
            gas_limit: 100000,
            gas_price: "20000000000".to_string(), // 20 gwei
            log_level: "info".to_string(),
            enable_metrics: true,
            metrics_port: 9090,
            health_check: true,
            server_port: 8080,
        }
    }
}

impl Config {
    pub fn from_env() -> Result<Self, config::ConfigError> {
        let mut settings = config::Config::default();
        
        // Start with default configuration
        settings.merge(config::Config::try_from(&Config::default())?)?;
        
        // Override with environment variables
        settings.merge(config::Environment::with_prefix("V402"))?;
        
        settings.try_into()
    }
    
    pub fn validate(&self) -> Result<(), String> {
        if self.base_url.is_empty() {
            return Err("Base URL cannot be empty".to_string());
        }
        
        if self.public_key.is_empty() {
            return Err("Public key cannot be empty".to_string());
        }
        
        if self.chain_id == 0 {
            return Err("Chain ID must be greater than 0".to_string());
        }
        
        if self.timeout == 0 {
            return Err("Timeout must be greater than 0".to_string());
        }
        
        if self.server_port == 0 {
            return Err("Server port must be greater than 0".to_string());
        }
        
        Ok(())
    }
    
    pub fn timeout_duration(&self) -> Duration {
        Duration::from_secs(self.timeout)
    }
}
