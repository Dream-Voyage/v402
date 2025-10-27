"""
Product management service.

This service handles all product-related business logic including creation,
updates, search, and analytics for content provider products.
"""

import uuid
from datetime import datetime
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.entities import (
    Product, ProductCreateDTO, ProductUpdateDTO, ProductStatus
)
from typing import List, Optional, Tuple, Dict, Any


class ProductService:
    """
    Service for managing products and content.

    Provides comprehensive product management functionality including:
    - CRUD operations with validation
    - Advanced search and filtering
    - Analytics and reporting
    - Access control and permissions
    - Content moderation support
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_product(
        self,
        owner_id: uuid.UUID,
        product_data: ProductCreateDTO
    ) -> Product:
        """
        Create a new product.

        Args:
            owner_id: UUID of the product owner
            product_data: Product creation data

        Returns:
            Created Product instance

        Raises:
            ValueError: If validation fails
        """
        # Validate price format
        try:
            price = int(product_data.price)
            if price < 0:
                raise ValueError("Price cannot be negative")
        except ValueError as e:
            if "invalid literal" in str(e):
                raise ValueError("Price must be a valid integer in wei")
            raise

        # Check for duplicate slug if provided
        if product_data.slug:
            existing = await self.db.execute(
                text("SELECT id FROM products WHERE slug = :slug"),
                {"slug": product_data.slug}
            )
            if existing.fetchone():
                raise ValueError(f"Slug '{product_data.slug}' already exists")

        # Generate slug if not provided
        slug = product_data.slug or self._generate_slug(product_data.title)

        # Create product instance
        product = Product(
            owner_id=owner_id,
            title=product_data.title,
            description=product_data.description,
            content_url=product_data.content_url,
            thumbnail_url=product_data.thumbnail_url,
            type=product_data.type,
            category=product_data.category,
            tags=product_data.tags,
            price=price,
            currency=product_data.currency,
            payment_scheme=product_data.payment_scheme,
            content_type=product_data.content_type,
            preview_content=product_data.preview_content,
            access_duration=product_data.access_duration,
            max_access_count=product_data.max_access_count,
            slug=slug,
            status=ProductStatus.DRAFT,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        self.db.add(product)
        await self.db.commit()
        await self.db.refresh(product)

        return product

    async def get_product_by_id(self, product_id: uuid.UUID) -> Optional[Product]:
        """
        Get product by ID with owner information.

        Args:
            product_id: UUID of the product

        Returns:
            Product instance or None if not found
        """
        result = await self.db.execute(
            text("""
                SELECT p.*, u.email as owner_email, u.username as owner_username,
                       u.company_name as owner_company
                FROM products p
                JOIN users u ON p.owner_id = u.id
                WHERE p.id = :product_id AND p.deleted_at IS NULL
            """),
            {"product_id": str(product_id)}
        )

        row = result.fetchone()
        if not row:
            return None

        # Convert row to Product object (simplified)
        product = Product()
        for key, value in row._asdict().items():
            if hasattr(product, key):
                setattr(product, key, value)

        return product

    async def list_products(
        self,
        filters: Dict[str, Any],
        page: int = 1,
        size: int = 20,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> Tuple[List[Product], int]:
        """
        List products with advanced filtering and pagination.

        Args:
            filters: Dictionary of filter criteria
            page: Page number (1-based)
            size: Items per page
            sort_by: Field to sort by
            sort_order: Sort direction (asc/desc)

        Returns:
            Tuple of (products list, total count)
        """
        # Build WHERE clause
        where_conditions = ["p.deleted_at IS NULL"]
        params = {}

        if filters.get("owner_id"):
            where_conditions.append("p.owner_id = :owner_id")
            params["owner_id"] = str(filters["owner_id"])

        if filters.get("status"):
            where_conditions.append("p.status = :status")
            params["status"] = filters["status"]

        if filters.get("category"):
            where_conditions.append("p.category = :category")
            params["category"] = filters["category"]

        if filters.get("type"):
            where_conditions.append("p.type = :type")
            params["type"] = filters["type"]

        if filters.get("search"):
            where_conditions.append(
                "(p.title ILIKE :search OR p.description ILIKE :search)"
            )
            params["search"] = f"%{filters['search']}%"

        if filters.get("min_price"):
            where_conditions.append("p.price >= :min_price")
            params["min_price"] = filters["min_price"]

        if filters.get("max_price"):
            where_conditions.append("p.price <= :max_price")
            params["max_price"] = filters["max_price"]

        where_clause = " AND ".join(where_conditions)

        # Validate sort parameters
        valid_sort_fields = [
            "created_at", "updated_at", "title", "price", "view_count",
            "purchase_count", "rating", "published_at"
        ]
        if sort_by not in valid_sort_fields:
            sort_by = "created_at"

        sort_direction = "DESC" if sort_order.lower() == "desc" else "ASC"

        # Count query
        count_query = f"""
            SELECT COUNT(*) as total
            FROM products p
            WHERE {where_clause}
        """

        count_result = await self.db.execute(text(count_query), params)
        total = count_result.scalar()

        # Main query with pagination
        offset = (page - 1) * size

        list_query = f"""
            SELECT p.*, u.email as owner_email, u.username as owner_username,
                   u.company_name as owner_company
            FROM products p
            JOIN users u ON p.owner_id = u.id
            WHERE {where_clause}
            ORDER BY p.{sort_by} {sort_direction}
            LIMIT :limit OFFSET :offset
        """

        params.update({"limit": size, "offset": offset})

        result = await self.db.execute(text(list_query), params)
        rows = result.fetchall()

        # Convert rows to Product objects
        products = []
        for row in rows:
            product = Product()
            for key, value in row._asdict().items():
                if hasattr(product, key):
                    setattr(product, key, value)
            products.append(product)

        return products, total

    async def update_product(
        self,
        product_id: uuid.UUID,
        product_data: ProductUpdateDTO
    ) -> Product:
        """
        Update an existing product.

        Args:
            product_id: UUID of the product to update
            product_data: Update data

        Returns:
            Updated Product instance

        Raises:
            ValueError: If product not found or validation fails
        """
        # Get existing product
        product = await self.get_product_by_id(product_id)
        if not product:
            raise ValueError("Product not found")

        # Build update query dynamically
        update_fields = []
        params = {"product_id": str(product_id), "updated_at": datetime.utcnow()}

        # Only update provided fields
        update_data = product_data.dict(exclude_unset=True)

        for field, value in update_data.items():
            if field == "price" and value is not None:
                # Validate price
                try:
                    price = int(value)
                    if price < 0:
                        raise ValueError("Price cannot be negative")
                    update_fields.append(f"{field} = :price")
                    params["price"] = price
                except ValueError as e:
                    if "invalid literal" in str(e):
                        raise ValueError("Price must be a valid integer in wei")
                    raise
            elif field == "slug" and value:
                # Check for duplicate slug
                existing = await self.db.execute(
                    text("SELECT id FROM products WHERE slug = :slug AND id != :product_id"),
                    {"slug": value, "product_id": str(product_id)}
                )
                if existing.fetchone():
                    raise ValueError(f"Slug '{value}' already exists")
                update_fields.append(f"{field} = :{field}")
                params[field] = value
            elif value is not None:
                update_fields.append(f"{field} = :{field}")
                params[field] = value

        if not update_fields:
            return product

        # Execute update
        update_query = f"""
            UPDATE products 
            SET {', '.join(update_fields)}, updated_at = :updated_at
            WHERE id = :product_id AND deleted_at IS NULL
        """

        await self.db.execute(text(update_query), params)
        await self.db.commit()

        # Return updated product
        return await self.get_product_by_id(product_id)

    async def delete_product(
        self,
        product_id: uuid.UUID,
        soft_delete: bool = True
    ) -> bool:
        """
        Delete a product (soft delete by default).

        Args:
            product_id: UUID of the product to delete
            soft_delete: Whether to soft delete (recommended)

        Returns:
            True if deleted successfully

        Raises:
            ValueError: If product not found
        """
        # Check if product exists
        product = await self.get_product_by_id(product_id)
        if not product:
            raise ValueError("Product not found")

        if soft_delete:
            # Soft delete - mark as deleted
            await self.db.execute(
                text("""
                    UPDATE products 
                    SET deleted_at = :deleted_at, status = :status, updated_at = :updated_at
                    WHERE id = :product_id
                """),
                {
                    "product_id": str(product_id),
                    "deleted_at": datetime.utcnow(),
                    "status": ProductStatus.DELETED,
                    "updated_at": datetime.utcnow()
                }
            )
        else:
            # Hard delete - remove from database
            await self.db.execute(
                text("DELETE FROM products WHERE id = :product_id"),
                {"product_id": str(product_id)}
            )

        await self.db.commit()
        return True

    async def get_product_analytics(
        self,
        product_id: uuid.UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive analytics for a product.

        Args:
            product_id: UUID of the product
            start_date: Start date for analytics period
            end_date: End date for analytics period

        Returns:
            Dictionary with analytics data
        """
        # Default date range (last 30 days)
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = datetime.utcnow().replace(day=1)  # First day of month

        # Access logs analytics
        access_query = text("""
            SELECT 
                DATE(created_at) as date,
                COUNT(*) as total_accesses,
                COUNT(CASE WHEN access_granted = true THEN 1 END) as successful_accesses,
                COUNT(CASE WHEN payment_id IS NOT NULL THEN 1 END) as paid_accesses,
                COUNT(DISTINCT ip_address) as unique_visitors,
                COUNT(DISTINCT country_code) as unique_countries
            FROM access_logs
            WHERE product_id = :product_id 
                AND created_at >= :start_date 
                AND created_at <= :end_date
            GROUP BY DATE(created_at)
            ORDER BY date
        """)

        access_result = await self.db.execute(access_query, {
            "product_id": str(product_id),
            "start_date": start_date,
            "end_date": end_date
        })

        access_data = [dict(row._asdict()) for row in access_result.fetchall()]

        # Payment analytics
        payment_query = text("""
            SELECT 
                DATE(created_at) as date,
                COUNT(*) as payment_attempts,
                COUNT(CASE WHEN status = 'confirmed' THEN 1 END) as successful_payments,
                COALESCE(SUM(CASE WHEN status = 'confirmed' THEN amount::numeric END), 0) as total_revenue,
                AVG(CASE WHEN status = 'confirmed' THEN amount::numeric END) as avg_payment_amount
            FROM payments
            WHERE product_id = :product_id 
                AND created_at >= :start_date 
                AND created_at <= :end_date
            GROUP BY DATE(created_at)
            ORDER BY date
        """)

        payment_result = await self.db.execute(payment_query, {
            "product_id": str(product_id),
            "start_date": start_date,
            "end_date": end_date
        })

        payment_data = [dict(row._asdict()) for row in payment_result.fetchall()]

        # Geographic distribution
        geo_query = text("""
            SELECT 
                country_code,
                COUNT(*) as access_count,
                COUNT(CASE WHEN access_granted = true THEN 1 END) as successful_count
            FROM access_logs
            WHERE product_id = :product_id 
                AND created_at >= :start_date 
                AND created_at <= :end_date
                AND country_code IS NOT NULL
            GROUP BY country_code
            ORDER BY access_count DESC
            LIMIT 10
        """)

        geo_result = await self.db.execute(geo_query, {
            "product_id": str(product_id),
            "start_date": start_date,
            "end_date": end_date
        })

        geo_data = [dict(row._asdict()) for row in geo_result.fetchall()]

        # Summary statistics
        summary_query = text("""
            SELECT 
                p.view_count,
                p.purchase_count,
                p.rating,
                COALESCE(SUM(CASE WHEN pay.status = 'confirmed' THEN pay.amount::numeric END), 0) as total_revenue,
                COUNT(DISTINCT al.ip_address) as unique_visitors,
                COUNT(al.id) as total_accesses
            FROM products p
            LEFT JOIN payments pay ON p.id = pay.product_id
            LEFT JOIN access_logs al ON p.id = al.product_id 
                AND al.created_at >= :start_date 
                AND al.created_at <= :end_date
            WHERE p.id = :product_id
            GROUP BY p.id, p.view_count, p.purchase_count, p.rating
        """)

        summary_result = await self.db.execute(summary_query, {
            "product_id": str(product_id),
            "start_date": start_date,
            "end_date": end_date
        })

        summary = dict(summary_result.fetchone()._asdict())

        # Calculate conversion rate
        conversion_rate = 0
        if summary["total_accesses"] > 0:
            conversion_rate = summary["purchase_count"] / summary["total_accesses"]

        return {
            "summary": {
                **summary,
                "conversion_rate": conversion_rate,
                "period_start": start_date.isoformat(),
                "period_end": end_date.isoformat()
            },
            "daily_access": access_data,
            "daily_payments": payment_data,
            "geographic_distribution": geo_data,
            "trends": self._calculate_trends(access_data, payment_data)
        }

    async def search_products(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        page: int = 1,
        size: int = 20
    ) -> Tuple[List[Product], int]:
        """
        Full-text search for products.

        Args:
            query: Search query
            filters: Additional filters
            page: Page number
            size: Items per page

        Returns:
            Tuple of (products, total_count)
        """
        filters = filters or {}
        filters["search"] = query

        return await self.list_products(
            filters=filters,
            page=page,
            size=size,
            sort_by="created_at",
            sort_order="desc"
        )

    def _generate_slug(self, title: str) -> str:
        """
        Generate URL-friendly slug from title.

        Args:
            title: Product title

        Returns:
            URL-friendly slug
        """
        import re

        # Convert to lowercase and replace spaces/special chars
        slug = re.sub(r'[^a-zA-Z0-9\s-]', '', title.lower())
        slug = re.sub(r'[\s-]+', '-', slug).strip('-')

        # Truncate if too long
        if len(slug) > 50:
            slug = slug[:50].rstrip('-')

        # Add random suffix to ensure uniqueness
        import secrets
        return f"{slug}-{secrets.token_hex(4)}"

    def _calculate_trends(
        self,
        access_data: List[Dict[str, Any]],
        payment_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate trend analysis from daily data.

        Args:
            access_data: Daily access statistics
            payment_data: Daily payment statistics

        Returns:
            Trend analysis
        """
        if len(access_data) < 2 or len(payment_data) < 2:
            return {
                "access_trend": 0,
                "revenue_trend": 0,
                "conversion_trend": 0
            }

        # Calculate simple growth rates
        first_access = access_data[0]["total_accesses"]
        last_access = access_data[-1]["total_accesses"]
        access_trend = ((last_access - first_access) / max(first_access, 1)) * 100

        first_revenue = float(payment_data[0]["total_revenue"] or 0)
        last_revenue = float(payment_data[-1]["total_revenue"] or 0)
        revenue_trend = ((last_revenue - first_revenue) / max(first_revenue, 1)) * 100

        # Calculate conversion trend
        first_conversion = (
            payment_data[0]["successful_payments"] / max(first_access, 1)
        )
        last_conversion = (
            payment_data[-1]["successful_payments"] / max(last_access, 1)
        )
        conversion_trend = ((last_conversion - first_conversion) / max(first_conversion, 0.01)) * 100

        return {
            "access_trend": round(access_trend, 2),
            "revenue_trend": round(revenue_trend, 2),
            "conversion_trend": round(conversion_trend, 2)
        }
