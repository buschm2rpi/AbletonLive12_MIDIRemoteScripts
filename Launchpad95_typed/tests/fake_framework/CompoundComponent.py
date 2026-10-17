"""Fake ``_Framework.CompoundComponent`` — clean-room re-implementation.

Mirrors the decompiled ``_Framework/CompoundComponent.py`` (intact).
"""

from __future__ import annotations

from .ControlSurfaceComponent import ControlSurfaceComponent


class CompoundComponent(ControlSurfaceComponent):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self._sub_components = []

    def update_all(self):
        self.update()
        for component in self._sub_components:
            component.update_all()

    def register_component(self, component):
        component._set_enabled_recursive(self.is_enabled())
        self._sub_components.append(component)
        return component

    def register_components(self, *a):
        return [self.register_component(c) for c in a]

    def has_component(self, component):
        return component in self._sub_components

    def set_enabled(self, enable):
        super().set_enabled(enable)
        for component in self._sub_components:
            component._set_enabled_recursive(self.is_enabled())

    def _set_enabled_recursive(self, enable):
        super()._set_enabled_recursive(enable)
        for component in self._sub_components:
            component._set_enabled_recursive(self.is_enabled())

    def set_allow_update(self, allow_updates):
        allow = bool(allow_updates)
        if self._allow_updates != allow:
            for component in self._sub_components:
                component.set_allow_update(allow)
            super().set_allow_update(allow)
