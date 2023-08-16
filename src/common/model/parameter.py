from __future__ import annotations
from typing import Optional

from src.common.model.symbol import Symbol
from src.common.model.type import Type
from src.common.model.value import Value


class Parameter:
    __symbol: Symbol
    __default: Optional[Value]
    __value_type: Optional[Type]

    def __init__(
            self, symbol: Symbol,
            default: Optional[Value],
            value_type: Optional[Type],
    ) -> None:
        self.__symbol = symbol
        self.__default = default
        self.__value_type = value_type

    @property
    def symbol(self) -> Symbol:
        return self.__symbol

    @property
    def default(self) -> Optional[Value]:
        return self.__default

    @property
    def value_type(self) -> Optional[Type]:
        return self.__value_type

    def merge(self, other_parameter: Parameter) -> Parameter:
        if self.symbol != other_parameter.symbol:
            print(self.symbol, other_parameter.symbol)
            raise RuntimeError("Parameters' symbol are not matched.")

        result_symbol: Symbol = self.symbol
        result_default: Optional[Value] = None
        result_value_type: Optional[Type] = None

        # default
        if self.default is None or self.default == Value.none_value():
            result_default = other_parameter.default
        elif other_parameter.default is None or other_parameter.default == Value.none_value():
            result_default = self.default
        else:
            if self.default != other_parameter.default:
                print("Warning: parameters' default value are not matched.")
            result_default = self.default

        # type
        result_value_type = self.value_type.merge(other_parameter.value_type)

        return Parameter(result_symbol, result_default, result_value_type)

    def __str__(self) -> str:
        return f"{{ \"symbol\": {self.symbol}, \"default\": {self.default}, \"value_type\": {self.value_type} }}"
