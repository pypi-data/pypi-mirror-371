import json

WRAPPERS = {"ShallowReactive", "Reactive", "Ref", "ShallowRef", "ComputedRef"}

class LazyRef:
    """lazy Proxy for a reference to a Nuxt payload entry."""
    def __init__(self, payload, idx):
        self._payload = payload
        self._idx = idx
        self._resolved = None

    def resolve(self, recursive: bool = False, _seen=None):
        """
        Resolve this reference.
        If recursive=True, also resolve nested structures.
        """
        if self._resolved is None:
            self._resolved = wrap(self._payload, self._payload[self._idx])

        if recursive:
            return LazyRef.deep_resolve(self._resolved, _seen=set() if _seen is None else _seen)
        return self._resolved

    @staticmethod
    def deep_resolve(value, _seen):
        if isinstance(value, LazyRef):
            key = (id(value._payload), value._idx)
            if key in _seen:
                return UnresolvableRef(value._payload, value._idx)
            _seen.add(key)
            return value.resolve(recursive=True, _seen=_seen)

        elif isinstance(value, dict):
            return {k: LazyRef.deep_resolve(v, _seen) for k, v in value.items()}

        elif isinstance(value, list):
            return [LazyRef.deep_resolve(v, _seen) for v in value]

        else:
            return value

    def __getitem__(self, key):
        return self.resolve()[key]

    def __getattr__(self, name):
        return getattr(self.resolve(), name)

    def __iter__(self):
        return iter(self.resolve())

    def __repr__(self):
        return f"<LazyRef idx={self._idx} resolved={self._resolved is not None}>"

    @property
    def value(self):
        return self._idx


class UnresolvableRef(LazyRef):
    """Represents a circular reference that cannot be fully resolved."""
    def __init__(self, payload, idx: int):
        super().__init__(payload, idx)
        self._resolved = None

    def resolve(self, recursive: bool = False, _seen=None):
        return self  # Always return itself; cannot resolve further

    def __repr__(self):
        return f"<UnresolvableRef idx={self._idx}>"


def wrap(payload, value):
    """
    Wrap values from a Nuxt 3 _payload.json into lazy-resolving objects.

    - Integers that fall within the payload range are treated as references 
      and wrapped into LazyRef.
    - Lists are recursively wrapped, with special handling for Vue/Nuxt 
      reactive wrappers like ["Reactive", idx].
    - Dictionaries are recursively wrapped.
    - Scalars are returned as-is.
    """
    if isinstance(value, int) and 0 <= value < len(payload):
        return LazyRef(payload, value)
    elif isinstance(value, list):
        if len(value) == 2 and value[0] in WRAPPERS:
            return wrap(payload, payload[value[1]])
        return [wrap(payload, v) for v in value]
    elif isinstance(value, dict):
        return {k: wrap(payload, v) for k, v in value.items()}
    return value

def load_payload(path: str):
    """
    Load a Nuxt 3 _payload.json file into a lazy-resolving Python structure.

    Each entry in the payload is wrapped using `wrap`, so references and 
    Vue/Nuxt wrappers are resolved on demand.
    """
    with open(path, "r", encoding="utf-8") as f:
        payload = json.load(f)
    return [wrap(payload, v) for v in payload]
