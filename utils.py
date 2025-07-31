"""
Utility functions for the Multi-Agent Educational Platform
"""
import asyncio
import logging
from typing import Any, Dict, Optional
from datetime import datetime, timezone


logger = logging.getLogger(__name__)


def get_current_timestamp() -> datetime:
    """Get current UTC timestamp"""
    return datetime.now(timezone.utc)


def safe_dict_get(data: Dict[str, Any], key: str, default: Any = None) -> Any:
    """Safely get value from dictionary with default"""
    return data.get(key, default)


async def retry_async(
    func,
    max_retries: int = 3,
    delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,)
) -> Any:
    """
    Retry an async function with exponential backoff

    Args:
        func: Async function to retry
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries
        backoff_factor: Multiplier for delay on each retry
        exceptions: Tuple of exceptions to catch and retry on

    Returns:
        Result of the function call

    Raises:
        Last exception if all retries fail
    """
    last_exception = None
    current_delay = delay

    for attempt in range(max_retries + 1):
        try:
            return await func()
        except exceptions as e:
            last_exception = e
            if attempt == max_retries:
                logger.error(f"Function failed after {max_retries} retries: {e}")
                break

            logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {current_delay}s...")
            await asyncio.sleep(current_delay)
            current_delay *= backoff_factor

    raise last_exception


def validate_input_type(input_data: Any, input_type: str) -> bool:
    """
    Validate input data based on expected type

    Args:
        input_data: Data to validate
        input_type: Expected type ('text', 'voice', 'image')

    Returns:
        True if valid, False otherwise
    """
    if input_type == "text":
        return isinstance(input_data, str) and len(input_data.strip()) > 0
    elif input_type == "voice":
        # TODO: Implement voice data validation
        return input_data is not None
    elif input_type == "image":
        # TODO: Implement image data validation
        return input_data is not None
    else:
        return False


def sanitize_string(text: str, max_length: int = 1000) -> str:
    """
    Sanitize string input for safe storage and processing

    Args:
        text: Input text to sanitize
        max_length: Maximum allowed length

    Returns:
        Sanitized string
    """
    if not isinstance(text, str):
        return ""

    # Remove null bytes and control characters
    sanitized = "".join(char for char in text if ord(char) >= 32 or char in "\n\r\t")

    # Truncate if too long
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + "..."

    return sanitized.strip()

def call_llm(prompt, model="gemma3n"):
    """
    Call a language model with a given prompt

    Args:
        prompt: Input prompt for the language model
        model: Language model to use

    Returns:
        Response from the language model
    """
    try:
        response = model(prompt)
        return response
    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        raise

def check_code(code: str):
    return
