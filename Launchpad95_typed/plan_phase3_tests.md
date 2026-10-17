# Plan: Phase 3 — First Test Modules (closes `plan_control_surface_protocols.md`)

**Status:** Done — all steps complete (see per-step execution notes below).
**Companion docs:** `plan_control_surface_protocols.md` (Phase 3 spec, §8), `CLAUDE.md`.
**Audience:** Any sub-agent or engineer picking up work on this repo. This document is self-contained; no prior conversation context is required.

---

## 1. Phase 3 spec (from `plan_control_surface_protocols.md` §8)

- Add `Launchpad95_typed/tests/` (`__init__.py`, `fakes.py`, first test modules).
- First candidates (pure logic, no MIDI needed): `MainSelectorComponent` mode
  transitions, `ScaleComponent` scale computation, `SkinMK1`/`SkinMK2` color mapping.
- **Acceptance:** `python3 -m pytest Launchpad95_typed/tests/` runs **outside** Live.
- Fakes must not import anything from `Live` or `_Framework`.

## 2. Current state (verified by probing the fake environment)

**Already done — the fakes:**

| File | Contents |
|------|----------|
| `tests/fakes.py` | `FakeHostApi` (records messages/midi_out/highlights/rebuilds) + `install_fake_environment()` (installs fake `Live` + `_Framework` module trees into `sys.modules`) |
| `tests/fake_live.py` | 1294 lines: `Song`, `Track`, `Scene`, `Clip`, `Parameter`, `Application` (incl. `get_all_scales_ordered` with real scale names), `MidiMap`, `make_fake_song()` |
| `tests/fake_core.py` | 1771 lines: signal/subject/task machinery mirroring `_Framework` internals |
| `tests/fake_framework/` | ~50 clean-room modules (`ControlSurface`, `SessionComponent`, `ButtonElement`, `Skin`, `ModeSelectorComponent`, …) |
| `tests/conftest.py` | Installs the fake env before collection; fixtures `host`, `song`, `surface` |

- `create_instance(FakeHostApi())` works outside Live (verified).
- **Missing:** `tests/__init__.py` and **all** test modules — the suite currently
  collects 0 items.
- **Runner:** the worktree root has `.venv` (Python 3.11.17, pytest 9.1.1). The
  system `python3` has no pytest. Run: `.venv/bin/python -m pytest Launchpad95_typed/tests/`
  from the worktree root. (This satisfies the plan's acceptance wording; `conftest.py`
  already documents the venv invocation.)

## 3. Known gaps (found by driving the fakes; all fixed in Step 0, `tests/` only)

1. **The `surface` fixture is half-initialized (two-stage init).**
   `create_instance()` runs only `Launchpad.__init__`, which sends the SYSEX
   challenge and leaves `_selector = None`. The full construction (skin, matrix,
   `MainSelectorComponent`) happens in `Launchpad.init()`, which Live triggers from
   the hardware's challenge response via `handle_sysex`.
   ⇒ In tests, drive it directly: set the model flag
   (`_mk2_rgb` / `_mk3_rgb` / `_lpx`, or none for MK1) then call `surface.init()`.
   - Note: the SYSEX handshake itself cannot be driven with the current fakes —
     fake `Application.encrypt_challenge2` is the identity function on a 31-bit
     challenge, so the 2-byte response comparison in `handle_sysex` can never
     match. Bypass it in the fixture. (Optionally, a later step could fix the fake
     to a 16-bit reduction and add `handle_sysex` tests — out of scope for Phase 3.)
2. **Fake scene/clip colors are `None`; real Live returns ints.**
   On mk2/mk3/lpx, `SpecialSessionComponent.__init__` calls
   `set_rgb_mode(CLIP_COLOR_TABLE, RGB_COLOR_TABLE)`, arming the
   `find_nearest_color` path in `SceneComponent._color_value`. With
   `scene.color = None`, `hex_to_channels(None)` raises `TypeError` and `init()`
   crashes. The real decompiled framework has the same unguarded code, so real
   Live must supply an int.
   ⇒ Fix in `fake_live.py`: default `Scene._color` / `Clip._color` to an int
   (e.g. `0x000000`).
3. **Fake `Parameter` lacks `default_value`.**
   `DefChannelStripComponent._on_volume_changed` reads `volume.default_value`
   (real Live's `Parameter` has it); pressing the Mixer mode button crashes.
   ⇒ Fix in `fake_live.py`: add a settable `default_value` to the fake
   `Parameter` (default `0.0`).
4. **`DeviceControllerStripServer` spawns non-daemon `while True` threads.**
   One per device-controller strip, created via `DeviceControllerStripProxy`
   during `init()`. They block interpreter shutdown → the test process hangs
   after the suite.
   ⇒ Test-only fix in `conftest.py`: after `install_fake_environment()`, set the
   class attribute `DeviceControllerStripServer.daemon = True`. No production
   code change.

## 4. Steps

### Step 0 — fix the fake environment (tests/ only) — **DONE**

Files: `tests/fake_live.py`, `tests/conftest.py`, new `tests/__init__.py`,
plus a new worktree-root `conftest.py` (see execution notes, item 3).

1. `fake_live.py`: `Scene.__init__` / `Clip.__init__` — `self._color = 0x000000`.
2. `fake_live.py`: `Parameter` — add `default_value` (settable, default `0.0`).
3. `conftest.py`: rewrite the `surface` fixture to complete two-stage init:

   ```python
   @pytest.fixture
   def surface(host, request):
       from Launchpad95_typed import create_instance
       s = create_instance(host)
       model = getattr(request, "param", "mk2")
       if model == "mk2":
           s._mk2_rgb = True
       elif model == "mk3":
           s._mk3_rgb = True
       elif model == "lpx":
           s._lpx = True
       # model == "mk1": no flag
       s.init()
       return s
   ```

   Default to **mk2** (exercises the RGB color-table path). Where a specific model
   matters, parameterize:
   `@pytest.mark.parametrize("surface", ["mk1", "mk2"], indirect=["surface"])`.
4. `conftest.py`: after `install_fake_environment()`:

   ```python
   from Launchpad95_typed.DeviceControllerStripServer import DeviceControllerStripServer
   DeviceControllerStripServer.daemon = True
   ```
5. Add empty `tests/__init__.py` (named in the Phase 3 spec).

**Acceptance:** a scratch script that builds the full surface, presses all four
mode buttons (127 then 0), and exits with code 0 in < 5 s. — **PASSED**
(exit 0 in ~0.3 s; verified via a scratch script that loads both conftest
files in pytest's order).

#### Step 0 execution notes (deviations from the plan as written)

1. **Gap 5 (found during the acceptance run):** the fake `Song` lacked
   `can_undo` / `can_redo` / `undo()` / `redo()` —
   `SpecialProSessionComponent._update_undo_button` (called from every mode
   switch via `update()`) crashed with `AttributeError`. Also missing:
   `tempo`, `signature_numerator` / `signature_denominator`, `nudge_up` /
   `nudge_down`, `tap_tempo()` (used by pro-session tap/nudge/OSD paths).
   All added to `fake_live.py` (settable props / no-op methods).
2. **The daemon fix as written does not work.** The `while True` thread is
   *not* the `DeviceControllerStripServer` instance (it subclasses `Thread`
   but is never started); `DeviceControllerStripProxy` starts a plain
   `Thread(target=self.server.run)`. And in Python 3.11 the daemon decision
   is made at `start()` time (`Thread._set_tstate_lock` reads `self.daemon`),
   so a class attribute or a post-hoc `daemon = True` is ineffective
   (verified: 8 non-daemon threads, process hangs). `conftest.py` instead
   swaps the proxy module's `Thread` reference for a subclass that forces
   `daemon = True` before `start()`. Still test-only, no production change.
3. **A worktree-root `conftest.py` is required.** `tests/__init__.py` (per
   the Phase 3 spec) makes `tests` a subpackage, so pytest imports
   `tests/conftest.py` as `Launchpad95_typed.tests.conftest`, which first
   executes `Launchpad95_typed/__init__.py` → real `_Framework` →
   `ModuleNotFoundError: No module named 'past'` (verified). Conftest files
   are imported top-down, so the root `conftest.py` pre-installs the fake
   environment before the package import. It is the only file outside
   `tests/` — test infrastructure, not production code.

### Step 1 — smoke module `tests/test_smoke.py` — **DONE**

Proves the whole fake stack end-to-end before component-level tests.

- `test_create_instance_returns_launchpad` — `type(surface).__name__ == "Launchpad"`,
  `surface._init_done is True`.
- `test_full_init_builds_selector` — `isinstance(surface._selector, MainSelectorComponent)`,
  `surface._selector.number_of_modes() == 8`.
- `test_loaded_message` — `host.messages` contains `"LaunchPad95 (mk2) Loaded !"`.
- `test_update_in_each_main_mode` — for `i in range(4)`: press
  `surface._selector._modes_buttons[i]` (`receive_value(127)` then `receive_value(0)`),
  assert `_main_mode_index == i`, no exception.
- `test_disconnect` — `surface.disconnect()` runs clean.

**Acceptance:** module passes; the suite exits without hanging. — **PASSED**
(5 passed in ~0.6 s, clean exit; run from the worktree root with `.venv`).

#### Step 1 execution notes (fake gaps found by the smoke tests)

1. **`FakeHostApi.log_message` was a no-op**, so the "LaunchPad95 (mk2)
   Loaded !" banner (emitted via `ControlSurface.log_message`, which prefixes
   the class name → `"(Launchpad) LaunchPad95 (mk2) Loaded !"`) never reached
   `host.messages`. `fakes.py` now records it alongside `show_message`; the
   test asserts substring containment.
2. **Fake `ApplicationView` had the wrong listener API.** Real Live uses
   `add/remove_is_view_visible_listener(view_name, callback)` (callback takes
   no args — see `DeviceControllerComponent`), but the fake was a generic
   `Subject` whose generated `remove_*_listener(slot)` takes one argument,
   crashing `surface.disconnect()`. `fake_live.py` now implements the
   two-argument per-view API explicitly (the Subject metaclass would reject
   same-named methods), with callbacks fired on `show_view` / `hide_view`.

### Step 2 — `tests/test_main_selector.py` (mode transitions) — **DONE**

Use the fully-initialized `surface`; `sel = surface._selector`.

- **Pure functions:**
  - `channel_for_current_mode()` table: session → 0; user1 sub 0/1/2 → 11/3/4;
    user2 sub 0/1/2 → 1/2/5; mixer → `6 + sub_modes.mode()`.
  - `getSkinName()`: `instrument`→`"Note"`, `device`→`"Device"`, `"user 1"`→`"User"`,
    `"user 2"`→`"User2"`, `"drum stepseq"`→`"StepSequencer"`,
    `"melodic stepseq"`→`"StepSequencer2"`.
- **Button-driven transitions:**
  - Pressing `_modes_buttons[i]` sets `_main_mode_index == i`; the pressed button
    is on, the other three off.
  - Re-pressing User1 cycles `_sub_mode_list[1]` through `Settings.USER_MODES_1`
    (instrument → device → instrument); User2 likewise through `USER_MODES_2`.
  - Mode-specific host messages: `"SESSION MODE"`, `"MIXER MODE"`,
    `"INSTRUMENT MODE"`, `"DEVICE CONTROLLER MODE"`, `"DRUM STEP SEQUENCER MODE"`,
    `"MELODIC SEQUENCER MODE"`.
  - Component enablement: in mixer mode `sel._sub_modes.is_enabled()` is True and
    `sel._session.is_enabled()` is False; inverted in session mode.
- **Long-press pro-session toggle** (recommended): monkeypatch `time.time` in the
  `MainSelectorComponent` namespace; press→release within 500 ms toggles
  `_pro_session_on` and emits `"PRO SESSION MODE"`.

**Acceptance:** all tests pass deterministically (no real sleeps, no wall-clock
dependence). — **PASSED** (15 tests; full suite 20 passed in ~3 s, clean exit,
repeated runs identical).

#### Step 2 execution notes (deviations from the plan as written)

1. **`surface` fixture now clears `_suppress_send_midi`.**
   `Launchpad._send_midi` drops every message while the flag is set; it is
   cleared by `handle_sysex` right before `init()` — which the tests bypass.
   Without it `host.midi_out` stays empty and button LED states are
   unobservable. The fixture sets `s._suppress_send_midi = False` before
   `init()` (mirroring `handle_sysex`).
2. **Fake `InputControlElement.send_value` had a decompiler artifact.** The
   decompiled real code places the `elif` (dedup → `_do_send_value`) at the
   outer `if`'s indentation level (uncompyle6 artifact), which makes plain
   `send_value` a no-op for controls with `send_depends_on_forwarding = False`
   (their delayed-messages task never runs) — the mode buttons would never
   light up. The fake now implements the logically correct nested version
   (`elif` inside the outer `if`); documented in the file header. (The fake
   had already fixed a sibling artifact in the same function: the
   decompiler's `first[:None]` → `first:`.)
3. **Component-enablement expectation corrected.** The plan expected
   `sel._session.is_enabled() is False` in mixer mode, but the real code
   (decompiled framework, mirrored by the fake) re-enables the session
   component at the end of every `MainSelectorComponent.update()` cycle:
   `set_allow_update(True)` on the zooming component flushes its `update()`,
   and `DeprecatedSessionZoomingComponent.update()` calls
   `_session_set_enabled(not self._is_zoomed_out)`. The test asserts the
   actual final state (session enabled in both modes) plus the setup-level
   intent (`sel._setup_session(False, True)` → disabled).
4. **Button-state assertions read `host.midi_out`.** mk2 mode buttons are
   `top_buttons[4:]` = CC 108–111 on channel 0; LED state is the last CC
   value sent, compared against the skin-resolved `button.on_value` /
   `button.off_value` (skin colors, not raw 127/0).
5. **Determinism:** the `clock` fixture replaces `time` in the
   `MainSelectorComponent` namespace (the only wall-clock use in the
   mode-button path); `press_and_release` holds 600 ms by default so a
   button-0 release never triggers the < 500 ms long-press pro-session
toggle. Two dedicated tests cover the toggle (200 ms → toggles) and the
   threshold (600 ms → no toggle).

### Step 3 — `tests/test_scale.py` (scale computation) — **DONE**

Construct `ScaleComponent(control_surface=surface, enabled=True)` — the real
surface provides both `song()` and `show_message`.

- **`notes` property:** `set_key(0, message=False)` + Major modus →
  `[0, 2, 4, 5, 7, 9, 11]`; `set_key(4)` → `[4, 6, 8, 9, 11, 1, 3]` (mod 12).
- **Host sync:** `set_key(4)` (message=True) writes `song().root_note == 4` and
  emits `"Selected Scale: F Major"`; `set_modus(i)` writes `song().scale_name`
  and emits its message.
- **Listener round-trip:** mutate `song().root_note` directly →
  `handle_root_note_changed` fires with `listener_called=True` (no recursion;
  `song().root_note` unchanged).
- **Octave clamping:** `TOP_OCTAVE` per mode (diatonic 6, chromatic 7,
  diatonic_ns 2, chromatic_gtr 7, diatonic_chords 7; drumrack 8); `set_octave`
  rejects out-of-range; `_set_top_octave` clamps the current octave.
- **`get_pattern().note(x, y)`:** `root` iff the note equals `scale[0]`;
  `highlight` iff `scale[2]` or `scale[4]`; `in_scale`; `valid` within 0..127;
  `index == (base_note + 12*octave + note) % 128` with
  `base_note == (octave + 1) * 12`.
- **Mode buttons:** `_matrix_pressed(1, x, 0, True)` for x = 2..7 sets
  `_mode` / `_interval` / `_is_horizontal` (chromatic_gtr 3/True, diatonic_ns
  3/True, diatonic_chords 2/False, diatonic 3/True, chromatic 3/True, drumrack
  `is_drumrack` True).
- **Circle of fifths:** `_matrix_pressed` at (y=2, x=7) advances the key one
  step in `CIRCLE_OF_FIFTHS`; (y=1, x=6) steps back.

**Acceptance:** all tests pass. — **PASSED** (20 tests; full suite 40 passed
in ~4 s, clean exit).

#### Step 3 execution notes (deviations from the plan as written)

1. **Construction needs the injector context.** `ControlSurfaceComponent`
   resolves `song` via `@depends` from the global injection registry, which
   is only populated inside the surface's injector context. The `scale`
   fixture constructs the component inside `with surface.component_guard():`
   (the same guard the production script uses); the constructor call itself
   matches the plan.
2. **`notes` for key 4 is `[4, 6, 8, 9, 11, 13, 15]`, not the plan's
   `[4, 6, 8, 9, 11, 1, 3]`.** `Modus.scale(base_note)` returns
   `[base_note + x for x in notes]` — it transposes without mod 12. The test
   asserts the actual values.
3. **The key-4 message is `"Selected Scale: E Major"`, not `"F Major"`.**
   `KEY_NAMES[4]` is `"E"` (C=0, C#=1, D=2, D#=3, E=4). The test asserts the
   actual message.
4. **Fake scale ordering:** the fake `get_all_scales_ordered()` table puts
   `"Chromatic"` at modus 0 and `"Major"` at modus 1, so tests look up modus
   indices by name (`scale._modus_names.index("Major")`) instead of hardcoding.
5. **scale_name listener round-trip:** the fake song starts with
   `scale_name == "Major"`, so the test sets a different value
   (`"Natural Minor"`) to fire `handle_scale_name_changed`.
6. **Trivial invariants noted in the tests:** `MelodicPattern.note()` always
   returns a note taken from the scale (`in_scale` is always True) and the
   `% 128` wrap makes `valid` always True — the tests pin both as-is.

### Step 4 — `tests/test_skins.py` (color mapping) — **DONE**

- `SkinMK1.make_skin()` / `SkinMK2.make_skin()` resolve a curated list of every
  color key the code references: `DefaultButton.On/Off/Disabled`,
  `Mode.{Session,ProSession,Note,Drum,Device,StepSequencer,StepSequencer2,User,
  User2,Mixer}.On/.Off`, `Session.Clip*`, `ProSession.*`, `Scale.*`
  (AbsoluteRoot, Horizontal, Mode, Key, Octave, Modus, CircleOfFifths,
  RelativeScale, QuickScale), `NoteRepeater.*`, `Quant.*`.
- **Spot-check values:** MK1 `Colors.Session.ClipStarted == Rgb.GREEN`
  (`Color(52)`); MK2 uses a different palette (`ProSession.On == Rgb.MINT`,
  `Device.On == Rgb.PURPLE`, `StepSequencer2.On == Rgb.PINK`, …).
- `skin["Bogus.Key"]` raises `SkinColorMissingError`.
- **Static cross-check (high value):** regex-scan the project `.py` files
  (excluding `tests/`) for string literals passed to `set_on_off_values`,
  `set_light`, `set_triggered_to_play_value`, `set_stopped_value`,
  `set_started_value`, `set_empty_value`, `set_selected_value`, and assert each
  dotted key resolves in **both** skins. Catches any skin entry missing from a
  palette.

**Acceptance:** all tests pass. — **PASSED** (89 tests in the module; full
suite 129 passed in ~5 s, clean exit, repeated runs identical).

#### Step 4 execution notes (deviations from the plan as written)

1. **The plan's spot-check `StepSequencer2.On == Rgb.PINK` is off by one.**
   In `SkinMK2` the *mode-button* color `Mode.StepSequencer2.On` is
   `Rgb.AMBER` (`Color(9)`); `Rgb.PINK` is `Mode.StepSequencer.On`. The test
   asserts the actual `Mode.StepSequencer2.On == Rgb.AMBER`.
2. **The plan's `ProSession.On == Rgb.MINT` means `Mode.ProSession.On`.**
   The top-level `ProSession.On` (zoom-in session) is `Rgb.GREEN` in the MK2
   palette; the *mode-button* color `Mode.ProSession.On` is `Rgb.MINT`
   (`Color(29)`). The test asserts `Mode.ProSession.On == Rgb.MINT`.
3. **`SkinColorMissingError` is imported via a production module, not
   `_Framework`.** The convention forbids tests importing `_Framework`
   directly, so the test pulls the exception from
   `Launchpad95_typed.ConfigurableButtonElement` (which imports it from
   `_Framework.Skin`).
4. **The static scanner found two production typos** (neither resolves in
   either skin): `"DefaultButton.Disable"` (`StepSequencerComponent.py:842`,
   `set_light`) and `"DefaultButton.Disaled"`
   (`StepSequencerComponent2.py:860`, single-arg `set_on_off_values`, which
   expands to `.On`/`.Off`). The anti-goals forbid editing production files in
   Phase 3, so the test pins them in `KNOWN_MISSING` and asserts the missing
   set equals *exactly* those — any new unresolved key (or a now-fixed typo)
   fails the test.
5. **Scanner semantics:** a single-string `set_on_off_values("X")` expands to
   `X.On`/`X.Off` (per `ConfigurableButtonElement.set_on_off_values`); calls
   with non-literal args (`"Mode." + mode1 + ".On"`,
   `"StepSequencer.NoteEditor.Velocity" + str(i)`, variables, ints) are out of
   scope for a literal scan; commented-out calls are also scanned (plain
   regex) — the keys they reference (`Zooming.Selected`/`Zooming.Stopped`)
   resolve in both skins, so this is harmless. The scan finds 152 distinct
   keys; `test_scan_finds_expected_keys` pins a lower bound (≥ 100) plus
   sentinel keys so a silently-broken scanner cannot pass.

### Step 5 — full suite, acceptance, docs — **DONE**

- From the worktree root: `.venv/bin/python -m pytest Launchpad95_typed/tests/ -v`
  → all green, clean exit (no hang), < 30 s.
- Grep check: no test file imports `Live` or `_Framework` directly (they arrive
  only via the fakes installed by `conftest.py`).
- Update `plan_control_surface_protocols.md`: mark Phase 3 complete (status line
  + pointer to this doc); note the acceptance command uses the worktree `.venv`
  (system `python3` has no pytest).
- Optional: one line in `CLAUDE.md`/README — "Tests:
  `.venv/bin/python -m pytest Launchpad95_typed/tests/` from the worktree root."

#### Step 5 execution notes

1. **Full suite:** 129 passed in ~4.3 s, exit 0, clean shutdown (no hang),
   repeated runs identical — well under the 30 s budget.
2. **Grep check:** no `import`/`from` of `Live` or `_Framework` in any test file
   (`__init__.py`, `conftest.py`, `test_smoke.py`, `test_main_selector.py`,
   `test_scale.py`, `test_skins.py`); no `__import__`/`sys.modules` access either.
   The only mentions are docstrings/comments. Fakes arrive via
   `conftest.py` → `fakes.install_fake_environment()`.
3. **Docs updated:** `plan_control_surface_protocols.md` status line now reports
   Phase 3 complete (Phases 0–1 complete, Phase 2 partial — `ControlSurfaceFacade`
   not yet wired, Phase 4 not started), the Phase 3 section is marked **DONE**
   with the venv acceptance note, and §10's Tests line points at the worktree
   `.venv`.
4. **CLAUDE.md:** the stale "No test framework" bullet in `Launchpad95_typed/CLAUDE.md`
   was replaced with the test-suite line. The worktree-root `README.md` is the
   upstream mirror's README (not this project's doc), so it was left untouched.

## 5. Conventions

- All changes live in `Launchpad95_typed/tests/` (plus the plan-doc status line
  in Step 5). **Zero production-code edits.**
- Tests import neither `Live` nor `_Framework` directly; the fake environment is
  installed by `conftest.py` before collection.
- Determinism: monkeypatch `time` where wall-clock is used; no real sleeps;
  function-scoped fixtures (fresh surface per test).
- Each module is independent; suite order must not matter.

## 6. Anti-goals

- **Do not edit `../_Framework/`** or any production file in `Launchpad95_typed/`.
- **Do not change the two-stage init logic** in `Launchpad.py`; tests drive
  `init()` directly.
- **Do not add third-party dependencies** (pytest is already in `.venv`; nothing
  else).
- **Do not make `DeviceControllerStripServer` threads daemon in production code**
  (runtime change; out of scope — the conftest patch covers tests).
- **Do not start Phase 4 work** (`_Framework` stubs, `SurfaceCore`).

## 7. Ordering & dependencies

```
Step 0 (fake fixes) → Step 1 (smoke) → { Step 2, Step 3, Step 4 in parallel } → Step 5
```

Rough sizes: Step 0 ≈ 4 small edits; each test module 50–150 lines.

## Appendix A: Evidence index (verified findings)

- Two-stage init: `Launchpad95_typed/Launchpad.py` — `__init__` (challenge,
  `_selector = None`), `init()` (full construction), `handle_sysex` (model
  detection: mk3 bytes[8:10]==(19,1), lpx (3,1), mk2 10-byte prefix
  `(240,0,32,41,2,24,64)`, mk1 8-byte prefix `(240,0,32,41,6)`).
- Color-table arming: `Launchpad95_typed/SpecialSessionComponent.py:14-20`
  (`set_rgb_mode(CLIP_COLOR_TABLE, RGB_COLOR_TABLE)` on mk2/mk3/lpx); crash path
  `tests/fake_framework/SceneComponent.py:160-167` →
  `tests/fake_framework/ClipSlotComponent.py:14-23` (`hex_to_channels(None)`);
  real framework has the same unguarded code
  (`../_Framework/SceneComponent.py:164-184`, `../_Framework/ClipSlotComponent.py`).
- `default_value` gap: `Launchpad95_typed/DefChannelStripComponent.py:228`.
- Thread hang: `Launchpad95_typed/DeviceControllerStripServer.py:24`
  (`class DeviceControllerStripServer(ButtonSliderElement, threading.Thread)`),
  `run()` at line 500 (`while True` loop, exits only on `"shutdown"` queue item);
  spawned via `DeviceControllerStripProxy.py:27`.
- Fake `encrypt_challenge2` is identity: `tests/fake_live.py:84`.
- Mode-button input path: `tests/fake_framework/ButtonElement.py`
  (`receive_value` → `notify_value` → `_mode_value` listener).
- `Settings.USER_MODES_1 = ["instrument", "device"]`,
  `USER_MODES_2 = ["drum stepseq", "melodic stepseq"]`: `Launchpad95_typed/Settings.py`.
