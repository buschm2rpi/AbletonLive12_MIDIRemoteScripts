"""Type stub for ``_Framework.Task`` (type-checking only).

The module namespace mirrors the real module: the ``Task`` class plus
module-level helpers (``run``, ``wait``, ``sequence``, ...), so
``Task.TaskGroup`` / ``Task.wait`` style access type-checks exactly as in
Live.
"""
from __future__ import annotations

from typing import Any, Callable


class Task:
    """Base class of Live's task system."""

    def clear(self) -> None:
        ...

    def pause(self) -> None:
        ...

    def resume(self) -> None:
        ...

    def kill(self) -> None:
        ...

    def update(self, timer: int) -> None:
        ...

    @property
    def is_running(self) -> bool:
        ...

    @property
    def parent_task(self) -> "TaskGroup":
        ...


class TaskGroup(Task):
    """A group of tasks (the surface's ``_task_group`` / component ``_tasks``)."""

    def add(self, task: Task) -> Task:
        ...

    def remove(self, task: Task) -> None:
        ...

    def find(self, task: Task) -> Task:
        ...

    def clear(self) -> None:
        ...

    def update(self, delta: int) -> None:
        ...


def run(func: Callable[..., Any], *a: Any, **k: Any) -> Task:
    """Task that runs ``func`` once."""
    ...


def sequence(*tasks: Task) -> Task:
    ...


def parallel(*tasks: Task) -> Task:
    ...


def loop(*tasks: Task) -> Task:
    ...


def wait(seconds: float) -> Task:
    ...


def delay(seconds: float) -> Task:
    ...
