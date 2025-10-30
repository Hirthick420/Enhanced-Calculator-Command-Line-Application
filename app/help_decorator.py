# app/help_decorator.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, List, Tuple, Dict

@dataclass(frozen=True)
class HelpItem:
    name: str
    desc: str

class _HelpRegistry:
    def __init__(self) -> None:
        self._items: Dict[str, HelpItem] = {}

    def register(self, name: str, desc: str) -> None:
        # last write wins; dedup by name
        self._items[name] = HelpItem(name, desc)

    def items(self) -> List[HelpItem]:
        # stable name sort for predictable output
        return [self._items[k] for k in sorted(self._items.keys())]

_HELP = _HelpRegistry()

def with_help(name: str, desc: str):
    """
    Decorator pattern: wraps a command handler function while registering
    its help metadata into a central registry that the UI can query.
    """
    def deco(func: Callable) -> Callable:
        _HELP.register(name, desc)
        # We do not alter behavior; the wrapper just passes through.
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        # keep introspection readable
        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        return wrapper
    return deco

def help_entries() -> List[Tuple[str, str]]:
    """Return (name, desc) pairs for all decorated commands."""
    return [(h.name, h.desc) for h in _HELP.items()]

def register_help(name: str, desc: str) -> None:
    """Programmatic registration for commands created dynamically."""
    _HELP.register(name, desc)
