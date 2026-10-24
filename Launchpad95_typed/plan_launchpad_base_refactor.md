# Plan: LaunchpadBase refactor — static model selection via per-model script folders

## Goal

Split the monolithic `Launchpad` class (which currently *detects* the hardware model
from the SYSEX handshake) into a `LaunchpadBase` class plus one concrete subclass per
Launchpad model. Since you always know which Launchpad you own, model detection is
removed from the per-model path: each subclass is configured statically for its
hardware, and you select the model by picking the matching Remote Script folder in
Live (same idea as the existing `Launchpad95_MK2/` folder).

Scope: **`Launchpad95_typed/` only.** Do not touch the decompiled stock folders
(`Launchpad/`, `Launchpad_MK2/`, `Launchpad_Mini_MK3/`, `Launchpad_X/`, ...) —
`Launchkey/` imports `Launchpad.ConfigurableButtonElement`, so the stock folders
must stay untouched.

## Current state (facts from the code)

- `Launchpad95_typed/Launchpad.py` — `class Launchpad(ControlSurface)`:
  - `__init__` does **not** build any controls. It sets `_selector = None`,
    the model flags `_lpx / _mk2_rgb / _mk3_rgb = False`, the challenge, and
    `_suppress_send_midi = True`.
  - `refresh_state` → schedules `_update_hardware` → `_send_challenge()` sends
    **all three probes at once** (identity request for MK3/LPX, sysex challenge
    for MK2, 4 CC messages for MK1) so that whichever pad is plugged in answers.
  - `handle_sysex` (lines ~255–304) branches on the response to decide the model,
    sets the corresponding flag, sends model-specific setup SYSEX (MK3/LPX
    programmer mode), then calls `init()`.
  - `init()` branches on the flags to pick skin (`SkinMK1` vs `SkinMK2`),
    side/drum notes, grid note numbering, top/side button CC vs NOTE; guarded by
    `_init_done`.
  - `disconnect()` branches on the flags for the model-specific quit SYSEX.
- Components read the flags directly off the control surface — **the flags are a
  compatibility surface and must keep their exact current semantics**:
  - `SpecialSessionComponent.py:14,18` — `lpx or mk3_rgb or mk2_rgb` (any RGB pad).
  - `SpecialProSessionComponent.py:459,531` — **only** `_mk2_rgb` (so today MK3/LPX
    do *not* get `ClipSlotMK2` in Pro session; preserve this quirk, note as possible
    follow-up).
- `Launchpad95_MK2/` is the reference pattern:
  - `LaunchpadBase.py` — shared machinery; the hardware-specific methods
    (`init`, `disconnect`, `handle_sysex`, `_send_challenge`) are **commented out**
    with triple-quoted strings, deferring them to subclasses.
  - `LP_MK2.py` — subclass: sets `_mk2_rgb = True`, skin/notes, builds controls in
    `__init__`, overrides `disconnect`, `handle_sysex` (own probe only) and
    `_send_challenge` (own probe only).
  - `__init__.py` — `create_instance` returns the concrete class; imports shared
    components from `Launchpad95_typed.*` (proves cross-folder import works when
    both folders are installed in `User Library/Remote Scripts/`).
- Tests: `Launchpad95_typed/tests/`, root `conftest.py` installs fakes first.
  `surface` fixture does `create_instance` → sets a model flag → `_suppress_send_midi
  = False` → `init()`. `test_smoke.py:15` asserts `type(surface).__name__ == "Launchpad"`.
- Baseline: **129 passed** with `Launchpad95_typed/.venv/bin/python -m pytest
  Launchpad95_typed/tests/` (run from the worktree root).

## Target architecture

```
Launchpad95_typed/
  LaunchpadBase.py      # shared ControlSurface machinery (extracted from Launchpad.py)
  Launchpad.py          # class Launchpad(LaunchpadBase) — auto-detect variant, default entry point
  LP_MK1.py             # class LP_MK1(LaunchpadBase)  — classic / S / Mini
  LP_MK2.py             # class LP_MK2(LaunchpadBase)  — Launchpad MK2
  LP_MK3.py             # class LP_MK3(LaunchpadBase)  — Launchpad Mini MK3
  LP_X.py               # class LP_X(LaunchpadBase)    — Launchpad X

Launchpad95_MK1/        # new folder: __init__.py only → LP_MK1
Launchpad95_MK2/        # exists (Phase 5 optionally rewires it to Launchpad95_typed.LP_MK2)
Launchpad95_MK3/        # new folder: __init__.py only → LP_MK3
Launchpad95_X/          # new folder: __init__.py only → LP_X
```

Folder names deliberately differ from the stock folders (`Launchpad_MK2`,
`Launchpad_Mini_MK3`, `Launchpad_X`) so both can be installed side by side.

### What stays in `LaunchpadBase`

Everything model-agnostic, i.e. everything that is already only written once:

- `host_api` property, `_active_instances` / combine-uncombine, `refresh_state`,
  `_update_hardware`, `_send_midi`, `_user_byte_value`, `_button_value`,
  `_config_value`, `_set_session_highlight`, `_init_note_repeat`,
  `build_midi_map` (reads `self._drum_notes`, already flag-driven).
- `init()` — the flag-driven control builder **unchanged** (skin, side/drum notes,
  grid formula, top/side button types are all branched on the flags already).
- `disconnect()` — flag-driven quit SYSEX **unchanged**.
- `_send_challenge()` — default keeps the current "send all three probes" behavior
  (needed by the auto-detect `Launchpad`).
- `handle_sysex()` — default keeps the current multi-branch detection behavior
  (needed by the auto-detect `Launchpad`).
- Module constants (`STD_MSG_HEADER`, `SYSEX_*`, `LP_MINI_MK3_ID`, ...).
- Class attributes `_lpx = _mk2_rgb = _mk3_rgb = False` (overridden per subclass).

### The four hooks a model subclass overrides

| Hook | Base / auto-detect `Launchpad` | `LP_MK1` | `LP_MK2` | `LP_MK3` | `LP_X` |
|---|---|---|---|---|---|
| flags (class attrs) | all `False` (set at runtime by detection) | all `False` | `_mk2_rgb = True` | `_mk3_rgb = True` | `_lpx = True` |
| `_send_challenge()` | all 3 probes | 4× CC `(176, 17+i, byte)` | sysex `(240,0,32,41,2,24,64)+4×7bit+(247,)` | identity request `(240,126,127,6,1,247)` | identity request |
| `handle_sysex()` | detection (sets flag → `init()` → enable) | match `(0,32,41,6)` + `encrypt_challenge2` → enable | match len-10 prefix + `encrypt_challenge2` → enable | match identity family `(19,1)` → programmer-mode SYSEX `(13,14,1)`, LED fb `(13,10,0,1)`, sleep off `(13,9,1)` → enable | same as MK3 with `LP_X_ID = 12`, family `(3,1)` |
| `__init__()` | common setup only (build deferred to handshake) | common setup → set flags → `self.init()` eagerly | same | same | same |
| `disconnect()` | flag-driven — works as-is for all subclasses | no quit SYSEX (flags false) | `(240,0,32,41,2,24,64,247)` | `(…,13,14,0)` + `(…,16,0)` | `(…,12,14,0)` + `(…,16,0)` |
| layout data (in `init()`, driven by flags) | see matrix below | | | | |

Layout matrix (already branched inside `init()`, no code change needed — just the
right flags set):

| | grid note | top buttons | side buttons | side notes | skin |
|---|---|---|---|---|---|
| MK1 | `row*16 + col` | CC `104+i` | NOTE | `(8,24,…,120)` | `SkinMK1` |
| MK2 | `(81 - 10*row) + col` | CC `104+i` | NOTE | `(89,79,…,19)` | `SkinMK2` |
| MK3 / LPX | `(81 - 10*row) + col` | CC `91+i` | CC | `(89,79,…,19)` | `SkinMK2` |

MK1 gets the MK1 drum-note table, MK2/MK3/LPX the MK2 table (flag-driven today).

### Why the eager `init()` is safe

Base `__init__` leaves `_suppress_send_midi = True`, so building controls eagerly
sends no MIDI. The handshake only flips `_suppress_send_midi = False` +
`set_enabled(True)` (and sends programmer-mode SYSEX on MK3/LPX) — exactly what
`Launchpad95_MK2/LP_MK2.py` already does successfully. The `_init_done` guard makes
a late `init()` call harmless if a subclass builds eagerly.

## Per-model script folders (model selection mechanism — your choice)

Each folder contains **only** `__init__.py`, following the repo's existing pattern:

```python
from _Framework.Capabilities import CONTROLLER_ID_KEY, PORTS_KEY, NOTES_CC, SCRIPT, SYNC, REMOTE, controller_id, inport, outport
from Launchpad95_typed.LP_MK3 import LP_MK3

def create_instance(c_instance):
    return LP_MK3(c_instance=c_instance)

def get_capabilities():
    return {CONTROLLER_ID_KEY: controller_id(vendor_id=4661,
                          product_ids=[275],
                          model_name=["Launchpad Mini MK3"]),
            PORTS_KEY: [inport(props=[NOTES_CC, REMOTE]),
                        inport(props=[NOTES_CC, REMOTE, SCRIPT]),
                        outport(props=[NOTES_CC, SYNC, REMOTE]),
                        outport(props=[NOTES_CC, SYNC, REMOTE, SCRIPT])]}
```

| Folder | Class | product_ids | model_name |
|---|---|---|---|
| `Launchpad95_MK1` | `LP_MK1` | `14, 32, 54` | `Launchpad`, `Launchpad S`, `Launchpad Mini` |
| `Launchpad95_MK2` (exists) | `LP_MK2` | `105…120` | `Launchpad MK2` … `Launchpad MK2 16` |
| `Launchpad95_MK3` | `LP_MK3` | `275` | `Launchpad Mini MK3` |
| `Launchpad95_X` | `LP_X` | `259` | `Launchpad X` |

- Product IDs / names taken from the stock folders' `get_capabilities()`.
- **PORTS_KEY**: reuse `Launchpad95_typed`'s 2-in/2-out set for all folders (it is
  proven to work for every model today); optionally trim to the stock per-model
  port sets later.
- `Launchpad95_typed/__init__.py` stays as-is: `create_instance` returns the
  auto-detecting `Launchpad`. The typed folder remains the "don't know / mixed"
  fallback and keeps the existing test entry point working.

## Backward-compatibility constraints (do not break)

1. `type(surface).__name__ == "Launchpad"` (`test_smoke.py:15`) — keep the
   auto-detect class named `Launchpad` and keep it as `create_instance`'s return.
2. The `surface` fixture flow (create → set flag → `_suppress_send_midi = False` →
   `init()`) must keep working for the auto-detect class.
3. Flag semantics stay byte-for-byte identical:
   - MK1 → no flags; MK2 → only `_mk2_rgb`; MK3 → only `_mk3_rgb`; LPX → only `_lpx`.
   - In particular `_mk2_rgb` must stay `False` on MK3/LPX (Pro-session quirk above).
4. Tabs for indentation in `Launchpad95_typed/` source files (match `Launchpad.py`).
5. Scripts are loaded by Live from `User Library/Remote Scripts/`; cross-folder
   imports (`Launchpad95_typed.*` from a sibling folder) are already proven by
   `Launchpad95_MK2/`.

## Phases

Each phase ends with the suite green: run from the worktree root

```
Launchpad95_typed/.venv/bin/python -m pytest Launchpad95_typed/tests/
```

- **Phase 0 — Baseline.** Suite currently **129 passed** (venv at
  `Launchpad95_typed/.venv`, Python 3.11, `pytest` + `future` installed).
- **Phase 1 — Mechanical extraction, no behavior change.**
  `git mv`-style move of the body of `class Launchpad` into a new
  `Launchpad95_typed/LaunchpadBase.py` as `class LaunchpadBase(ControlSurface)`;
  rewrite `Launchpad.py` to `class Launchpad(LaunchpadBase): pass`;
  `__init__.py` import path unchanged (`from .Launchpad import Launchpad`).
  Green suite = proof nothing moved wrongly.
- **Phase 2 — Static configuration on top of the base.**
  Give `LaunchpadBase` class-level flags (`_lpx = _mk2_rgb = _mk3_rgb = False`)
  and add the per-model hook overrides (`_send_challenge`, `handle_sysex`, eager
  `init()` in `__init__`). `handle_sysex` for concrete classes matches **only its
  own** response and forwards everything else to `ControlSurface.handle_sysex`.
- **Phase 3 — Concrete classes.** Add `LP_MK1.py`, `LP_MK2.py`, `LP_MK3.py`,
  `LP_X.py` under `Launchpad95_typed/` (one small file each, per the hook table).
  New tests: for each class —
  - constructed on the fake host, `_init_done is True`, flags exact, selector built;
  - grid/side/top button identifiers match the layout matrix;
  - with `_suppress_send_midi = False`, `_send_challenge()` emits **only** that
    model's probe (assert on `host.midi_out`);
  - `disconnect()` emits the model's quit SYSEX.
- **Phase 4 — Per-model folders.** Add `Launchpad95_MK1/`, `Launchpad95_MK3/`,
  `Launchpad95_X/` (`__init__.py` only). New tests: import each folder's
  `__init__`, assert `create_instance(host)` returns the right class and
  `get_capabilities()` carries the right `product_ids`.
- **Phase 5 (optional) — Dedupe `Launchpad95_MK2/`.** Point its `__init__.py` at
  `Launchpad95_typed.LP_MK2` and drop its local `LaunchpadBase.py` / `LP_MK2.py`
  bodies. Only do this after diffing behavior — the current local `LP_MK2` builds
  controls directly and has small differences (e.g. no `_init_note_repeat` guard
  ordering); decide then whether to keep the legacy folder untouched.
- **Phase 6 — Docs.** Update:
  - `Launchpad95_typed/CLAUDE.md` line 13 (entry-point description) and lines
    49–50 (line-number references into `Launchpad.py` will have moved);
  - `plan_phase3_tests.md` lines ~45 / 91–95 (fixture description) if the fixture
    gains a concrete-class path;
  - root `AGENTS.md` test command if the venv path is adopted there.

## Test-fixture evolution (Phase 3 detail)

Keep the current fixture for the auto-detect class, and add a second fixture (or
parametrize) for concrete classes:

```python
@pytest.fixture(params=[LP_MK1, LP_MK2, LP_MK3, LP_X])
def static_surface(host, request):
    s = request.param(c_instance=host)   # builds eagerly; _init_done True
    s._suppress_send_midi = False        # tests bypass the handshake
    return s
```

Known limitation (per `AGENTS.md` / `plan_phase3_tests.md`): the fakes do not
exercise the `handle_sysex()` path, so handshake logic is verified by
construction + probe/disconnect MIDI assertions, not by simulated responses.

## Risks / gotchas

- **Eager `init()` before handshake** must not emit MIDI: relies on
  `_suppress_send_midi = True` held by base `__init__` — do not flip it in
  subclass `__init__`.
- **MK3/LPX identity request**: with a known model we could skip the identity
  round-trip, but don't — the pad may need the wake-up/handshake before it
  accepts programmer-mode SYSEX. Keep handshake as an *enable gate*, only drop
  *detection*.
- **Auto-detect must keep probing all three protocols** or the fallback
  `Launchpad95_typed` folder regresses for users who rely on it.
- **`Live.Application.encrypt_challenge2` / `combine_apcs()`** are only available
  inside Live (faked in tests) — no new import-time dependencies.
- **Stock folders / `Launchkey`**: never modify `Launchpad/` etc.
- Two `LP_MK2` classes will briefly coexist (`Launchpad95_MK2.LP_MK2` and
  `Launchpad95_typed.LP_MK2`) until Phase 5 — acceptable, they live in different
  packages; do not import them into the same namespace.

## Open decisions (small, can be settled during implementation)

1. Phase 5 (rewire `Launchpad95_MK2`) — do it, or leave the legacy folder alone?
   *(Suggest: leave alone first, consider after the new folders are proven.)*
2. Trim `PORTS_KEY` per folder to match stock scripts, or keep the shared set?
   *(Suggest: keep shared set — proven across all models.)*
3. Whether `_suggested_input_port` / `_suggested_output_port` in the base should
   become a per-model override (currently one tuple listing every name). Not
   required for correctness; optional polish.
