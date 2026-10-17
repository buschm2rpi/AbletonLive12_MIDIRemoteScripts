"""Fake ``_Framework.DeviceBankRegistry`` — clean-room re-implementation.

Mirrors the decompiled ``_Framework/DeviceBankRegistry.py`` (intact).
"""

from __future__ import annotations

from .SubjectSlot import Subject


class DeviceBankRegistry(Subject):
    __subject_events__ = ("device_bank",)

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self._device_bank_registry = {}
        self._device_bank_listeners = []

    def compact_registry(self):
        newreg = dict([k for k in list(self._device_bank_registry.items()) if k[0] is not None])
        self._device_bank_registry = newreg

    def set_device_bank(self, device, bank):
        key = self._find_device_bank_key(device) or device
        old = self._device_bank_registry[key] if key in self._device_bank_registry else 0
        if old != bank:
            self._device_bank_registry[key] = bank
            self.notify_device_bank(device, bank)

    def get_device_bank(self, device):
        return self._device_bank_registry.get(self._find_device_bank_key(device), 0)

    def _find_device_bank_key(self, device):
        for k in self._device_bank_registry.keys():
            if k == device:
                return k
