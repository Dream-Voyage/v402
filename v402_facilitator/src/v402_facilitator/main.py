"""
Main FastAPI application for v402 Facilitator.

This module defines the REST API endpoints for payment verification,
settlement, and resource discovery.
"""

import json
import logging
import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional

# Add x402 to path for local import
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../x402/src"))

from x402.types import PaymentPayload, PaymentRequirements

from v402_facilitator.config import settings
from v402_facilitator.types import (
    VerifyRequest,
    VerifyResponseModel,
    SettleRequest,
    SettleResponseModel,
    SupportedResponse,
    SupportedKind,
    DiscoveryResponse,
    DiscoveryPagination,
    DiscoveryResource,
)
from v402_facilitator.verification import PaymentVerifier
from v402_facilitator.settlement import SettlementEngine
from v402_facilitator.database import DatabaseManager

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Global instances
db_manager: Optional[DatabaseManager] = None
payment_verifier: Optional[PaymentVerifier] = None
settlement_engine: Optional[SettlementEngine] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.

    Handles startup and shutdown of database connections and
    blockchain clients.
    """
    global db_manager, payment_verifier, settlement_engine

    logger.info("Starting v402 Facilitator...")

    # Initialize database
    db_manager = DatabaseManager(settings.database_url)
    await db_manager.init_db()

    # Initialize payment verifier
    payment_verifier = PaymentVerifier()

    # Initialize settlement engine
    if settings.rpc_url and settings.private_key:
        settlement_engine = SettlementEngine(
            rpc_url=settings.rpc_url,
            private_key=settings.private_key,
            chain_id=settings.chain_id,
        )
        logger.info("Settlement engine initialized")
    else:
        logger.warning(
            "Settlement engine not initialized - RPC_URL or PRIVATE_KEY missing"
        )

    logger.info(f"v402 Facilitator started on {settings.network}")

    yield

    # Cleanup
    logger.info("Shutting down v402 Facilitator...")
    if db_manager:
        await db_manager.close()


# Create FastAPI app
app = FastAPI(
    title="v402 Facilitator",
    description="Backend settlement service for x402 payments",
    version="0.1.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency to get database manager
def get_db() -> DatabaseManager:
    """Get database manager instance."""
    if db_manager is None:
        raise HTTPException(status_code=500, detail="Database not initialized")
    return db_manager


# Dependency to get payment verifier
def get_verifier() -> PaymentVerifier:
    """Get payment verifier instance."""
    if payment_verifier is None:
        raise HTTPException(status_code=500, detail="Verifier not initialized")
    return payment_verifier


# Dependency to get settlement engine
def get_settlement() -> SettlementEngine:
    """Get settlement engine instance."""
    if settlement_engine is None:
        raise HTTPException(status_code=503, detail="Settlement engine not available")
    return settlement_engine


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "v402 Facilitator",
        "version": "0.1.0",
        "network": settings.network,
        "status": "operational",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "network": settings.network,
        "database": "connected" if db_manager else "disconnected",
        "settlement": "available" if settlement_engine else "unavailable",
    }


@app.post("/verify", response_model=VerifyResponseModel)
async def verify_payment(
    request: VerifyRequest,
    verifier: PaymentVerifier = Depends(get_verifier),
):
    """
    Verify a payment signature and authorization.

    This endpoint verifies that:
    - The payment signature is cryptographically valid
    - The payment amount matches requirements
    - The payment is within valid time window
    - The payment hasn't been used before (nonce check)

    Args:
        request: Verification request containing payment payload and requirements

    Returns:
        Verification response with validity status and payer address
    """
    try:
        logger.info(f"Verifying payment for resource: {request.payment_requirements.get('resource')}")

        # Parse payment payload and requirements
        payment_payload = PaymentPayload(**request.payment_payload)
        payment_requirements = PaymentRequirements(**request.payment_requirements)

        # Verify payment
        is_valid, error_reason, payer = await verifier.verify_payment(
            payment_payload, payment_requirements
        )

        response = VerifyResponseModel(
            is_valid=is_valid,
            invalid_reason=error_reason,
            payer=payer,
        )

        logger.info(
            f"Verification result: valid={is_valid}, payer={payer}, "
            f"reason={error_reason}"
        )

        return response

    except Exception as e:
        logger.error(f"Verification error: {e}")
        return VerifyResponseModel(
            is_valid=False,
            invalid_reason=str(e),
            payer=None,
        )


@app.post("/settle", response_model=SettleResponseModel)
async def settle_payment(
    request: SettleRequest,
    verifier: PaymentVerifier = Depends(get_verifier),
    settlement: SettlementEngine = Depends(get_settlement),
    db: DatabaseManager = Depends(get_db),
):
    """
    Settle a payment on-chain.

    This endpoint:
    1. Verifies the payment is valid
    2. Submits the payment transaction to blockchain
    3. Waits for transaction confirmation
    4. Records the transaction in database

    Args:
        request: Settlement request containing payment payload and requirements

    Returns:
        Settlement response with transaction details
    """
    try:
        logger.info(f"Settling payment for resource: {request.payment_requirements.get('resource')}")

        # Parse payment payload and requirements
        payment_payload = PaymentPayload(**request.payment_payload)
        payment_requirements = PaymentRequirements(**request.payment_requirements)

        # Verify payment first
        is_valid, error_reason, payer = await verifier.verify_payment(
            payment_payload, payment_requirements
        )

        if not is_valid:
            return SettleResponseModel(
                success=False,
                error_reason=f"Payment verification failed: {error_reason}",
                transaction=None,
                network=None,
                payer=payer,
            )

        # Settle payment on-chain
        success, tx_hash, error_msg = await settlement.settle_payment(
            payment_payload, payment_requirements, payer
        )

        if success and tx_hash:
            # Record transaction in database
            await db.create_transaction(
                transaction_hash=tx_hash,
                payer=payer,
                payee=payment_requirements.pay_to,
                amount=payment_requirements.max_amount_required,
                network=settings.network,
                scheme=payment_payload.scheme,
                resource=payment_requirements.resource,
                status="confirmed",
            )

            logger.info(f"Payment settled successfully: {tx_hash}")

            return SettleResponseModel(
                success=True,
                error_reason=None,
                transaction=tx_hash,
                network=settings.network,
                payer=payer,
            )
        else:
            logger.error(f"Settlement failed: {error_msg}")
            return SettleResponseModel(
                success=False,
                error_reason=error_msg,
                transaction=None,
                network=settings.network,
                payer=payer,
            )

    except Exception as e:
        logger.error(f"Settlement error: {e}")
        return SettleResponseModel(
            success=False,
            error_reason=str(e),
            transaction=None,
            network=None,
            payer=None,
        )


@app.get("/supported", response_model=SupportedResponse)
async def get_supported():
    """
    Get supported payment schemes and networks.

    Returns list of (scheme, network) pairs that this facilitator supports.
    """
    kinds = []

    for scheme in settings.supported_schemes:
        kinds.append(SupportedKind(scheme=scheme, network=settings.network))

    return SupportedResponse(kinds=kinds)


@app.get("/discovery/resources", response_model=DiscoveryResponse)
async def discover_resources(
    type: Optional[str] = None,
    limit: int = 10,
    offset: int = 0,
    db: DatabaseManager = Depends(get_db),
):
    """
    Discover available paid resources.

    This endpoint allows AI platforms to discover what paid content
    is available through this facilitator.

    Args:
        type: Filter by resource type (e.g., "http")
        limit: Maximum results per page
        offset: Pagination offset

    Returns:
        List of discoverable resources with pagination info
    """
    try:
        # Get resources from database
        resources, total = await db.get_discovery_resources(
            type_filter=type, limit=limit, offset=offset
        )

        # Convert to response format
        items = []
        for resource in resources:
            items.append(
                DiscoveryResource(
                    resource=resource.resource,
                    type=resource.type,
                    x402_version=resource.x402_version,
                    accepts=json.loads(resource.accepts),
                    last_updated=resource.last_updated,
                    metadata=json.loads(resource.metadata)
                    if resource.metadata
                    else None,
                )
            )

        pagination = DiscoveryPagination(
            limit=limit,
            offset=offset,
            total=total,
        )

        return DiscoveryResponse(
            x402_version=settings.x402_version,
            items=items,
            pagination=pagination,
        )

    except Exception as e:
        logger.error(f"Discovery error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/discovery/resources")
async def register_resource(
    request: Request,
    db: DatabaseManager = Depends(get_db),
):
    """
    Register a new resource for discovery.

    Content providers can register their resources here so AI platforms
    can discover them.

    Args:
        request: Resource registration request

    Returns:
        Success status
    """
    try:
        data = await request.json()

        resource = data.get("resource")
        accepts = data.get("accepts")
        metadata = data.get("metadata")

        if not resource or not accepts:
            raise HTTPException(status_code=400, detail="Missing required fields")

        # Store in database
        await db.create_discovery_resource(
            resource=resource,
            accepts=json.dumps(accepts),
            metadata=json.dumps(metadata) if metadata else None,
        )

        logger.info(f"Resource registered: {resource}")

        return {"success": True, "resource": resource}

    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)},
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "v402_facilitator.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        workers=settings.workers,
    )

