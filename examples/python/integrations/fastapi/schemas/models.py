"""
Pydantic schemas for FastAPI integration
"""

from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class ProductStatus(str, Enum):
    """Product status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DRAFT = "draft"

class PaymentStatus(str, Enum):
    """Payment status enumeration"""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

class AccessType(str, Enum):
    """Access type enumeration"""
    VIEW = "view"
    PURCHASE = "purchase"
    ACCESS = "access"

class MetricType(str, Enum):
    """Metric type enumeration"""
    VIEWS = "views"
    PURCHASES = "purchases"
    REVENUE = "revenue"

class PeriodType(str, Enum):
    """Period type enumeration"""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"

# Product Schemas
class ProductBase(BaseModel):
    """Base product schema"""
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=1000)
    price: str = Field(..., regex=r'^\d+\.\d{2}$')
    currency: str = Field(default="USDC", max_length=10)
    content_url: str = Field(..., min_length=1, max_length=500)
    category: Optional[str] = Field(None, max_length=50)
    tags: Optional[List[str]] = Field(default_factory=list)
    author: Optional[str] = Field(None, max_length=100)

class ProductCreate(ProductBase):
    """Product creation schema"""
    pass

class ProductUpdate(BaseModel):
    """Product update schema"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1, max_length=1000)
    price: Optional[str] = Field(None, regex=r'^\d+\.\d{2}$')
    currency: Optional[str] = Field(None, max_length=10)
    content_url: Optional[str] = Field(None, min_length=1, max_length=500)
    category: Optional[str] = Field(None, max_length=50)
    tags: Optional[List[str]] = None
    author: Optional[str] = Field(None, max_length=100)
    status: Optional[ProductStatus] = None

class Product(ProductBase):
    """Product response schema"""
    id: str
    status: ProductStatus
    view_count: int = 0
    purchase_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ProductList(BaseModel):
    """Product list response schema"""
    products: List[Product]
    total: int
    page: int
    limit: int
    has_next: bool
    has_prev: bool

# Payment Schemas
class PaymentRequest(BaseModel):
    """Payment request schema"""
    product_id: str
    amount: str
    currency: str
    user_address: str = Field(..., regex=r'^0x[a-fA-F0-9]{40}$')
    nonce: str
    signature: str

class PaymentResponse(BaseModel):
    """Payment response schema"""
    transaction_hash: str
    status: PaymentStatus
    amount: str
    currency: str
    timestamp: datetime
    block_number: Optional[int]
    gas_used: Optional[int]
    error: Optional[str]

class PaymentList(BaseModel):
    """Payment list response schema"""
    payments: List[PaymentResponse]
    total: int
    page: int
    limit: int

# Access Schemas
class AccessRequest(BaseModel):
    """Access request schema"""
    product_id: str
    user_address: str = Field(..., regex=r'^0x[a-fA-F0-9]{40}$')
    timestamp: int
    signature: str

class AccessResponse(BaseModel):
    """Access response schema"""
    has_access: bool
    reason: Optional[str]
    expires_at: Optional[int]

# Analytics Schemas
class AnalyticsRequest(BaseModel):
    """Analytics request schema"""
    product_id: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    period: PeriodType = PeriodType.DAILY

class AnalyticsResponse(BaseModel):
    """Analytics response schema"""
    product_id: Optional[str]
    views: int
    purchases: int
    revenue: str
    currency: str
    period: PeriodType
    generated_at: datetime
    conversion_rate: float
    top_countries: List[Dict[str, Any]]
    top_referrers: List[Dict[str, Any]]

class MetricData(BaseModel):
    """Metric data schema"""
    metric_type: MetricType
    value: float
    currency: Optional[str]
    date: datetime
    metadata: Optional[Dict[str, Any]]

# User Schemas
class UserBase(BaseModel):
    """Base user schema"""
    public_key: str = Field(..., regex=r'^0x[a-fA-F0-9]{40}$')
    username: Optional[str] = Field(None, max_length=50)
    email: Optional[str] = Field(None, max_length=100)

class UserCreate(UserBase):
    """User creation schema"""
    pass

class UserUpdate(BaseModel):
    """User update schema"""
    username: Optional[str] = Field(None, max_length=50)
    email: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None

class User(UserBase):
    """User response schema"""
    id: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Access Log Schemas
class AccessLogCreate(BaseModel):
    """Access log creation schema"""
    product_id: str
    user_address: str = Field(..., regex=r'^0x[a-fA-F0-9]{40}$')
    access_type: AccessType
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    referrer: Optional[str] = None
    country: Optional[str] = Field(None, max_length=2)

class AccessLog(BaseModel):
    """Access log response schema"""
    id: str
    product_id: str
    user_address: str
    access_type: AccessType
    ip_address: Optional[str]
    user_agent: Optional[str]
    referrer: Optional[str]
    country: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

# Error Schemas
class ErrorResponse(BaseModel):
    """Error response schema"""
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ValidationError(BaseModel):
    """Validation error schema"""
    field: str
    message: str
    value: Optional[Any] = None

class ValidationErrorResponse(BaseModel):
    """Validation error response schema"""
    errors: List[ValidationError]
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# Health Check Schema
class HealthCheck(BaseModel):
    """Health check response schema"""
    status: str
    timestamp: datetime
    version: str
    uptime: Optional[float] = None
    database_status: Optional[str] = None
    redis_status: Optional[str] = None
