from typing import Optional, Union

from src.common.model.class_object import ClassObject
from src.common.model.document.library import Library
from src.common.model.function import Function
from src.common.model.generic_type import GenericType
from src.common.model.parameter import Parameter
from src.common.model.symbol import Symbol
from src.common.model.type import Type
from src.common.model.value import Value
from src.extraction.document.model.result_doc import ResultDoc
from src.extraction.repository.pytorch_html_code_api import PyTorchHtmlCodeApi
from src.extraction.source_code.model.ast.method_source_code import MethodSourceCode
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
                print(f"[Search Error] class {doc_class.symbol} does not exist in Source code.")
                continue
            if not isinstance(source_code_class, ClassObject):
                print(f"[Search Error] class {doc_class.symbol} is not a class. {type(source_code_class)}")
                continue
            self.compare_class(doc_class=doc_class, source_code_class=source_code_class)
        for doc_function in doc_function_list:  # Document에 있는 정의만 range로 한정.
            source_code_function_list: Optional[list[Function]] = self.search_function(doc_function.symbol)
            if source_code_function_list is None:
                continue
            if isinstance(source_code_function_list[0], MethodSourceCode):
                self.compare_method(doc_method=doc_function, source_code_method_list=source_code_function_list)
            else:
                self.compare_function(doc_function=doc_function, source_code_function_list=source_code_function_list)

    def search_function(self, doc_function_symbol: Symbol) -> Optional[list[Function]]:
        source_code_function_list: Optional[list[Function]] = self.__source_code_result.search(doc_function_symbol)
        if source_code_function_list is None:
            print(f"[Search Error] function {doc_function_symbol} does not exist in Source code.")
            return None
        if not isinstance(source_code_function_list, list):
            print(f"[Search Error] function {doc_function_symbol} is not a function. {type(source_code_function_list)}")
            return None
        all_function_assert = True
        for function in source_code_function_list:
            if not isinstance(function, Function):
                print(f"[Search Error] function {doc_function_symbol} is not a function. {type(function)}")
                all_function_assert = False
        if not all_function_assert:
            return None
        return source_code_function_list

    def search_method(self, doc_class_symbol: Symbol, doc_method_symbol: Symbol) -> Optional[list[Function]]:
        source_code_function_list: Optional[list[Function]] = self.__source_code_result.search(doc_method_symbol)
        if source_code_function_list is None:
            print(f"[Search Error] class {doc_class_symbol} method "
                  f"{doc_method_symbol} does not exist in Source code.")
            return None
        if not isinstance(source_code_function_list, list):
            print(f"[Search Error] method {doc_method_symbol} is not a method. {type(source_code_function_list)}")
            return None
        all_function_assert = True
        for function in source_code_function_list:
            if not isinstance(function, Function):
                print(f"[Search Error] method {doc_method_symbol} is not a method. {type(function)}")
                all_function_assert = False
        if not all_function_assert:
            return None
        return source_code_function_list

    def compare_class(self, doc_class: ClassObject, source_code_class: ClassObject) -> None:
        for source_code_parameter in source_code_class.param_list:  # Source code에 있는 파라미터가 정확한 파라미터라고 가정.
            if source_code_parameter.symbol.name == 'self':  # filtering method self.
                continue
            searched_doc_parameter: Optional[Parameter] = None
            for doc_parameter in doc_class.param_list:
                if doc_parameter.symbol == source_code_parameter.symbol:
                    self.compare_parameter(doc_class, doc_parameter, source_code_parameter, False)
                    searched_doc_parameter = doc_parameter
                    break
            if searched_doc_parameter is None:
                print(f"[Parameter Exist Error] class {doc_class.symbol} parameter "
                      f"{source_code_parameter.symbol} does not exist in Document.")
            else:
                pass
        for doc_method in doc_class.method_list:
            source_code_function_list: Optional[list[Function]] = self.search_method(doc_class.symbol, doc_method.symbol)
            if source_code_function_list is None:
                continue
            self.compare_method(doc_method, source_code_function_list)

    def compare_function(self, doc_function: Function, source_code_function_list: list[Function]) -> None:
        if len(source_code_function_list) > 1:
            # overloaded functions
            is_parameter_exist_ok = False
            right_source_code_function: Optional[Function] = None
            for source_code_function in source_code_function_list:
                is_all_parameter_ok = True
                for source_code_parameter in source_code_function.param_list:
                    is_parameter_exist = False
                    for doc_parameter in doc_function.param_list:
                        if doc_parameter.symbol == source_code_parameter.symbol:
                            is_parameter_exist = True
                            break
                    is_all_parameter_ok = is_all_parameter_ok and is_parameter_exist  # 전부 다 참이어야 함
                if is_all_parameter_ok:
                    right_source_code_function = source_code_function
                is_parameter_exist_ok = is_parameter_exist_ok or is_all_parameter_ok  # 하나만 참이어도 됨
            if not is_parameter_exist_ok:
                print(f"[Parameter Exist Error] overloaded function {doc_function.symbol} has something wrong.")
            else:
                for source_code_parameter in right_source_code_function.param_list:
                    for doc_parameter in doc_function.param_list:
                        if doc_parameter.symbol == source_code_parameter.symbol:
                            self.compare_parameter(doc_function, doc_parameter, source_code_parameter, True)
        else:
            # one function
            for source_code_parameter in source_code_function_list[0].param_list:
                # Source code에 있는 파라미터가 정확한 파라미터라고 가정.
                is_parameter_exist = False
                for doc_parameter in doc_function.param_list:
                    if doc_parameter.symbol == source_code_parameter.symbol:
                        self.compare_parameter(doc_function, doc_parameter, source_code_parameter, False)
                        is_parameter_exist = True
                        break
                if not is_parameter_exist:
                    print(f"[Parameter Exist Error] function {doc_function.symbol} parameter "
                          f"{source_code_parameter.symbol} does not exist in Document.")
                else:
                    pass

    def compare_method(self, doc_method: Function, source_code_method_list: list[Function]) -> None:
        if len(source_code_method_list) > 1:
            print("Overloading exists...")
            return
        for source_code_parameter in source_code_method_list[0].param_list:
            if source_code_parameter.symbol.name == 'self' or source_code_parameter.symbol.name == 'cls':
                # filtering method self and cls.
                continue
            # Source code에 있는 파라미터가 정확한 파라미터라고 가정.
            is_parameter_exist = False
            for doc_parameter in doc_method.param_list:
                if doc_parameter.symbol == source_code_parameter.symbol:
                    self.compare_parameter(doc_method, doc_parameter, source_code_parameter, False)
                    is_parameter_exist = True
                    break
            if not is_parameter_exist:
                print(f"[Parameter Exist Error] method {doc_method.symbol} parameter "
                      f"{source_code_parameter.symbol} does not exist in Document.")
            else:
                pass

    def compare_parameter(
            self,
            doc: Union[ClassObject, Function],
            doc_parameter: Parameter,
            source_code_parameter: Parameter,
            is_overloaded: bool
    ) -> None:
        """EXCEPT_CASE = [Symbol("Any"), Symbol("_size_any_t"), Symbol("_size_1_t"), Symbol("_size_2_t"),
                       Symbol("_size_3_t"), Symbol("_size_4_t"), Symbol("_size_5_t"), Symbol("_size_6_t"),
                       Symbol("_size_any_opt_t"), Symbol("_size_2_opt_t"), Symbol("_size_3_opt_t"),
                       Symbol("_ratio_any_t"), Symbol("_ratio_2_t"), Symbol("_ratio_3_t"), Symbol("_tensor_list_t"),
                       Symbol("_maybe_indices_t")]"""
        EXCEPT_CASE = [Symbol("Any")]
        if source_code_parameter.value_type == Type.none_type() or \
                source_code_parameter.value_type.symbol in EXCEPT_CASE:  # 이 로직을 Type.__eq__ 로 옮기면 재귀적으로 적용이 가능할듯.
            return
        if doc_parameter.value_type == Type.none_type():
            print(f"[Parameter Type Warning] {'class' if isinstance(doc, ClassObject) else 'function'} {doc.symbol}"
                  f" parameter {doc_parameter.symbol}:{doc_parameter.value_type} Document Type is not described.")
            return
        doc_type = doc_parameter.value_type
        source_code_type = source_code_parameter.value_type
        # Optional 처리
        OPTIONAL_SYMBOL = Symbol("Optional")
        # 만약 doc에 optional이 붙어있고, 코드에 optional 이 붙어있지 않을 때
        if isinstance(doc_type, GenericType) and doc_type.symbol == OPTIONAL_SYMBOL \
                and source_code_type.symbol != OPTIONAL_SYMBOL:
            # doc에 default value가 명시되어 있지 않다면 -> 에러
            if doc_parameter.default == Value.none_value():
                print(f"[Parameter Type Error] "
                      f"{'class' if isinstance(doc, ClassObject) else 'overloaded function' if is_overloaded else 'function'}"
                      f" {doc.symbol} "
                      f"parameter {doc_parameter.symbol}:{doc_parameter.value_type} "
                      f"does not same with {source_code_parameter.value_type} in Source code."
                      f": Doc type has optional, but there is no default value.")
                return

            # doc에 optional을 떼고 코드와 비교했을 때 타입이 다르면 -> 에러
            compare_result = source_code_type.equal(doc_type.generic_list[0])
            if compare_result[0] != 'Match':
                print(f"[Parameter Type {compare_result[0]}] "
                      f"{'class' if isinstance(doc, ClassObject) else 'overloaded function' if is_overloaded else 'function'}"
                      f" {doc.symbol} "
                      f"parameter {doc_parameter.symbol}:{doc_parameter.value_type} "
                      f"does not same with {source_code_parameter.value_type} in Source code."
                      f": {compare_result[1]}, Optional Error")
            return
        # 만약 코드에 Optional이 붙어있고, doc에 optional이 붙어있지 않을 때 -> 에러
        if doc_type.symbol != OPTIONAL_SYMBOL and isinstance(source_code_type, GenericType) \
                and source_code_type.symbol == OPTIONAL_SYMBOL:
            print(f"[Parameter Type Error] "
                  f"{'class' if isinstance(doc, ClassObject) else 'overloaded function' if is_overloaded else 'function'}"
                  f" {doc.symbol} "
                  f"parameter {doc_parameter.symbol}:{doc_parameter.value_type} "
                  f"does not same with {source_code_parameter.value_type} in Source code."
                  f": Source code type has Optional, but Doc type doesn't have optional.")
            return
        compare_result = source_code_parameter.value_type.equal(doc_parameter.value_type)
        if compare_result[0] != 'Match':
            # if is_overloaded:
            #     return
            print(f"[Parameter Type {compare_result[0]}] "
                  f"{'class' if isinstance(doc, ClassObject) else 'overloaded function' if is_overloaded else 'function'}"
                  f" {doc.symbol} "
                  f"parameter {doc_parameter.symbol}:{doc_parameter.value_type} "
                  f"does not same with {source_code_parameter.value_type} in Source code."
                  f": {compare_result[1]}")
        pass

    def compare_type(self, doc_type: Type, source_code_type: Type) -> None:
        pass

    def compare_value(self, doc_value: Value, source_code_value: Value) -> None:
        pass

    def compare_symbol(self, doc_symbol: Symbol, source_code_symbol: Symbol) -> None:
        pass
