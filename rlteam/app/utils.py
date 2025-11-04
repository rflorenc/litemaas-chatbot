"""
Utility functions for input validation and sanitization.
"""

import re
import html
from typing import Optional


def sanitize_input(text: str) -> str:
    """
    Sanitize user input to prevent injection attacks and prompt manipulation.

    Args:
        text: Raw user input

    Returns:
        Sanitized text safe for processing
    """
    if not text:
        return ""

    # Remove HTML tags
    text = html.escape(text)

    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)

    # Trim to reasonable length (prevent token exhaustion)
    max_length = 500
    if len(text) > max_length:
        text = text[:max_length] + "..."

    # Remove potential prompt injection patterns
    # These are common patterns used to manipulate LLMs
    injection_patterns = [
        r'ignore previous instructions',
        r'forget what i told you',
        r'you are now',
        r'system:',
        r'assistant:',
        r'<\|im_start\|>',
        r'<\|im_end\|>',
    ]

    for pattern in injection_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)

    return text.strip()


def validate_chat_request(data: dict) -> Optional[str]:
    """
    Validate the chat request payload.

    Args:
        data: Request JSON data

    Returns:
        Error message if validation fails, None if valid
    """
    if 'message' not in data:
        return "Missing 'message' field in request"

    message = data['message']

    if not isinstance(message, str):
        return "'message' must be a string"

    if not message.strip():
        return "'message' cannot be empty"

    if len(message) > 1000:
        return "'message' is too long (max 1000 characters)"

    return None


def is_valid_subdomain(subdomain: str) -> bool:
    """
    Validate subdomain format.

    Args:
        subdomain: Subdomain to validate

    Returns:
        True if valid, False otherwise
    """
    pattern = r'^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?$'
    return bool(re.match(pattern, subdomain))
