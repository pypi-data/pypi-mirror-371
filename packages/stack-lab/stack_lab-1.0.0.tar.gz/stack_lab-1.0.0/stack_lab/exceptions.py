"""
exceptions.py - Custom exception classes for stack_lab.

This module defines specialized exceptions to make debugging and 
error handling more intuitive and user-friendly.
"""

class StackError(Exception):
    """Base class for all stack-related errors."""
    pass


class StackOverflowError(StackError):
    """Raised when pushing to a full stack."""
    def __init__(self, message="Stack Overflow: Cannot push to a full stack."):
        super().__init__(message)


class StackUnderflowError(StackError):
    """Raised when popping from an empty stack."""
    def __init__(self, message="Stack Underflow: Cannot pop from an empty stack."):
        super().__init__(message)


class StackEmptyError(StackError):
    """Raised when attempting to peek at an empty stack."""
    def __init__(self, message="Stack is empty: Nothing to peek."):
        super().__init__(message)
