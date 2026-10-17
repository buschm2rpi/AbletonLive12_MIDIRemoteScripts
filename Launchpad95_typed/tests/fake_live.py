"""Clean-room fake of Ableton's ``Live`` host module, for the test environment.

Ableton's ``Live`` module is provided by Live at runtime and cannot be imported
outside of it. This module re-implements the small slice of the Live *model* API
that ``Launchpad95_typed`` depends on, as plain Python classes.

All model classes are ``Subject``-based (from ``fake_core``): property setters
fire the corresponding subject event, so the signal/slot machinery of the fake
``_Framework`` works against them exactly as it would against real Live objects.

``fakes.install_fake_environment()`` assembles these classes into a fake
``Live`` module object (with the usual ``Live.Song`` / ``Live.Track`` / ...
submodule layout) and installs it in ``sys.modules``.
"""

from __future__ import annotations

from fake_core import Subject, SubjectEvent  # noqa: F401  (re-exported for fakes.py)


# ---------------------------------------------------------------------------
# Base
# ---------------------------------------------------------------------------

class LimitationError(Exception):
    """Raised by Live when a document limit is hit (mirrors Live.Base.LimitationError)."""


def log(message):
    print("Live: %s" % message)


# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------

class ApplicationView(Subject):
    """Minimal fake of Live's application view (the one with is_view_visible).

    Listener API matches real Live: ``add_is_view_visible_listener(view_name,
    callback)`` / ``remove_is_view_visible_listener(view_name, callback)`` —
    the callback is invoked (with no arguments) whenever that view's
    visibility changes. (The generic Subject listener machinery does not fit
    this two-argument API, so it is implemented explicitly.)
    """

    def __init__(self):
        super().__init__()
        self._visible_views = set()
        self._view_listeners = {}

    def is_view_visible(self, view_name):
        return view_name in self._visible_views

    def add_is_view_visible_listener(self, view_name, callback):
        self._view_listeners.setdefault(view_name, []).append(callback)

    def remove_is_view_visible_listener(self, view_name, callback):
        listeners = self._view_listeners.get(view_name)
        if listeners and callback in listeners:
            listeners.remove(callback)

    def show_view(self, view_name):
        if view_name not in self._visible_views:
            self._visible_views.add(view_name)
            self._fire_view_listeners(view_name)

    def hide_view(self, view_name):
        if view_name in self._visible_views:
            self._visible_views.discard(view_name)
            self._fire_view_listeners(view_name)

    def _fire_view_listeners(self, view_name):
        for callback in list(self._view_listeners.get(view_name, ())):
            callback()

    def disconnect(self):
        self._view_listeners.clear()


class Application:
    _instance = None

    @classmethod
    def combine_apcs(cls):
        return False

    @classmethod
    def get_application(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def get_random_int(cls, min_value, max_value):
        import random
        return random.randint(min_value, max_value)

    @classmethod
    def encrypt_challenge(cls, challenge):
        # The real implementation is a non-trivial hash; identity is fine for tests.
        return challenge

    @classmethod
    def encrypt_challenge2(cls, challenge):
        return challenge

    def get_document(self):
        return self._document

    def get_major_version(self):
        return 12

    def get_minor_version(self):
        return 0

    def get_bugfix_version(self):
        return 0

    @property
    def view(self):
        return self._view

    def __init__(self):
        self._document = None
        self._view = ApplicationView()


# ---------------------------------------------------------------------------
# MidiMap
# ---------------------------------------------------------------------------

class MapMode:
    absolute = 0
    relative = 1
    relative_smooth_two_compliment = 2
    relative_smooth_signed_bit = 3
    relative_smooth_binary_offset = 4
    absolute_14_bit = 5


class NoteFeedbackRule:
    def __init__(self):
        self.note_no = 0
        self.vel_map = ()


class CCFeedbackRule:
    def __init__(self):
        self.cc_no = 0
        self.cc_value_map = ()


class PitchBendFeedbackRule:
    def __init__(self):
        self.value_pair_map = ()


def map_midi_note_with_feedback_map(midi_map_handle, parameter, channel, note_no, feedback_rule):
    return True


def map_midi_cc_with_feedback_map(midi_map_handle, parameter, channel, cc_no, map_mode,
                                  feedback_rule, do_not_takeover, sensitivity):
    return True


def map_midi_pitchbend_with_feedback_map(midi_map_handle, parameter, channel, feedback_rule, do_not_takeover):
    return True


def send_feedback_for_parameter(midi_map_handle, parameter):
    return None


def forward_midi_note(handle, midi_map_handle, channel, note_no):
    return True


def forward_midi_cc(handle, midi_map_handle, channel, cc_no):
    return True


def forward_midi_pitchbend(handle, midi_map_handle, channel):
    return True


# ---------------------------------------------------------------------------
# Quantization / status enums
# ---------------------------------------------------------------------------

class Quantization:
    q_no_q = 0
    q_quarter = 1
    q_eight = 2
    q_sixtenth = 3
    q_thirtytwoth = 4
    q_quarter_triplet = 5
    q_eight_triplet = 6
    q_sixtenth_triplet = 7
    q_thirtysecond_triplet = 8
    q_half = 9
    q_half_triplet = 10
    q_bar = 11
    q_2_bars = 12
    q_4_bars = 13
    q_8_bars = 14


class RecordingQuantization:
    rec_q_no_q = 0
    rec_q_quarter = 1
    rec_q_eight = 2
    rec_q_sixtenth = 3
    rec_q_thirtysecond = 4
    rec_q_quarter_triplet = 5
    rec_q_eight_triplet = 6
    rec_q_sixtenth_triplet = 7
    rec_q_eight_eight_triplet = 8
    rec_q_sixtenth_sixtenth_triplet = 9


class SessionRecordStatus:
    off = 0
    on = 1
    transition = 2


class CaptureMode:
    all = 0
    all_except_selected = 1
    selected = 2


# ---------------------------------------------------------------------------
# Model objects
# ---------------------------------------------------------------------------

class Parameter(Subject):
    """A Live device parameter (the thing controls map to)."""

    __subject_events__ = ("value",)

    def __init__(self, name="Parameter", min=0.0, max=1.0, value=0.0, is_enabled=True,
                 default_value=0.0):
        super().__init__()
        self._name = name
        self._min = min
        self._max = max
        self._value = value
        self._is_enabled = is_enabled
        self._default_value = default_value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def min(self):
        return self._min

    @property
    def max(self):
        return self._max

    @property
    def is_enabled(self):
        return self._is_enabled

    @is_enabled.setter
    def is_enabled(self, value):
        self._is_enabled = value

    @property
    def default_value(self):
        return self._default_value

    @default_value.setter
    def default_value(self, value):
        self._default_value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        if new_value != self._value:
            self._value = new_value
            self.notify_value()

    def begin_gesture(self):
        pass

    def end_gesture(self):
        pass


class MixerDevice(Subject):
    __subject_events__ = ("crossfade_assign", "sends")

    def __init__(self):
        super().__init__()
        self.volume = Parameter("Volume")
        self.panning = Parameter("Panning", min=-1.0, max=1.0)
        self._sends = []
        self._crossfade_assign = 1
        self._crossfade_assignments = type("CrossfadeAssignments", (), {"values": [1, 2, 3, 4]})()

    @property
    def sends(self):
        return self._sends

    @sends.setter
    def sends(self, value):
        self._sends = list(value)
        self.notify_sends()

    @property
    def crossfade_assign(self):
        return self._crossfade_assign

    @crossfade_assign.setter
    def crossfade_assign(self, value):
        if value != self._crossfade_assign:
            self._crossfade_assign = value
            self.notify_crossfade_assign()

    @property
    def crossfade_assignments(self):
        return self._crossfade_assignments


class TrackView(Subject):
    __subject_events__ = ("selected_device",)

    def __init__(self, track=None):
        super().__init__()
        self._track = track
        self._selected_device = None

    @property
    def selected_device(self):
        return self._selected_device

    @selected_device.setter
    def selected_device(self, value):
        if value != self._selected_device:
            self._selected_device = value
            self.notify_selected_device()


class Track(Subject):
    __subject_events__ = ("mute", "solo", "arm", "implicit_arm", "input_routing_type",
                          "name", "fired_slot_index", "playing_slot_index",
                          "is_visible", "devices", "clip_slots")

    def __init__(self, name="Track", is_return=False, is_master=False):
        super().__init__()
        self._name = name
        self._is_return = is_return
        self._is_master = is_master
        self._mute = False
        self._solo = False
        self._arm = False
        self._implicit_arm = False
        self._input_routing_type = 0
        self._fired_slot_index = -1
        self._playing_slot_index = -1
        self._is_visible = True
        self._devices = []
        self._clip_slots = []
        self.mixer_device = MixerDevice()
        self.view = TrackView(self)
        self.canonical_parent = None

    # -- properties ------------------------------------------------------
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if value != self._name:
            self._name = value
            self.notify_name()

    @property
    def mute(self):
        return self._mute

    @mute.setter
    def mute(self, value):
        if value != self._mute:
            self._mute = value
            self.notify_mute()

    @property
    def solo(self):
        return self._solo

    @solo.setter
    def solo(self, value):
        if value != self._solo:
            self._solo = value
            self.notify_solo()

    @property
    def arm(self):
        return self._arm

    @arm.setter
    def arm(self, value):
        if value != self._arm:
            self._arm = value
            self.notify_arm()

    @property
    def implicit_arm(self):
        return self._implicit_arm

    @implicit_arm.setter
    def implicit_arm(self, value):
        if value != self._implicit_arm:
            self._implicit_arm = value
            self.notify_implicit_arm()

    @property
    def input_routing_type(self):
        return self._input_routing_type

    @input_routing_type.setter
    def input_routing_type(self, value):
        if value != self._input_routing_type:
            self._input_routing_type = value
            self.notify_input_routing_type()

    @property
    def fired_slot_index(self):
        return self._fired_slot_index

    @fired_slot_index.setter
    def fired_slot_index(self, value):
        if value != self._fired_slot_index:
            self._fired_slot_index = value
            self.notify_fired_slot_index()

    @property
    def playing_slot_index(self):
        return self._playing_slot_index

    @playing_slot_index.setter
    def playing_slot_index(self, value):
        if value != self._playing_slot_index:
            self._playing_slot_index = value
            self.notify_playing_slot_index()

    @property
    def is_visible(self):
        return self._is_visible

    @is_visible.setter
    def is_visible(self, value):
        if value != self._is_visible:
            self._is_visible = value
            self.notify_is_visible()

    @property
    def is_part_of_selection(self):
        return False

    @property
    def can_be_armed(self):
        return not self._is_return and not self._is_master

    @property
    def has_midi_input(self):
        return not self._is_master

    @property
    def is_frozen(self):
        return False

    @property
    def devices(self):
        return self._devices

    @devices.setter
    def devices(self, value):
        self._devices = list(value)
        self.notify_devices()

    @property
    def clip_slots(self):
        return self._clip_slots

    @clip_slots.setter
    def clip_slots(self, value):
        self._clip_slots = list(value)
        self.notify_clip_slots()

    # -- methods ---------------------------------------------------------
    def stop_all_clips(self, force=False):
        for slot in self._clip_slots:
            if slot.clip is not None:
                slot.clip._stop()
        self.fired_slot_index = -1
        self.playing_slot_index = -1

    def duplicate_clip_slot(self, index):
        if 0 <= index < len(self._clip_slots):
            new_slot = ClipSlot()
            self._clip_slots.insert(index + 1, new_slot)
            self.notify_clip_slots()


class Scene(Subject):
    __subject_events__ = ("is_triggered", "color")

    def __init__(self, name="Scene"):
        super().__init__()
        self._name = name
        self._is_triggered = False
        self._color = 0x000000
        self._clip_slots = []
        self.canonical_parent = None

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def is_triggered(self):
        return self._is_triggered

    @is_triggered.setter
    def is_triggered(self, value):
        if value != self._is_triggered:
            self._is_triggered = value
            self.notify_is_triggered()

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        if value != self._color:
            self._color = value
            self.notify_color()

    @property
    def clip_slots(self):
        return self._clip_slots

    @clip_slots.setter
    def clip_slots(self, value):
        self._clip_slots = list(value)

    @property
    def is_empty(self):
        return all(slot.clip is None for slot in self._clip_slots)

    def fire(self):
        self.is_triggered = True

    def set_fire_button_state(self, state):
        self.is_triggered = bool(state)


class Clip(Subject):
    __subject_events__ = ("playing_status", "is_recording", "color")

    STOPPED, PLAYING, FINISHED = 0, 1, 2

    def __init__(self, name="Clip"):
        super().__init__()
        self._name = name
        self._playing_status = Clip.STOPPED
        self._is_recording = False
        self._color = 0x000000
        self._is_triggered = False
        self._will_record_on_start = False
        self.canonical_parent = None

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def playing_status(self):
        return self._playing_status

    @playing_status.setter
    def playing_status(self, value):
        if value != self._playing_status:
            self._playing_status = value
            self.notify_playing_status()

    @property
    def is_playing(self):
        return self._playing_status == Clip.PLAYING

    @property
    def is_recording(self):
        return self._is_recording

    @is_recording.setter
    def is_recording(self, value):
        if value != self._is_recording:
            self._is_recording = value
            self.notify_is_recording()

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        if value != self._color:
            self._color = value
            self.notify_color()

    @property
    def is_triggered(self):
        return self._is_triggered

    @property
    def will_record_on_start(self):
        return self._will_record_on_start

    @will_record_on_start.setter
    def will_record_on_start(self, value):
        self._will_record_on_start = value

    def fire(self):
        self._is_triggered = True
        self.playing_status = Clip.PLAYING

    def set_fire_button_state(self, state):
        self._is_triggered = bool(state)
        self.playing_status = Clip.PLAYING if state else Clip.STOPPED

    def _stop(self):
        self.playing_status = Clip.STOPPED
        self._is_triggered = False

    def quantize(self, quantization, amount):
        pass

    def clear_all_envelopes(self):
        pass


class ClipSlot(Subject):
    __subject_events__ = ("has_clip", "controls_other_clips", "color",
                          "playing_status", "is_triggered", "has_stop_button")

    def __init__(self):
        super().__init__()
        self._clip = None
        self._controls_other_clips = True
        self._color = None
        self._is_triggered = False
        self._has_stop_button = False
        self._will_record_on_start = False
        self.canonical_parent = None

    @property
    def clip(self):
        return self._clip

    @clip.setter
    def clip(self, value):
        if value != self._clip:
            self._clip = value
            if self._clip is not None:
                self._clip.canonical_parent = self
            self.notify_has_clip()

    @property
    def has_clip(self):
        return self._clip is not None

    @property
    def controls_other_clips(self):
        return self._controls_other_clips

    @controls_other_clips.setter
    def controls_other_clips(self, value):
        if value != self._controls_other_clips:
            self._controls_other_clips = value
            self.notify_controls_other_clips()

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        if value != self._color:
            self._color = value
            self.notify_color()

    @property
    def is_triggered(self):
        return self._is_triggered

    @is_triggered.setter
    def is_triggered(self, value):
        if value != self._is_triggered:
            self._is_triggered = value
            self.notify_is_triggered()

    @property
    def playing_status(self):
        return self._clip.playing_status if self._clip is not None else Clip.STOPPED

    @property
    def has_stop_button(self):
        return self._has_stop_button

    @has_stop_button.setter
    def has_stop_button(self, value):
        if value != self._has_stop_button:
            self._has_stop_button = value
            self.notify_has_stop_button()

    @property
    def will_record_on_start(self):
        return self._will_record_on_start

    @will_record_on_start.setter
    def will_record_on_start(self, value):
        self._will_record_on_start = value

    def fire(self):
        self._is_triggered = True
        if self._clip is not None:
            self._clip.fire()
        else:
            self.notify_is_triggered()

    def set_fire_button_state(self, state):
        self._is_triggered = bool(state)
        if self._clip is not None:
            self._clip.set_fire_button_state(state)

    def create_clip(self, length):
        clip = Clip()
        self.clip = clip
        return clip

    def delete_clip(self):
        self.clip = None


class SongView(Subject):
    __subject_events__ = ("selected_track", "selected_scene", "detail_clip",
                          "selected_device", "selected_chain", "highlighted_clip_slot")

    def __init__(self, song=None):
        super().__init__()
        self._song = song
        self._selected_track = None
        self._selected_scene = None
        self._detail_clip = None
        self._selected_device = None
        self._selected_chain = None
        self._highlighted_clip_slot = None

    @property
    def selected_track(self):
        return self._selected_track

    @selected_track.setter
    def selected_track(self, value):
        if value != self._selected_track:
            self._selected_track = value
            self.notify_selected_track()

    @property
    def selected_scene(self):
        return self._selected_scene

    @selected_scene.setter
    def selected_scene(self, value):
        if value != self._selected_scene:
            self._selected_scene = value
            self.notify_selected_scene()

    @property
    def detail_clip(self):
        return self._detail_clip

    @detail_clip.setter
    def detail_clip(self, value):
        if value != self._detail_clip:
            self._detail_clip = value
            self.notify_detail_clip()

    @property
    def selected_device(self):
        return self._selected_device

    @selected_device.setter
    def selected_device(self, value):
        if value != self._selected_device:
            self._selected_device = value
            self.notify_selected_device()

    @property
    def selected_chain(self):
        return self._selected_chain

    @selected_chain.setter
    def selected_chain(self, value):
        if value != self._selected_chain:
            self._selected_chain = value
            self.notify_selected_chain()

    @property
    def highlighted_clip_slot(self):
        return self._highlighted_clip_slot

    @highlighted_clip_slot.setter
    def highlighted_clip_slot(self, value):
        if value != self._highlighted_clip_slot:
            self._highlighted_clip_slot = value
            self.notify_highlighted_clip_slot()

    def select_device(self, device, select_chain=False):
        self.selected_device = device


class Song(Subject):
    __subject_events__ = ("visible_tracks", "scenes", "tracks", "return_tracks",
                          "overdub", "session_record_status", "is_playing",
                          "appointed_device", "session_record", "root_note",
                          "scale_name", "clip_trigger_quantization",
                          "midi_recording_quantization", "metronome", "swing_amount",
                          "session_automation_record", "re_enable_automation_enabled",
                          "has_envelopes")

    # A reasonable approximation of Live's ordered scale table:
    # (name, [semitone intervals]).
    _ALL_SCALES = [
        ("Chromatic", [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]),
        ("Major", [0, 2, 4, 5, 7, 9, 11]),
        ("Natural Minor", [0, 2, 3, 5, 7, 8, 10]),
        ("Harmonic Minor", [0, 2, 3, 5, 7, 8, 11]),
        ("Melodic Minor", [0, 2, 3, 5, 7, 9, 11]),
        ("Major Pentatonic", [0, 2, 4, 7, 9]),
        ("Minor Pentatonic", [0, 3, 5, 7, 10]),
        ("Blues", [0, 3, 5, 6, 7, 10]),
        ("Dorian", [0, 2, 3, 5, 7, 9, 10]),
        ("Phrygian", [0, 1, 3, 5, 7, 8, 10]),
        ("Lydian", [0, 2, 4, 6, 7, 9, 11]),
        ("Mixolydian", [0, 2, 4, 5, 7, 9, 10]),
        ("Whole Tone", [0, 2, 4, 6, 8, 10]),
        ("Chromatic Ascending", [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]),
        ("Chromatic Descending", [0, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]),
    ]

    @classmethod
    def get_all_scales_ordered(cls):
        return list(cls._ALL_SCALES)

    def __init__(self):
        super().__init__()
        self._tracks = []
        self._return_tracks = []
        self._scenes = []
        self._master_track = Track(name="Master", is_master=True)
        self._view = SongView(self)
        self._session_record = False
        self._session_record_status = SessionRecordStatus.off
        self._is_playing = False
        self._overdub = False
        self._appointed_device = None
        self._root_note = 0
        self._scale_name = "Major"
        self._clip_trigger_quantization = Quantization.q_no_q
        self._midi_recording_quantization = RecordingQuantization.rec_q_no_q
        self._metronome = False
        self._swing_amount = 0.0
        self._session_automation_record = False
        self._re_enable_automation_enabled = False
        self._has_envelopes = False
        self._exclusive_solo = False
        self._exclusive_arm = False
        self._select_on_launch = True
        self._can_undo = False
        self._can_redo = False
        self._tempo = 120.0
        self._signature_numerator = 4
        self._signature_denominator = 4
        self._nudge_up = False
        self._nudge_down = False

    # -- list properties ---------------------------------------------------
    @property
    def tracks(self):
        return self._tracks

    @tracks.setter
    def tracks(self, value):
        self._tracks = list(value)
        self.notify_tracks()

    @property
    def visible_tracks(self):
        return [t for t in self._tracks if t.is_visible]

    @visible_tracks.setter
    def visible_tracks(self, value):
        self._tracks = list(value)
        self.notify_visible_tracks()

    @property
    def return_tracks(self):
        return self._return_tracks

    @return_tracks.setter
    def return_tracks(self, value):
        self._return_tracks = list(value)
        self.notify_return_tracks()

    @property
    def scenes(self):
        return self._scenes

    @scenes.setter
    def scenes(self, value):
        self._scenes = list(value)
        self.notify_scenes()

    @property
    def master_track(self):
        return self._master_track

    @property
    def view(self):
        return self._view

    # -- scalar properties ---------------------------------------------------
    @property
    def session_record(self):
        return self._session_record

    @session_record.setter
    def session_record(self, value):
        if value != self._session_record:
            self._session_record = value
            self._session_record_status = SessionRecordStatus.on if value else SessionRecordStatus.off
            self.notify_session_record()
            self.notify_session_record_status()

    @property
    def session_record_status(self):
        return self._session_record_status

    @session_record_status.setter
    def session_record_status(self, value):
        if value != self._session_record_status:
            self._session_record_status = value
            self.notify_session_record_status()

    @property
    def is_playing(self):
        return self._is_playing

    @is_playing.setter
    def is_playing(self, value):
        if value != self._is_playing:
            self._is_playing = value
            self.notify_is_playing()

    @property
    def overdub(self):
        return self._overdub

    @overdub.setter
    def overdub(self, value):
        if value != self._overdub:
            self._overdub = value
            self.notify_overdub()

    @property
    def appointed_device(self):
        return self._appointed_device

    @appointed_device.setter
    def appointed_device(self, value):
        if value != self._appointed_device:
            self._appointed_device = value
            self.notify_appointed_device()

    @property
    def root_note(self):
        return self._root_note

    @root_note.setter
    def root_note(self, value):
        if value != self._root_note:
            self._root_note = value
            self.notify_root_note()

    @property
    def scale_name(self):
        return self._scale_name

    @scale_name.setter
    def scale_name(self, value):
        if value != self._scale_name:
            self._scale_name = value
            self.notify_scale_name()

    @property
    def clip_trigger_quantization(self):
        return self._clip_trigger_quantization

    @clip_trigger_quantization.setter
    def clip_trigger_quantization(self, value):
        if value != self._clip_trigger_quantization:
            self._clip_trigger_quantization = value
            self.notify_clip_trigger_quantization()

    @property
    def midi_recording_quantization(self):
        return self._midi_recording_quantization

    @midi_recording_quantization.setter
    def midi_recording_quantization(self, value):
        if value != self._midi_recording_quantization:
            self._midi_recording_quantization = value
            self.notify_midi_recording_quantization()

    @property
    def metronome(self):
        return self._metronome

    @metronome.setter
    def metronome(self, value):
        if value != self._metronome:
            self._metronome = value
            self.notify_metronome()

    @property
    def swing_amount(self):
        return self._swing_amount

    @swing_amount.setter
    def swing_amount(self, value):
        if value != self._swing_amount:
            self._swing_amount = value
            self.notify_swing_amount()

    @property
    def session_automation_record(self):
        return self._session_automation_record

    @session_automation_record.setter
    def session_automation_record(self, value):
        if value != self._session_automation_record:
            self._session_automation_record = value
            self.notify_session_automation_record()

    @property
    def re_enable_automation_enabled(self):
        return self._re_enable_automation_enabled

    @re_enable_automation_enabled.setter
    def re_enable_automation_enabled(self, value):
        if value != self._re_enable_automation_enabled:
            self._re_enable_automation_enabled = value
            self.notify_re_enable_automation_enabled()

    @property
    def has_envelopes(self):
        return self._has_envelopes

    @has_envelopes.setter
    def has_envelopes(self, value):
        if value != self._has_envelopes:
            self._has_envelopes = value
            self.notify_has_envelopes()

    @property
    def exclusive_solo(self):
        return self._exclusive_solo

    @exclusive_solo.setter
    def exclusive_solo(self, value):
        self._exclusive_solo = value

    @property
    def exclusive_arm(self):
        return self._exclusive_arm

    @exclusive_arm.setter
    def exclusive_arm(self, value):
        self._exclusive_arm = value

    @property
    def select_on_launch(self):
        return self._select_on_launch

    @select_on_launch.setter
    def select_on_launch(self, value):
        self._select_on_launch = value

    @property
    def can_undo(self):
        return self._can_undo

    @can_undo.setter
    def can_undo(self, value):
        self._can_undo = value

    @property
    def can_redo(self):
        return self._can_redo

    @can_redo.setter
    def can_redo(self, value):
        self._can_redo = value

    @property
    def tempo(self):
        return self._tempo

    @tempo.setter
    def tempo(self, value):
        self._tempo = value

    @property
    def signature_numerator(self):
        return self._signature_numerator

    @property
    def signature_denominator(self):
        return self._signature_denominator

    @property
    def nudge_up(self):
        return self._nudge_up

    @nudge_up.setter
    def nudge_up(self, value):
        self._nudge_up = value

    @property
    def nudge_down(self):
        return self._nudge_down

    @nudge_down.setter
    def nudge_down(self, value):
        self._nudge_down = value

    # -- methods -----------------------------------------------------------
    def stop_all_clips(self, force=False):
        for track in self._tracks:
            track.stop_all_clips(force)
        for scene in self._scenes:
            scene.is_triggered = False

    def create_scene(self, index=-1):
        scene = Scene()
        scene.canonical_parent = self
        if index < 0 or index > len(self._scenes):
            index = len(self._scenes)
        self._scenes.insert(index, scene)
        self.notify_scenes()
        return scene

    def delete_scene(self, index):
        if 0 <= index < len(self._scenes):
            self._scenes.pop(index)
            self.notify_scenes()

    def capture_and_insert_scene(self, mode):
        self.create_scene()

    def re_enable_automation(self):
        pass

    def begin_undo_step(self):
        pass

    def end_undo_step(self):
        pass

    def undo(self):
        pass

    def redo(self):
        pass

    def tap_tempo(self):
        pass


class DeviceType:
    instrument = 0
    effect = 1
    drum = 2


class DeviceView(Subject):
    __subject_events__ = ("selected_chain",)

    def __init__(self, device=None):
        super().__init__()
        self._device = device
        self._selected_chain = None

    @property
    def selected_chain(self):
        return self._selected_chain

    @selected_chain.setter
    def selected_chain(self, value):
        if value != self._selected_chain:
            self._selected_chain = value
            self.notify_selected_chain()


class Device(Subject):
    __subject_events__ = ("name", "parameters", "chains", "has_macro_mappings")

    def __init__(self, name="Device", type=DeviceType.effect):
        super().__init__()
        self._name = name
        self.type = type
        self._parameters = []
        self._chains = []
        self._can_have_drum_pads = False
        self._can_have_chains = False
        self._has_macro_mappings = False
        self.view = DeviceView(self)
        self.canonical_parent = None

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if value != self._name:
            self._name = value
            self.notify_name()

    @property
    def parameters(self):
        return self._parameters

    @parameters.setter
    def parameters(self, value):
        self._parameters = list(value)
        self.notify_parameters()

    @property
    def chains(self):
        return self._chains

    @chains.setter
    def chains(self, value):
        self._chains = list(value)
        self.notify_chains()

    @property
    def can_have_drum_pads(self):
        return self._can_have_drum_pads

    @property
    def can_have_chains(self):
        return self._can_have_chains

    @property
    def has_macro_mappings(self):
        return self._has_macro_mappings

    @has_macro_mappings.setter
    def has_macro_mappings(self, value):
        if value != self._has_macro_mappings:
            self._has_macro_mappings = value
            self.notify_has_macro_mappings()


class RackDevice(Device):
    def __init__(self, name="Rack", type=DeviceType.instrument):
        super().__init__(name=name, type=type)
        self._can_have_drum_pads = True
        self._can_have_chains = True
        self._has_macro_mappings = True


class Chain(Subject):
    __subject_events__ = ("devices",)

    def __init__(self, name="Chain"):
        super().__init__()
        self._name = name
        self._devices = []
        self.canonical_parent = None

    @property
    def name(self):
        return self._name

    @property
    def devices(self):
        return self._devices

    @devices.setter
    def devices(self, value):
        self._devices = list(value)
        self.notify_devices()


class MidiRemoteScript:
    """Base class of Live's remote-script host object (c_instance).

    The test fake (``fakes.FakeHostApi``) is the concrete stand-in; this class
    exists so ``Live.MidiRemoteScript`` resolves for type references.
    """

    def __init__(self):
        self._song = Song()

    def song(self):
        return self._song


# ---------------------------------------------------------------------------
# Convenience: a fully populated fake song for tests
# ---------------------------------------------------------------------------

def make_fake_song(num_tracks=8, num_scenes=8, num_returns=0):
    """Build a FakeSong with tracks/scenes/clip slots wired up like a session."""
    song = Song()
    tracks = []
    for i in range(num_tracks):
        track = Track(name="Track %d" % (i + 1))
        for j in range(num_scenes):
            slot = ClipSlot()
            slot.canonical_parent = track
            track.clip_slots.append(slot)
        tracks.append(track)
    song.tracks = tracks
    scenes = []
    for j in range(num_scenes):
        scene = Scene(name="Scene %d" % (j + 1))
        scene.canonical_parent = song
        scenes.append(scene)
    song.scenes = scenes
    for i in range(num_returns):
        song.return_tracks.append(Track(name="Return %d" % (i + 1), is_return=True))
    song.view.selected_track = tracks[0] if tracks else None
    song.view.selected_scene = scenes[0] if scenes else None
    return song


# Aliases used by tests (so test code can write FakeSong(...) etc.)
FakeSong = Song
FakeSongView = SongView
FakeTrack = Track
FakeScene = Scene
FakeClip = Clip
FakeClipSlot = ClipSlot
FakeDevice = Device
FakeRackDevice = RackDevice
FakeChain = Chain
FakeMixerDevice = MixerDevice
FakeParameter = Parameter
FakeApplication = Application
