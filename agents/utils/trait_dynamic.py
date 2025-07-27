# agents/utils/trait_dynamic.py
from __future__ import annotations
from math import isfinite


class DynamicTrait:
    """
    Trait động nằm trong [0.0, 1.0] và có thể so sánh / dùng như float.
    """

    __slots__ = ("_value",)

    def __init__(self, initial_value: float):
        if not isfinite(initial_value):
            raise ValueError("Trait value must be finite")
        self._value: float = max(0.0, min(1.0, float(initial_value)))

    # ------------- API công khai ------------- #
    def increase(self, delta: float) -> None:
        """Tăng giá trị, giới hạn 1.0"""
        self._value = min(1.0, self._value + float(delta))

    def decrease(self, delta: float) -> None:
        """Giảm giá trị, giới hạn 0.0"""
        self._value = max(0.0, self._value - float(delta))

    def get(self) -> float:
        return self._value

    # ------------- Hành vi như số thực ------------- #
    def _to_float(self, other) -> float:
        return float(other._value) if isinstance(other, DynamicTrait) else float(other)

    def __float__(self) -> float:
        return self._value

    # so sánh
    def __lt__(self, other): return self._value <  self._to_float(other)
    def __le__(self, other): return self._value <= self._to_float(other)
    def __gt__(self, other): return self._value >  self._to_float(other)
    def __ge__(self, other): return self._value >= self._to_float(other)
    def __eq__(self, other): return self._value == self._to_float(other)
    def __ne__(self, other): return self._value != self._to_float(other)

    # toán học cơ bản (tùy chọn, tiện cho thống kê)
    def __add__(self, other): return self._value + self._to_float(other)
    def __radd__(self, other): return self._to_float(other) + self._value
    def __sub__(self, other): return self._value - self._to_float(other)
    def __rsub__(self, other): return self._to_float(other) - self._value
    def __mul__(self, other): return self._value * self._to_float(other)
    def __rmul__(self, other): return self._to_float(other) * self._value

    # ------------- Hiển thị ------------- #
    def __repr__(self):
        return f"DynamicTrait({self._value:.2f})"
