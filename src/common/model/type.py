from __future__ import annotations

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

    def __str__(self):
        return self.symbol.__str__()
