import ast
from typing import Optional

from src.common.model.parameter import Parameter
from src.common.model.symbol import Symbol
from src.common.model.type import Type
from src.common.model.value import Value
from src.extraction.source_code.model.ast.type_source_code import TypeSourceCode


class ParameterSourceCode(Parameter):

    __arg: ast.arg
    __default: Optional[ast.expr]

    def __init__(self, arg: ast.arg, default: Optional[ast.expr]):
        self.__arg = arg
        self.__default = default
        symbol: Symbol = self.__extract_parameter_name()
        default: Value = self.__extract_default_value()
        value_type: Type = self.__extract_value_type()
        super().__init__(symbol, default, value_type)

    def __extract_parameter_name(self) -> Symbol:
        return Symbol(self.__arg.arg)

    def __extract_default_value(self) -> Value:
        if self.__default is None:
            return Value.none_value()
        else:
            return Value[str](ast.unparse(self.__default))

    def __extract_value_type(self) -> Type:
        return TypeSourceCode.extract_type(self.__arg.annotation)

    @classmethod
    def extract_param_list_with_inspect(cls, signature_parameter) -> list[Parameter]:
        parameter_list: list[Parameter] = list()
        for name, t in signature_parameter.items():
            symbol: Symbol = Symbol(name)
            if ':' in str(t):
                parameter_def_str = str(t).split(':')[1].strip()
            else:
                parameter_list.append(Parameter(symbol, Value.none_value(), Type.none_type()))
                continue
            if '=' in parameter_def_str:
                parameter_type: Type = TypeSourceCode.extract_type_by_str(parameter_def_str.split('=')[0].strip())
                default: Value = Value(parameter_def_str.split('=')[1].strip())
            else:
                parameter_type: Type = TypeSourceCode.extract_type_by_str(parameter_def_str)
                default: Value = Value.none_value()

            parameter_list.append(Parameter(symbol, default, parameter_type))

        return parameter_list

