from typing import Union

from src.common.model.symbol import Symbol
from src.common.model.type import Type
from src.common.model.value import Value


class Parameter:
    __symbol: Union[Symbol, None]
    __default: Union[Value, None]
    __value_type: Union[Type, None]
    __is_optional: Union[bool, None]

    def __init__(
            self, symbol: Union[Symbol, None],
            default: Union[Value, None],
            value_type: Union[Type, None],
            is_optional: Union[bool, None]
    ) -> None:
        self.__symbol = symbol
        self.__default = default
        self.__value_type = value_type
        self.__is_optional = is_optional

    @property
    def symbol(self) -> Symbol:
        return self.__symbol

    @property
    def default(self) -> Value:
        return self.__default

    @property
    def value_type(self) -> Type:
        return self.__value_type

    @property
    def is_optional(self) -> bool:
        return self.__is_optional

    def __str__(self) -> str:
        return f"{{symbol: {self.symbol}, default: {self.default}, value_type: {self.value_type} }}"
