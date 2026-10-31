# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Launchpad95 is an Ableton Live remote script for Novation Launchpad hardware controllers (Launchpad, Launchpad Mini, Launchpad S, Launchpad MK2, Launchpad X, Launchpad Mini MK3). It is a plain Python remote script — no Max for Live (M4L) required for core functionality. The script runs inside Ableton Live's Python environment and uses Ableton's internal `_Framework` modules.

## Architecture

### Entry Point
- `__init__.py` — Defines `create_instance(c_instance)` and `get_capabilities()`. Ableton instantiates this module as the control surface.
- `LaunchpadBase.py` — Shared `ControlSurface` machinery (init/disconnect/mapping, hardware probes, SYSEX detection). Class-level flags `_lpx` / `_mk2_rgb` / `_mk3_rgb` control skin/layout/drum notes.
- `Launchpad.py` — Auto-detecting entry point `class Launchpad(LaunchpadBase)` (kept for backward compatibility). Sends all three probes and identifies the model from the SYSEX challenge/identity response (two-stage init: detect model → configure buttons/skins). Supports 4 hardware variants: classic (MK1), MK2 RGB, MK3 RGB, and LPX.
- `LP_MK1.py`, `LP_MK2.py`, `LP_MK3.py`, `LP_X.py` — Statically configured subclasses that build eagerly in `__init__()` and only use the handshake as an enable gate. For model selection via Live, use the per-model script folders (`Launchpad95_MK1/`, `Launchpad95_MK2/`, `Launchpad95_MK3/`, `Launchpad95_X/`), each containing only `__init__.py` that re-exports the corresponding class from `Launchpad95_typed`.

### Mode Selection Hierarchy
The script uses a 3-tier mode selector architecture:

1. **MainSelectorComponent** (`MainSelectorComponent.py`) — Top-level mode selector with 8 modes controlled by the 4 top-right mode buttons. Each button can have sub-modes:
   - **Mode 0: Session** — Clip launching and arrangement navigation (with optional Pro Session mode via long-press Session button)
   - **Mode 1: User 1** — Sub-modes configured in `Settings.USER_MODES_1`: `instrument` (Push-like instrument control with scales), `device` (device parameter control), optionally `user 1`
   - **Mode 2: User 2** — Sub-modes configured in `Settings.USER_MODES_2`: `drum stepseq`, `melodic stepseq`, optionally `user 2`
   - **Mode 3: Mixer** — Channel strip control with sub-modes via `SubSelectorComponent`

2. **SubSelectorComponent** (`SubSelectorComponent.py`) — Mixer sub-modes: overview (buttons), volume sliders, pan sliders, send 1, send 2. Uses `PreciseButtonSliderElement` for nuanced slider control.

3. **Component Activation** — `MainSelectorComponent.update()` enables/disables sub-components and reassigns button matrix roles per mode via `_setup_*` methods.

### Key Components
- `SpecialSessionComponent` — Extended `SessionComponent` with custom clip slot skinning (MK2+), OSd updates, and multi-device linking
- `SpecialProSessionComponent` — Pro session variant with stop clip buttons on bottom row
- `StepSequencerComponent` / `StepSequencerComponent2` — Drum and melodic step sequencers with loop selection, note editing, scale editing, and quantization
- `InstrumentControllerComponent` — Push-like instrument mode with scale visualization, note repeat, and track control
- `DeviceControllerComponent` — Device parameter control with stepless/precision mode, lockable banks, and TDC (time-sensitive stepless fader)
- `SubSelectorComponent` — Mixer mode selector with volume/pan/send sliders
- `TrackControllerComponent` — Single-track controller (arm/solo/mute, clip navigation)
- `ScaleComponent` — Musical scale computation using Ableton's `Live.Song.get_all_scales_ordered()`
- `SpecialMixerComponent` / `DefChannelStripComponent` — Custom mixer and channel strips
- `PreciseButtonSliderElement` / `ButtonSliderElement` — Slider abstractions for nuanced parameter control
- `M4LInterface` (M4LInterface.py) — On-screen display mock; provides OSD data without requiring M4L device
- `DeviceControllerStripServer` / `DeviceControllerStripProxy` — IPC for external device parameter server

### Configuration
- `Settings.py` — Central `Settings` class with toggles for session linking, step seq linking, device controller stepless mode, velocity thresholds, TDC timing, volume levels, and logging. Read via `from .Settings import Settings` pattern.
- `SkinMK1.py` / `SkinMK2.py` — Skin factories for different hardware generations. MK2+ and MK3+ use RGB skin; classic uses 8x8 grid.
- `ColorsMK1.py` / `ColorsMK2.py` — Color lookup tables for clip states and feedback.

### Hardware
- Button mapping: 8x8 matrix + 8 top buttons (nav + mode) + 8 side buttons (scene launch + transport)
- MIDI notes/CCs differ between hardware generations (see `LaunchpadBase.py` `init()` layout logic; top buttons CC 104 vs 91 depending on model, side buttons NOTE vs CC on MK3/LPX)
- SYSEX identity/challenge detection in `LaunchpadBase.handle_sysex()` and per-model `handle_sysex()` overrides; probes sent by `_send_challenge()` (auto-detect sends all three, static models send only their own)

## Development Notes

- **Tests:** `Launchpad95_typed/tests/` is a fake-environment pytest suite that runs **outside** Live (fakes for `Live` + `_Framework`; no production-code imports of either). Run from the worktree root: `Launchpad95_typed/.venv/bin/python -m pytest Launchpad95_typed/tests/` (the system `python3` has no pytest). Fixtures: `surface` (auto-detect, default mk2, two-stage init via flags+`init()`) and `static_surface` (parametrized over `LP_MK1/LP_MK2/LP_MK3/LP_X`, eager init). Execution notes: `Launchpad95_typed/plan_phase3_tests.md`.
- **Type checking:** `mypy --config-file Launchpad95_typed/mypy.ini Launchpad95_typed/` from the worktree root. `Launchpad95_typed/stubs/` (`.pyi` files, type-checker-only, never imported at runtime) provides typed stubs for the host `Live` module and the `_Framework` package, which the config surfaces via `mypy_path`. The stubs mirror the API surface exercised by the test fakes (`tests/fake_live.py`, `tests/fake_framework/`); see `stubs/README.md` and the Phase 4a notes in `plan_control_surface_protocols.md`.
- **Python 3.11+ only**: Ableton Live 12 is the only supported host, so new code may use modern Python 3 syntax and type annotations. Legacy py2-style patterns in older files (`from __future__ import with_statement`, `xrange`/`imap` polyfills) may be left in place but should not be added to new code.
- **Ableton _Framework**: All components inherit from Ableton's `_Framework` base classes (`ControlSurface`, `ModeSelectorComponent`, `SessionComponent`, `MixerComponent`, `DeviceComponent`, `CompoundComponent`, `ControlSurfaceComponent`). These are provided by Ableton Live at runtime and are not importable externally.
- **Installation**: Place the `Launchpad95_typed` folder in `~/Documents/Ableton/User Library/Remote Scripts/`.
- **No build/lint step**: Pure Python, no compilation. No linting configuration exists.
- The `Launchpad95_typed/` subdirectory appears to be a secondary copy or variant of the script.
