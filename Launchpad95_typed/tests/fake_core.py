"""Clean-room, minimal re-implementation of the runtime machinery that
Ableton's ``_Framework`` base classes are built from.

This module is part of the *test* environment for ``Launchpad95_typed``.
It is imported only by ``tests/conftest.py`` (via ``fakes.install_fake_environment``)
and is never imported by the remote script itself.

The public API mirrors the decompiled ``_Framework`` sources in ``../_Framework/``
(read-only reference; several of those files contain decompiler artifacts, so this
re-implementation is written from the API surface rather than copied).

Modules provided here (assembled into fake ``_Framework.*`` modules by
``fakes.install_fake_environment``):

- ``Util``            — small functional helpers (clamp, find_if, lazy_attribute, ...)
- ``Signal``          — the signal/slot notification primitive
- ``Disconnectable``  — disconnect bookkeeping for compounds
- ``SubjectSlot``     — Subject metaclass, subject_slot / subject_slot_group
- ``Dependency``      — the ``inject`` / ``depends`` / ``dependency`` DI system
- ``Defaults``        — timing constants
- ``Task``            — the task/timer system (TaskGroup, sequence, wait, ...)
- ``Resource``        — resource grab/release (button ownership)
- ``Proxy``           — attribute proxying base

Everything here is plain Python 3.11+ with zero third-party dependencies.
"""

from __future__ import annotations

from contextlib import contextmanager
from functools import partial, reduce, wraps
from itertools import chain, repeat as _repeat
from numbers import Number


# ---------------------------------------------------------------------------
# Util
# ---------------------------------------------------------------------------

def clamp(val, minv, maxv):
    return max(minv, min(val, maxv))


def linear(minv, maxv, val):
    return minv + (maxv - minv) * val


def nop(*a, **k):
    if a:
        return a[0]
    return None


def negate(value):
    return not value


def const(value):
    return (lambda *a, **k: value)


def in_range(value, lower_bound, upper_open_bound):
    if not isinstance(value, Number):
        return False
    return value >= lower_bound and value < upper_open_bound


def sign(value):
    return 1.0 if value >= 0.0 else -1.0


def to_slice(obj):
    if isinstance(obj, slice):
        return obj
    if obj != -1:
        return slice(obj, obj + 1)
    return slice(obj, None)


def slice_size(s, width):
    return len(list(range(width))[s])


def maybe(fn):
    return (lambda x: fn(x) if x is not None else None)


def memoize(function):
    memoized = {}

    @wraps(function)
    def wrapper(*args):
        try:
            ret = memoized[args]
        except KeyError:
            ret = memoized[args] = function(*args)
        return ret

    return wrapper


@memoize
def mixin(*args):
    if len(args) == 1:
        return args[0]
    name = "Mixin_%s" % "_".join(cls.__name__ for cls in args)
    return type(name, args, {})


def monkeypatch(target, name=None, override=False, doc=None):
    def patcher(func):
        patchname = func.__name__ if name is None else name
        if not override and hasattr(target, patchname):
            raise TypeError("Class %s already has method %s" % (target.__name__, patchname))
        setattr(target, patchname, func)
        try:
            func.__name__ = patchname
        except AttributeError:
            pass
        if doc is not None:
            func.__doc__ = doc
        return func

    return patcher


def monkeypatch_extend(target, name=None):
    def patcher(func):
        newfunc = func
        patchname = func.__name__ if name is None else name
        if hasattr(target, patchname):
            oldfunc = getattr(target, patchname)
            if not callable(oldfunc):
                raise TypeError("Cannot extend non callable attribute")

            @wraps(oldfunc)
            def extended(*a, **k):
                ret = oldfunc(*a, **k)
                func(*a, **k)
                return ret

            newfunc = extended
        setattr(target, patchname, newfunc)
        return func

    return patcher


def instance_decorator(decorator):
    class Decorator:
        def __init__(self, func=nop, *args, **kws):
            self.__name__ = func.__name__
            self.__doc__ = func.__doc__
            self._data_name = "%s_%d_decorated_instance" % (func.__name__, id(self))
            self._func = func
            self._args = args
            self._kws = kws

        def __get__(self, obj, cls=None):
            if obj is None:
                return
            data_name = self._data_name
            try:
                return obj.__dict__[data_name]
            except KeyError:
                decorated = decorator(obj, self._func, *self._args, **self._kws)
                obj.__dict__[data_name] = decorated
                return decorated

    return Decorator


def forward_property(member):
    class Descriptor:
        def __init__(self, func_or_name):
            self._property_name = func_or_name.__name__ if callable(func_or_name) else func_or_name

        def __get__(self, obj, cls=None):
            return getattr(getattr(obj, member), self._property_name)

        def __set__(self, obj, value):
            setattr(getattr(obj, member), self._property_name, value)

    return Descriptor


class lazy_attribute:
    def __init__(self, func, name=None):
        wraps(func)(self)
        self._func = func
        if name:
            self.__name__ = name

    def __get__(self, obj, cls=None):
        if obj is None:
            return self
        result = obj.__dict__[self.__name__] = self._func(obj)
        return result


def remove_if(predicate, lst):
    return [elem for elem in lst if not predicate(elem)]


def flatten(lst):
    return chain(*lst)


def group(lst, n):
    from itertools import zip_longest
    return list(zip_longest(*[lst[i:i + n] for i in range(n)]))


def find_if(predicate, seq):
    for x in seq:
        if predicate(x):
            return x
    return None


def index_if(predicate, seq):
    idx = 0
    for x in seq:
        if predicate(x):
            return idx
        idx += 1
    return idx


def union(a, b):
    a = dict(a)
    a.update(b)
    return a


def product(iter_a, iter_b):
    for a in iter_a:
        for b in iter_b:
            yield (a, b)


def is_iterable(value):
    try:
        it = iter(value)
        return bool(it)
    except TypeError:
        return False


def recursive_map(fn, element, sequence_type=None):
    if sequence_type is None:
        return recursive_map(fn, element, type(element))
    if isinstance(element, sequence_type):
        return [recursive_map(fn, x, sequence_type) for x in element]
    return fn(element)


def chain_from_iterable(iterables):
    for it in iterables:
        for element in it:
            yield element


def is_matrix(iterable):
    if is_iterable(iterable):
        if len(iterable) > 0:
            return all(is_iterable(x) and len(iterable[0]) == len(x) and len(x) > 0 for x in iterable)
    return False


def first(seq):
    return seq[0]


def second(seq):
    return seq[1]


def third(seq):
    return seq[2]


def compose(*funcs):
    return (lambda x: reduce(lambda v, f: f(v), funcs[:-1], x))


def is_contextmanager(value):
    return callable(getattr(value, "__enter__", None)) and callable(getattr(value, "__exit__", None))


def infinite_context_manager(generator):
    make_context_manager = contextmanager(generator)

    class InfiniteContextManager:
        def __enter__(self):
            self._delegate = make_context_manager()
            self._delegate.__enter__()

        def __exit__(self, type, err, trace):
            self._delegate.__exit__(type, err, trace)
            del self._delegate

    return InfiniteContextManager


class BooleanContext:
    default_value = False

    def __init__(self, default_value=None, *a, **k):
        if default_value is not None:
            self.default_value = default_value
        self._current_value = self.default_value

    def __bool__(self):
        return bool(self._current_value)

    def __call__(self, update_value=None):
        return self.Manager(self, update_value)

    @property
    def value(self):
        return self._current_value

    class Manager:
        def __init__(self, managed=None, update_value=None, *a, **k):
            self._managed = managed
            self._update_value = update_value if update_value is not None else not managed.default_value

        def __enter__(self):
            managed = self._managed
            self._old_value = managed._current_value
            managed._current_value = self._update_value
            return self

        def __exit__(self, *a, **k):
            self._managed._current_value = self._old_value


def dict_diff(left, right):
    dummy = object()
    return dict((k_v for k_v in iter(right.items()) if left.get(k_v[0], dummy) != k_v[1]))


class NamedTuple:
    def __init__(self, *others, **k):
        for other in others:
            diff = dict_diff(self._eq_dict, other._eq_dict)
            self._eq_dict.update(diff)
            self.__dict__.update(diff)
        self.__dict__.update(k)
        if "_eq_dict" in self.__dict__:
            self._eq_dict.update(k)

    def __setattr__(self, name, value):
        raise AttributeError("Named tuple is constant")

    def __delattr__(self, name):
        raise AttributeError("Named tuple is constant")

    def __getitem__(self, name):
        return self.__dict__[name]

    @lazy_attribute
    def _eq_dict(self):
        def public(objdict):
            return dict((k__ for k__ in iter(objdict.items()) if not k__.startswith("_")))

        return reduce(lambda a, b: union(b, a), [public(c.__dict__) for c in type(self).__mro__], public(self.__dict__))

    def __eq__(self, other):
        return isinstance(other, NamedTuple) and self._eq_dict == other._eq_dict

    def __hash__(self):
        return hash(id(self))

    def __getstate__(self):
        res = dict(self.__dict__)
        try:
            del res["_eq_dict"]
        except KeyError:
            pass
        return res


class Slicer:
    def __init__(self, dimensions=1, extractor=nop, keys=tuple(), *a, **k):
        self._keys = keys
        self._dimensions = dimensions
        self._extractor = extractor

    def __getitem__(self, key):
        new = key if isinstance(key, tuple) else (key,)
        keys = self._keys + new
        if len(keys) == self._dimensions:
            return self._extractor(*keys)
        return Slicer(dimensions=self._dimensions, extractor=self._extractor, keys=keys)

    def __call__(self):
        return self


get_slice = Slicer()


def slicer(dimensions):
    def decorator(extractor):
        @wraps(extractor)
        def make_slicer(*a, **k):
            return Slicer(dimensions=dimensions, extractor=partial(extractor, *a, **k))
        return make_slicer
    return decorator


def print_message(*messages):
    print(" ".join(map(str, messages)))


class overlaymap:
    def __init__(self, *maps):
        self._maps = maps

    def __getitem__(self, key):
        for m in self._maps:
            if key in m:
                return m[key]
        raise KeyError(key)

    def keys(self):
        res = set()
        for key in chain_from_iterable(self._maps):
            res.add(key)
        return list(res)

    def values(self):
        return [self[key] for key in self.keys()]

    def iteritems(self):
        for key in self.keys():
            yield self[key]


def trace_value(value, msg='Value: '):
    print(msg, value)
    return value


class Bindable:
    _bound_instances = None

    def __get__(self, obj, cls=None):
        import weakref
        if obj is None:
            return self
        if self._bound_instances is None:
            self._bound_instances = weakref.WeakKeyDictionary()
        bound_dict = self._bound_instances.setdefault(obj, weakref.WeakKeyDictionary())
        try:
            bound = bound_dict[self]
        except KeyError:
            bound = self.bind(weakref.proxy(obj))
            bound_dict[self] = bound
        return bound

    def bind(self, bind_to_object):
        raise NotImplementedError


# ---------------------------------------------------------------------------
# Signal
# ---------------------------------------------------------------------------

def default_combiner(results):
    for _ in results:
        pass


class Slot:
    def __init__(self, callback=None, *a, **k):
        self.callback = callback

    def __call__(self, *a, **k):
        return self.callback(*a, **k)

    def __eq__(self, other):
        return id(self) == id(other) or self.callback == other


class IdentifyingSlot(Slot):
    def __init__(self, sender=None, *a, **k):
        Slot.__init__(self, *a, **k)
        self.sender = sender

    def __call__(self, *a, **k):
        return self.callback(*a + (self.sender,), **k)


class Signal:
    def __init__(self, combiner=default_combiner, sender=None, *a, **k):
        self._slots = []
        self._combiner = combiner

    def connect(self, slot, in_front=False, sender=None):
        if slot not in self._slots:
            slot = IdentifyingSlot(sender, slot) if sender is not None else Slot(slot)
            if in_front:
                self._slots.insert(0, slot)
            else:
                self._slots.append(slot)
        else:
            slot = find_if((lambda x: x == slot), self._slots)
        return slot

    def disconnect(self, slot):
        if slot in self._slots:
            self._slots.remove(slot)

    def disconnect_all(self):
        self._slots = []

    @property
    def count(self):
        return len(self._slots)

    def is_connected(self, slot):
        return slot in self._slots

    def __call__(self, *a, **k):
        return self._combiner(_slot_notification_generator(self._slots, a, k))


def _slot_notification_generator(slots, args, kws):
    for slot in slots:
        yield slot(*args, **kws)


def short_circuit_combiner(slot_results):
    return find_if(nop, slot_results)


short_circuit_signal = partial(Signal, short_circuit_combiner)


# ---------------------------------------------------------------------------
# Disconnectable
# ---------------------------------------------------------------------------

class Disconnectable:
    def disconnect(self):
        pass


class CompoundDisconnectable(Disconnectable):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self._registered_disconnectables = []

    def register_disconnectable(self, slot):
        if slot not in self._registered_disconnectables:
            self._registered_disconnectables.append(slot)
        return slot

    def unregister_disconnectable(self, slot):
        if slot in self._registered_disconnectables:
            self._registered_disconnectables.remove(slot)

    def disconnect_disconnectable(self, slot):
        if slot in self._registered_disconnectables:
            self._registered_disconnectables.remove(slot)
            slot.disconnect()

    def find_disconnectable(self, predicate):
        return find_if(predicate, self._registered_disconnectables)

    def has_disconnectable(self, slot):
        return slot in self._registered_disconnectables

    def disconnect(self):
        for slot in self._registered_disconnectables:
            slot.disconnect()
        self._registered_disconnectables = []
        super().disconnect()


class disconnectable:
    def __init__(self, managed=None, *a, **k):
        self._managed = managed

    def __enter__(self):
        return self._managed

    def __exit__(self, *a, **k):
        if self._managed is not None:
            self._managed.disconnect()


# ---------------------------------------------------------------------------
# SubjectSlot
# ---------------------------------------------------------------------------

class SubjectSlotError(Exception):
    pass


class SubjectEvent(NamedTuple):
    name = None
    doc = ""
    signal = Signal
    override = False


def subject_add_event(cls, event_name_or_event):
    if isinstance(event_name_or_event, str):
        event = SubjectEvent(name=event_name_or_event)
    else:
        event = event_name_or_event
    signal_attr = "_" + event.name + "_signal"

    def get_signal(self):
        try:
            return getattr(self, signal_attr)
        except AttributeError:
            signal = event.signal(sender=self)
            setattr(self, signal_attr, signal)
            return signal

    kwargs = dict(doc=event.doc, override=event.override)

    @monkeypatch(cls, event.name + "_has_listener", **kwargs)
    def has_method(self, slot):
        return get_signal(self).is_connected(slot)

    @monkeypatch(cls, "add_" + event.name + "_listener", **kwargs)
    def add_method(self, slot, identify_sender=False, *a, **k):
        sender = self if identify_sender else None
        return get_signal(self).connect(slot, *a, sender=sender, **k)

    @monkeypatch(cls, "remove_" + event.name + "_listener", **kwargs)
    def remove_method(self, slot):
        return get_signal(self).disconnect(slot)

    @monkeypatch(cls, "notify_" + event.name, **kwargs)
    def notify_method(self, *a, **k):
        return get_signal(self)(*a, **k)

    @monkeypatch(cls, "clear_" + event.name + "_listeners", **kwargs)
    def clear_method(self):
        return get_signal(self).disconnect_all()

    @monkeypatch(cls, event.name + "_listener_count", **kwargs)
    def listener_count_method(self):
        return get_signal(self).count

    @monkeypatch_extend(cls)
    def disconnect(self):
        get_signal(self).disconnect_all()


def setup_subject(cls, listeners):
    for lst in listeners:
        subject_add_event(cls, lst)


class SubjectMeta(type):
    def __new__(cls, name, bases, dct):
        events = dct.get("__subject_events__", [])
        if events:
            if "disconnect" not in dct:
                dct["disconnect"] = lambda self: super(cls, self).disconnect()
        cls = super().__new__(cls, name, bases, dct)
        setup_subject(cls, events)
        return cls


class Subject(Disconnectable, metaclass=SubjectMeta):
    pass


class SlotManager(CompoundDisconnectable):
    def register_slot(self, *a, **k):
        slot = a[0] if (a and isinstance(a[0], SubjectSlot)) else SubjectSlot(*a, **k)
        self.register_disconnectable(slot)
        return slot

    def register_slot_manager(self, *a, **k):
        manager = a[0] if (a and isinstance(a[0], SlotManager)) else SlotManager(*a, **k)
        self.register_disconnectable(manager)
        return manager


class SubjectSlot(Disconnectable):
    _extra_kws = {}
    _extra_args = []

    def __init__(self, subject=None, listener=None, event=None, extra_kws=None, extra_args=None, *a, **k):
        super().__init__(*a, **k)
        self._event = event
        if extra_kws is not None:
            self._extra_kws = extra_kws
        if extra_args is not None:
            self._extra_args = extra_args
        self._subject = None
        self._listener = None
        self.subject = subject
        self.listener = listener

    def disconnect(self):
        self.subject = None
        self.listener = None
        super().disconnect()

    def _check_subject_interface(self, subject):
        if not callable(getattr(subject, "add_" + self._event + "_listener", None)):
            raise SubjectSlotError('Subject %s missing "add" method for event: %s' % (subject, self._event))
        elif not callable(getattr(subject, "remove_" + self._event + "_listener", None)):
            raise SubjectSlotError('Subject %s missing "remove" method for event: %s' % (subject, self._event))
        assert callable(getattr(subject, self._event + "_has_listener", None)), \
            'Subject %s missing "has" method for event: %s' % (subject, self._event)

    def connect(self):
        if not self.is_connected:
            if self._subject is not None and self._listener is not None:
                add_method = getattr(self._subject, "add_" + self._event + "_listener")
                all_args = tuple(self._extra_args) + (self._listener,)
                try:
                    add_method(*all_args, **self._extra_kws)
                except RuntimeError:
                    pass

    def soft_disconnect(self):
        if self.is_connected:
            if self._subject is not None:
                if self._listener is not None:
                    all_args = tuple(self._extra_args) + (self._listener,)
                    remove_method = getattr(self._subject, "remove_" + self._event + "_listener")
                    try:
                        remove_method(*all_args)
                    except RuntimeError:
                        pass

    @property
    def is_connected(self):
        all_args = tuple(self._extra_args) + (self._listener,)
        connected = False
        try:
            connected = bool(self._subject is not None and self._listener is not None
                             and getattr(self._subject, self._event + "_has_listener")(*all_args))
        except RuntimeError:
            pass
        return connected

    def _get_subject(self):
        return self._subject

    def _set_subject(self, subject):
        if subject != self._subject:
            if subject is not None:
                self._check_subject_interface(subject)
            self.soft_disconnect()
            self._subject = subject
            self.connect()

    subject = property(_get_subject, _set_subject)

    def _get_listener(self):
        return self._listener

    def _set_listener(self, listener):
        if listener != self._listener:
            self.soft_disconnect()
            self._listener = listener
            self.connect()

    listener = property(_get_listener, _set_listener)


class CallableSlotMixin:
    def __init__(self, function=None, *a, **k):
        super().__init__(*a, **k)
        self.function = function

    def __call__(self, *a, **k):
        return self.function(*a, **k)


class SubjectSlotGroup(SlotManager):
    listener = None
    _extra_kws = None
    _extra_args = None

    def __init__(self, listener=None, event=None, extra_kws=None, extra_args=None, *a, **k):
        super().__init__(*a, **k)
        self.listener = listener
        self._event = event
        if listener is not None:
            self.listener = listener
        if extra_kws is not None:
            self._extra_kws = extra_kws
        if extra_args is not None:
            self._extra_args = extra_args

    def replace_subjects(self, subjects, identifiers=_repeat(None)):
        self.disconnect()
        for subject, identifier in zip(subjects, identifiers):
            self.add_subject(subject, identifier=identifier)

    def add_subject(self, subject, identifier=None):
        if identifier is None:
            identifier = subject
        listener = self._listener_for_subject(identifier)
        self.register_slot(subject, listener, self._event, self._extra_kws, self._extra_args)

    def remove_subject(self, subject):
        slot = self.find_disconnectable(lambda x: x.subject == subject)
        self.disconnect_disconnectable(slot)

    def has_subject(self, subject):
        return self.find_disconnectable(lambda x: x.subject == subject) is not None

    def _listener_for_subject(self, identifier):
        return (lambda *a, **k: self.listener and self.listener(*a + (identifier,), **k))


class MultiSubjectSlot(SlotManager, SubjectSlot):
    def __init__(self, subject=None, listener=None, event=None, extra_kws=None, extra_args=None, *a, **k):
        self._original_listener = listener
        self._slot_subject = None
        self._nested_slot = None
        super().__init__(event=event[0],
                          listener=self._event_fired,
                          subject=subject,
                          extra_kws=extra_kws,
                          extra_args=extra_args)
        if len(event) > 1:
            self._nested_slot = self.register_disconnectable(
                MultiSubjectSlot(event=event[1:],
                                 listener=listener,
                                 subject=subject,
                                 extra_kws=extra_kws,
                                 extra_args=extra_args))
            self._update_nested_subject()

    def _get_subject(self):
        return super()._get_subject()

    def _set_subject(self, subject):
        try:
            try:
                super()._set_subject(subject)
            except SubjectSlotError:
                if self._nested_slot is None:
                    raise
        finally:
            self._slot_subject = subject
            self._update_nested_subject()

    subject = property(_get_subject, _set_subject)

    def _event_fired(self, *a, **k):
        self._update_nested_subject()
        self._original_listener(*a, **k)

    def _update_nested_subject(self):
        if self._nested_slot is not None:
            self._nested_slot.subject = getattr(self._slot_subject, self._event) if self._slot_subject is not None else None


def subject_slot(events, *a, **k):
    @instance_decorator
    def decorator(self, method):
        function = partial(method, self)
        event_list = events.split(".")
        num_events = len(event_list)
        event = event_list if num_events > 1 else events
        base_class = MultiSubjectSlot if num_events > 1 else SubjectSlot
        slot = wraps(method)(mixin(base_class, CallableSlotMixin)(event=event,
                                                                  extra_kws=k,
                                                                  extra_args=a,
                                                                  listener=function,
                                                                  function=function))
        self.register_slot(slot)
        return slot

    return decorator


class CallableSubjectSlotGroup(SubjectSlotGroup, CallableSlotMixin):
    pass


def subject_slot_group(event, *a, **k):
    @instance_decorator
    def decorator(self, method):
        function = partial(method, self)
        slot = wraps(method)(CallableSubjectSlotGroup(event=event,
                                                      extra_kws=k,
                                                      extra_args=a,
                                                      listener=function,
                                                      function=function))
        self.register_slot_manager(slot)
        return slot

    return decorator


# ---------------------------------------------------------------------------
# Dependency (DI)
# ---------------------------------------------------------------------------

__all__ = ('inject', 'depends', 'dependency')


class DependencyError(Exception):
    pass


class InjectionRegistry:
    def __init__(self, parent=None, *a, **k):
        self._key_registry = {}

    def register_key(self, key, injector):
        self._key_registry.setdefault(key, []).append(injector)

    def unregister_key(self, key, injector):
        injectors = self._key_registry.get(key)
        if injectors and injector in injectors:
            injectors.remove(injector)
            if not injectors:
                del self._key_registry[key]

    def get(self, key, default=None):
        try:
            return self._key_registry[key][-1].provides[key]
        except KeyError:
            return default


_global_injection_registry = InjectionRegistry()


def get_dependency_for(obj, name, default=None):
    accessor = _global_injection_registry.get(name, default)
    if accessor is not None:
        return accessor()
    raise DependencyError("Required dependency %s not provided for %s" % (name, str(obj)))


class dependency:
    def __init__(self, **k):
        self._dependency_name, self._dependency_default = list(k.items())[0]

    def __get__(self, obj, cls=None):
        if obj is None:
            obj = cls
        return get_dependency_for(obj, self._dependency_name, self._dependency_default)


def depends(**dependencies):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *a, **explicit):
            deps = dict((k, get_dependency_for(self, k, v)) for k, v in dependencies.items() if k not in explicit)
            return func(self, *a, **union(deps, explicit))
        return wrapper
    return decorator


class Injector:
    @property
    def provides(self):
        return {}

    def register(self):
        pass

    def unregister(self):
        pass

    def __enter__(self):
        self.register()
        return self

    def __exit__(self, *a):
        self.unregister()


class RegistryInjector(Injector):
    def __init__(self, provides=None, registry=None, *a, **k):
        self._provides_dict = provides
        self._registry = registry

    @property
    def provides(self):
        return self._provides_dict

    def register(self):
        registry = self._registry
        for k in self._provides_dict:
            registry.register_key(k, self)

    def unregister(self):
        registry = self._registry
        for k in self._provides_dict:
            registry.unregister_key(k, self)


class InjectionFactory:
    def __init__(self, provides=None, *a, **k):
        self._provides_dict = provides

    def everywhere(self):
        return RegistryInjector(provides=self._provides_dict,
                                registry=_global_injection_registry)

    into_object = NotImplemented
    into_class = NotImplemented


def inject(**k):
    return InjectionFactory(k)


# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------

TIMER_DELAY = 0.1
MOMENTARY_DELAY = 0.3
MOMENTARY_DELAY_TICKS = int(MOMENTARY_DELAY / TIMER_DELAY)


# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------

class TaskError(Exception):
    pass


KILLED = 0
RUNNING = 1
PAUSED = 2


class Task:
    def __init__(self, *a, **k):
        self._state = RUNNING
        self._next = []
        self._task_manager = None

    def clear(self):
        pass

    def do_update(self, timer):
        pass

    def do_restart(self):
        pass

    def add_next(self, task):
        self._next.append(task)
        return task

    def update(self, timer):
        if self._state == RUNNING:
            self.do_update(timer)
        return self._state

    def pause(self):
        if self._state != KILLED:
            self._state = PAUSED
        return self

    def resume(self):
        if self._state != KILLED:
            self._state = RUNNING
        return self

    def toggle_pause(self):
        if self._state != KILLED:
            self._state = RUNNING if self._state == PAUSED else PAUSED
        return self

    def restart(self):
        self.do_restart()
        self._state = RUNNING
        if self._task_manager:
            if self._task_manager.find(self) is None:
                manager = self._task_manager
                self._task_manager = None
                manager.add(self)
        return self

    def kill(self):
        self._state = KILLED
        if self._task_manager:
            for task in self._next:
                self._task_manager.add(task)
        return self

    @property
    def is_running(self):
        return self._state == RUNNING

    @property
    def is_paused(self):
        return self._state == PAUSED

    @property
    def is_killed(self):
        return self._state == KILLED

    @property
    def state(self):
        return self._state

    @property
    def parent_task(self):
        return self._task_manager

    def _set_parent(self, manager):
        if self._task_manager:
            if manager:
                raise TaskError("Already attached to: " + str(self._task_manager))
        self._task_manager = manager

    def _task_equivalent(self, other):
        return self == other


class WrapperTask(Task):
    def __init__(self, wrapped_task=None, *a, **k):
        super().__init__(*a, **k)
        self.wrapped_task = wrapped_task

    def update(self, delta):
        super().update(delta)
        self.wrapped_task.update(delta)

    def _set_parent(self, manager):
        super()._set_parent(manager)
        self.wrapped_task._set_parent(manager)

    def _task_equivalent(self, other):
        return self.wrapped_task._task_equivalent(other)


class FuncTask(Task):
    def __init__(self, func=None, equivalent=None, *a, **k):
        super().__init__(*a, **k)
        self._func = func
        self._equivalent = equivalent

    def _set_func(self, func):
        self._func = func

    def _get_func(self):
        return self._orig

    def do_update(self, timer):
        super().do_update(timer)
        action = self._func(timer)
        if not action or action == KILLED:
            self.kill()
        else:
            if action == PAUSED:
                self.pause()

    def _task_equivalent(self, other):
        return self == other or self._func == other or self._equivalent == other

    func = property(_get_func, _set_func)


class GeneratorTask(Task):
    class Param:
        delta = 0

    def __init__(self, generator=None, equivalent=None, *a, **k):
        super().__init__(*a, **k)
        self._param = GeneratorTask.Param()
        self._set_generator(generator)
        self._equivalent = equivalent

    def _set_generator(self, generator):
        self._orig = generator
        self._iter = generator(self._param)

    def _get_generator(self):
        return self._orig

    def do_update(self, delta):
        super().do_update(delta)
        self._param.delta = delta
        try:
            action = next(self._iter)
        except StopIteration:
            action = KILLED
        if not action or action == KILLED:
            self.kill()
        else:
            if action == PAUSED:
                self.pause()

    def _task_equivalent(self, other):
        return self == other or self._orig == other or self._equivalent == other

    generator = property(_get_generator, _set_generator)


class TaskGroup(Task):
    auto_kill = True
    auto_remove = True
    loop = False

    def __init__(self, tasks=[], auto_kill=None, auto_remove=None, loop=None, *a, **k):
        super().__init__(*a, **k)
        if auto_kill is not None:
            self.auto_kill = auto_kill
        if auto_remove is not None:
            self.auto_remove = auto_remove
        if loop is not None:
            self.loop = loop
        self._tasks = []
        for task in tasks:
            self.add(task)

    def clear(self):
        for t in self._tasks:
            t._set_parent(None)
        self._tasks = []
        super().clear()

    def do_update(self, timer):
        super().do_update(timer)
        for task in self._tasks:
            if not task.is_killed:
                try:
                    task.update(timer)
                except Exception:
                    task.kill()
                    import traceback
                    traceback.print_exc()
        if self.auto_remove:
            self._tasks = remove_if(lambda t: t.is_killed, self._tasks)
        all_killed = len([t for t in self._tasks if t.is_killed]) == self.count
        if self.auto_kill and all_killed:
            self.kill()
        else:
            if self.loop:
                if all_killed:
                    self.restart()

    def add(self, task):
        task = totask(task)
        task._set_parent(self)
        self._tasks.append(task)
        if self.is_killed:
            super().restart()
        return task

    def remove(self, task):
        self._tasks.remove(task)
        task._set_parent(None)

    def find(self, task):
        return find_if(lambda t: t._task_equivalent(task), self._tasks)

    def restart(self):
        super().restart()
        for x in self._tasks:
            x.restart()

    @property
    def count(self):
        return len(self._tasks)


class WaitTask(Task):
    duration = 1.0

    def __init__(self, duration=None, *a, **k):
        super().__init__(*a, **k)
        if duration is not None:
            self.duration = duration
        self.remaining = self.duration

    def do_update(self, delta):
        super().do_update(delta)
        self.remaining -= delta
        if self.remaining <= 0:
            self.kill()
            self.remaining = 0

    def do_restart(self):
        self.remaining = self.duration


class DelayTask(Task):
    duration = 1

    def __init__(self, duration=None, *a, **k):
        super().__init__(*a, **k)
        if duration is not None:
            self.duration = duration
        self.remaining = self.duration

    def do_restart(self):
        self.remaining = self.duration

    def do_update(self, delta):
        super().do_update(delta)
        self.remaining -= 1
        if self.remaining <= 0:
            self.kill()
            self.remaining = 0


class TimerTask(WaitTask):
    def do_update(self, timer):
        super().do_update(timer)
        if self.remaining == 0:
            self.on_finish()
        else:
            self.on_tick()

    def on_tick(self):
        pass

    def on_finish(self):
        pass


class FadeTask(Task):
    def __init__(self, func=(lambda x: x), duration=1.0, loop=False, init=False, *a, **k):
        super().__init__(*a, **k)
        self.func = func
        self.curr = 0.0
        self.loop = loop
        self.duration = duration
        if init:
            func(0.0)

    def do_update(self, delta):
        super().do_update(delta)
        self.func(self.curr / self.duration)
        self.curr += delta
        if self.curr >= self.duration:
            if self.loop:
                self.curr -= self.duration
            else:
                self.curr = self.duration
                self.kill()
                self.func(self.curr / self.duration)

    def do_restart(self):
        super().do_restart()
        self.curr = 0.0


class SequenceTask(Task):
    def __init__(self, tasks=[], *a, **k):
        super().__init__(*a, **k)
        self._tasks = tasks
        self._iter = iter(tasks)
        self._current = None
        self._advance_sequence()

    def _advance_sequence(self):
        try:
            self._current = next(self._iter)
        except StopIteration:
            self.kill()

    def do_update(self, delta):
        super().do_update(delta)
        if self._current is not None:
            self._current.update(delta)
            if self._current.is_killed:
                self._advance_sequence()

    def do_restart(self):
        for x in self._tasks:
            x.restart()
        self._iter = iter(self._tasks)
        self._advance_sequence()


class TimedCallbackTask(SequenceTask):
    _callback = nop

    def start(self, duration, callback):
        if duration is not None:
            self._tasks = [DelayTask(duration), FuncTask(self._call)]
            self._callback = callback or nop
        else:
            self._tasks = []
        self.restart()

    def _call(self, _time_expired):
        self.cancel()
        self._callback()

    def cancel(self):
        self.kill()


def totask(task):
    if not isinstance(task, Task):
        if not callable(task):
            raise TaskError("You can add either tasks or callables. " + str(task))
        task = FuncTask(func=task)
    return task


def generator(orig):
    equiv = [None]

    @wraps(orig)
    def wrapper():
        return GeneratorTask(orig, equiv[0])

    equiv[0] = wrapper
    return wrapper


def sequence(*tasks):
    return SequenceTask(list(map(totask, tasks)))


def parallel(*tasks):
    return TaskGroup(tasks=tasks, auto_remove=False)


def loop(*tasks):
    return TaskGroup(tasks=tasks, auto_remove=False, auto_kill=False, loop=True)


wait = WaitTask
fade = FadeTask
delay = DelayTask


def invfade(f, *a, **k):
    return fade((lambda x: f(1.0 - x)), *a, **k)


def linear_task(f, min, max, *a, **k):
    return fade((lambda x: f(linear(min, max, x))), *a, **k)


import math  # noqa: E402


def sinusoid(f, min=0.0, max=1.0, *a, **k):
    return fade((lambda x: f(min + (max - min) * math.sin(x * math.pi / 2.0))), *a, **k)


def run(func, *a, **k):
    return FuncTask((lambda t: None if func(*a, **k) else None))


def repeat(task):
    task = totask(task)
    task.kill = task.restart
    return WrapperTask(task)


# ---------------------------------------------------------------------------
# Resource
# ---------------------------------------------------------------------------

DEFAULT_PRIORITY = 0


class Resource:
    def grab(self, client, *a, **k):
        raise NotImplementedError

    def release(self, client):
        raise NotImplementedError

    def get_owner(self):
        raise NotImplementedError

    owner = property(lambda self: self.get_owner())


class CompoundResource(Resource):
    def __init__(self, first_resource=None, second_resource=None, *a, **k):
        self._first_resource = first_resource
        self._second_resource = second_resource

    def grab(self, client, *a, **k):
        if self._first_resource.grab(client, *a, **k):
            if self._second_resource.grab(client, *a, **k):
                pass
            else:
                self._first_resource.release(client)
        return self.owner == client

    def release(self, client):
        if client == self.owner:
            self._second_resource.release(client)
            self._first_resource.release(client)
            return True
        return False

    def get_owner(self):
        return self._first_resource.owner or self._second_resource.owner

    @property
    def first(self):
        return self._first_resource

    @property
    def second(self):
        return self._second_resource


def compose_resources(*resources):
    return reduce(CompoundResource, resources)


class ExclusiveResource(Resource):
    def __init__(self, on_received_callback=None, on_lost_callback=None, *a, **k):
        self._owner = None
        if on_received_callback:
            self.on_received = on_received_callback
        if on_lost_callback:
            self.on_lost = on_lost_callback

    def grab(self, client, *a, **k):
        if self._owner is None:
            self.on_received(client, *a, **k)
            self._owner = client
        return self._owner == client

    def release(self, client):
        if client == self._owner:
            self._owner = None
            self.on_lost(client)
            return True
        return False

    def get_owner(self):
        return self._owner

    def on_received(self, client, *a, **k):
        raise NotImplementedError("Override or pass callback")

    def on_lost(self, client):
        raise NotImplementedError("Override or pass callback")


class SharedResource(Resource):
    def __init__(self, on_received_callback=None, on_lost_callback=None, *a, **k):
        if on_received_callback:
            self.on_received = on_received_callback
        if on_lost_callback:
            self.on_lost = on_lost_callback
        self._clients = set()

    def grab(self, client, *a, **k):
        self.on_received(client, *a, **k)
        self._clients.add(client)
        return True

    def release(self, client):
        if client in self._clients:
            self.on_lost(client)
            self._clients.remove(client)
            for client in self._clients:
                self.on_received(client)
            return True
        return False

    def get_owner(self):
        pass

    def on_received(self, client, *a, **k):
        raise NotImplementedError("Override or pass callback")

    def on_lost(self, client):
        raise NotImplementedError("Override or pass callback")


class StackingResource(Resource):
    def __init__(self, on_received_callback=None, on_lost_callback=None, *a, **k):
        self._clients = []
        self._owners = set()
        if on_received_callback:
            self.on_received = on_received_callback
        if on_lost_callback:
            self.on_lost = on_lost_callback

    def grab(self, client, priority=None):
        if priority is None:
            priority = DEFAULT_PRIORITY
        old_owners = self._owners
        self._remove_client(client)
        self._add_client(client, priority)
        new_owners = self._actual_owners()
        if new_owners != old_owners:
            self._on_lost_set(set(old_owners) - set(new_owners))
            self._on_received_set(new_owners)
            self._owners = new_owners
        return True

    def _on_lost_set(self, clients):
        for client in clients:
            self.on_lost(client)

    def _on_received_set(self, clients):
        for client in clients:
            self.on_received(client)

    def release(self, client):
        old_owners = self._owners
        result = self._remove_client(client)
        new_owners = self._actual_owners()
        if new_owners != old_owners:
            self._owners = new_owners
            self._on_lost_set(set(old_owners) - set(new_owners))
            self._on_received_set(new_owners)
        return result

    def release_all(self):
        for client, _ in list(self._clients):
            self.release(client)

    def _add_client(self, client, priority):
        idx = index_if((lambda c: c[1] > priority), self._clients)
        self._clients.insert(idx, (client, priority))

    def _remove_client(self, client):
        idx = index_if((lambda c: c[0] == client), self._clients)
        if idx != len(self._clients):
            del self._clients[idx]
            return True

    def _actual_owners(self):
        if self._clients:
            return [self._clients[-1][0]]
        return []

    @property
    def max_priority(self):
        if self._clients:
            return self._clients[-1][1]
        return DEFAULT_PRIORITY

    @property
    def stack_size(self):
        return len(self._clients)

    def get_owner(self):
        for owner in self._owners:
            return owner

    @property
    def clients(self):
        return list(map(first, self._clients))

    @property
    def owners(self):
        return self._owners

    def on_received(self, client):
        raise NotImplementedError("Override or pass callback")

    def on_lost(self, client):
        raise NotImplementedError("Override or pass callback")

    def release_stacked(self):
        clients = self.clients
        owners = self.owners
        for client in clients:
            if client not in owners:
                self.release(client)


class PrioritizedResource(StackingResource):
    def _actual_owners(self):
        max_priority = self.max_priority
        return [client for client, priority in self._clients if priority == max_priority]


class ClientWrapper(NamedTuple):
    wrap = partial(nop)
    unwrap = partial(nop)


class ProxyResource:
    """Minimal stand-in for the real ProxyResource (not needed by tests)."""

    def __init__(self, proxied_resource=None, client_wrapper=ClientWrapper(), *a, **k):
        self._proxied_resource = proxied_resource
        self._client_wrapper = client_wrapper

    def grab(self, client, *a, **k):
        return self._proxied_resource.grab(self._client_wrapper.wrap(client), *a, **k)

    def release(self, client):
        return self._proxied_resource.release(self._client_wrapper.wrap(client))

    @property
    def owner(self):
        return self._client_wrapper.unwrap(self._proxied_resource.owner)

    @property
    def owners(self):
        return list(map(self._client_wrapper.unwrap, self._proxied_resource.owners))


# ---------------------------------------------------------------------------
# Proxy
# ---------------------------------------------------------------------------

class ProxyBase:
    _skip_wrapper_lookup = None

    def __init__(self, *a, **k):
        self._skip_wrapper_lookup = BooleanContext()

    def proxy_old_hasattr(self, attr):
        with self._skip_wrapper_lookup():
            return hasattr(self, attr)

    def __getattr__(self, name):
        if not self._skip_wrapper_lookup:
            obj = self.proxied_object
            interface = self.proxied_interface
            if obj:
                if hasattr(interface, name):
                    return getattr(obj, name)
            return getattr(interface, name)
        raise AttributeError("Does not have attribute %s" % name)

    def __setattr__(self, name, value):
        obj = self.proxied_object
        interface = self.proxied_interface
        if obj and hasattr(interface, name):
            if self.proxy_old_hasattr(name):
                raise AttributeError("Ambiguous set attribute: %s proxied: %s" % (name, obj))
            setattr(obj, name, value)
        else:
            if hasattr(interface, name):
                raise AttributeError("Ambiguous set attribute: %s proxied: %s" % (name, obj))
            self.__dict__[name] = value

    @property
    def proxied_object(self):
        pass

    @property
    def proxied_interface(self):
        obj = self.proxied_object
        return getattr(obj, "proxied_interface", obj)


class Proxy(ProxyBase):
    proxied_object = None
    _proxied_interface = None

    @property
    def proxied_interface(self):
        return self._proxied_interface or super().proxied_interface

    def __init__(self, proxied_object=None, proxied_interface=None, *a, **k):
        self.proxied_object = proxied_object
        self._proxied_interface = proxied_interface
