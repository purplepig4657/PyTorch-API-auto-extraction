from src.common.model.class_object import ClassObject
from src.common.model.function import Function
from src.common.model.source_code.module import Module
from src.common.model.symbol import Symbol
from src.extraction.source_code.model.file_model.file_leaf import FileLeaf


class ModuleSourceCode(Module):

    def __init__(self, module_file_leaf: FileLeaf):
        symbol: Symbol = Symbol(module_file_leaf.name)
        class_list: list[ClassObject] = self.__extract_all_class_list()
        function_list: list[Function] = self.__extract_all_function_list()
        source_code: str = module_file_leaf.content
        super().__init__(symbol, class_list, function_list, source_code)

    def __extract_all_class_list(self) -> list[ClassObject]:
        pass

    def __extract_all_function_list(self) -> list[Function]:
        pass
