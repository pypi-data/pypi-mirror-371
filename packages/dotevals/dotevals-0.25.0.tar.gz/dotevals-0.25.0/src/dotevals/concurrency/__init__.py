"""Concurrency strategies for dotevals."""

from .adaptive import Adaptive
from .async_sequential import AsyncSequential
from .sequential import Sequential
from .sliding_window import SlidingWindow

# Type aliases
SyncConcurrencyStrategy = Sequential
AsyncConcurrencyStrategy = SlidingWindow | Adaptive | AsyncSequential

__all__ = [
    "Adaptive",
    "AsyncSequential",
    "Sequential",
    "SlidingWindow",
    # Type unions
    "SyncConcurrencyStrategy",
    "AsyncConcurrencyStrategy",
]
