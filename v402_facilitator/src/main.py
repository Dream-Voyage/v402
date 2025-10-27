"""
v402 Facilitator - Main application entry point.

This is the main FastAPI application that provides the v402 payment facilitation service.
It implements the x402 protocol and provides comprehensive APIs for content providers
and index clients.
"""

import logging
import sys
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from pathlib import Path
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from api.v1 import admin, clients, providers
from core.config import get_settings
from core.database import init_db, close_db
from core.logging import setup_logging
from core.middleware import (
    RateLimitMiddleware, SecurityHeadersMiddleware, RequestLoggingMiddleware,
    MetricsMiddleware, ErrorHandlingMiddleware
)
from models.entities import APIErrorDTO, HealthCheckDTO


# Global settings
settings = get_settings()

# Setup logging
setup_logging(settings.monitoring.LOG_LEVEL, settings.monitoring.LOG_FORMAT)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.

    Handles startup and shutdown procedures including database initialization,
    connection pooling, and graceful cleanup.
    """
    logger.info("Starting v402 Facilitator...")

    try:
        # Initialize database connections
        await init_db()
        logger.info("Database connections established")

        # Initialize background tasks
        # TODO: Start background payment processing, webhook delivery, etc.

        if settings.STARTUP_BANNER:
            print_startup_banner()

        logger.info("v402 Facilitator started successfully")

        yield  # Application is running

    except Exception as e:
        logger.error(f"Startup failed: {e}", exc_info=True)
        raise
    finally:
        # Cleanup
        logger.info("Shutting down v402 Facilitator...")

        try:
            # Close database connections
            await close_db()
            logger.info("Database connections closed")

            # Stop background tasks
            # TODO: Cleanup background tasks

            logger.info("v402 Facilitator shutdown complete")

        except Exception as e:
            logger.error(f"Shutdown error: {e}", exc_info=True)


# Create FastAPI application
app = FastAPI(
    title=settings.api.DOCS_TITLE,
    description=settings.api.DOCS_DESCRIPTION,
    version=settings.APP_VERSION,
    docs_url=settings.api.DOCS_URL if not settings.is_production() else None,
    redoc_url=settings.api.REDOC_URL if not settings.is_production() else None,
    openapi_url=settings.api.OPENAPI_URL if not settings.is_production() else None,
    lifespan=lifespan,
)


# =============================================================================
# MIDDLEWARE CONFIGURATION
# =============================================================================

# Security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

# Trusted host middleware (production security)
if settings.is_production():
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["facilitator.v402.network", "*.v402.network"]
    )

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.security.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=settings.security.CORS_METHODS,
    allow_headers=settings.security.CORS_HEADERS,
)

# Compression middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Custom middleware (order matters - last added is executed first)
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(MetricsMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RateLimitMiddleware, requests_per_minute=settings.security.RATE_LIMIT_REQUESTS_PER_MINUTE)


# =============================================================================
# EXCEPTION HANDLERS
# =============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with structured error responses."""
    return JSONResponse(
        status_code=exc.status_code,
        content=APIErrorDTO(
            error=f"HTTP_{exc.status_code}",
            message=exc.detail,
            details=getattr(exc, "headers", None)
        ).dict()
    )


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """Handle value errors as 400 Bad Request."""
    logger.warning(f"Value error in {request.url}: {exc}")
    return JSONResponse(
        status_code=400,
        content=APIErrorDTO(
            error="VALIDATION_ERROR",
            message=str(exc)
        ).dict()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.error(f"Unhandled exception in {request.url}: {exc}", exc_info=True)

    if settings.DEBUG:
        # In debug mode, return detailed error information
        return JSONResponse(
            status_code=500,
            content=APIErrorDTO(
                error="INTERNAL_SERVER_ERROR",
                message=str(exc),
                details={"type": type(exc).__name__, "traceback": str(exc)}
            ).dict()
        )
    else:
        # In production, return generic error message
        return JSONResponse(
            status_code=500,
            content=APIErrorDTO(
                error="INTERNAL_SERVER_ERROR",
                message="An internal server error occurred"
            ).dict()
        )


# =============================================================================
# API ROUTES
# =============================================================================

# Include API version 1 routers
app.include_router(
    providers.router,
    prefix=settings.api.API_PREFIX,
    dependencies=[]
)

app.include_router(
    clients.router,
    prefix=settings.api.API_PREFIX,
    dependencies=[]
)

app.include_router(
    admin.router,
    prefix=settings.api.API_PREFIX,
    dependencies=[]
)


# =============================================================================
# CORE ENDPOINTS
# =============================================================================

@app.get("/", response_model=dict)
async def root():
    """
    Root endpoint with basic service information.
    """
    return {
        "service": "v402 Facilitator",
        "version": settings.APP_VERSION,
        "description": "Enterprise payment facilitation service for v402 protocol",
        "environment": settings.ENVIRONMENT,
        "documentation": f"{settings.api.DOCS_URL}" if settings.api.DOCS_URL else None,
        "api_version": settings.api.API_VERSION,
        "status": "operational"
    }


@app.get("/health", response_model=HealthCheckDTO)
async def health_check():
    """
    Health check endpoint for load balancers and monitoring systems.

    Returns comprehensive health status including:
    - Database connectivity
    - Redis cache status
    - External service dependencies
    - Resource utilization
    """
    try:
        from services.monitoring_service import MonitoringService
        from core.database import get_db

        # Get database session for health checks
        async for db in get_db():
            monitoring_service = MonitoringService(db)
            health_status = await monitoring_service.get_basic_health()
            break

        return health_status

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthCheckDTO(
            status="unhealthy",
            version=settings.APP_VERSION,
            timestamp=datetime.utcnow(),
            components={"error": str(e)},
            uptime=0
        )


@app.get("/metrics")
async def metrics():
    """
    Prometheus metrics endpoint.

    Returns metrics in Prometheus exposition format for monitoring and alerting.
    """
    if not settings.monitoring.METRICS_ENABLED:
        raise HTTPException(status_code=404, detail="Metrics endpoint disabled")

    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/version")
async def version():
    """
    Version information endpoint.
    """
    return {
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "build_timestamp": "2024-01-01T00:00:00Z",  # TODO: Add actual build timestamp
        "git_commit": "abcdef123456",  # TODO: Add actual git commit
        "api_version": settings.api.API_VERSION
    }


# =============================================================================
# X402 PROTOCOL ENDPOINTS
# =============================================================================

@app.options("/{path:path}")
async def handle_preflight(request: Request, path: str):
    """
    Handle CORS preflight requests for x402 protocol compatibility.
    """
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Payment",
            "Access-Control-Max-Age": "86400"
        }
    )


@app.get("/.well-known/x402")
async def x402_discovery():
    """
    x402 protocol discovery endpoint.

    Provides information about supported payment methods and facilitator capabilities.
    """
    return {
        "version": "1.0",
        "facilitator": {
            "name": "v402 Facilitator",
            "version": settings.APP_VERSION,
            "url": settings.api.API_PREFIX,
        },
        "supported_chains": settings.blockchain.SUPPORTED_CHAINS,
        "supported_schemes": ["exact", "upto", "dynamic"],
        "features": [
            "payment_verification",
            "multi_chain_support",
            "batch_payments",
            "webhooks",
            "analytics"
        ],
        "endpoints": {
            "discovery": f"{settings.api.API_PREFIX}/clients/discover",
            "payment": f"{settings.api.API_PREFIX}/clients/payments",
            "access": f"{settings.api.API_PREFIX}/clients/access"
        }
    }


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def print_startup_banner():
    """Print startup banner with service information."""
    banner = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                              v402 Facilitator                               ║
║                    Enterprise Payment Facilitation Service                  ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Version:     {settings.APP_VERSION:<20} Environment: {settings.ENVIRONMENT:<15} ║
║  Port:        {settings.api.PORT:<20} Workers:     {settings.api.WORKERS:<15} ║
║  Database:    PostgreSQL + Redis         Blockchain:  Multi-chain    ║
║  Monitoring:  {"Enabled" if settings.monitoring.METRICS_ENABLED else "Disabled":<20} Documentation: {"Enabled" if settings.api.DOCS_URL else "Disabled":<10} ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  API Endpoints:                                                              ║
║    • Content Providers: /api/v1/providers/*                                 ║
║    • Index Clients:     /api/v1/clients/*                                   ║
║    • Admin Panel:       /api/v1/admin/*                                     ║
║    • Health Check:      /health                                              ║
║    • Metrics:           /metrics                                             ║
║    • Documentation:     {settings.api.DOCS_URL or "Disabled":<50} ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Supported Chains: {", ".join(settings.blockchain.SUPPORTED_CHAINS):<57} ║
║  Protocol: x402 v1.0 + v402 Extensions                                      ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """
    print(banner)


# =============================================================================
# DEVELOPMENT SERVER
# =============================================================================

if __name__ == "__main__":
    # Development server configuration
    uvicorn.run(
        "main:app",
        host=settings.api.HOST,
        port=settings.api.PORT,
        reload=settings.api.RELOAD and settings.is_development(),
        workers=1 if settings.api.RELOAD else settings.api.WORKERS,
        log_level=settings.monitoring.LOG_LEVEL.lower(),
        access_log=settings.is_development(),
        use_colors=settings.is_development(),
        ssl_keyfile=settings.security.SSL_KEYFILE,
        ssl_certfile=settings.security.SSL_CERTFILE,
    )
