"""Fake ``_Framework.ClipCreator`` — clean-room re-implementation.

Mirrors the decompiled ``_Framework/ClipCreator.py`` (intact); the
``Live.Song.Quantization`` reference comes from ``fake_live``.
"""

from __future__ import annotations

from fake_live import Quantization as _Q


class ClipCreator:
    grid_quantization = None
    is_grid_triplet = False
    fixed_length = 8

    def create(self, slot, length=None):
        if length is None:
            length = self.fixed_length
        slot.create_clip(length)
        if self.grid_quantization is not None:
            slot.clip.view.grid_quantization = self.grid_quantization
            slot.clip.view.grid_is_triplet = self.is_grid_triplet
        slot.fire(force_legato=True, launch_quantization=_Q.q_no_q)
