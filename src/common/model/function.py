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

    def __str__(self) -> str:
        return f"{{ \"symbol\": {self.symbol}, \"param_list\": {list(map(str, self.param_list))}, " \
               f"\"return_type\": {self.return_type} }}"
