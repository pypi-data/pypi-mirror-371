from __future__ import annotations

from dataclasses import dataclass

from .interned import interned
from .op import Op


@interned
@dataclass(frozen=True, order=True, slots=True)
class Dice:
    number: int
    sides: int
    op: Op = Op.PLUS

    def __post_init__(self):
        assert self.number >= 0
        assert self.sides >= 0

    def __repr__(self) -> str:
        cls_name = self.__class__.__name__
        if Op.PLUS == self.op:
            return f'{cls_name}({self.number}, {self.sides})'
        else:
            return f'{cls_name}({self.number}, {self.sides}, {self.op!r})'

    def __str__(self) -> str:
        if self.is_mod:
            mod = self.number * self.sides
            return f'{self.op}{mod}'
        else:
            op = '' if Op.PLUS == self.op else self.op
            number = '' if 1 == self.number else self.number
            return f'{op}{number}d{self.sides}'

    @property
    def is_mod(self) -> bool:
        return 0 == self.number or 0 == self.sides or 1 == self.sides

    def to_plus(self) -> Dice:
        return self.__class__(self.number, self.sides, Op.PLUS)

    def to_minus(self) -> Dice:
        return self.__class__(self.number, self.sides, Op.MINUS)

    def to_times(self) -> Dice:
        return self.__class__(self.number, self.sides, Op.TIMES)

    @classmethod
    def die(cls, sides: int) -> Dice:
        return cls(1, sides)

    @classmethod
    def mod(cls, op: Op, value: int) -> Dice:
        return cls(value, 1, op)

    @classmethod
    def n_dice(cls, number: int, sides: int | Dice) -> Dice:
        sides_value = sides.sides if isinstance(sides, Dice) else sides
        return cls(number, sides_value, Op.PLUS)


d = Dice.die
mod = Dice.mod
nd = Dice.n_dice
