"""Worktree-root pytest bootstrap.

Installs the fake ``Live`` / ``_Framework`` environment *before* pytest
imports anything from the ``Launchpad95_typed`` package.

Why this file exists: ``Launchpad95_typed/tests/__init__.py`` makes ``tests``
a subpackage, so pytest imports ``tests/conftest.py`` as
``Launchpad95_typed.tests.conftest`` — which first executes
``Launchpad95_typed/__init__.py`` (``from _Framework.Capabilities import
...``). Without the fakes installed, that import resolves the *real*
``_Framework`` from the worktree root and fails outside of Ableton Live
(``ModuleNotFoundError: No module named 'past'``). Conftest files are
imported top-down (this file first), so installing the fakes here guarantees
the package ``__init__`` sees the fake ``_Framework`` / ``Live``.

The real bootstrap (fixtures, daemon patch) lives in
``Launchpad95_typed/tests/conftest.py``; this file only pre-installs the
fakes so that package import succeeds.
"""

from __future__ import annotations

import os
import sys

_ROOT = os.path.dirname(os.path.abspath(__file__))
_TESTS_DIR = os.path.join(_ROOT, "Launchpad95_typed", "tests")

for _path in (_TESTS_DIR, _ROOT):
    if _path not in sys.path:
        sys.path.insert(0, _path)

from fakes import install_fake_environment  # noqa: E402

install_fake_environment()
