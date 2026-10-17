"""Fake ``_Framework.Task`` — re-exports from ``fake_core``.

Mirrors the real module's namespace: the ``Task`` class plus the module-level
helpers (``run``, ``wait``, ``sequence``, ``loop``, ``delay``, ``fade``, ...),
so ``Task.TaskGroup`` / ``Task.wait`` style access works exactly as in Live.
"""

from fake_core import (  # noqa: F401
    KILLED,
    PAUSED,
    RUNNING,
    DelayTask,
    FadeTask,
    FuncTask,
    GeneratorTask,
    SequenceTask,
    Task,
    TaskError,
    TaskGroup,
    TimedCallbackTask,
    TimerTask,
    WaitTask,
    WrapperTask,
    delay,
    fade,
    generator,
    invfade,
    linear_task,
    loop,
    parallel,
    repeat,
    run,
    sequence,
    sinusoid,
    totask,
    wait,
)
