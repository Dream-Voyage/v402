"""
Comprehensive data models for v402 facilitator.

This module defines all database entities, business objects, and data transfer objects
with full type safety, validation, and relationship mapping.
"""

import uuid
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from pydantic import BaseModel, Field
from sqlalchemy import (
    Boolean, Column, DateTime, Enum as SQLEnum, ForeignKey, Index, Integer,
    JSON, Numeric, String, Text
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from typing import Any, Dict, List, Optional

# Database Base
Base = declarative_base()


# =============================================================================
# ENUMS
# =============================================================================

class UserRole(str, Enum):
    """User roles in the system."""
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    CONTENT_PROVIDER = "content_provider"
    INDEX_CLIENT = "index_client"
    END_USER = "end_user"


class UserStatus(str, Enum):
    """User account status."""
    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    BANNED = "banned"
    DELETED = "deleted"


class ChainType(str, Enum):
    """Blockchain network types."""
    ETHEREUM = "ethereum"
    BASE = "base"
    POLYGON = "polygon"
    ARBITRUM = "arbitrum"
    OPTIMISM = "optimism"
    BSC = "bsc"
    SOLANA = "solana"


class PaymentStatus(str, Enum):
    """Payment transaction status."""
    PENDING = "pending"
    PROCESSING = "processing"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    EXPIRED = "expired"
    REFUNDED = "refunded"
    DISPUTED = "disputed"


class PaymentScheme(str, Enum):
    """Payment scheme types."""
    EXACT = "exact"
    UPTO = "upto"
    DYNAMIC = "dynamic"
    SUBSCRIPTION = "subscription"


class ProductType(str, Enum):
    """Product/content types."""
    ARTICLE = "article"
    VIDEO = "video"
    AUDIO = "audio"
    IMAGE = "image"
    PDF = "pdf"
    API_CALL = "api_call"
    DATASET = "dataset"
    SOFTWARE = "software"
    COURSE = "course"
    TEMPLATE = "template"
    OTHER = "other"


class ProductStatus(str, Enum):
    """Product availability status."""
    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"
    DELETED = "deleted"
    ARCHIVED = "archived"


class AccessLogStatus(str, Enum):
    """Access attempt status."""
    REQUESTED = "requested"
    PAID = "paid"
    DENIED = "denied"
    ERROR = "error"


class WebhookEventType(str, Enum):
    """Webhook event types."""
    PAYMENT_CREATED = "payment.created"
    PAYMENT_CONFIRMED = "payment.confirmed"
    PAYMENT_FAILED = "payment.failed"
    PRODUCT_CREATED = "product.created"
    PRODUCT_UPDATED = "product.updated"
    USER_REGISTERED = "user.registered"
    ACCESS_GRANTED = "access.granted"
    ACCESS_DENIED = "access.denied"


class AnalyticsEventType(str, Enum):
    """Analytics event types."""
    PAGE_VIEW = "page_view"
    PRODUCT_VIEW = "product_view"
    PAYMENT_ATTEMPT = "payment_attempt"
    PAYMENT_SUCCESS = "payment_success"
    PAYMENT_FAILURE = "payment_failure"
    USER_SIGNUP = "user_signup"
    USER_LOGIN = "user_login"


# =============================================================================
# DATABASE MODELS
# =============================================================================

class User(Base):
    """User account model."""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=True, index=True)
    full_name = Column(String(200), nullable=True)

    # Authentication
    password_hash = Column(String(255), nullable=False)
    is_email_verified = Column(Boolean, default=False)
    email_verification_token = Column(String(255), nullable=True)

    # Profile
    role = Column(SQLEnum(UserRole), default=UserRole.END_USER, nullable=False)
    status = Column(SQLEnum(UserStatus), default=UserStatus.PENDING, nullable=False)
    avatar_url = Column(String(500), nullable=True)
    timezone = Column(String(50), default="UTC")
    language = Column(String(10), default="en")

    # Blockchain
    wallet_address = Column(String(100), nullable=True, index=True)
    preferred_chain = Column(SQLEnum(ChainType), default=ChainType.ETHEREUM)

    # API Access
    api_key = Column(String(100), unique=True, nullable=True, index=True)
    api_key_created_at = Column(DateTime, nullable=True)
    rate_limit = Column(Integer, default=1000)  # requests per hour

    # Business Information (for providers)
    company_name = Column(String(200), nullable=True)
    website_url = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    last_login_at = Column(DateTime, nullable=True)
    deleted_at = Column(DateTime, nullable=True)

    # Relationships
    products = relationship("Product", back_populates="owner")
    payments_made = relationship("Payment", foreign_keys="Payment.payer_id", back_populates="payer")
    payments_received = relationship("Payment", foreign_keys="Payment.payee_id", back_populates="payee")
    access_logs = relationship("AccessLog", back_populates="user")
    analytics_events = relationship("AnalyticsEvent", back_populates="user")

    __table_args__ = (
        Index('idx_users_email_status', 'email', 'status'),
        Index('idx_users_role_status', 'role', 'status'),
    )


class Product(Base):
    """Content/product model."""

    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Basic Information
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    content_url = Column(String(1000), nullable=False)
    thumbnail_url = Column(String(500), nullable=True)

    # Classification
    type = Column(SQLEnum(ProductType), default=ProductType.ARTICLE, nullable=False)
    category = Column(String(100), nullable=True, index=True)
    tags = Column(JSON, nullable=True)  # List of strings

    # Pricing
    price = Column(Numeric(20, 0), nullable=False)  # Price in wei
    currency = Column(String(10), default="ETH")
    payment_scheme = Column(SQLEnum(PaymentScheme), default=PaymentScheme.EXACT)

    # Access Control
    status = Column(SQLEnum(ProductStatus), default=ProductStatus.DRAFT, nullable=False)
    is_featured = Column(Boolean, default=False)
    access_duration = Column(Integer, nullable=True)  # Access duration in seconds
    max_access_count = Column(Integer, nullable=True)  # Maximum number of accesses

    # Content Metadata
    content_type = Column(String(100), nullable=True)  # MIME type
    content_size = Column(Integer, nullable=True)  # Size in bytes
    content_hash = Column(String(100), nullable=True)  # Content hash for verification
    preview_content = Column(Text, nullable=True)  # Preview/snippet

    # SEO & Discovery
    slug = Column(String(200), unique=True, nullable=True, index=True)
    seo_title = Column(String(200), nullable=True)
    seo_description = Column(String(500), nullable=True)
    keywords = Column(JSON, nullable=True)  # List of strings

    # Analytics
    view_count = Column(Integer, default=0)
    purchase_count = Column(Integer, default=0)
    rating = Column(Numeric(3, 2), nullable=True)  # 0.00 to 5.00
    review_count = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    published_at = Column(DateTime, nullable=True)
    deleted_at = Column(DateTime, nullable=True)

    # Relationships
    owner = relationship("User", back_populates="products")
    payments = relationship("Payment", back_populates="product")
    access_logs = relationship("AccessLog", back_populates="product")
    analytics_events = relationship("AnalyticsEvent", back_populates="product")

    __table_args__ = (
        Index('idx_products_owner_status', 'owner_id', 'status'),
        Index('idx_products_type_category', 'type', 'category'),
        Index('idx_products_price_status', 'price', 'status'),
    )


class Payment(Base):
    """Payment transaction model."""

    __tablename__ = "payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Transaction Details
    transaction_hash = Column(String(100), unique=True, nullable=True, index=True)
    chain = Column(SQLEnum(ChainType), nullable=False)
    block_number = Column(Integer, nullable=True)

    # Parties
    payer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    payee_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    payer_address = Column(String(100), nullable=False, index=True)
    payee_address = Column(String(100), nullable=False, index=True)

    # Product & Amount
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    amount = Column(Numeric(20, 0), nullable=False)  # Amount in wei
    currency = Column(String(10), default="ETH")
    facilitator_fee = Column(Numeric(20, 0), nullable=False)

    # Payment Processing
    status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    payment_scheme = Column(SQLEnum(PaymentScheme), default=PaymentScheme.EXACT)
    confirmation_count = Column(Integer, default=0)
    required_confirmations = Column(Integer, default=3)

    # Gas & Fees
    gas_used = Column(Integer, nullable=True)
    gas_price = Column(Numeric(20, 0), nullable=True)
    network_fee = Column(Numeric(20, 0), nullable=True)

    # Metadata
    payment_metadata = Column(JSON, nullable=True)
    failure_reason = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)

    # External References
    external_reference = Column(String(200), nullable=True, index=True)
    invoice_id = Column(String(100), nullable=True, index=True)

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime, nullable=True)
    confirmed_at = Column(DateTime, nullable=True)

    # Relationships
    payer = relationship("User", foreign_keys=[payer_id], back_populates="payments_made")
    payee = relationship("User", foreign_keys=[payee_id], back_populates="payments_received")
    product = relationship("Product", back_populates="payments")

    __table_args__ = (
        Index('idx_payments_payer_status', 'payer_address', 'status'),
        Index('idx_payments_product_status', 'product_id', 'status'),
        Index('idx_payments_chain_block', 'chain', 'block_number'),
    )


class AccessLog(Base):
    """Content access log model."""

    __tablename__ = "access_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Access Details
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    payment_id = Column(UUID(as_uuid=True), ForeignKey("payments.id"), nullable=True)

    # Request Information
    ip_address = Column(String(45), nullable=False, index=True)  # IPv6 support
    user_agent = Column(Text, nullable=True)
    referer = Column(String(1000), nullable=True)
    request_url = Column(String(1000), nullable=False)
    request_method = Column(String(10), default="GET")

    # Access Control
    status = Column(SQLEnum(AccessLogStatus), nullable=False)
    access_granted = Column(Boolean, default=False)
    denial_reason = Column(String(200), nullable=True)

    # Geographic Information
    country_code = Column(String(2), nullable=True)
    region = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)

    # Technical Details
    response_size = Column(Integer, nullable=True)
    response_time_ms = Column(Integer, nullable=True)
    content_served = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="access_logs")
    product = relationship("Product", back_populates="access_logs")

    __table_args__ = (
        Index('idx_access_logs_product_status', 'product_id', 'status'),
        Index('idx_access_logs_ip_created', 'ip_address', 'created_at'),
        Index('idx_access_logs_user_created', 'user_id', 'created_at'),
    )


class Webhook(Base):
    """Webhook configuration model."""

    __tablename__ = "webhooks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Webhook Configuration
    url = Column(String(1000), nullable=False)
    secret = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)

    # Event Subscription
    subscribed_events = Column(JSON, nullable=False)  # List of WebhookEventType

    # Retry Configuration
    max_retries = Column(Integer, default=5)
    retry_delay = Column(Integer, default=60)  # seconds
    timeout = Column(Integer, default=30)  # seconds

    # Statistics
    success_count = Column(Integer, default=0)
    failure_count = Column(Integer, default=0)
    last_success_at = Column(DateTime, nullable=True)
    last_failure_at = Column(DateTime, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User")


class WebhookDelivery(Base):
    """Webhook delivery log model."""

    __tablename__ = "webhook_deliveries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    webhook_id = Column(UUID(as_uuid=True), ForeignKey("webhooks.id"), nullable=False)

    # Event Details
    event_type = Column(SQLEnum(WebhookEventType), nullable=False)
    payload = Column(JSON, nullable=False)

    # Delivery Information
    http_status = Column(Integer, nullable=True)
    response_body = Column(Text, nullable=True)
    response_time_ms = Column(Integer, nullable=True)

    # Retry Information
    attempt_count = Column(Integer, default=1)
    is_successful = Column(Boolean, default=False)
    error_message = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    delivered_at = Column(DateTime, nullable=True)

    # Relationships
    webhook = relationship("Webhook")

    __table_args__ = (
        Index('idx_webhook_deliveries_webhook_created', 'webhook_id', 'created_at'),
    )


class AnalyticsEvent(Base):
    """Analytics event model."""

    __tablename__ = "analytics_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Event Details
    event_type = Column(SQLEnum(AnalyticsEventType), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=True)

    # Session Information
    session_id = Column(String(100), nullable=True, index=True)
    visitor_id = Column(String(100), nullable=True, index=True)

    # Request Context
    ip_address = Column(String(45), nullable=False)
    user_agent = Column(Text, nullable=True)
    referer = Column(String(1000), nullable=True)

    # Event Properties
    properties = Column(JSON, nullable=True)

    # Geographic Information
    country_code = Column(String(2), nullable=True)
    region = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="analytics_events")
    product = relationship("Product", back_populates="analytics_events")

    __table_args__ = (
        Index('idx_analytics_events_type_created', 'event_type', 'created_at'),
        Index('idx_analytics_events_user_created', 'user_id', 'created_at'),
        Index('idx_analytics_events_product_created', 'product_id', 'created_at'),
    )


# =============================================================================
# PYDANTIC MODELS (DTOs)
# =============================================================================

class BaseDTO(BaseModel):
    """Base data transfer object."""

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Decimal: str,
            uuid.UUID: str,
        }


# User DTOs
class UserCreateDTO(BaseDTO):
    """User creation data."""
    email: str = Field(..., description="User email address")
    username: Optional[str] = Field(None, description="Unique username")
    password: str = Field(..., min_length=8, description="User password")
    full_name: Optional[str] = Field(None, description="User full name")
    role: UserRole = Field(UserRole.END_USER, description="User role")
    wallet_address: Optional[str] = Field(None, description="Blockchain wallet address")
    company_name: Optional[str] = Field(None, description="Company name")
    website_url: Optional[str] = Field(None, description="Website URL")


class UserUpdateDTO(BaseDTO):
    """User update data."""
    username: Optional[str] = None
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    timezone: Optional[str] = None
    language: Optional[str] = None
    wallet_address: Optional[str] = None
    preferred_chain: Optional[ChainType] = None
    company_name: Optional[str] = None
    website_url: Optional[str] = None
    description: Optional[str] = None


class UserResponseDTO(BaseDTO):
    """User response data."""
    id: uuid.UUID
    email: str
    username: Optional[str]
    full_name: Optional[str]
    role: UserRole
    status: UserStatus
    avatar_url: Optional[str]
    wallet_address: Optional[str]
    preferred_chain: ChainType
    company_name: Optional[str]
    website_url: Optional[str]
    created_at: datetime
    last_login_at: Optional[datetime]


# Product DTOs
class ProductCreateDTO(BaseDTO):
    """Product creation data."""
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    content_url: str = Field(..., description="URL to the content")
    type: ProductType = Field(ProductType.ARTICLE)
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    price: str = Field(..., description="Price in wei")
    currency: str = Field("ETH")
    payment_scheme: PaymentScheme = Field(PaymentScheme.EXACT)
    thumbnail_url: Optional[str] = None
    content_type: Optional[str] = None
    preview_content: Optional[str] = None
    access_duration: Optional[int] = None
    max_access_count: Optional[int] = None


class ProductUpdateDTO(BaseDTO):
    """Product update data."""
    title: Optional[str] = None
    description: Optional[str] = None
    content_url: Optional[str] = None
    type: Optional[ProductType] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    price: Optional[str] = None
    currency: Optional[str] = None
    payment_scheme: Optional[PaymentScheme] = None
    status: Optional[ProductStatus] = None
    thumbnail_url: Optional[str] = None
    content_type: Optional[str] = None
    preview_content: Optional[str] = None
    is_featured: Optional[bool] = None
    access_duration: Optional[int] = None
    max_access_count: Optional[int] = None


class ProductResponseDTO(BaseDTO):
    """Product response data."""
    id: uuid.UUID
    owner_id: uuid.UUID
    title: str
    description: Optional[str]
    content_url: str
    type: ProductType
    category: Optional[str]
    tags: Optional[List[str]]
    price: str
    currency: str
    payment_scheme: PaymentScheme
    status: ProductStatus
    is_featured: bool
    thumbnail_url: Optional[str]
    view_count: int
    purchase_count: int
    rating: Optional[Decimal]
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime]


# Payment DTOs
class PaymentCreateDTO(BaseDTO):
    """Payment creation data."""
    product_id: uuid.UUID
    payer_address: str
    payee_address: str
    amount: str = Field(..., description="Payment amount in wei")
    chain: ChainType
    currency: str = Field("ETH")
    payment_scheme: PaymentScheme = Field(PaymentScheme.EXACT)
    external_reference: Optional[str] = None


class PaymentUpdateDTO(BaseDTO):
    """Payment update data."""
    transaction_hash: Optional[str] = None
    status: Optional[PaymentStatus] = None
    block_number: Optional[int] = None
    confirmation_count: Optional[int] = None
    gas_used: Optional[int] = None
    gas_price: Optional[str] = None
    failure_reason: Optional[str] = None


class PaymentResponseDTO(BaseDTO):
    """Payment response data."""
    id: uuid.UUID
    transaction_hash: Optional[str]
    chain: ChainType
    block_number: Optional[int]
    payer_address: str
    payee_address: str
    product_id: uuid.UUID
    amount: str
    currency: str
    facilitator_fee: str
    status: PaymentStatus
    payment_scheme: PaymentScheme
    confirmation_count: int
    required_confirmations: int
    created_at: datetime
    updated_at: datetime
    expires_at: Optional[datetime]
    confirmed_at: Optional[datetime]


# Analytics DTOs
class AnalyticsRequestDTO(BaseDTO):
    """Analytics request parameters."""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    product_id: Optional[uuid.UUID] = None
    user_id: Optional[uuid.UUID] = None
    event_type: Optional[AnalyticsEventType] = None
    country_code: Optional[str] = None
    group_by: Optional[str] = None  # day, week, month, product, user, etc.
    limit: Optional[int] = Field(100, ge=1, le=10000)
    offset: Optional[int] = Field(0, ge=0)


class AnalyticsResponseDTO(BaseDTO):
    """Analytics response data."""
    total_count: int
    data: List[Dict[str, Any]]
    summary: Dict[str, Any]


# API Response DTOs
class PaginatedResponseDTO(BaseDTO):
    """Paginated response wrapper."""
    items: List[Any]
    total: int
    page: int
    size: int
    pages: int


class APIErrorDTO(BaseDTO):
    """API error response."""
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class HealthCheckDTO(BaseDTO):
    """Health check response."""
    status: str
    version: str
    timestamp: datetime
    components: Dict[str, Any]
    uptime: int  # seconds
