"""
Admin API endpoints for system management.

This module provides comprehensive administrative endpoints for managing
users, monitoring system health, and accessing detailed analytics.
"""

import uuid
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import get_db
from src.core.security import require_role
from src.models.entities import (
    PaginatedResponseDTO, User, UserRole, UserStatus, UserResponseDTO,
    PaymentStatus, ProductStatus, HealthCheckDTO
)
from src.services.admin_service import AdminService
from src.services.analytics_service import AnalyticsService
from src.services.monitoring_service import MonitoringService
from typing import Any, Dict, Optional

router = APIRouter(prefix="/admin", tags=["Admin"])


# =============================================================================
# USER MANAGEMENT
# =============================================================================

@router.get("/users", response_model=PaginatedResponseDTO)
async def list_users(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=500),
    role: Optional[UserRole] = Query(None, description="Filter by user role"),
    status: Optional[UserStatus] = Query(None, description="Filter by user status"),
    search: Optional[str] = Query(None, description="Search in email/username"),
    created_after: Optional[datetime] = Query(None, description="Created after date"),
    created_before: Optional[datetime] = Query(None, description="Created before date"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SUPER_ADMIN]))
):
    """
    List all users with advanced filtering and search.

    **Required permissions:** Admin or Super Admin

    **Query Parameters:**
    - page/size: Pagination controls
    - role: Filter by user role
    - status: Filter by account status
    - search: Search in email or username
    - created_after/created_before: Date range filters

    **Response:**
    Returns paginated list of users with full profile information.
    """
    try:
        admin_service = AdminService(db)

        filters = {
            "role": role,
            "status": status,
            "search": search,
            "created_after": created_after,
            "created_before": created_before
        }

        users, total = await admin_service.list_users(
            filters=filters,
            page=page,
            size=size
        )

        return PaginatedResponseDTO(
            items=[UserResponseDTO.from_orm(user) for user in users],
            total=total,
            page=page,
            size=size,
            pages=(total + size - 1) // size
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/users/{user_id}", response_model=UserResponseDTO)
async def get_user_details(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SUPER_ADMIN]))
):
    """
    Get detailed information about a specific user.

    **Path Parameters:**
    - user_id: UUID of the user

    **Response:**
    Returns complete user profile with statistics and activity.
    """
    try:
        admin_service = AdminService(db)
        user_details = await admin_service.get_user_details(user_id)

        if not user_details:
            raise HTTPException(status_code=404, detail="User not found")

        return user_details

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.patch("/users/{user_id}/status")
async def update_user_status(
    user_id: uuid.UUID,
    new_status: UserStatus,
    reason: Optional[str] = Query(None, description="Reason for status change"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SUPER_ADMIN]))
):
    """
    Update user account status.

    **Path Parameters:**
    - user_id: UUID of the user

    **Request Body:**
    - new_status: New status to set
    - reason: Optional reason for the change

    **Response:**
    Returns success confirmation with updated user information.
    """
    try:
        admin_service = AdminService(db)

        updated_user = await admin_service.update_user_status(
            user_id=user_id,
            new_status=new_status,
            reason=reason,
            updated_by=current_user.id
        )

        return {
            "message": "User status updated successfully",
            "user": UserResponseDTO.from_orm(updated_user),
            "updated_by": current_user.email,
            "timestamp": datetime.utcnow()
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/users/{user_id}/reset-api-key")
async def reset_user_api_key(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SUPER_ADMIN]))
):
    """
    Reset user's API key.

    **Path Parameters:**
    - user_id: UUID of the user

    **Response:**
    Returns new API key (this is the only time it will be shown).
    """
    try:
        admin_service = AdminService(db)

        new_api_key = await admin_service.reset_user_api_key(
            user_id=user_id,
            reset_by=current_user.id
        )

        return {
            "message": "API key reset successfully",
            "api_key": new_api_key,
            "warning": "This is the only time the API key will be displayed. Store it securely."
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


# =============================================================================
# SYSTEM ANALYTICS
# =============================================================================

@router.get("/analytics/overview", response_model=Dict[str, Any])
async def get_system_overview(
    period: str = Query("30d", regex="^(24h|7d|30d|90d|1y)$"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SUPER_ADMIN]))
):
    """
    Get comprehensive system overview and metrics.

    **Query Parameters:**
    - period: Time period for analytics (24h, 7d, 30d, 90d, 1y)

    **Response:**
    Returns system-wide statistics including:
    - User registrations and activity
    - Content creation and consumption
    - Payment volume and success rates
    - Revenue and fees collected
    - Platform health metrics
    """
    try:
        analytics_service = AnalyticsService(db)

        overview = await analytics_service.get_system_overview(period=period)

        return overview

    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/analytics/revenue", response_model=Dict[str, Any])
async def get_revenue_analytics(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    group_by: str = Query("day", regex="^(hour|day|week|month)$"),
    chain: Optional[str] = Query(None, description="Filter by blockchain"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SUPER_ADMIN]))
):
    """
    Get detailed revenue analytics and trends.

    **Query Parameters:**
    - start_date/end_date: Date range filter
    - group_by: Group results by time period
    - chain: Filter by specific blockchain

    **Response:**
    Returns revenue data including:
    - Total platform revenue
    - Facilitator fees collected
    - Revenue by chain/network
    - Growth trends and projections
    """
    try:
        analytics_service = AnalyticsService(db)

        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()

        revenue_data = await analytics_service.get_platform_revenue(
            start_date=start_date,
            end_date=end_date,
            group_by=group_by,
            chain=chain
        )

        return revenue_data

    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/analytics/users", response_model=Dict[str, Any])
async def get_user_analytics(
    period: str = Query("30d", regex="^(7d|30d|90d|1y)$"),
    segment: Optional[str] = Query(None, description="User segment to analyze"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SUPER_ADMIN]))
):
    """
    Get user analytics and behavior insights.

    **Response:**
    Returns user data including:
    - Registration trends
    - User engagement metrics
    - Retention rates
    - Geographic distribution
    - Role distribution
    """
    try:
        analytics_service = AnalyticsService(db)

        user_analytics = await analytics_service.get_user_analytics(
            period=period,
            segment=segment
        )

        return user_analytics

    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/analytics/content", response_model=Dict[str, Any])
async def get_content_analytics(
    period: str = Query("30d", regex="^(7d|30d|90d|1y)$"),
    content_type: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SUPER_ADMIN]))
):
    """
    Get content performance analytics.

    **Response:**
    Returns content data including:
    - Content creation trends
    - Most popular content types
    - Category performance
    - Content monetization rates
    - Quality metrics
    """
    try:
        analytics_service = AnalyticsService(db)

        content_analytics = await analytics_service.get_content_analytics(
            period=period,
            content_type=content_type,
            category=category
        )

        return content_analytics

    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


# =============================================================================
# SYSTEM MONITORING
# =============================================================================

@router.get("/health", response_model=HealthCheckDTO)
async def get_system_health(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SUPER_ADMIN]))
):
    """
    Get comprehensive system health status.

    **Response:**
    Returns health status for all system components:
    - Database connectivity and performance
    - Redis cache status
    - Blockchain network connections
    - External service dependencies
    - Resource utilization
    """
    try:
        monitoring_service = MonitoringService(db)

        health_status = await monitoring_service.get_comprehensive_health()

        return health_status

    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/metrics", response_model=Dict[str, Any])
async def get_system_metrics(
    metric_type: str = Query("all", regex="^(all|performance|business|technical)$"),
    time_range: str = Query("1h", regex="^(5m|15m|1h|6h|24h)$"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SUPER_ADMIN]))
):
    """
    Get real-time system metrics.

    **Query Parameters:**
    - metric_type: Type of metrics to retrieve
    - time_range: Time range for metrics

    **Response:**
    Returns real-time metrics including:
    - API response times and error rates
    - Database query performance
    - Payment processing metrics
    - Resource utilization (CPU, memory, etc.)
    """
    try:
        monitoring_service = MonitoringService(db)

        metrics = await monitoring_service.get_system_metrics(
            metric_type=metric_type,
            time_range=time_range
        )

        return metrics

    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/logs", response_model=Dict[str, Any])
async def get_system_logs(
    level: str = Query("ERROR", regex="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$"),
    limit: int = Query(100, ge=1, le=1000),
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None),
    service: Optional[str] = Query(None, description="Filter by service name"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SUPER_ADMIN]))
):
    """
    Get system logs for debugging and monitoring.

    **Query Parameters:**
    - level: Minimum log level to include
    - limit: Maximum number of log entries
    - start_time/end_time: Time range filter
    - service: Filter by specific service

    **Response:**
    Returns structured log entries with filtering and search.
    """
    try:
        monitoring_service = MonitoringService(db)

        logs = await monitoring_service.get_system_logs(
            level=level,
            limit=limit,
            start_time=start_time,
            end_time=end_time,
            service=service
        )

        return logs

    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


# =============================================================================
# PAYMENT MANAGEMENT
# =============================================================================

@router.get("/payments", response_model=PaginatedResponseDTO)
async def list_all_payments(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=500),
    status: Optional[PaymentStatus] = Query(None),
    chain: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    min_amount: Optional[str] = Query(None),
    max_amount: Optional[str] = Query(None),
    user_email: Optional[str] = Query(None, description="Filter by payer email"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SUPER_ADMIN]))
):
    """
    List all payments in the system with advanced filtering.

    **Response:**
    Returns paginated list of all payments with full transaction details.
    """
    try:
        admin_service = AdminService(db)

        filters = {
            "status": status,
            "chain": chain,
            "start_date": start_date,
            "end_date": end_date,
            "min_amount": min_amount,
            "max_amount": max_amount,
            "user_email": user_email
        }

        payments, total = await admin_service.list_all_payments(
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


@router.post("/payments/{payment_id}/refund")
async def refund_payment(
    payment_id: uuid.UUID,
    refund_data: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SUPER_ADMIN]))
):
    """
    Initiate payment refund (admin only).

    **Path Parameters:**
    - payment_id: UUID of the payment to refund

    **Request Body:**
    - reason: Refund reason
    - amount: Refund amount (optional, defaults to full amount)
    - notify_user: Whether to notify the user

    **Response:**
    Returns refund transaction details.
    """
    try:
        admin_service = AdminService(db)

        refund = await admin_service.process_refund(
            payment_id=payment_id,
            refund_reason=refund_data.get("reason", "Admin refund"),
            refund_amount=refund_data.get("amount"),
            notify_user=refund_data.get("notify_user", True),
            processed_by=current_user.id
        )

        return refund

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


# =============================================================================
# CONTENT MANAGEMENT
# =============================================================================

@router.get("/products", response_model=PaginatedResponseDTO)
async def list_all_products(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=500),
    status: Optional[ProductStatus] = Query(None),
    owner_email: Optional[str] = Query(None, description="Filter by owner email"),
    category: Optional[str] = Query(None),
    flagged_only: bool = Query(False, description="Show only flagged content"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SUPER_ADMIN]))
):
    """
    List all products/content in the system.

    **Response:**
    Returns paginated list of all content with moderation information.
    """
    try:
        admin_service = AdminService(db)

        filters = {
            "status": status,
            "owner_email": owner_email,
            "category": category,
            "flagged_only": flagged_only
        }

        products, total = await admin_service.list_all_products(
            filters=filters,
            page=page,
            size=size
        )

        return PaginatedResponseDTO(
            items=products,
            total=total,
            page=page,
            size=size,
            pages=(total + size - 1) // size
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/products/{product_id}/moderate")
async def moderate_content(
    product_id: uuid.UUID,
    moderation_action: str = Query(..., regex="^(approve|reject|flag|unflag)$"),
    reason: Optional[str] = Query(None, description="Moderation reason"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SUPER_ADMIN]))
):
    """
    Moderate content (approve, reject, flag, etc.).

    **Path Parameters:**
    - product_id: UUID of the product to moderate

    **Query Parameters:**
    - moderation_action: Action to take (approve, reject, flag, unflag)
    - reason: Optional reason for the action

    **Response:**
    Returns updated product status with moderation history.
    """
    try:
        admin_service = AdminService(db)

        result = await admin_service.moderate_content(
            product_id=product_id,
            action=moderation_action,
            reason=reason,
            moderated_by=current_user.id
        )

        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


# =============================================================================
# SYSTEM CONFIGURATION
# =============================================================================

@router.get("/config", response_model=Dict[str, Any])
async def get_system_config(
    current_user: User = Depends(require_role([UserRole.SUPER_ADMIN]))
):
    """
    Get current system configuration (Super Admin only).

    **Response:**
    Returns current system configuration settings.
    """
    try:
        admin_service = AdminService(db)
        config = await admin_service.get_system_config()

        return config

    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/config")
async def update_system_config(
    config_updates: Dict[str, Any],
    current_user: User = Depends(require_role([UserRole.SUPER_ADMIN]))
):
    """
    Update system configuration (Super Admin only).

    **Request Body:**
    Configuration updates to apply.

    **Response:**
    Returns success confirmation with updated configuration.
    """
    try:
        admin_service = AdminService(db)

        updated_config = await admin_service.update_system_config(
            config_updates=config_updates,
            updated_by=current_user.id
        )

        return {
            "message": "Configuration updated successfully",
            "config": updated_config,
            "updated_by": current_user.email,
            "timestamp": datetime.utcnow()
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
