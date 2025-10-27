"""
Payment validation utilities for v402 Facilitator.

Validates payment data, amounts, currencies, and payment methods.
"""

import logging
import re
from decimal import Decimal, InvalidOperation
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

# Supported currencies
SUPPORTED_CURRENCIES = [
    'ETH', 'BTC', 'MATIC', 'BNB', 'USDT', 'USDC', 'DAI',
    'SOL', 'AVAX', 'FTM', 'BASE', 'ARB', 'OP'
]

# Payment amount constraints
MIN_AMOUNT = Decimal('0.000001')
MAX_AMOUNT = Decimal('1000000000')


class PaymentValidator:
    """Validates payment-related data."""
    
    @staticmethod
    def validate_amount(amount: str) -> Tuple[bool, Optional[str]]:
        """
        Validate payment amount.
        
        Args:
            amount: Payment amount as string
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            decimal_amount = Decimal(amount)
            
            if decimal_amount <= 0:
                return False, "Amount must be greater than zero"
                
            if decimal_amount < MIN_AMOUNT:
                return False, f"Amount must be at least {MIN_AMOUNT}"
                
            if decimal_amount > MAX_AMOUNT:
                return False, f"Amount must not exceed {MAX_AMOUNT}"
                
            return True, None
            
        except InvalidOperation:
            return False, "Invalid amount format"
            
    @staticmethod
    def validate_currency(currency: str) -> Tuple[bool, Optional[str]]:
        """
        Validate currency code.
        
        Args:
            currency: Currency code (uppercase)
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not currency:
            return False, "Currency is required"
            
        if len(currency) < 2 or len(currency) > 5:
            return False, "Currency code must be 2-5 characters"
            
        # Check if supported
        if currency not in SUPPORTED_CURRENCIES:
            logger.warning(f"Unsupported currency: {currency}")
            # Still return True, but log warning for future support
            
        return True, None
        
    @staticmethod
    def validate_payment_method(method: str) -> Tuple[bool, Optional[str]]:
        """
        Validate payment method.
        
        Args:
            method: Payment method identifier
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not method:
            return False, "Payment method is required"
            
        if len(method) < 2 or len(method) > 50:
            return False, "Payment method must be 2-50 characters"
            
        # Check for valid characters only
        if not re.match(r'^[a-zA-Z0-9_-]+$', method):
            return False, "Payment method contains invalid characters"
            
        return True, None
        
    @staticmethod
    def validate_product_id(product_id: str) -> Tuple[bool, Optional[str]]:
        """
        Validate product identifier.
        
        Args:
            product_id: Product identifier (UUID format expected)
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not product_id:
            return False, "Product ID is required"
            
        # UUID validation pattern
        uuid_pattern = re.compile(
            r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
            re.IGNORECASE
        )
        
        if not uuid_pattern.match(product_id):
            return False, "Product ID must be a valid UUID"
            
        return True, None
        
    @staticmethod
    def validate_client_id(client_id: str) -> Tuple[bool, Optional[str]]:
        """
        Validate client identifier.
        
        Args:
            client_id: Client identifier (can be UUID or custom format)
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not client_id:
            return False, "Client ID is required"
            
        if len(client_id) < 2 or len(client_id) > 128:
            return False, "Client ID must be 2-128 characters"
            
        # Allow alphanumeric with hyphens and underscores
        if not re.match(r'^[a-zA-Z0-9_-]+$', client_id):
            return False, "Client ID contains invalid characters"
            
        return True, None

