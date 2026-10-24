# surface_core.py
"""Homegrown SurfaceCore facade composing the protocol collaborators.

Phase 4b of plan_control_surface_protocols.md: builds a facade that composes
the responsibilities defined in contracts.py, providing a testable,
decoupled interface around the control surface functionality.

This module lives entirely inside Launchpad95_typed/ as required.
"""
from __future__ import annotations

from contextlib import contextmanager
from typing import TYPE_CHECKING, Any, Callable, Iterator, List, Optional

if TYPE_CHECKING:
    from .contracts import (
        ComponentLifecycle,
        ComponentRegistry,
        ControlSurfaceFacade,
        DeviceLockManager,
        HostApi,
        MidiDispatcher,
        MidiMapManager,
        MidiTransport,
        ReentrancyGuard,
        SessionHighlighter,
        SongStateListener,
        TaskScheduler,
    )
    from _Framework.ControlElement import ControlElement
    from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
    from _Framework.DeviceComponent import DeviceComponent
    from _Framework.SessionComponent import SessionComponent


class HostApiAdapter:
    """Adapter exposing the host API through the HostApi protocol."""
    
    def __init__(self, c_instance: Any) -> None:
        self._c_instance = c_instance
    
    def send_midi(self, midi_bytes: bytes) -> None:
        if self._c_instance is not None:
            self._c_instance.send_midi(midi_bytes)
    
    def show_message(self, message: str) -> None:
        if self._c_instance is not None:
            self._c_instance.show_message(message)
    
    def log_message(self, message: str) -> None:
        if self._c_instance is not None:
            self._c_instance.log_message(message)
    
    def request_rebuild_midi_map(self) -> None:
        if self._c_instance is not None:
            self._c_instance.request_rebuild_midi_map()
    
    def set_pad_translation(self, translations: Any) -> None:
        if self._c_instance is not None and hasattr(self._c_instance, 'set_pad_translation'):
            self._c_instance.set_pad_translation(translations)
        elif self._c_instance is not None:
            self._c_instance.set_pad_translations(translations)
    
    def set_session_highlight(self, track_offset: int, scene_offset: int,
                              width: int, height: int,
                              include_return_tracks: bool) -> None:
        if self._c_instance is not None:
            self._c_instance.set_session_highlight(track_offset, scene_offset, width, height, include_return_tracks)
    
    def toggle_lock(self) -> None:
        if self._c_instance is not None:
            self._c_instance.toggle_lock()
    
    def update_locks(self) -> None:
        if self._c_instance is not None and hasattr(self._c_instance, 'update_locks'):
            self._c_instance.update_locks()
    
    def set_feedback_channels(self, channels: Any) -> None:
        if self._c_instance is not None:
            self._c_instance.set_feedback_channels(channels)
    
    def set_feedback_velocity(self, velocity: int) -> None:
        if self._c_instance is not None:
            self._c_instance.set_feedback_velocity(velocity)
    
    def set_controlled_track(self, track: Any) -> None:
        if self._c_instance is not None:
            self._c_instance.set_controlled_track(track)
    
    def release_controlled_track(self) -> None:
        if self._c_instance is not None:
            self._c_instance.release_controlled_track()
    
    def instance_identifier(self) -> int:
        if self._c_instance is not None:
            return self._c_instance.instance_identifier()
        return 0
    
    def handle(self) -> int:
        if self._c_instance is not None and hasattr(self._c_instance, 'handle'):
            return self._c_instance.handle()
        return 0
    
    def song(self) -> Any:
        if self._c_instance is not None:
            return self._c_instance.song()
        return None
    
    @property
    def note_repeat(self) -> Any:
        if self._c_instance is not None:
            return getattr(self._c_instance, 'note_repeat')
        return None


class MidiTransportAdapter:
    """Adapter for MIDI transport operations."""
    
    def __init__(self, control_surface: Any) -> None:
        self._control_surface = control_surface
    
    def send(self, midi_bytes: bytes, optimized: bool = True) -> bool:
        if hasattr(self._control_surface, '_send_midi'):
            result = self._control_surface._send_midi(midi_bytes, optimized=optimized)
            return bool(result) if result is not None else True
        elif hasattr(self._control_surface, 'send_midi'):
            self._control_surface.send_midi(midi_bytes)
            return True
        return False
    
    def receive(self, midi_bytes: bytes) -> None:
        if hasattr(self._control_surface, 'receive_midi'):
            self._control_surface.receive_midi(midi_bytes)
    
    def is_sysex(self, midi_bytes: bytes) -> bool:
        if hasattr(self._control_surface, 'is_sysex_message'):
            return bool(self._control_surface.is_sysex_message(midi_bytes))
        if midi_bytes:
            return midi_bytes[0] == 0xF0 and midi_bytes[-1] == 0xF7
        return False


class MidiDispatcherAdapter:
    """Adapter for MIDI dispatching."""
    
    def __init__(self, control_surface: Any) -> None:
        self._control_surface = control_surface
    
    def handle_nonsysex(self, midi_bytes: bytes) -> None:
        if hasattr(self._control_surface, 'handle_nonsysex'):
            self._control_surface.handle_nonsysex(midi_bytes)
    
    def handle_sysex(self, midi_bytes: bytes) -> None:
        if hasattr(self._control_surface, 'handle_sysex'):
            self._control_surface.handle_sysex(midi_bytes)


class MidiMapManagerAdapter:
    """Adapter for MIDI map management."""
    
    def __init__(self, control_surface: Any) -> None:
        self._control_surface = control_surface
    
    def request_rebuild(self) -> None:
        if hasattr(self._control_surface, 'request_rebuild_midi_map'):
            self._control_surface.request_rebuild_midi_map()
    
    def build(self, midi_map_handle: int) -> None:
        if hasattr(self._control_surface, 'build_midi_map'):
            self._control_surface.build_midi_map(midi_map_handle)
    
    def set_pad_translations(self, translations: Any) -> None:
        if hasattr(self._control_surface, 'set_pad_translations'):
            self._control_surface.set_pad_translations(translations)
    
    def suggest_input_port(self) -> str:
        if hasattr(self._control_surface, 'suggest_input_port'):
            return self._control_surface.suggest_input_port()
        return ""
    
    def suggest_output_port(self) -> str:
        if hasattr(self._control_surface, 'suggest_output_port'):
            return self._control_surface.suggest_output_port()
        return ""
    
    def suggest_map_mode(self, cc_no: int, channel: int) -> int:
        if hasattr(self._control_surface, 'suggest_map_mode'):
            return self._control_surface.suggest_map_mode(cc_no, channel)
        return 0
    
    def suggest_needs_takeover(self, cc_no: int, channel: int) -> bool:
        if hasattr(self._control_surface, 'suggest_needs_takeover'):
            return bool(self._control_surface.suggest_needs_takeover(cc_no, channel))
        return False
    
    @contextmanager
    def suppressing_rebuild_requests(self) -> Iterator[None]:
        if hasattr(self._control_surface, 'suppressing_rebuild_requests'):
            with self._control_surface.suppressing_rebuild_requests():
                yield
        else:
            yield


class ComponentRegistryAdapter:
    """Adapter for component registry."""
    
    def __init__(self, control_surface: Any) -> None:
        self._control_surface = control_surface
    
    def register_component(self, component: Any) -> None:
        if hasattr(self._control_surface, '_register_component'):
            self._control_surface._register_component(component)
    
    def register_control(self, control: Any) -> None:
        if hasattr(self._control_surface, '_register_control'):
            self._control_surface._register_control(control)
    
    @property
    def components(self) -> tuple:
        if hasattr(self._control_surface, 'components'):
            comps = self._control_surface.components
            return tuple(comps) if comps is not None else ()
        return ()
    
    @property
    def root_components(self) -> tuple:
        if hasattr(self._control_surface, 'root_components'):
            comps = self._control_surface.root_components
            return tuple(comps) if comps is not None else ()
        return ()
    
    @property
    def controls(self) -> List[Any]:
        if hasattr(self._control_surface, 'controls') and self._control_surface.controls is not None:
            return list(self._control_surface.controls)
        return []
    
    def get_control_by_name(self, name: str) -> Optional[Any]:
        if hasattr(self._control_surface, 'get_control_by_name'):
            return self._control_surface.get_control_by_name(name)
        return None
    
    def disconnect_all(self) -> None:
        pass


class ComponentLifecycleAdapter:
    """Adapter for component lifecycle."""
    
    def __init__(self, control_surface: Any) -> None:
        self._control_surface = control_surface
    
    def update(self) -> None:
        if hasattr(self._control_surface, 'update'):
            self._control_surface.update()
    
    def refresh_state(self) -> None:
        if hasattr(self._control_surface, 'refresh_state'):
            self._control_surface.refresh_state()
    
    def set_enabled(self, enable: bool) -> None:
        if hasattr(self._control_surface, 'set_enabled'):
            self._control_surface.set_enabled(enable)
    
    def disconnect(self) -> None:
        if hasattr(self._control_surface, 'disconnect'):
            self._control_surface.disconnect()


class TaskSchedulerAdapter:
    """Adapter for task scheduling."""
    
    def __init__(self, control_surface: Any) -> None:
        self._control_surface = control_surface
    
    def schedule_message(self, delay_in_ticks: int,
                         callback: Callable[[], None],
                         parameter: Any = None) -> None:
        if hasattr(self._control_surface, 'schedule_message'):
            self._control_surface.schedule_message(delay_in_ticks, callback, parameter)
    
    def update(self, delta: int) -> None:
        pass
    
    def clear(self) -> None:
        pass


class DeviceLockManagerAdapter:
    """Adapter for device lock management."""
    
    def __init__(self, control_surface: Any) -> None:
        self._control_surface = control_surface
    
    def set_device_component(self, component: Optional[Any]) -> None:
        if hasattr(self._control_surface, 'set_device_component'):
            self._control_surface.set_device_component(component)
    
    def can_lock_to_devices(self) -> bool:
        if hasattr(self._control_surface, 'can_lock_to_devices'):
            return bool(self._control_surface.can_lock_to_devices())
        return False
    
    def lock_to_device(self, device: Any) -> None:
        if hasattr(self._control_surface, 'lock_to_device'):
            self._control_surface.lock_to_device(device)
    
    def unlock_from_device(self, device: Any) -> None:
        if hasattr(self._control_surface, 'unlock_from_device'):
            self._control_surface.unlock_from_device(device)
    
    def restore_bank(self, bank_index: int) -> None:
        if hasattr(self._control_surface, 'restore_bank'):
            self._control_surface.restore_bank(bank_index)


class SessionHighlighterAdapter:
    """Adapter for session highlighting."""
    
    def __init__(self, control_surface: Any) -> None:
        self._control_surface = control_surface
    
    def set_highlighting_session_component(self, comp: Optional[Any]) -> None:
        if hasattr(self._control_surface, 'set_highlighting_session_component'):
            self._control_surface.set_highlighting_session_component(comp)
    
    def highlighting_session_component(self) -> Optional[Any]:
        if hasattr(self._control_surface, 'highlighting_session_component'):
            return self._control_surface.highlighting_session_component()
        return None


class ReentrancyGuardAdapter:
    """Adapter for reentrancy guarding."""
    
    def __init__(self, control_surface: Any) -> None:
        self._control_surface = control_surface
    
    @contextmanager
    def component_guard(self) -> Iterator[None]:
        if hasattr(self._control_surface, 'component_guard'):
            with self._control_surface.component_guard():
                yield
        else:
            yield
    
    @property
    def in_component_guard(self) -> bool:
        if hasattr(self._control_surface, 'in_component_guard'):
            return bool(self._control_surface.in_component_guard)
        return False
    
    @contextmanager
    def accumulating_midi_messages(self) -> Iterator[None]:
        if hasattr(self._control_surface, 'accumulating_midi_messages'):
            with self._control_surface.accumulating_midi_messages():
                yield
        else:
            yield
    
    @contextmanager
    def suppressing_rebuild_requests(self) -> Iterator[None]:
        if hasattr(self._control_surface, 'suppressing_rebuild_requests'):
            with self._control_surface.suppressing_rebuild_requests():
                yield
        else:
            yield


class SurfaceCore:
    """Homegrown facade composing all protocol collaborators.
    
    As described in plan_control_surface_protocols.md §5.2:
    assembles collaborators for host_api, midi, dispatcher, midi_map,
    registry, lifecycle, scheduler, locks, highlighter, guard.
    """
    
    def __init__(self, control_surface: Any = None, c_instance: Any = None) -> None:
        self._control_surface = control_surface
        # Use c_instance from control_surface if not provided
        if c_instance is None and control_surface is not None:
            c_instance = getattr(control_surface, '_c_instance', None)
        self.host_api = HostApiAdapter(c_instance)
        self.midi = MidiTransportAdapter(control_surface)
        self.dispatcher = MidiDispatcherAdapter(control_surface)
        self.midi_map = MidiMapManagerAdapter(control_surface)
        self.registry = ComponentRegistryAdapter(control_surface)
        self.lifecycle = ComponentLifecycleAdapter(control_surface)
        self.scheduler = TaskSchedulerAdapter(control_surface)
        self.locks = DeviceLockManagerAdapter(control_surface)
        self.highlighter = SessionHighlighterAdapter(control_surface)
        self.guard = ReentrancyGuardAdapter(control_surface)
    
    # Convenience methods matching ControlSurfaceFacade
    @property
    def controls(self) -> List[Any]:
        if self._control_surface is not None and hasattr(self._control_surface, 'controls'):
            if self._control_surface.controls is not None:
                return list(self._control_surface.controls)
        return []
    
    def show_message(self, message: str) -> None:
        self.host_api.show_message(message)
    
    def log_message(self, *message: Any) -> None:
        msg = ' '.join(str(m) for m in message)
        if self._control_surface is not None and hasattr(self._control_surface, 'log_message'):
            self._control_surface.log_message(*message)
        else:
            self.host_api.log_message(msg)
    
    def schedule_message(self, delay_in_ticks: int,
                         callback: Callable[[], None],
                         parameter: Any = None) -> None:
        if self._control_surface is not None and hasattr(self._control_surface, 'schedule_message'):
            self._control_surface.schedule_message(delay_in_ticks, callback, parameter)
        else:
            self.scheduler.schedule_message(delay_in_ticks, callback, parameter)
    
    def request_rebuild_midi_map(self) -> None:
        if self._control_surface is not None and hasattr(self._control_surface, 'request_rebuild_midi_map'):
            self._control_surface.request_rebuild_midi_map()
        else:
            self.midi_map.request_rebuild()
    
    def set_enabled(self, enable: bool) -> None:
        self.lifecycle.set_enabled(enable)
    
    def update(self) -> None:
        self.lifecycle.update()
    
    def disconnect(self) -> None:
        self.lifecycle.disconnect()
    
    def get_control_by_name(self, name: str) -> Optional[Any]:
        if self._control_surface is not None and hasattr(self._control_surface, 'get_control_by_name'):
            return self._control_surface.get_control_by_name(name)
        return self.registry.get_control_by_name(name)
    
    @contextmanager
    def component_guard(self) -> Iterator[None]:
        with self.guard.component_guard():
            yield
    
    @property
    def song(self) -> Any:
        return self.host_api.song()
    
    def application(self) -> Any:
        if self._control_surface is not None and hasattr(self._control_surface, 'application'):
            return self._control_surface.application()
        if hasattr(self.host_api, '_c_instance') and self.host_api._c_instance is not None:
            if hasattr(self.host_api._c_instance, 'application'):
                return self.host_api._c_instance.application()
        return None


# Alias for compatibility
ControlSurfaceCore = SurfaceCore
