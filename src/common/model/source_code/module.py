from src.common.model.class_object import ClassObject
from src.common.model.function import Function
from src.common.model.symbol import Symbol


class Module:
    __symbol: Symbol
    __class_object_list: list[ClassObject]
    __function_list: list[Function]
    __source_code: str

    def __init__(
            self,
            symbol: Symbol,
            class_list: list[ClassObject],
            function_list: list[Function],
            source_code: str
    ):
        self.__symbol = symbol
        self.__class_object_list = class_list
        self.__function_list = function_list
        self.__source_code = source_code

    @property
    def symbol(self) -> Symbol:
        return self.__symbol

    @property
    def class_list(self) -> list[ClassObject]:
        return self.__class_object_list

    @property
    def function_list(self) -> list[Function]:
        return self.__function_list

    @property
    def source_code(self) -> str:
        return self.__source_code
