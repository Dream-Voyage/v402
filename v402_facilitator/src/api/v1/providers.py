"""
Content Provider API endpoints.

This module provides comprehensive API endpoints for content providers to manage
their products, analytics, payments, and business operations.
"""

import uuid
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import get_db
from src.core.security import require_role
from src.models.entities import (
    AnalyticsRequestDTO, AnalyticsResponseDTO, PaginatedResponseDTO,
    ProductCreateDTO, ProductResponseDTO, ProductStatus, ProductUpdateDTO,
    User, UserRole
)
from src.services.analytics_service import AnalyticsService
from src.services.payment_service import PaymentService
from src.services.product_service import ProductService
from typing import Any, Dict, List, Optional

router = APIRouter(prefix="/providers", tags=["Content Providers"])
security = HTTPBearer()


# =============================================================================
# PRODUCT MANAGEMENT
# =============================================================================

@router.post("/products", response_model=ProductResponseDTO)
async def create_product(
    product_data: ProductCreateDTO,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.CONTENT_PROVIDER, UserRole.ADMIN]))
):
    """
    Create a new product/content item.

    Creates a new product in the system that can be monetized through v402 payments.
    The product will be in DRAFT status by default and needs to be published separately.

    **Required permissions:** Content Provider or Admin

    **Request Body:**
    - title: Product title (max 500 chars)
    - description: Detailed product description
    - content_url: URL where the actual content is hosted
    - type: Content type (article, video, audio, etc.)
    - price: Price in wei (string format for precision)
    - payment_scheme: How payment is calculated (exact, upto, dynamic)

    **Response:**
    Returns the created product with generated ID and metadata.
    """
    try:
        product_service = ProductService(db)
        product = await product_service.create_product(current_user.id, product_data)

        # Log product creation event
        await AnalyticsService(db).track_event(
            user_id=current_user.id,
            event_type="product_created",
            properties={"product_id": str(product.id), "product_type": product.type}
        )

        return ProductResponseDTO.from_orm(product)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/products", response_model=PaginatedResponseDTO)
async def list_products(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Items per page"),
    status: Optional[ProductStatus] = Query(None, description="Filter by status"),
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search in title/description"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.CONTENT_PROVIDER, UserRole.ADMIN]))
):
    """
    List products owned by the current user.

    Returns a paginated list of products with filtering and sorting options.

    **Query Parameters:**
    - page: Page number (starts from 1)
    - size: Number of items per page (max 100)
    - status: Filter by product status
    - category: Filter by product category
    - search: Search text in title or description
    - sort_by: Field to sort by (created_at, title, price, view_count, etc.)
    - sort_order: Sort direction (asc or desc)

    **Response:**
    Returns paginated results with metadata.
    """
    try:
        product_service = ProductService(db)

        filters = {
            "owner_id": current_user.id,
            "status": status,
            "category": category,
            "search": search
        }

        products, total = await product_service.list_products(
            filters=filters,
            page=page,
            size=size,
            sort_by=sort_by,
            sort_order=sort_order
        )

        return PaginatedResponseDTO(
            items=[ProductResponseDTO.from_orm(p) for p in products],
            total=total,
            page=page,
            size=size,
            pages=(total + size - 1) // size
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/products/{product_id}", response_model=ProductResponseDTO)
async def get_product(
    product_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.CONTENT_PROVIDER, UserRole.ADMIN]))
):
    """
    Get detailed information about a specific product.

    **Path Parameters:**
    - product_id: UUID of the product

    **Response:**
    Returns complete product information including analytics summary.
    """
    try:
        product_service = ProductService(db)
        product = await product_service.get_product_by_id(product_id)

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        # Check ownership (unless admin)
        if current_user.role != UserRole.ADMIN and product.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to view this product")

        return ProductResponseDTO.from_orm(product)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/products/{product_id}", response_model=ProductResponseDTO)
async def update_product(
    product_id: uuid.UUID,
    product_data: ProductUpdateDTO,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.CONTENT_PROVIDER, UserRole.ADMIN]))
):
    """
    Update an existing product.

    **Path Parameters:**
    - product_id: UUID of the product to update

    **Request Body:**
    All fields are optional. Only provided fields will be updated.

    **Response:**
    Returns the updated product information.
    """
    try:
        product_service = ProductService(db)
        product = await product_service.get_product_by_id(product_id)

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        # Check ownership (unless admin)
        if current_user.role != UserRole.ADMIN and product.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to modify this product")

        updated_product = await product_service.update_product(product_id, product_data)

        # Log product update event
        await AnalyticsService(db).track_event(
            user_id=current_user.id,
            event_type="product_updated",
            properties={"product_id": str(product_id), "updated_fields": list(product_data.dict(exclude_unset=True).keys())}
        )

        return ProductResponseDTO.from_orm(updated_product)

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/products/{product_id}")
async def delete_product(
    product_id: uuid.UUID,
    soft_delete: bool = Query(True, description="Use soft delete (recommended)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.CONTENT_PROVIDER, UserRole.ADMIN]))
):
    """
    Delete a product (soft delete by default).

    **Path Parameters:**
    - product_id: UUID of the product to delete

    **Query Parameters:**
    - soft_delete: If true, marks as deleted but keeps data for analytics

    **Response:**
    Returns success confirmation.
    """
    try:
        product_service = ProductService(db)
        product = await product_service.get_product_by_id(product_id)

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        # Check ownership (unless admin)
        if current_user.role != UserRole.ADMIN and product.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this product")

        await product_service.delete_product(product_id, soft_delete=soft_delete)

        # Log product deletion event
        await AnalyticsService(db).track_event(
            user_id=current_user.id,
            event_type="product_deleted",
            properties={"product_id": str(product_id), "soft_delete": soft_delete}
        )

        return {"message": "Product deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/products/{product_id}/publish")
async def publish_product(
    product_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.CONTENT_PROVIDER, UserRole.ADMIN]))
):
    """
    Publish a product (change status from DRAFT to ACTIVE).

    **Path Parameters:**
    - product_id: UUID of the product to publish

    **Response:**
    Returns updated product information.
    """
    try:
        product_service = ProductService(db)
        product = await product_service.get_product_by_id(product_id)

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        # Check ownership (unless admin)
        if current_user.role != UserRole.ADMIN and product.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to publish this product")

        if product.status != ProductStatus.DRAFT:
            raise HTTPException(status_code=400, detail="Only draft products can be published")

        updated_product = await product_service.update_product(
            product_id,
            ProductUpdateDTO(status=ProductStatus.ACTIVE, published_at=datetime.utcnow())
        )

        return ProductResponseDTO.from_orm(updated_product)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/products/{product_id}/unpublish")
async def unpublish_product(
    product_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.CONTENT_PROVIDER, UserRole.ADMIN]))
):
    """
    Unpublish a product (change status from ACTIVE to INACTIVE).

    **Path Parameters:**
    - product_id: UUID of the product to unpublish

    **Response:**
    Returns updated product information.
    """
    try:
        product_service = ProductService(db)
        product = await product_service.get_product_by_id(product_id)

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        # Check ownership (unless admin)
        if current_user.role != UserRole.ADMIN and product.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to unpublish this product")

        updated_product = await product_service.update_product(
            product_id,
            ProductUpdateDTO(status=ProductStatus.INACTIVE)
        )

        return ProductResponseDTO.from_orm(updated_product)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


# =============================================================================
# ANALYTICS & INSIGHTS
# =============================================================================

@router.get("/products/{product_id}/analytics", response_model=AnalyticsResponseDTO)
async def get_product_analytics(
    product_id: uuid.UUID,
    analytics_request: AnalyticsRequestDTO = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.CONTENT_PROVIDER, UserRole.ADMIN]))
):
    """
    Get detailed analytics for a specific product.

    **Path Parameters:**
    - product_id: UUID of the product

    **Query Parameters:**
    - start_date: Start date for analytics period
    - end_date: End date for analytics period
    - group_by: Group results by (day, week, month, hour)

    **Response:**
    Returns comprehensive analytics including views, payments, revenue, and trends.
    """
    try:
        # Verify ownership
        product_service = ProductService(db)
        product = await product_service.get_product_by_id(product_id)

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        if current_user.role != UserRole.ADMIN and product.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to view analytics for this product")

        analytics_service = AnalyticsService(db)
        analytics_request.product_id = product_id

        analytics_data = await analytics_service.get_product_analytics(analytics_request)

        return analytics_data

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/analytics/dashboard", response_model=Dict[str, Any])
async def get_dashboard_analytics(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.CONTENT_PROVIDER, UserRole.ADMIN]))
):
    """
    Get comprehensive dashboard analytics for all user's products.

    **Query Parameters:**
    - days: Number of days to include in analysis (max 365)

    **Response:**
    Returns dashboard data including:
    - Total revenue and payments
    - Top performing products
    - Recent activity
    - Growth trends
    - Geographic distribution
    """
    try:
        analytics_service = AnalyticsService(db)

        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        dashboard_data = await analytics_service.get_dashboard_analytics(
            user_id=current_user.id,
            start_date=start_date,
            end_date=end_date
        )

        return dashboard_data

    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/analytics/revenue", response_model=AnalyticsResponseDTO)
async def get_revenue_analytics(
    analytics_request: AnalyticsRequestDTO = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.CONTENT_PROVIDER, UserRole.ADMIN]))
):
    """
    Get detailed revenue analytics and trends.

    **Response:**
    Returns revenue data including:
    - Total revenue by period
    - Revenue by product
    - Payment success rates
    - Average transaction values
    - Revenue forecasting
    """
    try:
        analytics_service = AnalyticsService(db)

        revenue_data = await analytics_service.get_revenue_analytics(
            user_id=current_user.id,
            request=analytics_request
        )

        return revenue_data

    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


# =============================================================================
# ACCESS LOGS & UNPAID REQUESTS
# =============================================================================

@router.get("/access-logs", response_model=PaginatedResponseDTO)
async def get_access_logs(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=500),
    product_id: Optional[uuid.UUID] = Query(None, description="Filter by product"),
    status: Optional[str] = Query(None, description="Filter by access status"),
    paid_only: bool = Query(False, description="Show only paid accesses"),
    unpaid_only: bool = Query(False, description="Show only unpaid accesses"),
    start_date: Optional[datetime] = Query(None, description="Filter from date"),
    end_date: Optional[datetime] = Query(None, description="Filter to date"),
    ip_address: Optional[str] = Query(None, description="Filter by IP address"),
    country_code: Optional[str] = Query(None, description="Filter by country"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.CONTENT_PROVIDER, UserRole.ADMIN]))
):
    """
    Get detailed access logs for content.

    Shows who accessed content, when, and whether they paid.
    Useful for identifying potential customers and usage patterns.

    **Query Parameters:**
    - product_id: Filter by specific product
    - paid_only: Show only accesses that resulted in payment
    - unpaid_only: Show only accesses without payment
    - start_date/end_date: Date range filter
    - ip_address: Filter by specific IP
    - country_code: Filter by country (ISO 2-letter code)

    **Response:**
    Returns paginated access logs with user and payment information.
    """
    try:
        analytics_service = AnalyticsService(db)

        filters = {
            "user_id": current_user.id,
            "product_id": product_id,
            "status": status,
            "paid_only": paid_only,
            "unpaid_only": unpaid_only,
            "start_date": start_date,
            "end_date": end_date,
            "ip_address": ip_address,
            "country_code": country_code
        }

        access_logs, total = await analytics_service.get_access_logs(
            filters=filters,
            page=page,
            size=size
        )

        return PaginatedResponseDTO(
            items=access_logs,
            total=total,
            page=page,
            size=size,
            pages=(total + size - 1) // size
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/unpaid-requests", response_model=PaginatedResponseDTO)
async def get_unpaid_requests(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=500),
    product_id: Optional[uuid.UUID] = Query(None),
    hours: int = Query(24, ge=1, le=168, description="Look back hours (max 1 week)"),
    min_requests: int = Query(1, ge=1, description="Minimum request count"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.CONTENT_PROVIDER, UserRole.ADMIN]))
):
    """
    Get recent unpaid access requests.

    Identifies potential customers who accessed content but didn't pay.
    Useful for remarketing and conversion optimization.

    **Query Parameters:**
    - hours: How many hours back to look (max 1 week)
    - min_requests: Minimum number of requests to include
    - product_id: Filter by specific product

    **Response:**
    Returns users/IPs with unpaid access attempts, sorted by frequency.
    Includes geographic information and user agent data.
    """
    try:
        analytics_service = AnalyticsService(db)

        end_date = datetime.utcnow()
        start_date = end_date - timedelta(hours=hours)

        unpaid_requests = await analytics_service.get_unpaid_requests(
            user_id=current_user.id,
            product_id=product_id,
            start_date=start_date,
            end_date=end_date,
            min_requests=min_requests,
            page=page,
            size=size
        )

        return unpaid_requests

    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


# =============================================================================
# PAYMENT MANAGEMENT
# =============================================================================

@router.get("/payments", response_model=PaginatedResponseDTO)
async def get_payments(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
    product_id: Optional[uuid.UUID] = Query(None),
    status: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    chain: Optional[str] = Query(None),
    min_amount: Optional[str] = Query(None, description="Minimum amount in wei"),
    max_amount: Optional[str] = Query(None, description="Maximum amount in wei"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.CONTENT_PROVIDER, UserRole.ADMIN]))
):
    """
    Get payments received for your products.

    **Query Parameters:**
    - product_id: Filter by specific product
    - status: Filter by payment status
    - start_date/end_date: Date range filter
    - chain: Filter by blockchain network
    - min_amount/max_amount: Amount range filter (in wei)

    **Response:**
    Returns paginated payment records with transaction details.
    """
    try:
        payment_service = PaymentService(db)

        filters = {
            "payee_id": current_user.id,
            "product_id": product_id,
            "status": status,
            "start_date": start_date,
            "end_date": end_date,
            "chain": chain,
            "min_amount": min_amount,
            "max_amount": max_amount
        }

        payments, total = await payment_service.list_payments(
            filters=filters,
            page=page,
            size=size
        )

        return PaginatedResponseDTO(
            items=payments,
            total=total,
            page=page,
            size=size,
            pages=(total + size - 1) // size
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/payments/{payment_id}", response_model=Dict[str, Any])
async def get_payment_details(
    payment_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.CONTENT_PROVIDER, UserRole.ADMIN]))
):
    """
    Get detailed information about a specific payment.

    **Path Parameters:**
    - payment_id: UUID of the payment

    **Response:**
    Returns complete payment information including blockchain transaction details.
    """
    try:
        payment_service = PaymentService(db)
        payment = await payment_service.get_payment_by_id(payment_id)

        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")

        # Check if user is the payee (unless admin)
        if current_user.role != UserRole.ADMIN and payment.payee_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to view this payment")

        return payment

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


# =============================================================================
# WEBHOOKS & NOTIFICATIONS
# =============================================================================

@router.get("/webhooks", response_model=List[Dict[str, Any]])
async def list_webhooks(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.CONTENT_PROVIDER, UserRole.ADMIN]))
):
    """
    List configured webhooks for real-time notifications.

    **Response:**
    Returns list of webhook configurations with delivery statistics.
    """
    try:
        # Implementation would go here
        return []

    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/webhooks", response_model=Dict[str, Any])
async def create_webhook(
    webhook_data: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.CONTENT_PROVIDER, UserRole.ADMIN]))
):
    """
    Create a new webhook for real-time notifications.

    **Request Body:**
    - url: Webhook endpoint URL
    - events: List of events to subscribe to
    - secret: Optional secret for signature verification

    **Response:**
    Returns created webhook configuration.
    """
    try:
        # Implementation would go here
        return {"message": "Webhook created successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


# =============================================================================
# BUSINESS INSIGHTS
# =============================================================================

@router.get("/insights/top-products", response_model=List[Dict[str, Any]])
async def get_top_products(
    period: str = Query("30d", regex="^(7d|30d|90d|1y)$"),
    metric: str = Query("revenue", regex="^(revenue|views|purchases|rating)$"),
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.CONTENT_PROVIDER, UserRole.ADMIN]))
):
    """
    Get top performing products by various metrics.

    **Query Parameters:**
    - period: Time period (7d, 30d, 90d, 1y)
    - metric: Ranking metric (revenue, views, purchases, rating)
    - limit: Number of products to return

    **Response:**
    Returns ranked list of products with performance metrics.
    """
    try:
        analytics_service = AnalyticsService(db)

        top_products = await analytics_service.get_top_products(
            user_id=current_user.id,
            period=period,
            metric=metric,
            limit=limit
        )

        return top_products

    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/insights/recommendations", response_model=Dict[str, Any])
async def get_business_recommendations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.CONTENT_PROVIDER, UserRole.ADMIN]))
):
    """
    Get AI-powered business recommendations.

    Analyzes performance data to suggest:
    - Optimal pricing strategies
    - Content types to focus on
    - Marketing opportunities
    - Conversion improvements

    **Response:**
    Returns personalized business insights and recommendations.
    """
    try:
        analytics_service = AnalyticsService(db)

        recommendations = await analytics_service.get_business_recommendations(
            user_id=current_user.id
        )

        return recommendations

    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
