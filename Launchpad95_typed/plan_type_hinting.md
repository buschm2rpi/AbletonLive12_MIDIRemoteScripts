# Plan: Add Python 3 Type Hinting to Launchpad95

## Goal
Add Python 3 type hints to all `.py` files in the `Launchpad95_typed/` directory.

## Key Challenges

1. **Ableton _Framework types are unavailable externally** — classes like `ControlSurface`, `ButtonElement`, `SessionComponent` can't be imported for type checking. They are provided by Ableton Live at runtime only.
2. **Python 2/3 compatibility** — code uses `from __future__` imports, `xrange` polyfills, `imap` polyfills.
3. **Large codebase** — many files with complex inter-component relationships.

## Strategy: `typing.TYPE_CHECKING` + `from __future__ import annotations`

- Add `from __future__ import annotations` at the top of each file so forward references work cleanly (Python 3.7+).
- Use `typing.TYPE_CHECKING` blocks to import _Framework types only during static type checking. These imports won't execute at runtime.
- For types we can't import or that lack stubs, use `object` or `Any` with clear comments.
- Use `mypy` or `pyright` for validation if needed, but accept that _Framework types will always be `Any`.

## What to Type

- **Public API** — `__init__.py` (`create_instance`, `get_capabilities`)
- **Component constructors and key methods** — the internal API surface between components
- **Standalone functions** — e.g., `level_to_value` in `SubSelectorComponent.py`, `log` in `Log.py`
- **Class attributes** — document the shape of data carried between components

## What to Skip

- Trivial getter/setter methods
- Methods that just delegate to parent classes
- Internal callback methods (listener patterns) where types add no value

## Phased Execution

### Phase 1: Core Infrastructure
- `__init__.py` — entry point, `create_instance`, `get_capabilities`
- `Launchpad.py` — main ControlSurface class
- `consts.py` — constants
- `Log.py` — logging utility
- `Settings.py` — Settings class
- `M4LInterface.py` — OSD interface

### Phase 2: Selector Chain
- `MainSelectorComponent.py` — top-level mode selector (largest file, most complex)
- `SubSelectorComponent.py` — mixer sub-modes

### Phase 3: Feature Components
- `SpecialSessionComponent.py` — session with custom clip skinning
- `SpecialProSessionComponent.py` — pro session variant
- `StepSequencerComponent.py` — drum step sequencer
- `StepSequencerComponent2.py` — melodic step sequencer
- `InstrumentControllerComponent.py` — Push-like instrument mode
- `DeviceControllerComponent.py` — device parameter control
- `TrackControllerComponent.py` — single-track controller
- `LoopSelectorComponent.py` — loop selection
- `NoteEditorComponent.py` — clip note editing
- `NoteSelectorComponent.py` — note selection
- `NoteRepeatComponent.py` — note repeat
- `TargetTrackComponent.py` — target track control

### Phase 4: Supporting Files
- `SpecialMixerComponent.py` — custom mixer
- `DefChannelStripComponent.py` — default channel strip
- `ClipSlotMK2.py` — custom clip slot
- `PreciseButtonSliderElement.py` / `ButtonSliderElement.py` — slider elements
- `ConfigurableButtonElement.py` — configurable button
- `ScaleComponent.py` — musical scale computation
- `SkinMK1.py` / `SkinMK2.py` — skin factories
- `ColorsMK1.py` / `ColorsMK2.py` — color tables
- `DeviceControllerStrip.py` / `DeviceControllerStripProxy.py` / `DeviceControllerStripServer.py` — device strip IPC
- `M4LInterface.py` — M4L interface (if not done in Phase 1)

## Implementation Notes

- Each phase should be reviewable independently.
- Use `# type: ignore` sparingly — prefer `TYPE_CHECKING` blocks.
- Keep Python 2/3 compatibility: `from __future__ import annotations` is available in Python 3.7+.
- The `Launchpad95_typed/` subdirectory is a secondary copy/variant — focus on the root-level files first.
