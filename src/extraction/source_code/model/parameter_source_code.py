import ast
from typing import Optional

from src.common.model.parameter import Parameter
from src.common.model.symbol import Symbol
from src.common.model.type import Type
from src.common.model.value import Value
from src.extraction.source_code.model.type_source_code import TypeSourceCode


class ParameterSourceCode(Parameter):

    __arg: ast.arg
    __default: Optional[ast.expr]

    def __init__(self, arg: ast.arg, default: Optional[ast.expr]):
        self.__arg = arg
        self.__default = default
        symbol: Symbol = self.__extract_parameter_name()
        default: Optional[Value] = self.__extract_default_value()
        value_type: Optional[Type] = self.__extract_value_type()
        super().__init__(symbol, default, value_type)

    def __extract_parameter_name(self) -> Symbol:
        return Symbol(self.__arg.arg)

    def __extract_default_value(self) -> Optional[Value]:
        if self.__default is None:
            return Value.none_value()
        else:
            return Value(ast.unparse(self.__default))

    def __extract_value_type(self) -> Optional[Type]:
        return TypeSourceCode.extract_type(self.__arg.annotation)
