from __future__ import annotations

from typing import Optional

from src.common.model.parameter import Parameter
from src.common.model.symbol import Symbol
from src.common.model.type import Type


class Function:
    __symbol: Symbol
    __param_list: list[Parameter]
    __return_type: Optional[Type]

    def __init__(self, symbol: Symbol, param_list: list[Parameter], return_type: Optional[Type]) -> None:
        self.__symbol = symbol
        self.__param_list = param_list
        self.__return_type = return_type

    @property
    def symbol(self) -> Symbol:
        return self.__symbol

    @property
    def param_list(self) -> list[Parameter]:
        return self.__param_list

    @property
    def return_type(self) -> Optional[Type]:
        return self.__return_type

    @symbol.setter
    def symbol(self, symbol):
        self.__symbol = symbol

    def to_json(self) -> str:
        return f"{{ \"symbol\": {self.symbol.to_json()}, \"param_list\": " \
               f"{[param.to_json() for param in self.param_list]}, " \
               f"\"return_type\": {self.return_type.to_json()} }}"

    def __str__(self) -> str:
        return f"{self.symbol}({list(map(str, self.param_list))}) -> {self.return_type}"

    def __eq__(self, other: Function):
        if len(self.param_list) != len(other.param_list):
            return False
        for self_parameter, other_parameter in zip(self.param_list, other.param_list):
            if self_parameter != other_parameter:
                return False
        if self.symbol != other.symbol:
            return False
        if self.return_type != other.return_type:
            return False
        return True
