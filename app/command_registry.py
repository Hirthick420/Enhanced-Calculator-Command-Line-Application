# app/command_registry.py
from __future__ import annotations
from typing import Callable, Dict, List, Tuple

Handler = Callable[[object, list[str]], str]

_commands: Dict[str, Handler] = {}
_help: Dict[str, str] = {}

def register(name: str, handler: Handler, help_text: str) -> None:
    _commands[name] = handler
    _help[name] = help_text

def command(name: str, help_text: str):
    """Decorator to register a command handler with help text."""
    def deco(fn: Handler) -> Handler:
        register(name, fn, help_text)
        return fn
    return deco

def get_commands() -> Dict[str, Handler]:
    return dict(_commands)

def help_lines() -> List[Tuple[str, str]]:
    # keep a stable order by name
    return sorted(_help.items(), key=lambda kv: kv[0])

def clear() -> None:
    _commands.clear()
    _help.clear()
