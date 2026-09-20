# Plan: Protocol Interfaces for ControlSurface Construction

**Status:** Proposal — not yet implemented.
**Companion docs:** `CLAUDE.md` (project overview), `plan_type_hinting.md` (type-hinting rollout).
**Audience:** Any sub-agent or engineer picking up work on this repo. This document is self-contained; no prior conversation context is required.

---

## 1. Hard Constraint (read first)

> **All software changes and all new code must live inside the `Launchpad95_typed/` directory.**
> (Absolute path: `/Users/michael/Github-Repos/AbletonLive12_MIDIRemoteScripts_worktree/Launchpad95_typed/`)

The sibling `../_Framework/` directory is **decompiled third-party code** (Ableton Live's internal framework, recovered with uncompyle6). It is:

- Owned by Ableton, provided by Live at runtime, not part of this project.
- **Strictly read-only.** Never edit, patch, or "fix" files there.
- Partially broken: 8 files contain decompiler artifacts that are Python syntax errors
  (`ControlSurface.py:516`, `DeviceComponent.py:269`, `EncoderElement.py:27`,
  `IdentifiableControlSurface.py:30`, `MixerComponent.py:225`, `SceneComponent.py:102`,
  `Task.py:462`, `Util.py:65`). A type checker **cannot parse** those files.

Consequence: we cannot refactor the `_Framework.ControlSurface` god-class itself.
Instead we define the **contracts our code depends on**, and build/adjust **our own** code
inside `Launchpad95_typed/` against those contracts.

---

## 2. Why this work (the problem)

`_Framework.ControlSurface` is a 567-line god-class. Our concrete subclass `Launchpad`
and ~20 components depend on it through a mix of inheritance, private-attribute access,
and constructor injection of the raw host object. Three concrete smells:

1. **Leaky host access.** Components reach into a *private* attribute of a third-party
   class to talk to Ableton's host API:
   - `NoteSelectorComponent.py:190` — `self._control_surface._c_instance.set_feedback_velocity(...)`
   - `InstrumentControllerComponent.py:126,128` — same pattern
   - `MainSelectorComponent.py:22,43,66` — takes raw `c_instance` in its constructor, stores it, calls `.song()`
2. **No testability.** There is no test suite because everything requires Ableton Live +
   hardware. The root cause is that the host boundary (`c_instance` / `Live.MidiRemoteScript`)
   is a concrete, unimportable, un-fakeable dependency.
3. **Untyped implicit ports.** The base class distributes 9 untyped callables to all
   components via its DI injector (see §4). A component asking for `show_message` gets
   whatever the surface happens to bind — with no static contract.

---

## 3. Responsibility map of `_Framework.ControlSurface`

Analysis of `../_Framework/ControlSurface.py` (read-only reference). The class mixes
11 distinct responsibilities:

| # | Responsibility | Methods (evidence) |
|---|----------------|--------------------|
| 1 | **Host bridge** — proxies calls to Ableton's `Live.MidiRemoteScript` (`c_instance`) | `show_message`, `log_message`, `instance_identifier`, `toggle_lock`, `set_feedback_channels`, `set_controlled_track`, `release_controlled_track`, `_do_send_midi`, `_set_session_highlight`, `_toggle_lock` |
| 2 | **Global registry** — publishes itself into `__builtins__` so Live can enumerate surfaces | `publish_control_surface`, `get_control_surfaces`, `_control_surfaces` |
| 3 | **MIDI receive pipeline** — entry point, dispatch, forwarding to controls | `receive_midi`, `_do_receive_midi`, `is_sysex_message`, `handle_nonsysex`, `handle_sysex`, `_forwarding_registry`, `get_recipient_for_nonsysex_midi_message`, `notify_received_midi` |
| 4 | **MIDI send pipeline** — with dedup/accumulation optimization | `_send_midi`, `_flush_midi_messages`, `_midi_message_dict`, `mxd_midi_scheduler` |
| 5 | **MIDI map management** — Live.MidiMap rule installation, port/map suggestions, rebuild suppression | `build_midi_map`, `_install_mapping`, `_install_forwarding`, `_translate_message`, `request_rebuild_midi_map`, `suppressing_rebuild_requests`, `suggest_input_port` / `suggest_output_port` / `suggest_map_mode` / `suggest_needs_takeover`, `set_pad_translations` |
| 6 | **Component & control registry + lifecycle** | `_register_component`, `_register_control`, `components` / `root_components`, `get_control_by_name`, `disconnect`, `set_enabled`, `update`, `refresh_state`, `port_settings_changed`, `update_display`, `_refresh_displays` |
| 7 | **Task / time management** | `_task_group`, `schedule_message`, `_remaining_scheduled_messages`, `_process_remaining_scheduled_messages`, `@_scheduled_method` |
| 8 | **Host-state observation** — slots on the song model, broadcast to components | slots on `song().visible_tracks`, `scenes`, `view.selected_track/scene` → `_on_track_list_changed` / `_on_scene_list_changed` / `_on_selected_track_changed` / `_on_selected_scene_changed` |
| 9 | **Device lock management** | `set_device_component`, `can_lock_to_devices`, `lock_to_device`, `unlock_from_device`, `restore_bank` |
| 10 | **Session highlighting** | `set_highlighting_session_component`, `highlighting_session_component`, `_set_session_highlight` |
| 11 | **Re-entrancy guarding + DI scope** | `component_guard`, `accumulating_midi_messages`, `in_component_guard`, `_control_surface_injector` |

---

## 4. Key observation: the DI injector keys are already an implicit protocol surface

`ControlSurface.__init__` (read-only reference) contains:

```python
self._control_surface_injector = inject(
    parent_task_group=(const(self._task_group)),
    show_message=(const(self.show_message)),
    log_message=(const(self.log_message)),
    register_component=(const(self._register_component)),
    register_control=(const(self._register_control)),
    request_rebuild_midi_map=(const(self.request_rebuild_midi_map)),
    set_pad_translations=(const(self.set_pad_translations)),
    send_midi=(const(self._send_midi)),
    song=(self.song)).everywhere()
```

These 9 keys are the ports every component consumes — already a de-facto interface,
just untyped and stringly-typed. The protocols in §5 make this surface explicit and
statically checkable. **We are not inventing new abstractions; we are naming the ones
that already exist.**

---

## 5. Proposed protocol interfaces

Two environment facts shape the design:

1. **Python version: do not assume a single answer.** The current Live 12
   installation runs **CPython 3.11** (custom remote scripts compile to 3.11-magic
   `.pyc` files). But the `_Framework` snapshot in this repo was decompiled from an
   **older, 3.7-era Ableton build** — every file's uncompyle6 header says
   `Python bytecode version base 3.7.0 (3394)` (magic 3394 = CPython 3.7),
   `Compiled at: 2024-03-09`. (The `Decompiled from: Python 3.12.2` line is the
   interpreter that ran the *decompiler tool*, not Live's Python — a common
   misreading.) ⇒ Protocols live under `if TYPE_CHECKING:` so the design is
   **version-agnostic**: identical behavior on 3.7-era and 3.11-era Live, with
   **zero runtime footprint** either way.
2. **`_Framework` sources are unparseable** (decompiler artifacts, §1). ⇒ Protocol
   signatures use `Any` (with comments) where a `_Framework` type would appear, instead
   of importing the broken modules. (Optional Phase 4 adds minimal local stubs if the
   team later wants real structural checking.)

### 5.1 New file: `Launchpad95_typed/contracts.py`

Paste-ready content:

```python
# contracts.py
"""Structural-typing contracts for the Launchpad95 control surface.

These protocols name the interfaces that *our* code depends on. They are
defined under TYPE_CHECKING so this module executes nothing at runtime:
zero footprint, zero behavior change, and identical behavior whether the
script runs on a 3.7-era or a 3.11-era Live. (typing.Protocol is importable
at runtime on 3.8+, but a remote script that crashes takes the controller
down with it; static-only contracts carry no such risk.)

_Framework types appear as `Any` because the decompiled _Framework sources
contain syntax errors and cannot be parsed by a type checker.
"""
from __future__ import annotations

from contextlib import contextmanager
from typing import TYPE_CHECKING, Any, Callable, Iterator, List, Optional, Tuple

if TYPE_CHECKING:
    from typing import Protocol, runtime_checkable

    # ------------------------------------------------------------------
    # 1. Host boundary (responsibility 1)
    # ------------------------------------------------------------------
    @runtime_checkable
    class HostApi(Protocol):
        """The full surface of Ableton's Live.MidiRemoteScript (c_instance)
        that this project uses. The one seam between our code and Live."""
        def send_midi(self, midi_bytes: bytes) -> None: ...
        def show_message(self, message: str) -> None: ...
        def log_message(self, message: str) -> None: ...
        def request_rebuild_midi_map(self) -> None: ...
        def set_pad_translation(self, translations: Any) -> None: ...
        def set_session_highlight(self, track_offset: int, scene_offset: int,
                                  width: int, height: int,
                                  include_return_tracks: bool) -> None: ...
        def toggle_lock(self) -> None: ...
        def update_locks(self) -> None: ...
        def set_feedback_channels(self, channels: Any) -> None: ...
        def set_feedback_velocity(self, velocity: int) -> None: ...
        def set_controlled_track(self, track: Any) -> None: ...
        def release_controlled_track(self) -> None: ...
        def instance_identifier(self) -> int: ...
        def handle(self) -> int: ...
        def song(self) -> Any: ...
        def note_repeat(self) -> Any: ...

    # ------------------------------------------------------------------
    # 3+4. MIDI transport (responsibilities 3, 4)
    # ------------------------------------------------------------------
    class MidiTransport(Protocol):
        def send(self, midi_bytes: bytes, optimized: bool = True) -> bool: ...
        def receive(self, midi_bytes: bytes) -> None: ...
        def is_sysex(self, midi_bytes: bytes) -> bool: ...

    class MidiDispatcher(Protocol):
        """Routes incoming bytes to registered input controls."""
        def handle_nonsysex(self, midi_bytes: bytes) -> None: ...
        def handle_sysex(self, midi_bytes: bytes) -> None: ...

    # ------------------------------------------------------------------
    # 5. MIDI map management (responsibility 5)
    # ------------------------------------------------------------------
    class MidiMapManager(Protocol):
        def request_rebuild(self) -> None: ...
        def build(self, midi_map_handle: int) -> None: ...
        def set_pad_translations(self, translations: Any) -> None: ...
        def suggest_input_port(self) -> str: ...
        def suggest_output_port(self) -> str: ...
        def suggest_map_mode(self, cc_no: int, channel: int) -> int: ...
        def suggest_needs_takeover(self, cc_no: int, channel: int) -> bool: ...
        @contextmanager
        def suppressing_rebuild_requests(self) -> Iterator[None]: ...

    # ------------------------------------------------------------------
    # 6. Component registry + lifecycle (responsibility 6)
    # ------------------------------------------------------------------
    class ComponentRegistry(Protocol):
        def register_component(self, component: Any) -> None: ...   # ControlSurfaceComponent
        def register_control(self, control: Any) -> None: ...       # ControlElement
        @property
        def components(self) -> Tuple[Any, ...]: ...
        @property
        def root_components(self) -> Tuple[Any, ...]: ...
        @property
        def controls(self) -> List[Any]: ...
        def get_control_by_name(self, name: str) -> Optional[Any]: ...
        def disconnect_all(self) -> None: ...

    class ComponentLifecycle(Protocol):
        def update(self) -> None: ...
        def refresh_state(self) -> None: ...
        def set_enabled(self, enable: bool) -> None: ...
        def disconnect(self) -> None: ...

    # ------------------------------------------------------------------
    # 7. Task / time management (responsibility 7)
    # ------------------------------------------------------------------
    class TaskScheduler(Protocol):
        def schedule_message(self, delay_in_ticks: int,
                             callback: Callable[[], None],
                             parameter: Any = None) -> None: ...
        def update(self, delta: int) -> None: ...
        def clear(self) -> None: ...

    # ------------------------------------------------------------------
    # 8. Host-state observation (responsibility 8) — component side
    # ------------------------------------------------------------------
    class SongStateListener(Protocol):
        """What the surface broadcasts to each registered component."""
        def on_track_list_changed(self) -> None: ...
        def on_scene_list_changed(self) -> None: ...
        def on_selected_track_changed(self) -> None: ...
        def on_selected_scene_changed(self) -> None: ...

    # ------------------------------------------------------------------
    # 9+10. Device locks, session highlighting (responsibilities 9, 10)
    # ------------------------------------------------------------------
    class DeviceLockManager(Protocol):
        def set_device_component(self, component: Optional[Any]) -> None: ...  # DeviceComponent
        def can_lock_to_devices(self) -> bool: ...
        def lock_to_device(self, device: Any) -> None: ...
        def unlock_from_device(self, device: Any) -> None: ...
        def restore_bank(self, bank_index: int) -> None: ...

    class SessionHighlighter(Protocol):
        def set_highlighting_session_component(self, comp: Optional[Any]) -> None: ...  # SessionComponent
        def highlighting_session_component(self) -> Optional[Any]: ...

    # ------------------------------------------------------------------
    # 11. Re-entrancy guarding (responsibility 11)
    # ------------------------------------------------------------------
    class ReentrancyGuard(Protocol):
        @contextmanager
        def component_guard(self) -> Iterator[None]: ...
        @property
        def in_component_guard(self) -> bool: ...
        @contextmanager
        def accumulating_midi_messages(self) -> Iterator[None]: ...
        @contextmanager
        def suppressing_rebuild_requests(self) -> Iterator[None]: ...

    # ------------------------------------------------------------------
    # Aggregate facade: what our components may call on the surface
    # ------------------------------------------------------------------
    class ControlSurfaceFacade(Protocol):
        """Union of the ports our components actually use. Type component
        constructor parameters against this (or a narrower protocol above)
        instead of the concrete _Framework.ControlSurface."""
        host_api: HostApi
        @property
        def controls(self) -> List[Any]: ...
        def show_message(self, message: str) -> None: ...
        def log_message(self, *message: Any) -> None: ...
        def schedule_message(self, delay_in_ticks: int,
                             callback: Callable[[], None],
                             parameter: Any = None) -> None: ...
        def request_rebuild_midi_map(self) -> None: ...
        def set_enabled(self, enable: bool) -> None: ...
        def update(self) -> None: ...
        def disconnect(self) -> None: ...
        def get_control_by_name(self, name: str) -> Optional[Any]: ...
        @contextmanager
        def component_guard(self) -> Iterator[None]: ...
```

### 5.2 Composition sketch (for reference; only relevant to optional Phase 4)

If we ever build our own surface core (we cannot modify the third-party base class),
the facade would be assembled from collaborators, each satisfying one protocol:

```python
class ControlSurface:
    host_api: HostApi
    midi: MidiTransport
    dispatcher: MidiDispatcher
    midi_map: MidiMapManager
    registry: ComponentRegistry
    lifecycle: ComponentLifecycle
    scheduler: TaskScheduler
    locks: DeviceLockManager
    highlighter: SessionHighlighter
    guard: ReentrancyGuard
```

Because protocols are structural, the existing `_Framework.ControlSurface` instance
already satisfies most of them without any modification — which is exactly what makes
this plan low-risk.

---

## 6. Justification (why a principal architect and senior engineers should agree)

Each change below rests on one universally accepted principle:

1. **Dependency inversion.** Components currently depend on a concrete third-party
   class's *private* attribute (`_c_instance`). They should depend on a named,
   minimal interface (`HostApi`). Depending on abstractions is the single most
   basic rule of decoupled design; nothing here is exotic.
2. **Structural typing is idiomatic Python and zero-risk.** `Protocol` requires no
   inheritance and no modification of the existing class. The concrete
   `ControlSurface` satisfies the protocols *by construction* — the change is
   purely declarative. There is no behavior change to argue about.
3. **One seam to the host.** Today, 5+ files know that the host object is reachable
   as `control_surface._c_instance`. One public, typed `host_api` property means one
   place to fake in tests and one place to adapt if Live's API ever changes.
4. **Testability is unblocked at the root cause.** The reason this project has no
   tests is that every component transitively requires Live. A fake `HostApi`
   (a few dozen lines) removes that blocker for all pure-logic components
   (mode selection, scale math, skin/color mapping) — no Live, no hardware.
5. **We refactor *around* unmodifiable code, not inside it.** The base class is
   decompiled third-party code with known syntax corruption. The only safe
   boundary to refactor is our own code's *use* of it.
6. **The abstractions already exist.** §4 shows the DI injector keys are a
   de-facto interface. Naming them is documentation that the type checker
   enforces, not a new architectural invention.
7. **Zero runtime footprint by construction.** Protocols under `TYPE_CHECKING`
   (§5) cannot affect the running remote script. The only runtime change in the
   core plan is one property + three call-site edits that are pure renames.

---

## 7. Change inventory (every item is inside `Launchpad95_typed/`)

| Item | Type | File(s) |
|------|------|---------|
| `contracts.py` — all protocols, `TYPE_CHECKING`-only | **new file** | `Launchpad95_typed/contracts.py` |
| `host_api` property on `Launchpad` (returns `self._c_instance`, typed `HostApi`) | small edit | `Launchpad95_typed/Launchpad.py` |
| Replace `self._control_surface._c_instance.set_feedback_velocity(...)` with `self._control_surface.host_api.set_feedback_velocity(...)` | small edit | `Launchpad95_typed/NoteSelectorComponent.py` (line 190) |
| Same replacement (2 sites) | small edit | `Launchpad95_typed/InstrumentControllerComponent.py` (lines 126, 128) |
| Type the `c_instance` constructor parameter as `HostApi` (or rename to `host_api`) | small edit | `Launchpad95_typed/MainSelectorComponent.py` (lines 22, 43, 66) + call site in `Launchpad.py` (`init()`) |
| `TYPE_CHECKING` imports + protocol types on component constructors | edits | all component files (coordinate with `plan_type_hinting.md` phases) |
| `tests/` package: `fakes.py` (`FakeHostApi`, `FakeSong`, `FakeSongView`) + first test modules | **new files** | `Launchpad95_typed/tests/` |

**Nothing else changes.** No edits to `../_Framework/`, no new runtime dependencies,
no changes to `__init__.py` capabilities, no behavior changes.

---

## 8. Phased execution plan

### Phase 0 — `contracts.py` (zero risk)
- Add `Launchpad95_typed/contracts.py` exactly as in §5.1.
- **Acceptance:** file imports cleanly inside Live (it executes nothing); type
  checker (run from the worktree root) accepts it; `git diff` of any other file is empty.
- **Rationale:** establishes the vocabulary for all later phases; independently reviewable.

### Phase 1 — the host seam (tiny, behavior-identical)
- Add to `Launchpad`:
  ```python
  @property
  def host_api(self) -> "HostApi":   # TYPE_CHECKING import
      return self._c_instance
  ```
- Fix the three leak sites (§7) to use `control_surface.host_api`.
- In `MainSelectorComponent`, type the `c_instance` parameter as `HostApi`
  (keep the parameter name to avoid touching the call site, or rename both — reviewer's choice).
- **Acceptance:** in Live, behavior is byte-identical (pure delegation/rename);
  `grep -rn "_c_instance" Launchpad95_typed/` returns hits only in `Launchpad.py`
  (and `__init__.py`'s `create_instance` signature).
- **Rationale:** eliminates all private-attribute reach-throughs into third-party code.

### Phase 2 — type our code against the protocols
- Add `TYPE_CHECKING` imports of the protocols; type `control_surface` parameters as
  `ControlSurfaceFacade` (or the narrowest protocol each component actually uses).
- Coordinate with `plan_type_hinting.md` — its Phase 1–4 file list is the work queue;
  this plan supplies the types to use.
- **Acceptance:** type checker passes from the worktree root; runtime diff is empty.
- **Rationale:** the contract becomes enforced instead of documented-in-comments.

### Phase 3 — fakes + first tests
- Add `Launchpad95_typed/tests/` (`__init__.py`, `fakes.py`, first test modules).
- First candidates (pure logic, no MIDI needed): `MainSelectorComponent` mode
  transitions, `ScaleComponent` scale computation, `SkinMK1`/`SkinMK2` color mapping.
- **Acceptance:** `python3 -m pytest Launchpad95_typed/tests/` runs **outside** Live.
- **Note for installers:** Ableton only imports the remote script's top-level
  `__init__.py` and its import graph; `tests/` is never imported in Live and is inert.
  Optionally exclude `tests/` when copying the folder to
  `~/Documents/Ableton/User Library/Remote Scripts/`.
- **Rationale:** converts the project's biggest known gap (no tests) from
  "impossible" to "routine".

### Phase 4 — optional, only if later requested
- (a) Minimal local `_Framework` stub package (inside `Launchpad95_typed/stubs/`,
  surfaced via a mypy config inside `Launchpad95_typed/`) to replace the `Any`
  placeholders in `contracts.py`; or
- (b) A homegrown `SurfaceCore` facade composing the §5.2 collaborators, with
  `Launchpad` delegating to it, to decouple from the third-party god-class behavior.
- **Rationale:** both are higher-effort, lower-urgency hardening; do not start
  without explicit sign-off.

---

## 9. Anti-goals / what NOT to do

- **Do not edit anything in `../_Framework/`** (or any sibling directory). Read-only.
- **Do not move protocols out of `TYPE_CHECKING`.** Current Live is 3.11, so
  `typing.Protocol` *would* import fine — but runtime protocol objects buy
  little (next bullet) and add a failure mode to an embedded, hard-to-debug
  environment. Static-only is the safer default, and it keeps the script
  compatible with older Live versions.
- **Do not change runtime behavior in Phases 0–2.** Those phases are declarative.
  The only runtime diff allowed in the core plan is the `host_api` property and the
  three call-site renames (all pure delegation).
- **Do not use `isinstance(x, SomeProtocol)` for control flow** in the remote script.
  `@runtime_checkable` only verifies method *presence*, not signatures — a shallow
  check that can pass for the wrong object. Protocols are for the type checker,
  full stop.
- **Do not touch the two-stage init** (`Launchpad.__init__` → SYSEX challenge →
  `init()`). It is load-bearing hardware-detection logic; the host seam work must
  leave it intact.
- **Do not add third-party dependencies.** Remote scripts are plain Python files
  installed into Live; there is no package manager.

---

## 10. Verification & environment notes

- **Type checker:** run from the worktree root
  (`/Users/michael/Github-Repos/AbletonLive12_MIDIRemoteScripts_worktree/`) so both
  `Launchpad95_typed` and the (broken) `_Framework` are visible. Expect mypy/pyright
  to fail parsing the 8 corrupted `_Framework` files; configure the checker to skip
  `_Framework` (e.g. `--follow-imports=skip` / `exclude`) — our code references
  `_Framework` types only as `Any` or under `TYPE_CHECKING`, so this is fine.
- **`_Framework` snapshot age:** the decompiled files in `../_Framework/` come
  from a 3.7-era Ableton build (header: compiled 2024-03-09) and may not match
  what the current (3.11-era) Live ships. Treat them as reference for *structure
  and intent*; when runtime behavior is in question, verify against the live
  installation (e.g. decompile the `.pyc` from the current Live.app).
- **Tests:** plain `python3 -m pytest` from the worktree root, outside Live.
  Fakes must not import anything from `Live` or `_Framework`.
- **Live install check** (after any runtime-touching phase): copy the folder to
  `~/Documents/Ableton/User Library/Remote Scripts/`, reload in Live, confirm the
  controller loads and the mode buttons behave as before.

---

## Appendix A: Evidence index (file:line)

- Responsibility map methods: `../_Framework/ControlSurface.py` (read-only).
- DI injector keys: `../_Framework/ControlSurface.py`, `__init__` (the `inject(...)` call).
- Host leaks: `Launchpad95_typed/NoteSelectorComponent.py:190`,
  `Launchpad95_typed/InstrumentControllerComponent.py:126,128`,
  `Launchpad95_typed/MainSelectorComponent.py:22,43,66`.
- `c_instance` entry point: `Launchpad95_typed/__init__.py` (`create_instance`).
- Two-stage init: `Launchpad95_typed/Launchpad.py` (`__init__`, `init`, `handle_sysex`).
- Corrupted decompiled files (8): see §1 list.

## Appendix B: Relationship to `plan_type_hinting.md`

That plan adds `from __future__ import annotations` + `TYPE_CHECKING` imports across
all files and uses `Any` for unimportable `_Framework` types. This plan is its
natural extension: where that plan would write `Any` for a *surface* or *host*
dependency, this plan supplies the named protocol instead. Execute Phase 0 of this
plan first, then run the type-hinting phases using these protocols as the types.
