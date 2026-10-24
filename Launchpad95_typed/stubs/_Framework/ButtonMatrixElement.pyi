"""Type stub for ``_Framework.ButtonMatrixElement`` (type-checking only)."""
from __future__ import annotations

from typing import Any, Iterator, List, Tuple

from _Framework.ButtonElement import ButtonElement
from _Framework.CompoundElement import CompoundElement


class ButtonMatrixElement(CompoundElement):
    """A 2-D matrix of buttons (the Launchpad's 8x8 grid)."""

    def __init__(self, rows: List[Tuple[ButtonElement, ...]] = [],
                 *a: Any, **k: Any) -> None:
        ...

    def add_row(self, buttons: Tuple[ButtonElement, ...]) -> None:
        ...

    def width(self) -> int:
        ...

    def height(self) -> int:
        ...

    def send_value(self, column: int, row: int, value: int,
                   force: bool = False) -> None:
        ...

    def set_light(self, column: int, row: int, value: Any) -> None:
        ...

    def get_button(self, column: int, row: int) -> ButtonElement:
        ...

    def reset(self) -> None:
        ...

    def __iter__(self) -> Iterator[ButtonElement]:
        ...

    def __getitem__(self, index: Any) -> Any:
        ...

    def __len__(self) -> int:
        ...

    def iterbuttons(self) -> Iterator[ButtonElement]:
        ...
