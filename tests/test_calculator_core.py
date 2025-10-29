# tests/test_calculator_core.py
from dataclasses import dataclass

def test_calculator_notify_via_add_observer(tmp_path, monkeypatch):
    # Use tiny limits and temp dirs so no I/O noise
    monkeypatch.setenv("CALCULATOR_LOG_DIR", str(tmp_path / "logs"))
    monkeypatch.setenv("CALCULATOR_HISTORY_DIR", str(tmp_path / "hist"))
    monkeypatch.setenv("CALCULATOR_AUTO_SAVE", "false")

    from app.calculator import Calculator, Observer

    @dataclass
    class FlagObserver(Observer):
        called: bool = False
        def on_new_calculation(self, calc, history):
            self.called = True

    obs = FlagObserver()
    c = Calculator(observers=[])
    c.add_observer(obs)         # ensure add_observer path is exercised
    result = c.execute("add", 2, 5)  # success path + notify loop
    assert result.result == 7
    assert obs.called is True
