"""Segee - High-performance segment tree implementation for Python.

This package provides an enterprise-grade Segment Tree data structure that supports
efficient range queries and point updates in O(log n) time complexity.

Examples:
    Basic usage with generic segment tree:

    >>> from segee import SegmentTree
    >>> import operator
    >>> tree = SegmentTree(5, 0, operator.add)
    >>> tree.set(0, 10)
    >>> tree.set(1, 20)
    >>> tree.prod(0, 2)  # Sum of elements from index 0 to 1
    30

    Convenient specialized classes:

    >>> from segee import SumSegmentTree, MinSegmentTree, MaxSegmentTree
    >>> sum_tree = SumSegmentTree(5)
    >>> sum_tree.set(0, 10)
    >>> sum_tree.sum(0, 2)  # More readable than prod()
    10
"""

from __future__ import annotations

from ._types import BinaryOperation, Predicate, SupportsComparison, T
from .exceptions import (
    SegmentTreeError,
    SegmentTreeIndexError,
    SegmentTreeInitializationError,
    SegmentTreeRangeError,
)
from .segment_tree import MaxSegmentTree, MinSegmentTree, SegmentTree, SumSegmentTree

__version__ = "0.1.0"
__author__ = "nodashin"
__email__ = "nodashin@example.com"

__all__ = [
    "BinaryOperation",
    "MaxSegmentTree",
    "MinSegmentTree",
    "Predicate",
    "SegmentTree",
    "SegmentTreeError",
    "SegmentTreeIndexError",
    "SegmentTreeInitializationError",
    "SegmentTreeRangeError",
    "SumSegmentTree",
    "SupportsComparison",
    "T",
    "__author__",
    "__email__",
    "__version__",
]
