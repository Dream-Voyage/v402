"""
Payment history management.
"""

import time
from datetime import datetime
from typing import List, Optional
from v402_client.types.enums import PaymentStatus, PaymentScheme, ChainType
from v402_client.types.models import PaymentHistory, PaymentStatistics


class PaymentHistoryManager:
    """Manages payment history and statistics."""

    def __init__(self, logger):
        self.logger = logger
        self._history: List[PaymentHistory] = []

    async def record_payment(
        self,
        url: str,
        amount: str,
        network: str,
        payer: str,
        payee: str,
        transaction_hash: str,
        description: str,
        status: PaymentStatus,
    ):
        """Record a new payment."""
        payment = PaymentHistory(
            payment_id=f"pay_{int(time.time())}_{len(self._history)}",
            url=url,
            amount=amount,
            transaction_hash=transaction_hash,
            network=network,
            chain_type=ChainType.EVM,  # Default to EVM
            payer=payer,
            payee=payee,
            timestamp=datetime.utcnow(),
            status=status,
            description=description,
            scheme=PaymentScheme.EXACT,
        )

        self._history.append(payment)
        self.logger.info(f"Recorded payment: {payment.payment_id}")

    async def get_history(
        self,
        limit: Optional[int] = None,
        since: Optional[time.struct_time] = None
    ) -> List[PaymentHistory]:
        """Get payment history."""
        history = self._history

        if since:
            since_dt = datetime.fromtimestamp(time.mktime(since))
            history = [p for p in history if p.timestamp >= since_dt]

        if limit:
            history = history[-limit:]

        return history

    async def get_statistics(
        self,
        start_time: Optional[time.struct_time] = None,
        end_time: Optional[time.struct_time] = None,
    ) -> PaymentStatistics:
        """Get payment statistics."""
        payments = self._history

        if start_time:
            start_dt = datetime.fromtimestamp(time.mktime(start_time))
            payments = [p for p in payments if p.timestamp >= start_dt]

        if end_time:
            end_dt = datetime.fromtimestamp(time.mktime(end_time))
            payments = [p for p in payments if p.timestamp <= end_dt]

        if not payments:
            return PaymentStatistics(
                total_payments=0,
                successful_payments=0,
                failed_payments=0,
                total_amount="0",
                average_amount="0",
                min_amount="0",
                max_amount="0",
                unique_resources=0,
                unique_networks=0,
                time_period_start=datetime.utcnow(),
                time_period_end=datetime.utcnow(),
            )

        successful = [p for p in payments if p.status == PaymentStatus.CONFIRMED]
        amounts = [int(p.amount) for p in successful]

        return PaymentStatistics(
            total_payments=len(payments),
            successful_payments=len(successful),
            failed_payments=len(payments) - len(successful),
            total_amount=str(sum(amounts)),
            average_amount=str(sum(amounts) // len(amounts) if amounts else 0),
            min_amount=str(min(amounts) if amounts else 0),
            max_amount=str(max(amounts) if amounts else 0),
            unique_resources=len(set(p.url for p in payments)),
            unique_networks=len(set(p.network for p in payments)),
            time_period_start=min(p.timestamp for p in payments),
            time_period_end=max(p.timestamp for p in payments),
        )
