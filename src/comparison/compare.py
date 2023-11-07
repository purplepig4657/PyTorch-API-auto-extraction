from typing import Optional

from src.common.model.class_object import ClassObject
from src.common.model.document.library import Library
from src.common.model.function import Function
from src.common.model.parameter import Parameter
from src.common.model.symbol import Symbol
from src.common.model.type import Type
from src.common.model.value import Value
from src.extraction.document.model.result_doc import ResultDoc
from src.extraction.repository.pytorch_html_code_api import PyTorchHtmlCodeApi
from src.extraction.source_code.model.file_model.file_tree import FileTree
from src.extraction.source_code.model.result_source_code import ResultSourceCode
from src.extraction.source_code.repository.pytorch_source_code_repository import PyTorchSourceCodeRepository
from src.repository.api.pytorch_html_code_api_impl import PyTorchHtmlCodeApiImpl
from src.repository.source_code.pytorch_source_code_repository_impl import PyTorchSourceCodeRepositoryImpl


class Compare:

    def __init__(self):
        self.__pytorch_html_code_api: PyTorchHtmlCodeApi = PyTorchHtmlCodeApiImpl()
        self.__pytorch_source_code_repository: PyTorchSourceCodeRepository = PyTorchSourceCodeRepositoryImpl()
        root_tree: FileTree = self.__pytorch_source_code_repository.get_source_code_tree()

        self.__doc_result: ResultDoc = ResultDoc(pytorch_html_code_api=self.__pytorch_html_code_api)
        self.__source_code_result: ResultSourceCode = ResultSourceCode(root_tree=root_tree)

    def compare(self) -> None:
        library_list: list[Library] = self.__doc_result.library_list
        for library in library_list:
            class_list: list[ClassObject] = library.class_list
            function_list: list[Function] = library.function_list
            for doc_class in class_list:
                source_code_class: ClassObject = self.__source_code_result.search(doc_class.symbol)
                self.compare_class(doc_class=doc_class, source_code_class=source_code_class)
            for doc_function in function_list:
                source_code_function: Function = self.__source_code_result.search(doc_function.symbol)
                self.compare_function(doc_function=doc_function, source_code_function=source_code_function)

    def compare_class(self, doc_class: ClassObject, source_code_class: Optional[ClassObject]) -> None:
        if source_code_class is None:
            print(f"[Compare Error] class {doc_class.symbol} is not exist.")

    def compare_function(self, doc_function: Function, source_code_function: Optional[Function]) -> None:
        if source_code_function is None:
            print(f"[Compare Error] function {doc_function.symbol} is not exist.")

    def compare_parameter(self, doc_parameter: Parameter, source_code_parameter: Parameter) -> None:
        pass

    def compare_type(self, doc_type: Type, source_code_type: Type) -> None:
        pass

    def compare_value(self, doc_value: Value, source_code_value: Value) -> None:
        pass

    def compare_symbol(self, doc_symbol: Symbol, source_code_symbol: Symbol) -> None:
        pass
