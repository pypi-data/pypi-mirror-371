"""Specialized Segment Tree implementations for common operations."""

from __future__ import annotations

import operator

from .segment_tree import SegmentTree

__all__ = ["MaxSegmentTree", "MinSegmentTree", "SumSegmentTree"]


class SumSegmentTree(SegmentTree[int | float]):
    """Specialized Segment Tree for sum range queries.

    A convenience class that pre-configures the segment tree for sum operations
    with identity element 0 and addition operation.

    Examples:
        >>> tree = SumSegmentTree(5)
        >>> tree.set(0, 10)
        >>> tree.set(1, 20)
        >>> tree.prod(0, 2)  # Sum of elements from index 0 to 1
        30
        >>> tree.all_prod()  # Sum of all elements
        30
    """

    def __init__(self, size: int) -> None:
        """Initialize a Sum Segment Tree.

        Args:
            size: The number of elements the segment tree will hold.
                Must be a positive integer.
        """
        super().__init__(size, 0, operator.add)

    def sum(self, left: int = 0, right: int | None = None) -> int | float:
        """Get the sum of elements in the range [left, right).

        This is an alias for the prod() method for better readability.

        Args:
            left: The left bound of the range (inclusive). Defaults to 0.
            right: The right bound of the range (exclusive). Defaults to size.

        Returns:
            The sum of all elements in the specified range.
        """
        return self.prod(left, right)

    def total(self) -> int | float:
        """Get the sum of all elements in the segment tree.

        This is an alias for the all_prod() method for better readability.

        Returns:
            The sum of all elements in the segment tree.
        """
        return self.all_prod()


class MinSegmentTree(SegmentTree[int | float]):
    """Specialized Segment Tree for minimum range queries.

    A convenience class that pre-configures the segment tree for minimum operations
    with identity element positive infinity and min operation.

    Examples:
        >>> tree = MinSegmentTree(5)
        >>> tree.set(0, 10)
        >>> tree.set(1, 5)
        >>> tree.set(2, 20)
        >>> tree.prod(0, 3)  # Minimum of elements from index 0 to 2
        5
        >>> tree.minimum(1, 3)  # Alternative method name
        5
    """

    def __init__(self, size: int) -> None:
        """Initialize a Min Segment Tree.

        Args:
            size: The number of elements the segment tree will hold.
                Must be a positive integer.
        """
        super().__init__(size, float("inf"), min)

    def minimum(self, left: int = 0, right: int | None = None) -> int | float:
        """Get the minimum element in the range [left, right).

        This is an alias for the prod() method for better readability.

        Args:
            left: The left bound of the range (inclusive). Defaults to 0.
            right: The right bound of the range (exclusive). Defaults to size.

        Returns:
            The minimum element in the specified range.
        """
        return self.prod(left, right)

    def global_min(self) -> int | float:
        """Get the minimum element in the entire segment tree.

        This is an alias for the all_prod() method for better readability.

        Returns:
            The minimum element in the segment tree.
        """
        return self.all_prod()


class MaxSegmentTree(SegmentTree[int | float]):
    """Specialized Segment Tree for maximum range queries.

    A convenience class that pre-configures the segment tree for maximum operations
    with identity element negative infinity and max operation.

    Examples:
        >>> tree = MaxSegmentTree(5)
        >>> tree.set(0, 10)
        >>> tree.set(1, 5)
        >>> tree.set(2, 20)
        >>> tree.prod(0, 3)  # Maximum of elements from index 0 to 2
        20
        >>> tree.maximum(1, 3)  # Alternative method name
        20
    """

    def __init__(self, size: int) -> None:
        """Initialize a Max Segment Tree.

        Args:
            size: The number of elements the segment tree will hold.
                Must be a positive integer.
        """
        super().__init__(size, float("-inf"), max)

    def maximum(self, left: int = 0, right: int | None = None) -> int | float:
        """Get the maximum element in the range [left, right).

        This is an alias for the prod() method for better readability.

        Args:
            left: The left bound of the range (inclusive). Defaults to 0.
            right: The right bound of the range (exclusive). Defaults to size.

        Returns:
            The maximum element in the specified range.
        """
        return self.prod(left, right)

    def global_max(self) -> int | float:
        """Get the maximum element in the entire segment tree.

        This is an alias for the all_prod() method for better readability.

        Returns:
            The maximum element in the segment tree.
        """
        return self.all_prod()
