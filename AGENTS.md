# AGENTS.md

## Purpose
Compact instructions for OpenCode sessions. Only include guidance that would be easy to miss in this repo.

## Repo overview
- Collection of Ableton Live 12.4 MIDI Remote Scripts (Python). Each top-level directory is a controller script that Live loads directly (e.g., `Launchpad/`, `Push2/`, `APC40/`, `Launchpad95_typed/`).
- Runtime deps: Ableton Live's internal `_Framework/` and `ableton/` packages exist only inside Live. They are **not** pip-installable. Any execution outside Live requires fakes (see Testing).
- Target runtime is **Ableton Live 12 only** (Python 3.11+). Modern Python 3 syntax (type annotations, f-strings, etc.) is fine; do not maintain Python 2 compatibility.
- Pure Python; no root build/lint/typecheck/formatter config, `pyproject.toml`, or `Makefile` (exception: `Launchpad95_typed/mypy.ini` targets Python 3.11).

## Entry points & structure
- Each script must expose `create_instance(c_instance)` and `get_capabilities()` in its `__init__.py` (Ableton API). Follow existing patterns in the specific controller directory you edit.
- `_Framework.*` provides base classes (`ControlSurface`, components). Do not import from real `_Framework` outside Live; in tests it is aliased via fakes.
- `Launchpad95_typed/` is a typed/variant subproject with its own `CLAUDE.md`, plans, and pytest fake environment. Treat `Launchpad95_typed/CLAUDE.md` as authoritative for that directory. Other top-level dirs are standard remote scripts.

## Setup (first time)
- Run `./setup.sh` from the repo root to create `Launchpad95_typed/.venv` and install test dependencies (`pytest`, `future`). Override Python with `PYTHON=python3.11 ./setup.sh` if needed.

## Testing (Launchpad95_typed only)
- Only `Launchpad95_typed/` has a runnable pytest suite using fakes. Other controller directories have no test harness in this repo.
- Run from the worktree root: `Launchpad95_typed/.venv/bin/python -m pytest Launchpad95_typed/tests/` (system `python3` has no pytest).
- Bootstrap: root `conftest.py` pre-installs the fake `Live`/`_Framework` environment before tests import the package. `Launchpad95_typed/tests/conftest.py` adds daemon-thread patch and fixtures (`host`, `song`, `surface`, `static_surface`).
- `surface` fixture defaults to **mk2**. Parameterize when model matters: `@pytest.mark.parametrize("surface", ["mk1","mk2","mk3","lpx"], indirect=True)`.
- `static_surface` is parametrized over `LP_MK1`/`LP_MK2`/`LP_MK3`/`LP_X` (eager init, no two-stage handshake). Per-model Live script folders (`Launchpad95_MK1/`, `Launchpad95_MK2/`, `Launchpad95_MK3/`, `Launchpad95_X/`) re-export those classes from `Launchpad95_typed`.
- Tests bypass the SYSEX handshake (fixture sets model flags and calls `init()` directly). Do not expect `handle_sysex()` path to work with current fakes.
- Fake details and known edge cases: see `Launchpad95_typed/plan_phase3_tests.md` and `Launchpad95_typed/tests/conftest.py`.

## Operational gotchas
- `copy_to.sh` is macOS-specific (copies to `~/Music/Ableton/User Library/Remote Scripts/`). Do not run as-is on Linux; adjust paths if needed.
- Python 3.11+ only (Ableton Live 12 is the only supported host). Legacy py2-style patterns in older files (`from __future__ import with_statement`, `xrange`/`imap` polyfills) may be left in place when editing, but do not add them to new code — modern Python 3 syntax and type annotations are fine.
- Changes must stay consistent with existing indentation, naming, and style in the target directory. Do not assume new tests are expected outside `Launchpad95_typed/`.

## Highest-value references
- `README.md` — project context/disclaimer
- `conftest.py` (root) — global test bootstrap for Launchpad95_typed
- `Launchpad95_typed/CLAUDE.md` — architecture, modes, components, hardware notes (most detailed)
- `Launchpad95_typed/tests/` — fakes, fixtures, how to run/assert