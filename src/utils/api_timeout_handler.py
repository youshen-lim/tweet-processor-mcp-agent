"""
API Timeout Handler - Robust timeout and retry logic for API calls

This module provides comprehensive timeout handling, retry logic, and graceful
degradation for all external API calls to prevent application stalling.
"""

import asyncio
import functools
import logging
from typing import Any, Callable, Optional, TypeVar, Union
from datetime import datetime
import signal
import sys

logger = logging.getLogger(__name__)

T = TypeVar('T')


class TimeoutError(Exception):
    """Raised when an operation times out."""
    pass


class APICallError(Exception):
    """Raised when an API call fails after all retries."""
    pass


async def with_timeout(
    coro,
    timeout_seconds: float,
    operation_name: str = "Operation",
    fallback_value: Optional[Any] = None,
    raise_on_timeout: bool = True
) -> Any:
    """
    Execute an async operation with a strict timeout.
    
    Args:
        coro: Coroutine to execute
        timeout_seconds: Maximum time to wait in seconds
        operation_name: Name of operation for logging
        fallback_value: Value to return if timeout occurs (if raise_on_timeout=False)
        raise_on_timeout: Whether to raise exception on timeout
        
    Returns:
        Result of the coroutine or fallback_value
        
    Raises:
        TimeoutError: If operation times out and raise_on_timeout=True
    """
    start_time = datetime.now()
    logger.info(f"⏱️  Starting {operation_name} (timeout: {timeout_seconds}s)")
    
    try:
        result = await asyncio.wait_for(coro, timeout=timeout_seconds)
        elapsed = (datetime.now() - start_time).total_seconds()
        logger.info(f"✅ {operation_name} completed in {elapsed:.2f}s")
        return result
        
    except asyncio.TimeoutError:
        elapsed = (datetime.now() - start_time).total_seconds()
        error_msg = f"⚠️  {operation_name} timed out after {elapsed:.2f}s (limit: {timeout_seconds}s)"
        logger.error(error_msg)
        
        if raise_on_timeout:
            raise TimeoutError(error_msg)
        else:
            logger.warning(f"Using fallback value for {operation_name}")
            return fallback_value
            
    except Exception as e:
        elapsed = (datetime.now() - start_time).total_seconds()
        logger.error(f"❌ {operation_name} failed after {elapsed:.2f}s: {e}")
        raise


async def with_retry(
    coro_func: Callable,
    max_retries: int = 3,
    retry_delay: float = 2.0,
    operation_name: str = "Operation",
    timeout_per_attempt: Optional[float] = None,
    exponential_backoff: bool = True
) -> Any:
    """
    Execute an async operation with retry logic.
    
    Args:
        coro_func: Async function to execute (will be called for each retry)
        max_retries: Maximum number of retry attempts
        retry_delay: Initial delay between retries in seconds
        operation_name: Name of operation for logging
        timeout_per_attempt: Optional timeout for each attempt
        exponential_backoff: Whether to use exponential backoff
        
    Returns:
        Result of the operation
        
    Raises:
        APICallError: If all retries fail
    """
    last_exception = None
    
    for attempt in range(max_retries):
        try:
            logger.info(f"🔄 {operation_name} - Attempt {attempt + 1}/{max_retries}")
            
            if timeout_per_attempt:
                result = await with_timeout(
                    coro_func(),
                    timeout_seconds=timeout_per_attempt,
                    operation_name=f"{operation_name} (attempt {attempt + 1})",
                    raise_on_timeout=True
                )
            else:
                result = await coro_func()
                
            logger.info(f"✅ {operation_name} succeeded on attempt {attempt + 1}")
            return result
            
        except (TimeoutError, asyncio.TimeoutError, Exception) as e:
            last_exception = e
            logger.warning(f"⚠️  {operation_name} attempt {attempt + 1} failed: {e}")
            
            if attempt < max_retries - 1:
                # Calculate delay with exponential backoff
                delay = retry_delay * (2 ** attempt) if exponential_backoff else retry_delay
                logger.info(f"⏳ Retrying in {delay:.1f}s...")
                await asyncio.sleep(delay)
            else:
                logger.error(f"❌ {operation_name} failed after {max_retries} attempts")
    
    raise APICallError(f"{operation_name} failed after {max_retries} attempts: {last_exception}")


def setup_signal_handlers():
    """
    Setup signal handlers for graceful shutdown on Windows.
    Handles Ctrl+C and Task Scheduler termination signals.
    """
    def signal_handler(signum, frame):
        logger.warning(f"⚠️  Received signal {signum}, initiating graceful shutdown...")
        print(f"\n⚠️  Received termination signal, shutting down gracefully...")
        sys.exit(0)
    
    # Handle Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    # Handle termination signal (Windows Task Scheduler)
    if hasattr(signal, 'SIGTERM'):
        signal.signal(signal.SIGTERM, signal_handler)
    
    # Handle break signal (Windows)
    if hasattr(signal, 'SIGBREAK'):
        signal.signal(signal.SIGBREAK, signal_handler)

