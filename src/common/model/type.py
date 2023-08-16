from __future__ import annotations

from src.common.model.symbol import Symbol


class Type:
    __symbol: Symbol

    def __init__(self, symbol: Symbol) -> None:
        self.__symbol = symbol

    @classmethod
    def none_type(cls) -> Type:
        return cls(Symbol("None"))

    @property
    def symbol(self) -> Symbol:
        return self.__symbol

    def merge(self, other_type: Type) -> Type:
        if self.symbol is None or self.symbol == Symbol("None"):
            result_type = other_type
        elif other_type.symbol is None or other_type.symbol == Symbol("None"):
            result_type = self
        else:
            if self.symbol != other_type.symbol:
                print("Warning: parameters' default value are not matched.")
            result_type = self

        return result_type

    def __eq__(self, other: Type) -> bool:
        return self.symbol == other.symbol

    def __str__(self):
        return self.symbol.__str__()
