from src.common.model.symbol import Symbol
from src.common.model.type import Type
from src.common.model.value import Value


class Parameter:
    __symbol: Symbol
    __default: Value
    __value_type: Type

    def __init__(self, symbol: Symbol, default: Value, value_type: Type) -> None:
        self.__symbol = symbol
        self.__default = default
        self.__value_type = value_type

    @property
    def symbol(self) -> Symbol:
        return self.__symbol

    @property
    def default(self) -> Value:
        return self.__default

    @property
    def value_type(self) -> Type:
        return self.__value_type

    def __str__(self) -> str:
        return f"{{symbol: {self.symbol}, default: {self.default}, value_type: {self.value_type} }}"
