"""
Database models and schemas for FastAPI integration
"""

import uuid
from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from typing import Dict, Any

Base = declarative_base()

class Product(Base):
    """Product model"""
    __tablename__ = "products"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    price = Column(String(20), nullable=False)
    currency = Column(String(10), default="USDC")
    content_url = Column(String(500), nullable=False)
    category = Column(String(50), nullable=True)
    tags = Column(JSON, default=list)
    author = Column(String(100), nullable=True)
    status = Column(String(20), default="active")
    view_count = Column(Integer, default=0)
    purchase_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "price": self.price,
            "currency": self.currency,
            "content_url": self.content_url,
            "category": self.category,
            "tags": self.tags or [],
            "author": self.author,
            "status": self.status,
            "view_count": self.view_count,
            "purchase_count": self.purchase_count,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

class Payment(Base):
    """Payment model"""
    __tablename__ = "payments"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    transaction_hash = Column(String(66), unique=True, nullable=False)
    product_id = Column(String, nullable=False)
    user_address = Column(String(42), nullable=False)
    amount = Column(String(20), nullable=False)
    currency = Column(String(10), nullable=False)
    status = Column(String(20), nullable=False)
    block_number = Column(Integer, nullable=True)
    gas_used = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "transaction_hash": self.transaction_hash,
            "product_id": self.product_id,
            "user_address": self.user_address,
            "amount": self.amount,
            "currency": self.currency,
            "status": self.status,
            "block_number": self.block_number,
            "gas_used": self.gas_used,
            "error_message": self.error_message,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

class User(Base):
    """User model"""
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    public_key = Column(String(42), unique=True, nullable=False)
    username = Column(String(50), unique=True, nullable=True)
    email = Column(String(100), unique=True, nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "public_key": self.public_key,
            "username": self.username,
            "email": self.email,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

class AccessLog(Base):
    """Access log model"""
    __tablename__ = "access_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id = Column(String, nullable=False)
    user_address = Column(String(42), nullable=False)
    access_type = Column(String(20), nullable=False)  # view, purchase, access
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    referrer = Column(String(500), nullable=True)
    country = Column(String(2), nullable=True)
    created_at = Column(DateTime, default=func.now())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "product_id": self.product_id,
            "user_address": self.user_address,
            "access_type": self.access_type,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "referrer": self.referrer,
            "country": self.country,
            "created_at": self.created_at
        }

class Analytics(Base):
    """Analytics model"""
    __tablename__ = "analytics"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id = Column(String, nullable=True)
    metric_type = Column(String(50), nullable=False)  # views, purchases, revenue
    metric_value = Column(Float, nullable=False)
    currency = Column(String(10), nullable=True)
    period = Column(String(20), nullable=False)  # hourly, daily, weekly, monthly
    date = Column(DateTime, nullable=False)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=func.now())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "product_id": self.product_id,
            "metric_type": self.metric_type,
            "metric_value": self.metric_value,
            "currency": self.currency,
            "period": self.period,
            "date": self.date,
            "metadata": self.metadata or {},
            "created_at": self.created_at
        }
