"""
Hyper-fast queue for Python

A high-performance queue implementation using Cython and C++.
"""

from .hyperq import BytesHyperQ, HyperQ

__version__ = "1.0.0"
__author__ = "Martin Mkhitaryan"
__email__ = "mkhitaryan.martin@2000gmail.com"

__all__ = ["HyperQ", "BytesHyperQ"]
