"""
FastAPI Integration Example for v402 Protocol
This example demonstrates how to integrate v402 protocol with FastAPI
"""

import logging
import uvicorn
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="v402 FastAPI Integration",
    description="Example FastAPI application integrated with v402 protocol",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Pydantic Models
class ProductCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=1000)
    price: str = Field(..., regex=r'^\d+\.\d{2}$')
    currency: str = Field(default="USDC", max_length=10)
    content_url: str = Field(..., min_length=1)
    category: Optional[str] = Field(None, max_length=50)
    tags: Optional[List[str]] = Field(default_factory=list)
    author: Optional[str] = Field(None, max_length=100)

class ProductUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1, max_length=1000)
    price: Optional[str] = Field(None, regex=r'^\d+\.\d{2}$')
    currency: Optional[str] = Field(None, max_length=10)
    content_url: Optional[str] = Field(None, min_length=1)
    category: Optional[str] = Field(None, max_length=50)
    tags: Optional[List[str]] = None
    author: Optional[str] = Field(None, max_length=100)
    status: Optional[str] = Field(None, regex=r'^(active|inactive|draft)$')

class Product(BaseModel):
    id: str
    title: str
    description: str
    price: str
    currency: str
    content_url: str
    category: Optional[str]
    tags: List[str]
    author: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime
    view_count: int = 0
    purchase_count: int = 0

class PaymentRequest(BaseModel):
    product_id: str
    amount: str
    currency: str
    user_address: str
    nonce: str
    signature: str

class PaymentResponse(BaseModel):
    transaction_hash: str
    status: str
    amount: str
    currency: str
    timestamp: datetime
    block_number: Optional[int]
    gas_used: Optional[int]
    error: Optional[str]

class AccessRequest(BaseModel):
    product_id: str
    user_address: str
    timestamp: int
    signature: str

class AccessResponse(BaseModel):
    has_access: bool
    reason: Optional[str]
    expires_at: Optional[int]

class AnalyticsRequest(BaseModel):
    product_id: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    period: str = Field(default="daily", regex=r'^(hourly|daily|weekly|monthly)$')

class AnalyticsResponse(BaseModel):
    product_id: Optional[str]
    views: int
    purchases: int
    revenue: str
    currency: str
    period: str
    generated_at: datetime
    conversion_rate: float
    top_countries: List[Dict[str, Any]]
    top_referrers: List[Dict[str, Any]]

# Dependency for authentication
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Extract user information from JWT token"""
    # In a real implementation, you would decode and validate the JWT token
    # For this example, we'll just return a mock user
    return {
        "user_id": "user-123",
        "public_key": "0x1234567890abcdef1234567890abcdef12345678",
        "permissions": ["read", "write", "admin"]
    }

# Mock database (in real implementation, use a proper database)
products_db: Dict[str, Product] = {}
payments_db: Dict[str, PaymentResponse] = {}

# Product endpoints
@app.post("/api/v1/products", response_model=Product, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: ProductCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new product"""
    try:
        # Generate product ID
        product_id = f"product-{len(products_db) + 1}"

        # Create product
        product = Product(
            id=product_id,
            title=product_data.title,
            description=product_data.description,
            price=product_data.price,
            currency=product_data.currency,
            content_url=product_data.content_url,
            category=product_data.category,
            tags=product_data.tags or [],
            author=product_data.author,
            status="active",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        # Store in database
        products_db[product_id] = product

        logger.info(f"Created product {product_id} by user {current_user['user_id']}")
        return product

    except Exception as e:
        logger.error(f"Error creating product: {e}")
        raise HTTPException(status_code=500, detail="Failed to create product")

@app.get("/api/v1/products", response_model=List[Product])
async def list_products(
    skip: int = 0,
    limit: int = 10,
    category: Optional[str] = None,
    status: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """List products with pagination and filtering"""
    try:
        products = list(products_db.values())

        # Apply filters
        if category:
            products = [p for p in products if p.category == category]
        if status:
            products = [p for p in products if p.status == status]

        # Apply pagination
        products = products[skip:skip + limit]

        return products

    except Exception as e:
        logger.error(f"Error listing products: {e}")
        raise HTTPException(status_code=500, detail="Failed to list products")

@app.get("/api/v1/products/{product_id}", response_model=Product)
async def get_product(
    product_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific product by ID"""
    try:
        if product_id not in products_db:
            raise HTTPException(status_code=404, detail="Product not found")

        product = products_db[product_id]

        # Increment view count
        product.view_count += 1
        products_db[product_id] = product

        return product

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting product: {e}")
        raise HTTPException(status_code=500, detail="Failed to get product")

@app.put("/api/v1/products/{product_id}", response_model=Product)
async def update_product(
    product_id: str,
    product_data: ProductUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update a product"""
    try:
        if product_id not in products_db:
            raise HTTPException(status_code=404, detail="Product not found")

        product = products_db[product_id]

        # Update fields
        update_data = product_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(product, field, value)

        product.updated_at = datetime.utcnow()
        products_db[product_id] = product

        logger.info(f"Updated product {product_id} by user {current_user['user_id']}")
        return product

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating product: {e}")
        raise HTTPException(status_code=500, detail="Failed to update product")

@app.delete("/api/v1/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a product"""
    try:
        if product_id not in products_db:
            raise HTTPException(status_code=404, detail="Product not found")

        del products_db[product_id]

        logger.info(f"Deleted product {product_id} by user {current_user['user_id']}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting product: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete product")

# Payment endpoints
@app.post("/api/v1/payments", response_model=PaymentResponse)
async def process_payment(
    payment_data: PaymentRequest,
    current_user: dict = Depends(get_current_user)
):
    """Process a payment for a product"""
    try:
        # Validate product exists
        if payment_data.product_id not in products_db:
            raise HTTPException(status_code=404, detail="Product not found")

        # In a real implementation, you would:
        # 1. Verify the signature
        # 2. Process the blockchain transaction
        # 3. Update the product purchase count

        # Mock payment processing
        transaction_hash = f"0x{'a' * 64}"

        payment_response = PaymentResponse(
            transaction_hash=transaction_hash,
            status="completed",
            amount=payment_data.amount,
            currency=payment_data.currency,
            timestamp=datetime.utcnow(),
            block_number=12345678,
            gas_used=50000
        )

        # Store payment
        payments_db[transaction_hash] = payment_response

        # Update product purchase count
        product = products_db[payment_data.product_id]
        product.purchase_count += 1
        products_db[payment_data.product_id] = product

        logger.info(f"Processed payment {transaction_hash} for product {payment_data.product_id}")
        return payment_response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing payment: {e}")
        raise HTTPException(status_code=500, detail="Failed to process payment")

@app.get("/api/v1/payments/{transaction_hash}", response_model=PaymentResponse)
async def get_payment(
    transaction_hash: str,
    current_user: dict = Depends(get_current_user)
):
    """Get payment details by transaction hash"""
    try:
        if transaction_hash not in payments_db:
            raise HTTPException(status_code=404, detail="Payment not found")

        return payments_db[transaction_hash]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting payment: {e}")
        raise HTTPException(status_code=500, detail="Failed to get payment")

# Access control endpoints
@app.post("/api/v1/access/check", response_model=AccessResponse)
async def check_access(
    access_data: AccessRequest,
    current_user: dict = Depends(get_current_user)
):
    """Check if a user has access to a product"""
    try:
        # In a real implementation, you would:
        # 1. Verify the signature
        # 2. Check if the user has paid for the product
        # 3. Check if the access hasn't expired

        # Mock access check
        has_access = access_data.product_id in products_db

        response = AccessResponse(
            has_access=has_access,
            reason="Payment verified" if has_access else "No payment found",
            expires_at=int((datetime.utcnow() + timedelta(days=30)).timestamp()) if has_access else None
        )

        return response

    except Exception as e:
        logger.error(f"Error checking access: {e}")
        raise HTTPException(status_code=500, detail="Failed to check access")

# Analytics endpoints
@app.post("/api/v1/analytics", response_model=AnalyticsResponse)
async def get_analytics(
    analytics_data: AnalyticsRequest,
    current_user: dict = Depends(get_current_user)
):
    """Get analytics data"""
    try:
        # In a real implementation, you would query analytics data from the database

        # Mock analytics data
        analytics = AnalyticsResponse(
            product_id=analytics_data.product_id,
            views=1250,
            purchases=45,
            revenue="450.00",
            currency="USDC",
            period=analytics_data.period,
            generated_at=datetime.utcnow(),
            conversion_rate=3.6,
            top_countries=[
                {"code": "US", "name": "United States", "count": 25},
                {"code": "GB", "name": "United Kingdom", "count": 12},
                {"code": "DE", "name": "Germany", "count": 8}
            ],
            top_referrers=[
                {"domain": "google.com", "count": 45},
                {"domain": "twitter.com", "count": 23},
                {"domain": "reddit.com", "count": 12}
            ]
        )

        return analytics

    except Exception as e:
        logger.error(f"Error getting analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get analytics")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow()}

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "v402 FastAPI Integration Example",
        "version": "1.0.0",
        "docs": "/docs"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
