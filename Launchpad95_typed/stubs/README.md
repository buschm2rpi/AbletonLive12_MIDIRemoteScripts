# `stubs/` — type-checker-only stubs for `Live` and `_Framework`

This package exists **only for the static type checker** (mypy). It declares
the API surface that `Launchpad95_typed` depends on:

- `Live/` — the host-provided Ableton Live module (the `c_instance` host
  object, the song/track/device/clip/scene model, the application object).
- `_Framework/` — Ableton's decompiled third-party framework (the
  read-only `../_Framework/` snapshot in the worktree root is partially
  corrupted with decompiler artifacts and cannot be parsed by a type
  checker; these stubs replace it for type checking).

## Never imported at runtime

Nothing in the remote script imports `stubs`. In Live, `import Live` and
`from _Framework.X import Y` resolve to Live's own modules; `stubs/` is an
inert subdirectory of the script folder, exactly like `tests/`.

**Installer note:** when copying `Launchpad95_typed/` to
`~/Documents/Ableton/User Library/Remote Scripts/`, you may exclude
`stubs/` and `tests/` (both are dev-only).

## How it is surfaced to mypy

`Launchpad95_typed/mypy.ini` sets:

```ini
mypy_path = $MYPY_CONFIG_FILE_DIR/stubs
```

mypy searches `mypy_path` entries **before** the source directory, so
`_Framework` and `Live` resolve to these stubs even though the (broken)
real `_Framework/` sits in the worktree root. Run from the worktree root:

```sh
mypy --config-file Launchpad95_typed/mypy.ini Launchpad95_typed/
```

## Source of truth for the declared surface

The stubs mirror, with types, the API surface the test fakes exercise:

- `tests/fake_live.py` + `tests/fakes.py` — the `Live` model and the host
  object (`FakeHostApi` is the concrete stand-in for `Live.MidiRemoteScript`).
- `tests/fake_framework/` — the `_Framework` base classes.
- The read-only decompiled `../_Framework/` sources — for exact signatures.

Where the fakes and the decompiled snapshot disagree, the fakes win (they
encode what the script actually needs at runtime on current Live); such
places are commented in the stubs.

## What is *not* stubbed

Only the modules the script imports are declared (plus the intra-stub
dependencies they reference). The rest of `_Framework` (the new `Control`
system, displays, profiles, ...) is out of scope. `Any` is used where the
underlying object is opaque or heterogeneous (e.g. skin color values,
parameter objects in a few places) — each such `Any` is commented.
