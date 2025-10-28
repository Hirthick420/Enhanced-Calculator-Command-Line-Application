# tests/test_history.py
import pytest
from app.history import History
from app.calculation import Calculation
from app.exceptions import OperationError

def _calc(op, a, b, result):
    return Calculation(operation=op, a=a, b=b, result=result)

def test_add_and_size_and_items_order():
    h = History(max_size=5)
    h.add(_calc("add", 1, 2, 3))
    h.add(_calc("multiply", 2, 3, 6))
    items = h.items()
    assert h.size() == 2
    assert items[0].operation == "add"
    assert items[1].operation == "multiply"
    # timestamp added automatically
    assert items[0].timestamp is not None

def test_undo_and_redo_roundtrip():
    h = History(max_size=5)
    c1 = _calc("add", 1, 2, 3)
    c2 = _calc("subtract", 9, 4, 5)
    h.extend([c1, c2])
    undone = h.undo()
    assert undone.operation == "subtract"
    assert h.size() == 1
    redone = h.redo()
    assert redone.operation == "subtract"
    assert h.size() == 2

def test_undo_empty_raises():
    h = History()
    with pytest.raises(OperationError):
        h.undo()

def test_redo_empty_raises():
    h = History()
    h.add(_calc("add", 1, 1, 2))
    with pytest.raises(OperationError):
        h.redo()  # nothing undone yet

def test_new_add_clears_redo_stack():
    h = History()
    h.extend([_calc("add", 1, 1, 2), _calc("add", 2, 2, 4)])
    h.undo()  # now one item in redo stack
    h.add(_calc("multiply", 2, 3, 6))  # must clear redo stack
    with pytest.raises(OperationError):
        h.redo()

def test_max_size_trims_oldest_fifo():
    h = History(max_size=3)
    h.extend([
        _calc("a", 1, 1, 2),
        _calc("b", 1, 1, 2),
        _calc("c", 1, 1, 2),
        _calc("d", 1, 1, 2),  # triggers trim of the oldest "a"
    ])
    ops = [c.operation for c in h.items()]
    assert ops == ["b", "c", "d"]

def test_create_and_restore_memento():
    h = History()
    h.extend([_calc("a", 1, 2, 3), _calc("b", 4, 5, 9)])
    m = h.create_memento()
    h.add(_calc("c", 2, 2, 4))  # diverge
    h.restore(m)  # go back to snapshot
    ops = [c.operation for c in h.items()]
    assert ops == ["a", "b"]

def test_invalid_add_type_raises():
    h = History()
    with pytest.raises(OperationError):
        h.add("not-a-calculation")  # type: ignore[arg-type]

def test_invalid_max_size_raises():
    with pytest.raises(OperationError):
        History(max_size=0)

def test_history_is_empty_and_size_zero():
    h = History()
    assert h.is_empty() is True
    assert h.size() == 0

def test_history_clear_empties_done_and_redo():
    h = History()
    h.add(Calculation("add", 1, 1, 2))
    h.add(Calculation("mul", 2, 3, 6))
    h.undo()  # put one item on redo stack
    h.clear()
    assert h.is_empty() is True
    with pytest.raises(Exception):
        h.redo()