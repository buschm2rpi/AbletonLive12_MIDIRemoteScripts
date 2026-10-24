"""Type stub for ``_Framework.Skin`` (type-checking only)."""
from __future__ import annotations

from typing import Any, Iterator, Tuple


class SkinColorMissingError(Exception):
    """Raised by ``Skin.__getitem__`` when a color name is missing."""


class Skin:
    """A name -> color lookup table built from a nested color class."""

    def __init__(self, colors: Any = None, *a: Any, **k: Any) -> None:
        ...

    def __getitem__(self, key: str) -> Any:
        """The color for ``key`` — a ``Color`` (RGB skins) or an ``Rgb``
        value (MK1 skins); raises ``SkinColorMissingError`` if absent."""
        ...

    def iteritems(self) -> Iterator[Tuple[str, Any]]:
        ...


def merge_skins(*skins: "Skin") -> "Skin":
    ...
