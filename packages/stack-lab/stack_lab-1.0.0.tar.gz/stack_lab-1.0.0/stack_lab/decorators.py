"""
decorators.py - Custom decorators for stack_lab.

Provides debugging, profiling, and safety layers for stack methods.
"""

import functools
import logging


def debug(func):
    """Logs detailed debug info for stack operations."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logging.debug(f"🔍 Calling {func.__name__} with args={args[1:]}, kwargs={kwargs}")
        result = func(*args, **kwargs)
        logging.debug(f"✅ {func.__name__} returned {result}")
        return result
    return wrapper


def safe_call(func):
    """Decorator to catch stack-related errors safely."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(f"❌ Error in {func.__name__}: {e}")
            raise
    return wrapper
