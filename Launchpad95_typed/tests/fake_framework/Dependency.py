"""Fake ``_Framework.Dependency`` — re-exports from ``fake_core``."""

from fake_core import (  # noqa: F401
    DependencyError,
    InjectionFactory,
    InjectionRegistry,
    Injector,
    RegistryInjector,
    dependency,
    depends,
    get_dependency_for,
    inject,
)
