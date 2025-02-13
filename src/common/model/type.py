from __future__ import annotations

from typing import Tuple

from src.common.model.symbol import Symbol


class Type:
    __symbol: Symbol
    __NONE_TYPE_SYMBOL = Symbol("아무거나괜찮아요")
    __PARSE_ERROR_SYMBOL = Symbol("ParseError")

    def __init__(self, symbol: Symbol) -> None:
        self.__symbol = symbol

    @classmethod
    def none_type(cls) -> Type:
        return cls(cls.__NONE_TYPE_SYMBOL)

    @classmethod
    def parse_error_type(cls) -> Type:
        return cls(cls.__PARSE_ERROR_SYMBOL)

    @property
    def symbol(self) -> Symbol:
        return self.__symbol

    def merge(self, other_type: Type) -> Type:

        if other_type.symbol is not None and other_type.symbol != other_type.__NONE_TYPE_SYMBOL \
                and other_type.symbol != other_type.__PARSE_ERROR_SYMBOL and other_type != Type.none_type():
            print(f"box has type: {self.symbol}")

        if self.symbol is None or self.symbol == self.__NONE_TYPE_SYMBOL \
                or self.symbol == self.__PARSE_ERROR_SYMBOL:
            result_type = other_type
        elif other_type.symbol is None or other_type.symbol == other_type.__NONE_TYPE_SYMBOL \
                or other_type.symbol == other_type.__PARSE_ERROR_SYMBOL:
            result_type = self
        else:
            if self != other_type:
                print("Warning: Types are not matched.")
            result_type = self

        return result_type

    def __eq__(self, other: Type) -> bool:
        if not isinstance(other, Type):
            return False
        return self.symbol == other.symbol

    def equal(self, other: Type) -> Tuple[str, str]:
        if not isinstance(other, Type):
            return 'Error', ''
        if type(self) == 'GenericType':
            return self.equal(other)
        if self.symbol == other.symbol:
            return 'Match', ''
        else:
            return 'Error', ''

    def __str__(self) -> str:
        return str(self.symbol.name)

    def to_json(self):
        return self.symbol.name
