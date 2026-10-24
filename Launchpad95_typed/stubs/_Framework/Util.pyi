"""Type stub for ``_Framework.Util`` (type-checking only).

Only the helpers the script imports are declared.
"""
from __future__ import annotations

from typing import Any, Callable, Iterable, Optional


def in_range(value: int, lower_bound: int, upper_open_bound: int) -> bool:
    """True if ``lower_bound <= value < upper_open_bound``."""
    ...


def find_if(predicate: Callable[[Any], Any], seq: Iterable[Any]) -> Optional[Any]:
    """First element of ``seq`` for which ``predicate`` is true, else None."""
    ...


def clamp(val: Any, minv: Any, maxv: Any) -> Any:
    ...
