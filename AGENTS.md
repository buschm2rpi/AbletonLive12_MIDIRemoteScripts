# AGENTS.md

## Purpose
Compact instructions for coding agents working in this repo. Only include guidance that would be easy to miss.

## Repo overview
- Collection of Ableton Live 12.4 MIDI Remote Scripts (Python). Each top-level directory is a controller script that Live loads directly (e.g., `Launchpad/`, `Launchkey/`, `Launchpad95_typed/`).
- Runtime deps: Ableton Live's internal `_Framework/` and `ableton/` packages exist only inside Live. They are **not** pip-installable. Any execution outside Live requires fakes (see Testing).
- Target runtime is **Ableton Live 12 only** (CPython 3.11; custom scripts compile to 3.11-magic `.pyc`). Modern Python 3 syntax (type annotations, f-strings) is the standard; do not maintain Python 2 compatibility. Note: `DeviceControllerStripProxy.py` still has a py2 `import Queue` shim (with `# type: ignore`) and `Launchpad.py` has a py2-style `_combine_active_instances` staticmethod — leave those alone.
- Pure Python; no root build/lint/formatter config or `pyproject.toml` (exception: `Launchpad95_typed/mypy.ini` targets Python 3.11).

## Hard constraint (read first)
- **All software changes must live inside `Launchpad95_typed/`** when working on the Launchpad95 script.
- The sibling `../_Framework/` directory is **decompiled third-party code** (Ableton Live's internal framework, recovered with uncompyle6 from a 3.7-era Ableton build, compiled 2024-03-09). It is owned by Ableton, provided by Live at runtime, and **strictly read-only — never edit, patch, or "fix" files there.**
- 8 files contain decompiler artifacts that are Python syntax errors: `ControlSurface.py:516`, `DeviceComponent.py:269`, `EncoderElement.py:27`, `IdentifiableControlSurface.py:30`, `MixerComponent.py:225`, `SceneComponent.py:102`, `Task.py:462`, `Util.py:65`. A type checker **cannot parse** them — that's why `Launchpad95_typed/stubs/` exists (see Type checking).
- The snapshot may not match what current (3.11-era) Live ships. Treat it as reference for *structure and intent*; when runtime behavior is in question, verify against the live installation (decompile the `.pyc` from the current Live.app).
- Do not add third-party dependencies. Remote scripts are plain Python files installed into Live; there is no package manager.

## Entry points & structure
- Each script must expose `create_instance(c_instance)` and `get_capabilities()` in its `__init__.py` (Ableton API). Follow existing patterns in the specific controller directory you edit.
- `_Framework.*` provides base classes (`ControlSurface`, components). Do not import from real `_Framework` outside Live; in tests it is aliased via fakes.
- `Launchpad95_typed/` is the active project (a typed extension of the Novation Launchpad/Pro-style remote script). See the **Launchpad95_typed** section. Other top-level dirs are standard upstream remote scripts.

## Setup (first time)
- Run `./setup.sh` from the repo root to create `Launchpad95_typed/.venv` and install `pytest` + `future`. Override Python with `PYTHON=python3.11 ./setup.sh`.
- Two venvs exist and both pass the suite:
  - Root `.venv` (Python 3.11.18, pytest) — the **canonical test venv**; every doc says to run tests with `.venv/bin/python -m pytest Launchpad95_typed/tests/` from the worktree root.
  - `Launchpad95_typed/.venv` (created by `setup.sh`; has pytest **and** mypy) — use it for mypy.
- System `python3` has no pytest.

## Testing (Launchpad95_typed only)
- Only `Launchpad95_typed/` has a runnable pytest suite using fakes. Other controller directories have no test harness.
- Run from the worktree root: `.venv/bin/python -m pytest Launchpad95_typed/tests/` (baseline: 8 test files, 193 passed / 4 skipped, ~12 s — a slower or hanging run is a red flag).
- Bootstrap: root `conftest.py` pre-installs the fake `Live`/`_Framework` environment *before* pytest imports anything from the package (`tests/__init__.py` makes `tests` a subpackage, so importing it executes `Launchpad95_typed/__init__.py`, which needs the fakes). `Launchpad95_typed/tests/conftest.py` adds the daemon-thread patch and fixtures (`host`, `song`, `surface`, `static_surface`).
- Test files: `test_autodetect_models.py`, `test_main_selector.py`, `test_model_folders.py`, `test_scale.py`, `test_skins.py`, `test_smoke.py`, `test_static_models.py`, `test_surface_core.py`.
- `surface` fixture: the auto-detecting `Launchpad`, default model **mk2**; parameterize with `@pytest.mark.parametrize("surface", ["mk1","mk2","mk3","lpx"], indirect=True)`. Tests set the model flag, clear `_suppress_send_midi`, and call `init()` directly — they **bypass the SYSEX handshake**.
- `static_surface` fixture: parametrized over `LP_MK1`/`LP_MK2`/`LP_MK3`/`LP_X` (static per-model classes, eager init).
- Fakes live in `tests/`: `fakes.py` (`FakeHostApi`, `install_fake_environment`), `fake_live.py`, `fake_core.py`, `fake_framework/`. Fakes must not import anything from `Live` or `_Framework`. The fakes are the **executable specification** of the host surface — when stubs and fakes disagreed, the fakes won (they encode what current Live actually provides).
- `_suppress_send_midi` drops every outgoing MIDI message until the (bypassed) handshake clears it. Tests must set `s._suppress_send_midi = False` to observe anything on `host.midi_out`.
- Device-controller strips spawn a background thread each (`DeviceControllerStripServer.run` loops forever); `tests/conftest.py` swaps the proxy's `Thread` for a daemon subclass so the suite exits cleanly. If you add components that start threads, expect the same treatment.
- `tests/` and `stubs/` are never imported inside Live and are inert; optionally exclude them when copying the folder to the Live Remote Scripts directory.

## Launchpad95_typed — architecture
A custom "LaunchPad95" remote script supporting four hardware models, auto-detected at runtime via SYSEX handshake. The code labels them **classic / mk2 / mk3 / LPX**; the per-model static classes are `LP_MK1`, `LP_MK2`, `LP_MK3`, `LP_X` (the "mk3" path uses the Launchpad Mini MK3 SYSEX identity, `LP_MINI_MK3_ID = 13`; `LP_X_ID = 12`).

### Two entry styles
- **`Launchpad`** (`Launchpad.py`): the auto-detecting entry point used by `__init__.py`. Two-stage, load-bearing init: `__init__` sends the SYSEX challenge and defers; the device's response is matched in `handle_sysex`, which sets a model flag (`_mk2_rgb` / `_mk3_rgb` / `_lpx`; unset = MK1), sends model-specific setup SYSEX (programmer mode, LED feedback internal-off/external-on, sleep-mode disable), clears `_suppress_send_midi`, calls `set_enabled(True)`, then `init()` performs full construction. **Do not touch the two-stage init or the handshake logic.**
  - Challenge sent on load (all models at once): Novation identity request `(240,47,1,127,2,1,247)` (MK3/LPX answer), an MK2 challenge `(240,0,32,41,2,24,64)` + 4 random challenge bytes, and 4× MK1 SysEx `(176,17+i,challenge_byte)`.
  - Response matching: MK3/LPX reply starts `(240,126,0,6,2,0,32,41)` with reply code `(19,1)` (MK3) or `(3,1)` (LPX); MK2/MK1 replies are validated with `Live.Application.encrypt_challenge2(self._challenge)`.
- **`LP_MK1` / `LP_MK2` / `LP_MK3` / `LP_X`** (`LP_*.py`): statically configured per-model classes that build everything eagerly in `__init__`. The per-model Live script folders (`Launchpad95_MK1/`, `Launchpad95_MK2/`, `Launchpad95_MK3/`, `Launchpad95_X/`) are thin wrappers re-exporting `create_instance`/`get_capabilities` and instantiating the matching class.
- `LaunchpadBase.py` is the shared base: SYSEX constants, `_build_controls()`, MIDI send/receive, the `host_api` property, and the `core` property.

### Model-specific hardware differences (set in `Launchpad.init()` / static classes)
- Skin/color tables: `SkinMK1.make_skin_mk1()` vs `SkinMK2.make_skin_mk2()` (+ `ColorsMK1`/`ColorsMK2`). MK2/MK3/LPX are RGB; MK1 is classic.
- Grid note mapping: `_grid_note_classic` (MK1) vs `_grid_note_rgb` (others); different `_side_notes` / `_drum_notes` tuples per model.
- `_top_button_cc_base`: 91 for MK3/LPX, 104 for MK1/MK2.
- `_side_button_midi_type`: `MIDI_CC_TYPE` for MK3/LPX, `MIDI_NOTE_TYPE` otherwise.

### Key files
- `__init__.py` — `create_instance` / `get_capabilities` (vendor 4661; product IDs for classic Launchpad, Mini, MK2 range 105–120, Mini MK3 275, Launchpad X 259).
- `LaunchpadBase.py` — base class (SYSEX, control building, MIDI, `host_api`, `core`).
- `Launchpad.py` — auto-detecting entry point (above).
- `LP_MK1/MK2/MK3/X.py` — static per-model classes.
- `surface_core.py` — `SurfaceCore` facade composing the 10 protocol adapters (`HostApiAdapter`, `MidiTransportAdapter`, `MidiDispatcherAdapter`, `MidiMapManagerAdapter`, `ComponentRegistryAdapter`, `ComponentLifecycleAdapter`, `TaskSchedulerAdapter`, `DeviceLockManagerAdapter`, `SessionHighlighterAdapter`, `ReentrancyGuardAdapter`).
- `contracts.py` — structural-typing protocols (`HostApi`, `ControlSurfaceFacade`, ...) declared under `TYPE_CHECKING`; **zero runtime footprint by construction**.
- `Settings.py`, `Log.py`, `M4LInterface.py` (OSD component) + `M4LDevice/Launchpad95OSDHelper.amxd` (Max-for-Live device that renders the on-screen display), `web/` (setup screenshots, manual PDF).
- Components (upstream Launchpad Pro-derived, typed): `MainSelectorComponent` (the big one: session/clip grid + mode switching), `SpecialSessionComponent` / `SpecialProSessionComponent` / `SpecialProSessionRecordingComponent`, `StepSequencerComponent` / `StepSequencerComponent2`, `DeviceControllerComponent` + `DeviceControllerStrip(Server/Proxy)` (background-thread OSC-ish device control), `TrackControllerComponent`, `DefChannelStripComponent`, `InstrumentControllerComponent`, `NoteEditorComponent`, `NoteSelectorComponent`, `NoteRepeatComponent`, `LoopSelectorComponent`, `ScaleComponent`, `SubSelectorComponent`, `TargetTrackComponent`, `SpecialMixerComponent`, `ButtonSliderElement` / `PreciseButtonSliderElement`, `ConfigurableButtonElement`, `ClipSlotMK2`.

### Typing / facade rules
- **Host seam:** components talk to the Ableton host through `control_surface.host_api` (a typed property returning `self._c_instance`). Do not reintroduce `control_surface._c_instance` reach-throughs in components.
- **Keep protocols under `TYPE_CHECKING`.** Do not move them to runtime, and do not use `isinstance(x, SomeProtocol)` for control flow — `@runtime_checkable` only checks method *presence*. Protocols are for the type checker, full stop.
- `_Framework.ControlSurface` is a 567-line god-class mixing 11 responsibilities (host bridge, global registry, MIDI RX/TX pipelines, MIDI-map management, component/control registry + lifecycle, task scheduling, host-state observation, device lock, session highlighting, re-entrancy guard + DI scope). We refactor *around* it, not inside it: its constructor injects 9 untyped callables (`parent_task_group`, `show_message`, `log_message`, `register_component`, `register_control`, `request_rebuild_midi_map`, `set_pad_translations`, `send_midi`, `song`) into every component — those keys are the de-facto interface the protocols name.
- `LaunchpadBase.core` lazily returns the `SurfaceCore` facade (or falls back to `self`); component constructors are typed against `ControlSurfaceFacade` under `TYPE_CHECKING`.

### Implementation notes
- No `__pycache__` in the Live script directories; do not commit them.
- `# @Reimport` marker comments (e.g. on the `SkinMK1`/`SkinMK2` imports in `Launchpad.py`): Live-specific hot-reload marker — on script reimport only `__init__.py` re-runs; marked imports re-execute so skin edits apply without restarting Live. No-op outside Live.
- `LaunchpadBase` schedules a deferred hardware update: `schedule_message(5, self._update_hardware)`.

## Type checking (mypy)
- Run from the worktree root: `Launchpad95_typed/.venv/bin/mypy --config-file Launchpad95_typed/mypy.ini Launchpad95_typed/` (expect: no issues; suite as of writing passes cleanly).
- `mypy.ini` sets `mypy_path = $MYPY_CONFIG_FILE_DIR/stubs`, so `import Live` / `from _Framework.X import Y` resolve to the local `.pyi` stub package (`Launchpad95_typed/stubs/`: `Live` module tree + the `_Framework` modules the script imports) instead of the corrupted decompiled sources. `tests/` and `stubs/` are excluded.
- mypy 2.x gotchas (documented in `mypy.ini`): keep the `exclude` value on a **single line** (multi-line makes mypy re-ingest the config file as a source); use `.pyi` files for stubs (`...`-bodied methods in `.py` stubs raise `empty-body`).
- Stubs are `.pyi` — not importable by CPython, zero runtime footprint. See `stubs/README.md`.

## Operational gotchas
- `copy_to.sh` is a macOS zsh script taking a directory argument (`copy_to.sh <scriptdir>`) that wipes + copies it to `~/Music/Ableton/User Library/Remote Scripts/`. Do not run as-is elsewhere; adjust paths if needed.
- Python 3.11+ only (Ableton Live 12 is the only supported host). Do not introduce legacy Python 2 patterns (new `Queue as queue`-style shims, `xrange`/`imap` polyfills, py2-era comments).
- Changes must stay consistent with existing indentation (tabs in the script sources), naming, and style in the target directory. Do not assume new tests are expected outside `Launchpad95_typed/`.
- After any runtime-touching change, verify in Live: copy the folder to `~/Music/Ableton/User Library/Remote Scripts/`, reload, and confirm the controller loads and mode buttons behave as before.

## Highest-value references
- `README.md` — upstream project context/disclaimer
- `conftest.py` (root) + `Launchpad95_typed/tests/conftest.py` — test bootstrap and fixtures
- `Launchpad95_typed/stubs/README.md` — stub package and mypy wiring
- `Launchpad95_typed/tests/` — fakes, fixtures, how to run/assert
