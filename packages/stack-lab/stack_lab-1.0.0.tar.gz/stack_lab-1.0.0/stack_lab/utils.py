"""
utils.py - Utility functions for stack_lab.

Contains helper functions for validation, logging, benchmarking, 
and pretty-printing stack data.
"""

import time
import functools
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)


def validate_capacity(capacity: int) -> None:
    """Ensures stack capacity is a valid positive integer."""
    if not isinstance(capacity, int) or capacity <= 0:
        raise ValueError("Stack capacity must be a positive integer.")


def pretty_print(stack) -> str:
    """Returns a clean string representation of the stack."""
    return "Stack[top -> bottom]: " + " -> ".join(map(str, reversed(stack)))


def benchmark(func):
    """Decorator to measure execution time of stack operations."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        duration = time.perf_counter() - start
        logging.info(f"⏱️ {func.__name__} executed in {duration:.6f}s")
        return result
    return wrapper
