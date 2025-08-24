"""Segment Tree implementation module."""

from __future__ import annotations

from .segment_tree import SegmentTree
from .specialized import MaxSegmentTree, MinSegmentTree, SumSegmentTree

__all__ = [
    "MaxSegmentTree",
    "MinSegmentTree",
    "SegmentTree",
    "SumSegmentTree",
]
