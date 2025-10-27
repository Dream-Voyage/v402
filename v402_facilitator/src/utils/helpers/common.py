"""
Common utility functions for v402 Facilitator.

Provides helper functions for common operations.
"""

import hashlib
import secrets
import uuid
from datetime import datetime, timezone
from typing import Any, Dict


def generate_id() -> str:
    """
    Generate a unique ID.

    Returns:
        str: Unique identifier
    """
    return str(uuid.uuid4())


def generate_token(length: int = 32) -> str:
    """
    Generate a cryptographically secure random token.

    Args:
        length: Token length in bytes

    Returns:
        str: Random token in hex format
    """
    return secrets.token_hex(length)


def hash_string(text: str, algorithm: str = 'sha256') -> str:
    """
    Hash a string using specified algorithm.

    Args:
        text: Text to hash
        algorithm: Hash algorithm (md5, sha1, sha256, sha512)

    Returns:
        str: Hashed value in hex format
    """
    hasher = hashlib.new(algorithm)
    hasher.update(text.encode('utf-8'))
    return hasher.hexdigest()


def utc_now() -> datetime:
    """
    Get current UTC timestamp.

    Returns:
        datetime: Current UTC datetime
    """
    return datetime.now(timezone.utc)


def utc_from_timestamp(timestamp: float) -> datetime:
    """
    Convert Unix timestamp to UTC datetime.

    Args:
        timestamp: Unix timestamp

    Returns:
        datetime: UTC datetime
    """
    return datetime.fromtimestamp(timestamp, tz=timezone.utc)


def safe_int(value: Any, default: int = 0) -> int:
    """
    Safely convert value to integer with default fallback.

    Args:
        value: Value to convert
        default: Default value if conversion fails

    Returns:
        int: Integer value or default
    """
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def safe_float(value: Any, default: float = 0.0) -> float:
    """
    Safely convert value to float with default fallback.

    Args:
        value: Value to convert
        default: Default value if conversion fails

    Returns:
        float: Float value or default
    """
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def truncate_string(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate string to specified length.

    Args:
        text: String to truncate
        max_length: Maximum length
        suffix: Suffix to append if truncated

    Returns:
        str: Truncated string
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def sanitize_input(text: str) -> str:
    """
    Sanitize user input by removing potentially dangerous characters.

    Args:
        text: Input string

    Returns:
        str: Sanitized string
    """
    # Remove null bytes and control characters
    return ''.join(char for char in text if ord(char) >= 32 and ord(char) != 127)


def extract_dict(data: Dict[str, Any], keys: list[str]) -> Dict[str, Any]:
    """
    Extract specified keys from dictionary.

    Args:
        data: Source dictionary
        keys: List of keys to extract

    Returns:
        dict: Dictionary with extracted keys only
    """
    return {key: data.get(key) for key in keys if key in data}


def nest_dict(data: Dict[str, Any], prefix: str) -> Dict[str, Any]:
    """
    Nest dictionary keys under a prefix.

    Args:
        data: Source dictionary
        prefix: Prefix to add to all keys

    Returns:
        dict: Nested dictionary
    """
    return {f"{prefix}.{key}": value for key, value in data.items()}

