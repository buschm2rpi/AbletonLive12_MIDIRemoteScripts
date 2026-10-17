"""Clean-room fake of Ableton's ``_Framework`` package, for the test environment.

This *package* mirrors the module layout of the decompiled ``../_Framework/``
sources (read-only reference). Each submodule here re-implements the small slice
of the corresponding real module that ``Launchpad95_typed`` depends on, as plain
Python with zero third-party dependencies.

The machinery that the real ``_Framework`` base classes are built from
(``Util``, ``Signal``, ``Disconnectable``, ``SubjectSlot``, ``Dependency``,
``Defaults``, ``Task``, ``Resource``, ``Proxy``) lives in ``tests/fake_core.py``;
the matching submodules below are thin re-exports of it.

The fake model of Ableton's ``Live`` module lives in ``tests/fake_live.py``.
Fake modules import from ``fake_core`` / ``fake_live`` directly — they never
import the real ``Live`` / ``_Framework`` / ``ableton`` / ``_Generic`` modules.

``fakes.install_fake_environment()`` imports this package and re-exports its
submodules into ``sys.modules`` under the ``_Framework`` / ``_Framework.*``
names (and installs the fake ``Live`` module), so that the unmodified
``Launchpad95_typed`` code can be imported and exercised outside of Live.
"""
