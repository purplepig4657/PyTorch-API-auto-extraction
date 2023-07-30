from src.common.model.function import Function
from src.common.model.parameter import Parameter
from src.common.model.symbol import Symbol
from src.common.model.type import Type


class Method(Function):

    def __init__(self, symbol: Symbol, param_list: list[Parameter], return_type: Type) -> None:
        super().__init__(symbol, param_list, return_type)
