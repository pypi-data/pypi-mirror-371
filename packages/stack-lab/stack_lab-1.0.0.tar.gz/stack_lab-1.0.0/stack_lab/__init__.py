"""
stack_lab
=========

A premium, feature-rich Python stack data structure implementation for 
serious developers, learners, and professionals.

Author: Anbu Kumaran
GitHub: https://github.com/anbukumaran1
Version: 1.0.0

This package provides:
----------------------
- A highly optimized, extendable, and feature-packed Stack class.
- Advanced stack operations beyond push/pop.
- Utility methods for analytics, visualization, and debugging.
- Clear and professional documentation to match production-level code.

Example usage:
--------------
>>> from stack_lab import Stack
>>> s = Stack()
>>> s.push(10)
>>> s.push(20)
>>> s.peek()
20
>>> s.pop()
20
>>> len(s)
1
"""

__version__ = "1.0.0"
__author__ = "Anbu Kumaran"
__email__ = "anbuku12345@gmail.com"
__license__ = "MIT"
__url__ = "https://github.com/anbukumaran1/stack-lab"

# Expose the main Stack class directly
from .core import Stack

# Define what should be imported if someone does: from stack_lab import *
__all__ = ["Stack"]
