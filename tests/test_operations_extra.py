# tests/test_operations_extra.py
import math
import pytest
from app.operations import create_operation
from app.exceptions import OperationError

def test_power_negative_exponent_on_zero_triggers_except_branch():
    # 0 ** -1 raises ZeroDivisionError inside **, which we wrap as OperationError
    with pytest.raises(OperationError):
        create_operation("power").execute(0.0, -1)

@pytest.mark.parametrize("a,n", [
    (float("inf"), 2),   # sqrt(inf) is inf -> not finite -> OperationError
    (float("nan"), 3),   # cbrt(nan) is nan -> not finite -> OperationError
])
def test_root_nonfinite_result_is_rejected(a, n):
    with pytest.raises(OperationError):
        create_operation("root").execute(a, n)


def test_power_nonfinite_result_triggers_guard():
    # inf ** 2 -> inf, which is not finite -> hits isfinite(result) guard
    with pytest.raises(OperationError):
        create_operation("power").execute(float("inf"), 2)

def test_root_nonfinite_result_triggers_guard():
    # root(inf, 2) -> inf, which is not finite -> hits isfinite(result) guard
    with pytest.raises(OperationError):
        create_operation("root").execute(float("inf"), 2)

def test_root_nan_triggers_nonfinite_guard():
    # nan root should compute but result is not finite, exercising lines 59-60
    with pytest.raises(OperationError):
        create_operation("root").execute(float("nan"), 2)

def test_root_inf_triggers_nonfinite_guard():
    # n is a valid nonzero integer; result becomes +inf, so the guard must raise
    with pytest.raises(OperationError):
        create_operation("root").execute(float("inf"), 1)

def test_root_nan_triggers_nonfinite_guard_strict():
    # n is a valid nonzero integer; result is NaN, so the guard must raise
    with pytest.raises(OperationError):
        create_operation("root").execute(float("nan"), 3)

def test_root_zero_negative_degree_triggers_except():
    # 0 ** (1 / -1) -> 0 ** -1 -> ZeroDivisionError inside **,
    # which the try/except converts to OperationError. This covers the except block.
    with pytest.raises(OperationError):
        create_operation("root").execute(0.0, -1)