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
from src.extraction.source_code.model.ast.result_source_code import ResultSourceCode
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

    @staticmethod
    def remove_duplicates(original_list):
        unique_list = []

        for item in original_list:
            is_duplicate = False
            for unique_item in unique_list:
                if item == unique_item:
                    is_duplicate = True
                    break

            if not is_duplicate:
                unique_list.append(item)

        return unique_list

    def compare(self) -> None:
        library_list: list[Library] = self.__doc_result.library_list
        doc_class_list: list[ClassObject] = list()
        doc_function_list: list[Function] = list()
        for library in library_list:
            doc_class_list.extend(library.class_list)
            doc_function_list.extend(library.function_list)

        doc_class_list = self.remove_duplicates(doc_class_list)
        doc_function_list = self.remove_duplicates(doc_function_list)

        for doc_class in doc_class_list:  # Document에 있는 정의만 range로 한정.
            source_code_class: Optional[ClassObject] = self.__source_code_result.search(doc_class.symbol)
            if source_code_class is None:
                print(f"[Compare Error] class {doc_class.symbol} does not exist in Source code.")
                continue
            if not isinstance(source_code_class, ClassObject):
                print(f"[Search Error] class {doc_class.symbol} is not a class. {type(source_code_class)}")
                continue
            self.compare_class(doc_class=doc_class, source_code_class=source_code_class)
        for doc_function in doc_function_list:  # Document에 있는 정의만 range로 한정.
            source_code_function_list: Optional[list[Function]] = self.__source_code_result.search(doc_function.symbol)
            if source_code_function_list is None:
                print(f"[Compare Error] function {doc_function.symbol} does not exist in Source code.")
                continue
            if not isinstance(source_code_function_list, list):
                print(f"[Search Error] function {doc_function.symbol} is not a function. {type(source_code_function_list)}")
                continue
            all_function_assert = True
            for function in source_code_function_list:
                if not isinstance(function, Function):
                    print(f"[Search Error] function {doc_function.symbol} is not a function. {type(function)}")
                    all_function_assert = False
            if not all_function_assert:
                continue
            self.compare_function(doc_function=doc_function, source_code_function_list=source_code_function_list)

    def compare_class(self, doc_class: ClassObject, source_code_class: ClassObject) -> None:
        for source_code_parameter in source_code_class.param_list:  # Source code에 있는 파라미터가 정확한 파라미터라고 가정.
            if source_code_parameter.symbol.name == 'self':  # filtering method self.
                continue
            searched_doc_parameter: Optional[Parameter] = None
            for doc_parameter in doc_class.param_list:
                if doc_parameter.symbol == source_code_parameter.symbol:
                    self.compare_parameter(doc_parameter, source_code_parameter)
                    searched_doc_parameter = doc_parameter
                    break
            if searched_doc_parameter is None:
                print(f"[Parameter Error] class {doc_class.symbol} parameter "
                      f"{source_code_parameter.symbol} does not exist in Document.")
            else:
                if source_code_parameter.value_type != searched_doc_parameter.value_type:
                    print(f"[Parameter Type Error] class {doc_class.symbol} "
                          f"parameter {searched_doc_parameter.symbol}:{searched_doc_parameter.value_type} "
                          f"does not same with {source_code_parameter.value_type} in Source code.")

    def compare_function(self, doc_function: Function, source_code_function_list: list[Function]) -> None:
        if len(source_code_function_list) > 1:
            # overloaded functions
            is_parameter_exist_ok = False
            for source_code_function in source_code_function_list:
                is_all_parameter_ok = True
                for source_code_parameter in source_code_function.param_list:
                    is_parameter_exist = False
                    for doc_parameter in doc_function.param_list:
                        if doc_parameter.symbol == source_code_parameter.symbol:
                            self.compare_parameter(doc_parameter, source_code_parameter)
                            is_parameter_exist = True
                            break
                    is_all_parameter_ok = is_all_parameter_ok and is_parameter_exist  # 전부 다 참이어야 함
                is_parameter_exist_ok = is_parameter_exist_ok or is_all_parameter_ok  # 하나만 참이어도 됨
            if not is_parameter_exist_ok:
                print(f"[Parameter Error] overloaded function {doc_function.symbol} has something wrong.")
        else:
            # one function
            for source_code_parameter in source_code_function_list[0].param_list:
                # Source code에 있는 파라미터가 정확한 파라미터라고 가정.
                is_parameter_exist = False
                for doc_parameter in doc_function.param_list:
                    if doc_parameter.symbol == source_code_parameter.symbol:
                        self.compare_parameter(doc_parameter, source_code_parameter)
                        is_parameter_exist = True
                        break
                if not is_parameter_exist:
                    print(f"[Parameter Error] function {doc_function.symbol} parameter "
                          f"{source_code_parameter.symbol} does not exist in Document.")
                else:
                    pass

    def compare_parameter(self, doc_parameter: Parameter, source_code_parameter: Parameter) -> None:
        pass

    def compare_type(self, doc_type: Type, source_code_type: Type) -> None:
        pass

    def compare_value(self, doc_value: Value, source_code_value: Value) -> None:
        pass

    def compare_symbol(self, doc_symbol: Symbol, source_code_symbol: Symbol) -> None:
        pass
