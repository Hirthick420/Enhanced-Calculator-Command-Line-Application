# tests/test_dynamic_help.py
import importlib
from app.repl import _seed_registry_if_needed
from app.help_decorator import register_help, help_entries
from app.command_registry import register, get_commands
from app.calculator import Calculator
from app.repl import process_line

def test_help_decorator_lists_registered_commands(monkeypatch):
    # seed and add a temporary command through both systems
    _seed_registry_if_needed()

    def _dummy(calc: Calculator, args: list[str]) -> str:
        return "ok"

    register_help("dummy", "decorated demo")
    register("dummy", _dummy, "decorated demo")

    cont, out = process_line(Calculator(observers=[]), "help")
    assert cont is True
    assert "dummy" in out
    assert "decorated demo" in out

def test_help_stays_dynamic_when_command_removed(monkeypatch):
    # Remove any orphan 'dummy' handler if present
    cmds = get_commands()
    cmds.pop("dummy", None)

    # Build help again and ensure 'dummy' is absent from printed help
    cont, out = process_line(Calculator(observers=[]), "help")
    assert cont is True
    assert "dummy" not in out
