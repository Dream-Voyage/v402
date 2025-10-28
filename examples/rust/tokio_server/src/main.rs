use anyhow::Result;
use axum::Router;
use std::net::SocketAddr;
use tokio::net::TcpListener;
use tracing::{info, error};

use crate::config::Config;
use crate::client::V402Client;
use crate::services::*;
use crate::handlers::{create_app, AppState};

pub struct Server {
    config: Config,
    state: AppState,
}

impl Server {
    pub fn new(config: Config) -> Result<Self> {
        // Create v402 client
        let client = V402Client::new(config.clone())?;
        
        // Create services
        let product_service = Arc::new(RwLock::new(ProductService::new(client.clone())));
        let payment_service = Arc::new(RwLock::new(PaymentService::new(client.clone())));
        let access_service = Arc::new(RwLock::new(AccessService::new(client.clone())));
        let analytics_service = Arc::new(RwLock::new(AnalyticsService::new(client.clone())));
        let health_service = Arc::new(RwLock::new(HealthService::new(client)));

        let state = AppState {
            product_service,
            payment_service,
            access_service,
            analytics_service,
            health_service,
        };

        Ok(Self { config, state })
    }

    pub async fn run(&self) -> Result<()> {
        // Create the application router
        let app = create_app(self.state.clone());

        // Create the address to bind to
        let addr = SocketAddr::from(([0, 0, 0, 0], self.config.server_port));
        
        info!("Starting server on {}", addr);

        // Create the TCP listener
        let listener = TcpListener::bind(addr).await?;
        
        info!("Server listening on {}", addr);

        // Start the server
        axum::serve(listener, app).await?;

        Ok(())
    }

    pub async fn run_with_graceful_shutdown(&self) -> Result<()> {
        // Create the application router
        let app = create_app(self.state.clone());

        // Create the address to bind to
        let addr = SocketAddr::from(([0, 0, 0, 0], self.config.server_port));
        
        info!("Starting server with graceful shutdown on {}", addr);

        // Create the TCP listener
        let listener = TcpListener::bind(addr).await?;
        
        info!("Server listening on {}", addr);

        // Handle graceful shutdown
        let shutdown_signal = async {
            tokio::signal::ctrl_c()
                .await
                .expect("Failed to install CTRL+C signal handler");
            info!("Received CTRL+C signal, starting graceful shutdown");
        };

        // Start the server with graceful shutdown
        axum::serve(listener, app)
            .with_graceful_shutdown(shutdown_signal)
            .await?;

        info!("Server shutdown complete");
        Ok(())
    }
}

#[tokio::main]
async fn main() -> Result<()> {
    // Initialize tracing
    tracing_subscriber::fmt::init();

    info!("Starting v402 Rust Tokio server");

    // Load configuration
    let config = Config::from_env().unwrap_or_default();
    
    // Validate configuration
    if let Err(e) = config.validate() {
        error!("Configuration validation failed: {}", e);
        return Err(anyhow::anyhow!("Invalid configuration: {}", e));
    }

    info!("Configuration loaded successfully");
    info!("Base URL: {}", config.base_url);
    info!("Server port: {}", config.server_port);
    info!("Timeout: {}s", config.timeout);

    // Create and run the server
    let server = Server::new(config)?;
    
    // Run with graceful shutdown
    if let Err(e) = server.run_with_graceful_shutdown().await {
        error!("Server error: {}", e);
        return Err(e);
    }

    info!("Server stopped");
    Ok(())
}
