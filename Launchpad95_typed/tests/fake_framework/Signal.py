"""Fake ``_Framework.Signal`` — re-exports from ``fake_core``."""

from fake_core import (  # noqa: F401
    IdentifyingSlot,
    Signal,
    Slot,
    default_combiner,
    short_circuit_combiner,
    short_circuit_signal,
)
