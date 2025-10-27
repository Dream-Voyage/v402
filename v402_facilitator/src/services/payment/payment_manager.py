"""
Payment management service for processing and tracking payments.

Handles payment creation, verification, settlement, and refunds.
"""

import logging
from core.config import get_settings
from datetime import datetime
from models.entities import Payment, PaymentStatus
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)
settings = get_settings()


class PaymentManager:
    """
    Manages payment lifecycle including creation, verification, settlement, and refunds.

    Features:
    - Payment request handling
    - Transaction verification
    - Settlement processing
    - Refund management
    - Payment status tracking
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_payment(
        self,
        product_id: str,
        client_id: str,
        amount: str,
        currency: str,
        method: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Payment:
        """
        Create a new payment record.

        Args:
            product_id: Product identifier
            client_id: Client identifier
            amount: Payment amount
            currency: Currency code
            method: Payment method
            metadata: Additional metadata

        Returns:
            Payment: Created payment object
        """
        logger.info(f"Creating payment for product {product_id}")

        try:
            payment = Payment(
                product_id=product_id,
                client_id=client_id,
                amount=amount,
                currency=currency,
                method=method,
                status=PaymentStatus.PENDING,
                metadata=metadata or {},
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )

            self.db.add(payment)
            await self.db.commit()
            await self.db.refresh(payment)

            logger.info(f"Payment {payment.id} created successfully")
            return payment

        except Exception as e:
            logger.error(f"Failed to create payment: {e}")
            await self.db.rollback()
            raise

    async def get_payment(self, payment_id: str) -> Optional[Payment]:
        """
        Retrieve a payment by ID.

        Args:
            payment_id: Payment identifier

        Returns:
            Payment or None if not found
        """
        try:
            result = await self.db.execute(
                select(Payment).where(Payment.id == payment_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Failed to get payment {payment_id}: {e}")
            raise

    async def update_payment_status(
        self,
        payment_id: str,
        status: PaymentStatus,
        transaction_hash: Optional[str] = None
    ) -> Optional[Payment]:
        """
        Update payment status.

        Args:
            payment_id: Payment identifier
            status: New payment status
            transaction_hash: Blockchain transaction hash

        Returns:
            Updated payment or None if not found
        """
        try:
            payment = await self.get_payment(payment_id)
            if not payment:
                logger.warning(f"Payment {payment_id} not found")
                return None

            payment.status = status
            payment.updated_at = datetime.utcnow()

            if transaction_hash:
                payment.transaction_hash = transaction_hash

            await self.db.commit()
            await self.db.refresh(payment)

            logger.info(f"Payment {payment_id} status updated to {status}")
            return payment

        except Exception as e:
            logger.error(f"Failed to update payment status: {e}")
            await self.db.rollback()
            raise

    async def verify_payment(
        self,
        payment_id: str,
        transaction_hash: str
    ) -> bool:
        """
        Verify payment transaction.

        Args:
            payment_id: Payment identifier
            transaction_hash: Transaction hash to verify

        Returns:
            True if verified, False otherwise
        """
        logger.info(f"Verifying payment {payment_id} with transaction {transaction_hash}")

        try:
            # TODO: Implement actual blockchain verification
            # This is a placeholder for blockchain verification logic

            payment = await self.get_payment(payment_id)
            if not payment:
                return False

            payment.status = PaymentStatus.CONFIRMED
            payment.transaction_hash = transaction_hash
            payment.updated_at = datetime.utcnow()

            await self.db.commit()

            logger.info(f"Payment {payment_id} verified successfully")
            return True

        except Exception as e:
            logger.error(f"Payment verification failed: {e}")
            return False

    async def get_payments_by_client(
        self,
        client_id: str,
        limit: int = 100
    ) -> List[Payment]:
        """
        Get all payments for a client.

        Args:
            client_id: Client identifier
            limit: Maximum number of payments to return

        Returns:
            List of payment objects
        """
        try:
            result = await self.db.execute(
                select(Payment)
                .where(Payment.client_id == client_id)
                .order_by(Payment.created_at.desc())
                .limit(limit)
            )
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Failed to get payments for client {client_id}: {e}")
            raise

