"""Type definitions for the Segee package."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, Protocol, TypeVar

__all__ = ["BinaryOperation", "Predicate", "SupportsComparison", "T"]

T = TypeVar("T")
"""Type variable for segment tree elements."""


class SupportsComparison(Protocol):
    """Protocol for types that support comparison operations."""

    def __lt__(self, other: Any) -> bool:
        """Less than comparison."""
        ...

    def __le__(self, other: Any) -> bool:
        """Less than or equal comparison."""
        ...

    def __gt__(self, other: Any) -> bool:
        """Greater than comparison."""
        ...

    def __ge__(self, other: Any) -> bool:
        """Greater than or equal comparison."""
        ...


BinaryOperation = Callable[[T, T], T]
"""Type alias for binary operations used in segment tree aggregation."""

Predicate = Callable[[T], bool]
"""Type alias for predicates used in segment tree searches."""
