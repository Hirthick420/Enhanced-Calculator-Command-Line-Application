# tests/test_operations.py
import math
import pytest
from app.operations import (
    create_operation,
    Add, Subtract, Multiply, Divide, Power, Root, Modulus, IntDivide, Percent, AbsDiff
)
from app.exceptions import OperationError

@pytest.mark.parametrize("a,b,expected", [
    (3, 4, 7),
    (-2, 5, 3),
    (1.5, 2.5, 4.0),
])
def test_add(a, b, expected):
    assert create_operation("add").execute(a, b) == expected

@pytest.mark.parametrize("a,b,expected", [
    (3, 4, -1),
    (-2, 5, -7),
    (1.5, 2.5, -1.0),
])
def test_subtract(a, b, expected):
    assert create_operation("subtract").execute(a, b) == expected

@pytest.mark.parametrize("a,b,expected", [
    (3, 4, 12),
    (-2, 5, -10),
    (1.5, 2.0, 3.0),
])
def test_multiply(a, b, expected):
    assert create_operation("multiply").execute(a, b) == expected

@pytest.mark.parametrize("a,b,expected", [
    (8, 4, 2),
    (-10, 5, -2),
    (7.5, 2.5, 3.0),
])
def test_divide(a, b, expected):
    assert create_operation("divide").execute(a, b) == pytest.approx(expected)

def test_divide_by_zero():
    with pytest.raises(OperationError):
        create_operation("divide").execute(1, 0)

@pytest.mark.parametrize("a,b,expected", [
    (2, 3, 8),
    (5, 0, 1),
    (9, 0.5, 3),
])
def test_power(a, b, expected):
    assert create_operation("power").execute(a, b) == pytest.approx(expected)

def test_power_overflow_guard():
    op = create_operation("power")
    with pytest.raises(OperationError):
        op.execute(1e308, 2)

@pytest.mark.parametrize("a,n,expected", [
    (27, 3, 3),
    (81, 4, 3),     # 4th root of 81 is 3
    (1, -1, 1),     # 1 ** (1/-1) = 1
])
def test_root(a, n, expected):
    assert create_operation("root").execute(a, n) == pytest.approx(expected)

@pytest.mark.parametrize("a,n", [
    (-8, 2),  # even root of negative
    (9, 0),   # zero degree
    (9, 2.5), # non-integer degree
])
def test_root_invalid(a, n):
    with pytest.raises(OperationError):
        create_operation("root").execute(a, n)

@pytest.mark.parametrize("a,b,expected", [
    (10, 3, 1),
    (-10, 3, -10 % 3),
])
def test_modulus(a, b, expected):
    assert create_operation("modulus").execute(a, b) == expected

def test_modulus_by_zero():
    with pytest.raises(OperationError):
        create_operation("modulus").execute(10, 0)

@pytest.mark.parametrize("a,b,expected", [
    (10, 3, 3),
    (-10, 3, -4),
    (10, -3, -4),
])
def test_int_divide(a, b, expected):
    assert create_operation("int_divide").execute(a, b) == expected

def test_int_divide_by_zero():
    with pytest.raises(OperationError):
        create_operation("int_divide").execute(10, 0)

@pytest.mark.parametrize("a,b,expected", [
    (50, 200, 25.0),
    (1, 4, 25.0),
])
def test_percent(a, b, expected):
    assert create_operation("percent").execute(a, b) == expected

def test_percent_zero_denominator():
    with pytest.raises(OperationError):
        create_operation("percent").execute(1, 0)

@pytest.mark.parametrize("a,b,expected", [
    (10, 3, 7),
    (3, 10, 7),
    (-5, -2, 3),
])
def test_abs_diff(a, b, expected):
    assert create_operation("abs_diff").execute(a, b) == expected

def test_unknown_operation():
    with pytest.raises(OperationError):
        create_operation("nope")
