from src.common.model.class_object import ClassObject
from src.common.model.function import Function
from src.common.model.symbol import Symbol


class Library:
    __symbol: Symbol
    __class_list: list[ClassObject]
    __function_list: list[Function]

    def __init__(self, symbol: Symbol, class_list: list[ClassObject], function_list: list[Function]) -> None:
        self.__symbol = symbol
        self.__class_list = class_list
        self.__function_list = function_list

    @property
    def symbol(self) -> Symbol:
        return self.__symbol

    @property
    def class_list(self) -> list[ClassObject]:
        return self.__class_list

    @property
    def function_list(self) -> list[Function]:
        return self.__function_list

    def __str__(self) -> str:

        def str_lambda(x) -> str:
            return str(x).replace("\'", "").replace("\\", "")

        class_list_str = list(map(str_lambda, self.class_list))
        function_list_str = list(map(str_lambda, self.function_list))
        return str_lambda(f"{{ symbol: {self.symbol}, class_list: {class_list_str}, function_list: {function_list_str} }}")
