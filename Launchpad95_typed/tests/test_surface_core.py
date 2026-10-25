"""Unit tests for SurfaceCore facade and protocol adapters (Phase 4b)."""
from Launchpad95_typed.surface_core import SurfaceCore


def test_surface_core_creation_and_core_property(surface):
    """Test that surface.core returns a valid SurfaceCore instance."""
    core = surface.core
    assert isinstance(core, SurfaceCore)
    assert core.host_api is not None
    assert core.midi is not None
    assert core.dispatcher is not None
    assert core.midi_map is not None
    assert core.registry is not None
    assert core.lifecycle is not None
    assert core.scheduler is not None
    assert core.locks is not None
    assert core.highlighter is not None
    assert core.guard is not None


def test_surface_core_delegates_to_host(surface, host):
    """Test that SurfaceCore convenience methods delegate to host API."""
    core = surface.core
    core.show_message("Test message")
    assert "Test message" in host.messages

    core.log_message("Log test message")
    assert any("Log test message" in m for m in host.messages)


def test_surface_core_song_and_application(surface):
    """Test that song and application access work on SurfaceCore."""
    core = surface.core
    assert core.song is not None
    assert core.application() is not None
