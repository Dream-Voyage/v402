"""
Index Client API endpoints.

This module provides API endpoints for index platforms, AI crawlers, and end users
to discover, access, and pay for content through the v402 protocol.
"""

import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import get_db
from src.core.security import get_current_user, get_optional_user
from src.models.entities import (
    ChainType, PaymentCreateDTO, PaymentResponseDTO, PaymentStatus,
    ProductResponseDTO, User
)
from src.services.analytics_service import AnalyticsService
from src.services.content_service import ContentService
from src.services.discovery_service import DiscoveryService
from src.services.payment_service import PaymentService
from typing import Any, Dict, List, Optional

router = APIRouter(prefix="/clients", tags=["Index Clients"])


# =============================================================================
# CONTENT DISCOVERY
# =============================================================================

@router.get("/discover", response_model=Dict[str, Any])
async def discover_content(
    query: Optional[str] = Query(None, description="Search query"),
    category: Optional[str] = Query(None, description="Content category"),
    content_type: Optional[str] = Query(None, description="Content type filter"),
    min_price: Optional[str] = Query(None, description="Minimum price in wei"),
    max_price: Optional[str] = Query(None, description="Maximum price in wei"),
    chain: Optional[ChainType] = Query(None, description="Preferred blockchain"),
    sort_by: str = Query("relevance", description="Sort by: relevance, price, rating, recent"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Discover available content for purchase.

    This endpoint allows AI platforms and index services to discover monetized content
    that can be accessed through v402 payments.

    **Query Parameters:**
    - query: Search text for content discovery
    - category: Filter by content category
    - content_type: Filter by MIME type or content type
    - min_price/max_price: Price range filter (in wei)
    - chain: Preferred blockchain for payment
    - sort_by: Sorting criteria (relevance, price, rating, recent)

    **Response:**
    Returns paginated list of available content with pricing and access information.

    **Rate Limiting:**
    - 100 requests per minute for authenticated users
    - 20 requests per minute for anonymous users
    """
    try:
        discovery_service = DiscoveryService(db)

        search_params = {
            "query": query,
            "category": category,
            "content_type": content_type,
            "min_price": min_price,
            "max_price": max_price,
            "chain": chain,
            "sort_by": sort_by,
            "page": page,
            "size": size
        }

        results = await discovery_service.discover_content(
            search_params=search_params,
            user_id=current_user.id if current_user else None
        )

        # Track discovery event for analytics
        if current_user:
            await AnalyticsService(db).track_event(
                user_id=current_user.id,
                event_type="content_discovery",
                properties={
                    "query": query,
                    "results_count": len(results.get("items", [])),
                    "filters_used": {k: v for k, v in search_params.items() if v is not None}
                }
            )

        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/content/{product_id}", response_model=ProductResponseDTO)
async def get_content_info(
    product_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Get detailed information about specific content.

    Returns metadata, pricing, and access requirements for a piece of content.

    **Path Parameters:**
    - product_id: UUID of the content/product

    **Response:**
    Returns content metadata including:
    - Title, description, and preview
    - Pricing and payment options
    - Access requirements
    - Provider information
    """
    try:
        discovery_service = DiscoveryService(db)
        content = await discovery_service.get_content_info(
            product_id=product_id,
            user_id=current_user.id if current_user else None
        )

        if not content:
            raise HTTPException(status_code=404, detail="Content not found")

        # Track content view event
        if current_user:
            await AnalyticsService(db).track_event(
                user_id=current_user.id,
                event_type="product_view",
                product_id=product_id,
                properties={"product_type": content.type}
            )

        return content

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/categories", response_model=List[Dict[str, Any]])
async def get_categories(
    include_count: bool = Query(False, description="Include product count per category"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get available content categories.

    **Query Parameters:**
    - include_count: Whether to include product count for each category

    **Response:**
    Returns list of available categories with optional product counts.
    """
    try:
        discovery_service = DiscoveryService(db)
        categories = await discovery_service.get_categories(include_count=include_count)

        return categories

    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/trending", response_model=List[ProductResponseDTO])
async def get_trending_content(
    period: str = Query("24h", regex="^(1h|6h|24h|7d|30d)$"),
    limit: int = Query(10, ge=1, le=50),
    category: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Get trending content based on recent activity.

    **Query Parameters:**
    - period: Time period for trending analysis
    - limit: Maximum number of items to return
    - category: Filter by specific category

    **Response:**
    Returns list of trending content sorted by popularity metrics.
    """
    try:
        discovery_service = DiscoveryService(db)
        trending = await discovery_service.get_trending_content(
            period=period,
            limit=limit,
            category=category,
            user_id=current_user.id if current_user else None
        )

        return trending

    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


# =============================================================================
# CONTENT ACCESS
# =============================================================================

@router.get("/access/{product_id}")
async def request_content_access(
    product_id: uuid.UUID,
    request: Request,
    user_agent: Optional[str] = Query(None, description="User agent string"),
    referer: Optional[str] = Query(None, description="Referer URL"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Request access to premium content (implements x402 protocol).

    This is the core endpoint that implements the v402/x402 protocol flow:
    1. Check if content exists and is available
    2. Verify if user has already paid
    3. Return 402 Payment Required with payment options
    4. Or return content if access is granted

    **Path Parameters:**
    - product_id: UUID of the content to access

    **Headers:**
    - User-Agent: Client user agent
    - Referer: Referring URL
    - X-PAYMENT: Payment authorization header (for paid requests)

    **Response:**
    - 200: Content accessible (with content or redirect)
    - 402: Payment Required (with payment requirements)
    - 404: Content not found
    - 403: Access denied
    """
    try:
        content_service = ContentService(db)

        # Get client IP address
        client_ip = request.client.host
        if "x-forwarded-for" in request.headers:
            client_ip = request.headers["x-forwarded-for"].split(",")[0].strip()

        # Check for payment header
        payment_header = request.headers.get("X-PAYMENT")

        # Log access attempt
        access_log = await content_service.log_access_attempt(
            product_id=product_id,
            user_id=current_user.id if current_user else None,
            ip_address=client_ip,
            user_agent=user_agent or request.headers.get("user-agent"),
            referer=referer or request.headers.get("referer"),
            request_url=str(request.url),
            payment_header=payment_header
        )

        # Handle content access request
        access_result = await content_service.handle_access_request(
            product_id=product_id,
            user_id=current_user.id if current_user else None,
            payment_header=payment_header,
            access_log_id=access_log.id
        )

        if access_result["status"] == "payment_required":
            # Return 402 Payment Required with x402 protocol response
            return JSONResponse(
                status_code=402,
                content={
                    "x402Version": 1,
                    "accepts": access_result["payment_requirements"],
                    "error": "Payment required to access this content"
                },
                headers={
                    "Content-Type": "application/json",
                    "WWW-Authenticate": "Bearer"
                }
            )

        elif access_result["status"] == "access_granted":
            # Update access log and return content
            await content_service.update_access_log(
                access_log.id,
                status="paid",
                payment_id=access_result.get("payment_id")
            )

            # Track successful access
            await AnalyticsService(db).track_event(
                user_id=current_user.id if current_user else None,
                event_type="access_granted",
                product_id=product_id,
                properties={
                    "payment_made": access_result.get("payment_made", False),
                    "amount": access_result.get("amount")
                }
            )

            return {
                "status": "success",
                "content_url": access_result["content_url"],
                "access_token": access_result.get("access_token"),
                "expires_at": access_result.get("expires_at"),
                "payment_info": access_result.get("payment_info")
            }

        else:
            # Access denied
            await content_service.update_access_log(
                access_log.id,
                status="denied",
                denial_reason=access_result.get("reason")
            )

            raise HTTPException(
                status_code=403,
                detail=access_result.get("reason", "Access denied")
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


# =============================================================================
# PAYMENT PROCESSING
# =============================================================================

@router.post("/payments", response_model=PaymentResponseDTO)
async def create_payment(
    payment_data: PaymentCreateDTO,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Create a new payment transaction.

    Initiates a payment for content access. This endpoint is called when
    a client wants to pay for content access.

    **Request Body:**
    - product_id: UUID of the content to purchase
    - payer_address: Blockchain address of the payer
    - payee_address: Blockchain address of the payee
    - amount: Payment amount in wei
    - chain: Blockchain network to use
    - payment_scheme: Payment calculation method

    **Response:**
    Returns payment information including transaction details.
    """
    try:
        payment_service = PaymentService(db)

        # Get client IP for fraud detection
        client_ip = request.client.host
        if "x-forwarded-for" in request.headers:
            client_ip = request.headers["x-forwarded-for"].split(",")[0].strip()

        payment = await payment_service.create_payment(
            payment_data=payment_data,
            payer_id=current_user.id if current_user else None,
            client_ip=client_ip
        )

        # Track payment creation
        await AnalyticsService(db).track_event(
            user_id=current_user.id if current_user else None,
            event_type="payment_attempt",
            product_id=payment_data.product_id,
            properties={
                "amount": payment_data.amount,
                "chain": payment_data.chain,
                "payment_id": str(payment.id)
            }
        )

        return PaymentResponseDTO.from_orm(payment)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/payments/{payment_id}", response_model=PaymentResponseDTO)
async def get_payment_status(
    payment_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Get payment status and details.

    **Path Parameters:**
    - payment_id: UUID of the payment transaction

    **Response:**
    Returns current payment status and transaction details.
    """
    try:
        payment_service = PaymentService(db)
        payment = await payment_service.get_payment_by_id(payment_id)

        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")

        # Check if user has access to this payment
        if current_user and payment.payer_id != current_user.id:
            # Allow access if user is the payer or if no authentication required for status checks
            pass

        return PaymentResponseDTO.from_orm(payment)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/payments/{payment_id}/confirm")
async def confirm_payment(
    payment_id: uuid.UUID,
    confirmation_data: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Confirm payment with blockchain transaction details.

    Called when a payment transaction has been submitted to the blockchain.
    Updates payment status and begins monitoring for confirmations.

    **Path Parameters:**
    - payment_id: UUID of the payment

    **Request Body:**
    - transaction_hash: Blockchain transaction hash
    - block_number: Block number (optional)
    - gas_used: Gas used for transaction (optional)
    - gas_price: Gas price (optional)

    **Response:**
    Returns updated payment information.
    """
    try:
        payment_service = PaymentService(db)

        payment = await payment_service.confirm_payment(
            payment_id=payment_id,
            transaction_hash=confirmation_data.get("transaction_hash"),
            block_number=confirmation_data.get("block_number"),
            gas_used=confirmation_data.get("gas_used"),
            gas_price=confirmation_data.get("gas_price")
        )

        # Track payment confirmation
        await AnalyticsService(db).track_event(
            user_id=current_user.id if current_user else None,
            event_type="payment_confirmed",
            product_id=payment.product_id,
            properties={
                "payment_id": str(payment_id),
                "transaction_hash": confirmation_data.get("transaction_hash"),
                "chain": payment.chain
            }
        )

        return PaymentResponseDTO.from_orm(payment)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/payments/{payment_id}/fail")
async def report_payment_failure(
    payment_id: uuid.UUID,
    failure_data: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Report payment failure.

    Called when a payment transaction fails or is rejected.

    **Path Parameters:**
    - payment_id: UUID of the payment

    **Request Body:**
    - reason: Failure reason
    - error_code: Error code (optional)
    - transaction_hash: Transaction hash if available (optional)

    **Response:**
    Returns updated payment information.
    """
    try:
        payment_service = PaymentService(db)

        payment = await payment_service.fail_payment(
            payment_id=payment_id,
            reason=failure_data.get("reason", "Payment failed"),
            error_code=failure_data.get("error_code")
        )

        # Track payment failure
        await AnalyticsService(db).track_event(
            user_id=current_user.id if current_user else None,
            event_type="payment_failure",
            product_id=payment.product_id,
            properties={
                "payment_id": str(payment_id),
                "reason": failure_data.get("reason"),
                "error_code": failure_data.get("error_code")
            }
        )

        return PaymentResponseDTO.from_orm(payment)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


# =============================================================================
# USER MANAGEMENT
# =============================================================================

@router.get("/profile", response_model=Dict[str, Any])
async def get_user_profile(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user profile information.

    **Response:**
    Returns user profile data including payment history and preferences.
    """
    try:
        return {
            "id": current_user.id,
            "email": current_user.email,
            "username": current_user.username,
            "role": current_user.role,
            "wallet_address": current_user.wallet_address,
            "preferred_chain": current_user.preferred_chain,
            "created_at": current_user.created_at
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/payment-history", response_model=List[PaymentResponseDTO])
async def get_user_payment_history(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    status: Optional[PaymentStatus] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get user's payment history.

    **Query Parameters:**
    - page: Page number for pagination
    - size: Items per page
    - status: Filter by payment status
    - start_date/end_date: Date range filter

    **Response:**
    Returns paginated list of user's payments.
    """
    try:
        payment_service = PaymentService(db)

        filters = {
            "payer_id": current_user.id,
            "status": status,
            "start_date": start_date,
            "end_date": end_date
        }

        payments, total = await payment_service.list_payments(
            filters=filters,
            page=page,
            size=size
        )

        return payments

    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


# =============================================================================
# SYSTEM STATUS
# =============================================================================

@router.get("/chains", response_model=List[Dict[str, Any]])
async def get_supported_chains(
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of supported blockchain networks.

    **Response:**
    Returns list of supported chains with status and fee information.
    """
    try:
        # Implementation would check chain status and return info
        chains = [
            {
                "name": "ethereum",
                "display_name": "Ethereum",
                "chain_id": 1,
                "currency": "ETH",
                "status": "active",
                "average_fee": "50000000000000000",  # 0.05 ETH in wei
                "confirmation_time": "3-5 minutes"
            },
            {
                "name": "base",
                "display_name": "Base",
                "chain_id": 8453,
                "currency": "ETH",
                "status": "active",
                "average_fee": "1000000000000000",  # 0.001 ETH in wei
                "confirmation_time": "10-30 seconds"
            },
            {
                "name": "polygon",
                "display_name": "Polygon",
                "chain_id": 137,
                "currency": "MATIC",
                "status": "active",
                "average_fee": "10000000000000000",  # 0.01 MATIC in wei
                "confirmation_time": "30-60 seconds"
            }
        ]

        return chains

    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
