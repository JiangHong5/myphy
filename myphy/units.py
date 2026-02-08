# m = 100
# px = 1
# s = 60
# frame = 1
# kg = 1
# g = 10 ** -3
# mg = 10 ** -6
# N = kg * m / (s ** 2)
# J = N * m

# def same_type_unit(unit1, unit2):
#     if unit1 in ['m', 'px'] and unit2 in ['m', 'px']:
#         return True
#     if unit1 in ['kg', 'g', 'mg'] and unit2 in ['kg', 'g', 'mg']:
#         return True
#     if unit1 in ['s', 'frame'] and unit2 in ['s', 'frame']:
#         return True
#     return False

# def get_transformer(unit1, unit2):
#     if not same_type_unit(unit1, unit2):
#         raise UnitError(unit1, unit2)
#     # If units are the same type, return a transformer function
#     if unit1 == 'm' and unit2 == 'px':
#         return 100
#     if unit1 == 'px' and unit2 == 'm':
#         return 1 / 100
#     if unit1 == 'kg' and unit2 == 'g':
#         return 1000
#     if unit1 == 'g' and unit2 == 'kg':
#         return 1 / 1000
#     if unit1 == 's' and unit2 == 'frame':
#         return 60
#     if unit1 == 'frame' and unit2 == 's':
#         return 1 / 60

# def unit_priority(unit):
#     if unit in ['m', 'kg', 's', 'N', 'J']:
#         return 1
#     if unit in ['px', 'g', 'frame']:
#         return 2
#     return 3

# class UnitError(Exception):
#     def __init__(self, u1, u2):
#         super().__init__(f"Cannot convert {u1} to {u2}")

# class Unit:
#     def __init__(self, unit):
#         self.unit = unit

#     def __add__(self, other: "Unit"):
#         if not same_type_unit(self.unit, other.unit):
#             raise UnitError(self.unit, other.unit)
#         if unit_priority(self.unit) < unit_priority(other.unit):
#             return Unit(other.unit)
#         return Unit(self.unit)

#     def __sub__(self, other: "Unit"):
#         return self.__add__(other)

#     def __mul__(self, other: "Unit"):
#         if self.unit == 'm' and other.unit == 'm':
#             return Unit('m2')
#         if self.unit == 'N' and other.unit == 'm' or self.unit == 'm' and other.unit == 'N':
#             return Unit('J')
#         if self.unit == other.unit:
#             return Unit(f"{self.unit}2")
#         return Unit(f"{self.unit}*{other.unit}")

#     def __truediv__(self, other: "Unit"):
#         if self.unit == other.unit:
#             return Unit('')
#         if self.unit == 'J' and other.unit == 'm':
#             return Unit('N')
#         if self.unit == 'N' and other.unit == 'm':
#             return Unit('kg/s2')
#         if self.unit == 'm2' and other.unit == 'm':
#             return Unit('m')
#         if self.unit == 'm' and other.unit == 's':
#             return Unit('m/s')
#         if self.unit == 'kg*m' and other.unit == 's2':
#             return Unit('N')
#         if self.unit.endswith('2') and not (other.unit.endswith('2')) and self.unit[:-1] == other.unit[:-1]:
#             return Unit(other.unit)
#         return Unit(f"{self.unit}/{other.unit}")

# class ValWithUnit:
#     def __init__(self, value, unit):
#         self.value = value
#         self.unit = Unit(unit)

from typing import Union, Any
from enum import Enum

type Unit = Union["_UnionUnit", "_BasicUnit"]
type AllUnit = Union["_UnionUnit", "_BasicUnit", "_SubUnit"]


class ConvertingError(TypeError):
    def __init__(self, unit1: AllUnit, unit2: AllUnit):
        super().__init__(f"Cannot convert {unit1} to {unit2}")


class OperationError(ValueError):
    def __init__(self, op: str, unit1: AllUnit, unit2: AllUnit):
        super().__init__(f"Cannot perform {op} between {unit1} and {unit2}")


class InvalidUnit(TypeError):
    def __init__(self, unit: Any) -> None:
        super().__init__(f"Invalid unit type: {unit.__class__}")


class DimensionError(ValueError):
    def __init__(self, unit1: AllUnit, unit2: AllUnit):
        super().__init__(f"Units {unit1} and {unit2} are of different dimensions")


def same_dimension(unit1: AllUnit, unit2: AllUnit) -> bool:
    if isinstance(unit1, _UnionUnit) and isinstance(unit2, _UnionUnit):
        return unit1 == unit2
    if isinstance(unit1, (_BasicUnit, _SubUnit)) and isinstance(
        unit2, (_BasicUnit, _SubUnit)
    ):
        if isinstance(unit1, _SubUnit):
            unit1 = unit1.base_unit
        if isinstance(unit2, _SubUnit):
            unit2 = unit2.base_unit
        return unit1 == unit2
    raise InvalidUnit(
        unit1 if not isinstance(unit1, (_BasicUnit, _SubUnit, _UnionUnit)) else unit2
    )


# class Dimension(Enum):
#     LENGTH = "length"
#     MASS = "mass"
#     TIME = "time"
#     FORCE = "force"
#     ENERGY = "energy"
# no need, just check "base_unit"

# expected:
# N == m * kg / s ** 2
# J == N * m == m ** 2 * kg / s / s
# N => UnionUnit
# UnionUnit => {all = [(m, 1), (kg, 1), (s, -2)]}
# other => BasicUnit


# I know all the basic units, how to represent them as UnionUnit and user can't DIY them?
class _BasicUnit:
    def __init__(self, name: str):
        self.name = name

    def __mul__(self, other: Union["_BasicUnit", "_UnionUnit"]):
        if isinstance(other, _BasicUnit):
            if self == other:
                return _UnionUnit({self: 2})
            return _UnionUnit({self: 1, other: 1})
        if isinstance(other, _UnionUnit):
            return other * self

    def __truediv__(self, other: Union["_BasicUnit", "_UnionUnit"]):
        if isinstance(other, _BasicUnit):
            if self == other:
                return _UnionUnit({})
            return _UnionUnit({self: 1, other: -1})
        if isinstance(other, _UnionUnit):
            return _UnionUnit({self: 1}) / other

    def __pow__(self, power: int):
        return _UnionUnit({self: power})

    def __repr__(self):
        return self.name

    def __eq__(self, other: Union["_BasicUnit", "_UnionUnit"]):
        # print("basic unit eq")
        if isinstance(other, _BasicUnit):
            return self.name == other.name
        if isinstance(other, _UnionUnit):
            return other == self
        return False

    def __hash__(self):
        return hash((self.name, self.__class__))

    def to_sub(self, unit: "_SubUnit"):
        if unit.base_unit != self:
            raise ValueError(f"Cannot convert {self} to {unit}")
        return _PhysicalValue(1 / unit.factor, self)

    @property
    def value(self):
        return _PhysicalValue(1, self)


m = _BasicUnit("m")
kg = _BasicUnit("kg")
s = _BasicUnit("s")

# How to make a mg / g / ms / px ... and they multiply a number to
# become to another unit?
# ms * 1000 => s
# px * 100 => m
# frame * 60 => s
# ...
# (== is ==, => is just changed to another)
#
# I think I can just don't implement it.
# (after) AI helped me to do it


class _UnionUnit:
    def __init__(self, all: dict[_BasicUnit, int]):
        self.all = all
        self.clear_zero()

    def __mul__(self, other: Union["_BasicUnit", "_UnionUnit"]):
        if isinstance(other, _BasicUnit):
            if other in self.all:
                new_all = self.all.copy()
                new_all[other] += 1
                return _UnionUnit(new_all)
            else:
                return _UnionUnit({**self.all, other: 1})
        if isinstance(other, _UnionUnit):
            new_all = self.all.copy()
            for k, v in other.all.items():
                if k in new_all:
                    new_all[k] += v
                else:
                    new_all[k] = v
            return _UnionUnit(new_all)
        raise TypeError(f"Cannot multiply {type(other)}")
    
    def __matmul__(self, other: float):
        return self.value * other

    def __truediv__(self, other: Union["_BasicUnit", "_UnionUnit"]):
        if isinstance(other, _BasicUnit):
            if other in self.all:
                new_all = self.all.copy()
                new_all[other] -= 1
                if new_all[other] == 0:
                    new_all.pop(other)
                return _UnionUnit(new_all)
            else:
                return _UnionUnit({**self.all, other: -1})
        if isinstance(other, _UnionUnit):
            new_all = self.all.copy()
            for k, v in other.all.items():
                if k in new_all:
                    new_all[k] -= v
                    if new_all[k] == 0:
                        new_all.pop(k)
                else:
                    new_all[k] = -v

            return _UnionUnit(new_all)
        raise TypeError(f"Cannot divide {type(other)}")

    def __pow__(self, power: int):
        self.clear_zero()
        new_all = {k: v * power for k, v in self.all.items()}
        return _UnionUnit(new_all)

    def __hash__(self) -> int:
        self.clear_zero()
        return hash(frozenset(self.all.items()))

    def __repr__(self):
        mul_part = _UnionUnit({})
        for k, v in self.all.items():
            if v > 0:
                mul_part = mul_part * (k**v)
        mul_part_repr = (
            " * ".join(
                [
                    f"{k}^{v}" if v != 1 else f"{k}"
                    for k, v in mul_part.all.items()
                    if v != 0
                ]
            )
            or "1"
        )
        div_part = _UnionUnit({})
        for k, v in self.all.items():
            if v < 0:
                div_part = div_part * (k ** (-v))
        div_part_repr = (
            " * ".join(
                [
                    f"{k}^{v}" if v != 1 else f"{k}"
                    for k, v in div_part.all.items()
                    if v != 0
                ]
            )
            or "1"
        )
        if div_part_repr == "1" and mul_part_repr == "1":
            return ""
        if div_part_repr == "1":
            return mul_part_repr
        if div_part_repr != "1" and mul_part_repr == "1":
            return f" / {div_part_repr}"
        return f"{mul_part_repr} / {div_part_repr}"

    def clear_zero(self):
        self.all = {k: v for k, v in self.all.items() if v != 0}

    def __eq__(self, other: "_UnionUnit"):
        self.clear_zero()
        # print("union unit eq")
        if isinstance(other, _UnionUnit):
            return self.all == other.all
        if isinstance(other, _BasicUnit):
            # print("self.all:", self.all)
            return len(self.all) == 1 and other in self.all and self.all[other] == 1
        return False

    @property
    def value(self):
        return _PhysicalValue(1, self)

one = _UnionUnit({})

class _PhysicalValue:
    def __init__(self, value: float, unit: _UnionUnit | _BasicUnit):
        self.value = round(value, 12)
        self.unit = unit

    def __repr__(self):
        return f"{self.value: .4g}{self.unit}"

    def __add__(self, other: "_PhysicalValue"):
        # print(f"adding {type(self.unit)} and {type(other.unit)}...")
        if self.unit == other.unit:
            return _PhysicalValue(self.value + other.value, self.unit)
        raise ValueError(f"Cannot add {self} and {other}")

    def __sub__(self, other: "_PhysicalValue"):
        if self.unit == other.unit:
            return _PhysicalValue(self.value - other.value, self.unit)
        raise ValueError(f"Cannot subtract {self} and {other}")

    def __mul__(self, other: Union[float, int, "_PhysicalValue"]):
        if isinstance(other, _PhysicalValue):
            return _PhysicalValue(self.value * other.value, self.unit * other.unit)
        return _PhysicalValue(self.value * other, self.unit)

    def __rmul__(self, other: Union[float, int]):
        return self.__mul__(other)

    def __truediv__(
        self, other: Union[float, int, "_PhysicalValue", "_UnionUnit", "_BasicUnit"]
    ):
        if isinstance(other, _PhysicalValue):
            return _PhysicalValue(self.value / other.value, self.unit / other.unit)
        if isinstance(other, (int, float)):
            return _PhysicalValue(self.value / other, self.unit)
        raise TypeError(f"Cannot divide {type(self)} by {type(other)}")

    def __rtruediv__(self, other: Union[float, int]):
        return _PhysicalValue(other / self.value, _UnionUnit({}) / self.unit)

    def __eq__(self, other: "_PhysicalValue"):
        # print(
        #     f"_PhysicalValue().__eq__: self: {self.value}, {self.unit}; other: {other.value}, {other.unit}"
        # )
        # if isinstance(self.unit, _UnionUnit) and isinstance(other.unit, _UnionUnit):
        #     print(
        #         f"_PhysicalValue().__eq__: self.unit.all: {self.unit.all}, other.unit.all: {other.unit.all}"
        #     )
        # if self.value == other.value:
        #     print("_PhysicalValue().__eq__: values are the same")
        # if self.unit == other.unit:
        #     print("_PhysicalValue().__eq__: unit are the same")
        return self.value == other.value and self.unit == other.unit

    def __lt__(self, other: "_PhysicalValue"):
        if self.unit != other.unit:
            return NotImplemented
        return self.value < other.value

    def __pow__(self, other: int):
        return _PhysicalValue(self.value**other, self.unit**other)

    def to_unit(self, unit: Union["_SubUnit", "_BasicUnit"]) -> "_PhysicalValue":
        if isinstance(unit, _BasicUnit):
            if self.unit != unit:
                raise ConvertingError(self.unit, unit)
            return _PhysicalValue(self.value, unit)
        if unit.base_unit != self.unit:
            raise ConvertingError(self.unit, unit)
        return _PhysicalValue(self.value / unit.factor, unit.base_unit)


# # I don't know can it work
# class _SubUnit(_BasicUnit):
#     """Represents a derived unit that is the inverse of another unit.
#     (cm, px, frame, eg.)
#     """
#     def __init__(self, name: str, base_unit: _BasicUnit, factor: float):
#         self.name = name
#         self.base_unit = base_unit
#         self.factor = factor  # multiply to become base_unit

#     def to_base(self):
#         return _PhysicalValue(self.factor, self.base_unit)

#     def __repr__(self):
#         return self.name

#     def __mul__(self, other: _BasicUnit | _UnionUnit | int | float):
#         if isinstance(other, (int, float)):
#             return _PhysicalValue(self.factor * other, self.base_unit)
#         if isinstance(other, _BasicUnit):
#             return self.base_unit * other
#         if isinstance(other, _UnionUnit):
#             return self.base_unit * other

#     def __rmul__(self, other: _BasicUnit | _UnionUnit | int | float):
#         return self.__mul__(other)

#     def __truediv__(self, other: _BasicUnit | _UnionUnit | int | float):
#         if isinstance(other, (int, float)):
#             return _PhysicalValue(self.factor / other, self.base_unit)
#         if isinstance(other, _BasicUnit):
#             return self.base_unit / other
#         if isinstance(other, _UnionUnit):
#             return self.base_unit / other

#     def __rtruediv__(self, other: _BasicUnit | _UnionUnit | int | float):
#         if isinstance(other, (int, float)):
#             return 1 / self.to_base() * other
#         if isinstance(other, (_BasicUnit, _UnionUnit)):
#             return other / self.base_unit


# AI's
class _SubUnit:
    """派生单位类，如克、像素、帧等，基于基础单位定义"""

    def __init__(self, name: str, base_unit: _BasicUnit, factor: float):
        self.name = name  # 派生单位名称（如"g"、"px"）
        self.base_unit = base_unit  # 对应的基础单位
        self.factor = factor  # 转换系数：1派生单位 = factor基础单位

    def to_base(self) -> _PhysicalValue:
        """转换为基础单位的物理量"""
        return _PhysicalValue(self.factor, self.base_unit)

    def __repr__(self):
        return self.name

    def __mul__(
        self, other: Union[float, int, "_PhysicalValue", "_BasicUnit", "_UnionUnit"]
    ):
        if isinstance(other, (int, float)):
            return _PhysicalValue(self.factor * other, self.base_unit)
        if isinstance(other, _PhysicalValue):
            return self.to_base() * other
        if isinstance(other, (_BasicUnit, _UnionUnit)):
            # 派生单位 × 基础单位/复合单位 = 基础单位 × 基础单位/复合单位
            return self.base_unit * other
        raise TypeError(f"Cannot multiply {type(self)} with {type(other)}")

    def __rmul__(
        self, other: Union[float, int, "_PhysicalValue", "_BasicUnit", "_UnionUnit"]
    ):
        return self.__mul__(other)

    def __truediv__(
        self, other: Union[float, int, "_PhysicalValue", "_BasicUnit", "_UnionUnit"]
    ):
        if isinstance(other, (int, float)):
            return _PhysicalValue(self.factor / other, self.base_unit)
        if isinstance(other, _PhysicalValue):
            return self.to_base() / other
        if isinstance(other, (_BasicUnit, _UnionUnit)):
            return self.base_unit / other
        raise TypeError(f"Cannot divide {type(self)} by {type(other)}")

    def __rtruediv__(
        self, other: Union[float, int, "_PhysicalValue", "_BasicUnit", "_UnionUnit"]
    ):
        if isinstance(other, (int, float)):
            return _PhysicalValue(other / self.factor, _UnionUnit({}) / self.base_unit)
        if isinstance(other, _PhysicalValue):
            return other / self.to_base()
        if isinstance(other, (_BasicUnit, _UnionUnit)):
            return other / self.base_unit
        raise TypeError(f"Cannot divide {type(other)} by {type(self)}")

    @property
    def value(self):
        return _PhysicalValue(self.factor, self.base_unit)

    def __pow__(self, other: int):
        return self.to_base() ** other


# type \
PhyValue = _PhysicalValue


def build_value(
    value: float, unit: AllUnit
) -> PhyValue:
    if isinstance(unit, _SubUnit):
        return value * unit.to_base()
    return _PhysicalValue(value, unit)


N = m * kg / (s**2)
J = m * N
W = J / s
m_p_s = m / s
m_p_s2 = m / (s**2)
m2 = m**2

g = _SubUnit("g", kg, 0.001)
px = _SubUnit("px", m, 0.01)
frame = _SubUnit("frame", s, 1 / 60)
cm = _SubUnit("cm", m, 0.01)
dm = _SubUnit("dm", m, 0.1)
ms = _SubUnit("ms", s, 0.001)

if __name__ == "__main__":
    # hope work fine
    print("========test 1: Units========")
    print(N, ":", N.all)
    print(J, ":", J.all)
    print("Is m_p_s2 == m / s / s:", m_p_s2 == m / s / s)
    # sorry, forgot comparing operators...
    # implemented
    print("Is m2 == m * m:", m2 == m * m)
    # fixed a bug when two same unit multiplies
    print("========test 2:PhyVal========")
    m1 = _PhysicalValue(1, m)
    m2 = _PhysicalValue(2, m)
    print(m1 + m2)
    print(m1 - m2)
    print(m1 * m2, (m1 * m2).unit)
    print(m1 / m2)
    print(m1**2)
    force = _PhysicalValue(1, N)
    print(force * m1)
    print(force / m1)
    print("=======test 3: SubUnit=======")
    print(g.to_base())
    print(px.to_base())
    print(30 * frame)
    print(5 * px)
    print("=======test 4: Convert=======")
    print(5 * kg.value.to_unit(g))
    print(5000 * g.value.to_unit(kg))
    print("========test 5: Final========")
    gravity1 = 9.8 * 10**-3 * N.value / g.value
    gravity2 = 9.8 * 10**-4 * cm.value / (ms**2)
    print(
        f"9.8*10^-3N/g({gravity1}) == 9.8*10^-4cm/ms^2({gravity2})?",
        gravity1 == gravity2,
    )

# 可以解析一下原代码的注释吗，可能可以得到作者的心路流程
