"""Signals for Python - inspired by Angular Signals / SolidJS. Reactive Declarative State Management Library for Python - automatic dependency tracking and reactive updates for your application state."""

from .context import untracked
from .scheduler import batch
from .signal import Signal, Computed, ComputeSignal
from .effect import Effect
from .utils import to_async_iter
from .thread_safety import set_thread_safety, is_thread_safety_enabled

from typing import TypeVar

T = TypeVar("T")


__version__ = "0.18.0"
__all__ = [
    "Signal",
    "ComputeSignal",
    "Computed",
    "Effect",
    "batch",
    "untracked",
    "to_async_iter",
    "set_thread_safety",
    "is_thread_safety_enabled",
]
