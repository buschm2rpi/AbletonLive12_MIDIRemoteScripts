"""Type stub for ``Live.Application`` (type-checking only).

In real Live this is a module containing the ``Application`` class plus
module-level convenience functions; the class methods mirror them, so both
``Live.Application.get_application()`` and
``Live.Application.Application.get_application()`` type-check.
"""
from __future__ import annotations

from typing import Callable

from Live.Song import Song


def combine_apcs() -> bool:
    """Whether Live supports combining multiple APC instances (8.2+)."""
    ...


def get_application() -> "Application":
    """The singleton Live application object."""
    ...


def get_random_int(min_value: int, max_value: int) -> int:
    ...


def encrypt_challenge(challenge: int) -> int:
    ...


def encrypt_challenge2(challenge: int) -> int:
    ...


class Application:
    """Live's application object (singleton via ``get_application``)."""

    @classmethod
    def combine_apcs(cls) -> bool:
        ...

    @classmethod
    def get_application(cls) -> "Application":
        ...

    @classmethod
    def get_random_int(cls, min_value: int, max_value: int) -> int:
        ...

    @classmethod
    def encrypt_challenge(cls, challenge: int) -> int:
        ...

    @classmethod
    def encrypt_challenge2(cls, challenge: int) -> int:
        ...

    def get_document(self) -> Song:
        ...

    def get_major_version(self) -> int:
        ...

    def get_minor_version(self) -> int:
        ...

    def get_bugfix_version(self) -> int:
        ...

    @property
    def view(self) -> "ApplicationView":
        ...


class ApplicationView:
    """Visibility state of Live's application views (Detail, etc.).

    Listener API matches real Live: the callback is invoked (with no
    arguments) whenever the given view's visibility changes.
    """

    def is_view_visible(self, view_name: str) -> bool:
        ...

    def show_view(self, view_name: str) -> None:
        ...

    def hide_view(self, view_name: str) -> None:
        ...

    def add_is_view_visible_listener(self, view_name: str,
                                     callback: Callable[[], None]) -> None:
        ...

    def remove_is_view_visible_listener(self, view_name: str,
                                        callback: Callable[[], None]) -> None:
        ...
