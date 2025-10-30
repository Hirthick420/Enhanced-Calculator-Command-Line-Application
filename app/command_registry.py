# app/command_registry.py
from __future__ import annotations
from typing import Callable

Handler = Callable[..., str]

# Single live registry + help store
_REGISTRY: dict[str, Handler] = {}
_HELP: list[tuple[str, str]] = []   # (name, description)


def register(name: str, handler: Handler, desc: str = "") -> None:
    """Register a command in the live registry."""
    _REGISTRY[name] = handler
    if desc:
        _HELP.append((name, desc))


def command(name: str, desc: str = ""):
    """Decorator for registering a command function."""
    def deco(fn: Handler) -> Handler:
        register(name, fn, desc)
        return fn
    return deco


def get_commands() -> dict[str, Handler]:
    """Return the LIVE registry (not a copy). Tests rely on this mutability."""
    return _REGISTRY


def help_lines() -> list[tuple[str, str]]:
    """
    Return accumulated (name, desc) pairs that describe commands.
    This list may contain stale items if commands were removed; callers should
    filter against the live registry.
    """
    return list(_HELP)


def clear() -> None:
    """
    Test helper: wipe both the live registry and the help list.
    Some tests import this symbol; keep it available.
    """
    _REGISTRY.clear()
    _HELP.clear()
