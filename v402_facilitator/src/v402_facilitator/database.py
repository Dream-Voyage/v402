"""
Database models and operations for v402 Facilitator.
"""

import logging
from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Text,
)
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)
from sqlalchemy.future import select
from sqlalchemy.orm import declarative_base
from typing import Optional, List

logger = logging.getLogger(__name__)

Base = declarative_base()


class Transaction(Base):
    """Database model for transaction records."""

    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    transaction_hash = Column(String(66), unique=True, nullable=False, index=True)
    payer = Column(String(42), nullable=False, index=True)
    payee = Column(String(42), nullable=False, index=True)
    amount = Column(String(78), nullable=False)  # uint256 as string
    network = Column(String(50), nullable=False)
    scheme = Column(String(50), nullable=False)
    resource = Column(Text, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    status = Column(
        String(20), nullable=False, default="pending"
    )  # pending, confirmed, failed
    gas_used = Column(String(78), nullable=True)
    block_number = Column(Integer, nullable=True)

    def __repr__(self) -> str:
        return (
            f"<Transaction(hash={self.transaction_hash}, "
            f"payer={self.payer}, amount={self.amount})>"
        )


class DiscoveryResourceModel(Base):
    """Database model for discoverable resources."""

    __tablename__ = "discovery_resources"

    id = Column(Integer, primary_key=True, autoincrement=True)
    resource = Column(Text, nullable=False, unique=True, index=True)
    type = Column(String(20), nullable=False, default="http")
    x402_version = Column(Integer, nullable=False, default=1)
    accepts = Column(Text, nullable=False)  # JSON string
    last_updated = Column(DateTime, nullable=False, default=datetime.utcnow)
    metadata = Column(Text, nullable=True)  # JSON string

    def __repr__(self) -> str:
        return f"<DiscoveryResource(resource={self.resource}, type={self.type})>"


class DatabaseManager:
    """
    Manages database connections and operations.

    Handles both SQLite and PostgreSQL databases with async support.
    """

    def __init__(self, database_url: str):
        """
        Initialize database manager.

        Args:
            database_url: Database connection URL
        """
        self.database_url = database_url
        self.engine = create_async_engine(database_url, echo=False)
        self.async_session = async_sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

        logger.info(f"DatabaseManager initialized with {database_url}")

    async def init_db(self) -> None:
        """Initialize database tables."""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created")

    async def create_transaction(
        self,
        transaction_hash: str,
        payer: str,
        payee: str,
        amount: str,
        network: str,
        scheme: str,
        resource: str,
        status: str = "pending",
    ) -> Transaction:
        """
        Create a new transaction record.

        Args:
            transaction_hash: Transaction hash
            payer: Payer address
            payee: Payee address
            amount: Payment amount
            network: Network name
            scheme: Payment scheme
            resource: Resource URL
            status: Transaction status

        Returns:
            Created transaction record
        """
        async with self.async_session() as session:
            transaction = Transaction(
                transaction_hash=transaction_hash,
                payer=payer,
                payee=payee,
                amount=amount,
                network=network,
                scheme=scheme,
                resource=resource,
                status=status,
                timestamp=datetime.utcnow(),
            )
            session.add(transaction)
            await session.commit()
            await session.refresh(transaction)
            logger.info(f"Transaction created: {transaction_hash}")
            return transaction

    async def get_transaction(self, transaction_hash: str) -> Optional[Transaction]:
        """
        Get transaction by hash.

        Args:
            transaction_hash: Transaction hash

        Returns:
            Transaction record or None
        """
        async with self.async_session() as session:
            result = await session.execute(
                select(Transaction).where(
                    Transaction.transaction_hash == transaction_hash
                )
            )
            return result.scalar_one_or_none()

    async def get_transactions_by_payer(
        self, payer: str, limit: int = 100
    ) -> List[Transaction]:
        """
        Get transactions by payer address.

        Args:
            payer: Payer address
            limit: Maximum results

        Returns:
            List of transactions
        """
        async with self.async_session() as session:
            result = await session.execute(
                select(Transaction)
                .where(Transaction.payer == payer)
                .order_by(Transaction.timestamp.desc())
                .limit(limit)
            )
            return list(result.scalars().all())

    async def get_transactions_by_payee(
        self, payee: str, limit: int = 100
    ) -> List[Transaction]:
        """
        Get transactions by payee address.

        Args:
            payee: Payee address
            limit: Maximum results

        Returns:
            List of transactions
        """
        async with self.async_session() as session:
            result = await session.execute(
                select(Transaction)
                .where(Transaction.payee == payee)
                .order_by(Transaction.timestamp.desc())
                .limit(limit)
            )
            return list(result.scalars().all())

    async def update_transaction_status(
        self,
        transaction_hash: str,
        status: str,
        gas_used: Optional[str] = None,
        block_number: Optional[int] = None,
    ) -> None:
        """
        Update transaction status.

        Args:
            transaction_hash: Transaction hash
            status: New status
            gas_used: Gas used (optional)
            block_number: Block number (optional)
        """
        async with self.async_session() as session:
            result = await session.execute(
                select(Transaction).where(
                    Transaction.transaction_hash == transaction_hash
                )
            )
            transaction = result.scalar_one_or_none()

            if transaction:
                transaction.status = status
                if gas_used:
                    transaction.gas_used = gas_used
                if block_number:
                    transaction.block_number = block_number

                await session.commit()
                logger.info(
                    f"Transaction {transaction_hash} status updated to {status}"
                )

    async def create_discovery_resource(
        self, resource: str, accepts: str, metadata: Optional[str] = None
    ) -> DiscoveryResourceModel:
        """
        Create or update a discovery resource.

        Args:
            resource: Resource URL
            accepts: JSON string of payment requirements
            metadata: Optional metadata JSON string

        Returns:
            Created/updated discovery resource
        """
        async with self.async_session() as session:
            # Check if exists
            result = await session.execute(
                select(DiscoveryResourceModel).where(
                    DiscoveryResourceModel.resource == resource
                )
            )
            existing = result.scalar_one_or_none()

            if existing:
                existing.accepts = accepts
                existing.metadata = metadata
                existing.last_updated = datetime.utcnow()
                await session.commit()
                await session.refresh(existing)
                return existing
            else:
                discovery = DiscoveryResourceModel(
                    resource=resource,
                    accepts=accepts,
                    metadata=metadata,
                    last_updated=datetime.utcnow(),
                )
                session.add(discovery)
                await session.commit()
                await session.refresh(discovery)
                logger.info(f"Discovery resource created: {resource}")
                return discovery

    async def get_discovery_resources(
        self, type_filter: Optional[str] = None, limit: int = 10, offset: int = 0
    ) -> tuple[List[DiscoveryResourceModel], int]:
        """
        Get discovery resources with pagination.

        Args:
            type_filter: Filter by type (optional)
            limit: Results per page
            offset: Pagination offset

        Returns:
            Tuple of (resources, total_count)
        """
        async with self.async_session() as session:
            query = select(DiscoveryResourceModel)

            if type_filter:
                query = query.where(DiscoveryResourceModel.type == type_filter)

            # Get total count
            count_result = await session.execute(query)
            total = len(list(count_result.scalars().all()))

            # Get paginated results
            query = query.order_by(DiscoveryResourceModel.last_updated.desc())
            query = query.limit(limit).offset(offset)
            result = await session.execute(query)

            return list(result.scalars().all()), total

    async def close(self) -> None:
        """Close database connections."""
        await self.engine.dispose()
        logger.info("Database connections closed")

