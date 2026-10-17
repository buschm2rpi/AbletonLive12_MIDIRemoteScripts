"""Fake ``_Framework.Resource`` — re-exports from ``fake_core``."""

from fake_core import (  # noqa: F401
    DEFAULT_PRIORITY,
    ClientWrapper,
    CompoundResource,
    ExclusiveResource,
    PrioritizedResource,
    ProxyResource,
    Resource,
    SharedResource,
    StackingResource,
    compose_resources,
)
