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
from src.common.classified_result import classified_result


class Compare:

    def __init__(self, result_dict: dict):
        self.__pytorch_html_code_api: PyTorchHtmlCodeApi = PyTorchHtmlCodeApiImpl()
        self.__pytorch_source_code_repository: PyTorchSourceCodeRepository = PyTorchSourceCodeRepositoryImpl()
        root_tree: FileTree = self.__pytorch_source_code_repository.get_source_code_tree()

        self.__doc_result: ResultDoc = ResultDoc(pytorch_html_code_api=self.__pytorch_html_code_api)
        self.__source_code_result: ResultSourceCode = ResultSourceCode(root_tree=root_tree)
        self.__result = classified_result
        self.__print_with_type = False
        self.__type_compare_count = 0

    @property
    def source_code_result(self):
        return self.__source_code_result

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

    def compare(self) -> dict:
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
                # print(f"[Search Error] class {doc_class.symbol} does not exist in Source code.")
                self.__result["error"]["exist"]["class_not_exist"].append(doc_class.symbol.name)
                continue
            if not isinstance(source_code_class, ClassObject):
                # print(f"[Search Error] class {doc_class.symbol} is not a class. {type(source_code_class)}")
                self.__result["error"]["exist"]["class_not_exist"].append(doc_class.symbol.name)
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

        self.__result["error"]["exist"]["class_not_exist"] = \
            sorted(list(set(self.__result["error"]["exist"]["class_not_exist"])))
        print(f"error_exist_class_not_exist: {len(self.__result['error']['exist']['class_not_exist'])}")

        self.__result["error"]["exist"]["function_not_exist"] = \
            sorted(list(set(self.__result["error"]["exist"]["function_not_exist"])))
        print(f"error_exist_function_not_exist: {len(self.__result['error']['exist']['function_not_exist'])}")

        self.__result["error"]["exist"]["parameter_not_exist"] = \
            sorted(list(set(self.__result["error"]["exist"]["parameter_not_exist"])))
        print(f"error_exist_parameter_not_exist: {len(self.__result['error']['exist']['parameter_not_exist'])}")

        self.__result["error"]["type"]["return_not_matched"] = \
            sorted(list(set(self.__result["error"]["type"]["return_not_matched"])))
        print(f"error_type_return_not_matched: {len(self.__result['error']['type']['return_not_matched'])}")

        self.__result["error"]["type"]["parameter_not_matched"] = \
            sorted(list(set(self.__result["error"]["type"]["parameter_not_matched"])))
        print(f"error_type_parameter_not_matched: {len(self.__result['error']['type']['parameter_not_matched'])}")

        self.__result["error"]["type"]["optional_wrong_used"] = \
            sorted(list(set(self.__result["error"]["type"]["optional_wrong_used"])))
        print(f"error_type_optional_wrong_used: {len(self.__result['error']['type']['optional_wrong_used'])}")

        self.__result["error"]["value"]["not_matched"] = sorted(list(set(self.__result["error"]["value"]["not_matched"])))
        print(f"error_value_not_matched: {len(self.__result['error']['value']['not_matched'])}")

        self.__result["warning"]["break_format"]["letter_case"] = \
            sorted(list(set(self.__result["warning"]["break_format"]["letter_case"])))
        print(f"warning_break_format_letter_case: {len(self.__result['warning']['break_format']['letter_case'])}")

        self.__result["warning"]["break_format"]["builtin_type"] = \
            sorted(list(set(self.__result["warning"]["break_format"]["builtin_type"])))
        print(f"warning_break_format_builtin_type: {len(self.__result['warning']['break_format']['builtin_type'])}")

        self.__result["warning"]["break_format"]["plural"] = \
            sorted(list(set(self.__result["warning"]["break_format"]["plural"])))
        print(f"warning_break_format_plural: {len(self.__result['warning']['break_format']['plural'])}")

        self.__result["warning"]["break_format"]["unknown_delimiter"] = \
            sorted(list(set(self.__result["warning"]["break_format"]["unknown_delimiter"])))
        print(f"warning_break_format_unknown_delimiter: {len(self.__result['warning']['break_format']['unknown_delimiter'])}")

        # self.__result["warning"]["break_format"]["unknown_non_type_word"] = \
        #     sorted(list(set(self.__result["warning"]["break_format"]["unknown_non_type_word"])))
        # print(f"warning_break_format_unknown_non_type_word: {len(self.__result['warning']['break_format']['unknown_non_type_word'])}")

        self.__result["warning"]["type"]["doc_parameter_generic_type_is_not_specified"] = \
            sorted(list(set(self.__result["warning"]["type"]["doc_parameter_generic_type_is_not_specified"])))
        print(f"warning_type_doc_parameter_generic_type_is_not_specified: {len(self.__result['warning']['type']['doc_parameter_generic_type_is_not_specified'])}")

        self.__result["warning"]["type"]["src_parameter_generic_type_is_not_specified"] = \
            sorted(list(set(self.__result["warning"]["type"]["src_parameter_generic_type_is_not_specified"])))
        print(f"warning_type_src_parameter_generic_type_is_not_specified: {len(self.__result['warning']['type']['src_parameter_generic_type_is_not_specified'])}")
 
        self.__result["warning"]["type"]["doc_return_generic_type_is_not_specified"] = \
            sorted(list(set(self.__result["warning"]["type"]["doc_return_generic_type_is_not_specified"])))
        print(f"warning_type_doc_return_generic_type_is_not_specified: {len(self.__result['warning']['type']['doc_return_generic_type_is_not_specified'])}")

        self.__result["warning"]["type"]["src_return_generic_type_is_not_specified"] = \
            sorted(list(set(self.__result["warning"]["type"]["src_return_generic_type_is_not_specified"])))
        print(f"warning_type_src_return_generic_type_is_not_specified: {len(self.__result['warning']['type']['src_return_generic_type_is_not_specified'])}")

        self.__result["warning"]["type"]["doc_undescribed_parameter_type"] = \
            sorted(list(set(self.__result["warning"]["type"]["doc_undescribed_parameter_type"])))
        print(f"warning_type_doc_undescribed_parameter_type: {len(self.__result['warning']['type']['doc_undescribed_parameter_type'])}")

        self.__result["warning"]["type"]["src_undescribed_parameter_type"] = \
            sorted(list(set(self.__result["warning"]["type"]["src_undescribed_parameter_type"])))
        print(f"warning_type_src_undescribed_parameter_type: {len(self.__result['warning']['type']['src_undescribed_parameter_type'])}")

        self.__result["warning"]["type"]["doc_undescribed_return_type"] = \
            sorted(list(set(self.__result["warning"]["type"]["doc_undescribed_return_type"])))
        print(f"warning_type_doc_undescribed_return_type: {len(self.__result['warning']['type']['doc_undescribed_return_type'])}")

        self.__result["warning"]["type"]["src_undescribed_return_type"] = \
            sorted(list(set(self.__result["warning"]["type"]["src_undescribed_return_type"])))
        print(f"warning_type_src_undescribed_return_type: {len(self.__result['warning']['type']['src_undescribed_return_type'])}")

        self.__result["warning"]["value"]["doc_undescribed_default"] = \
            sorted(list(set(self.__result["warning"]["value"]["doc_undescribed_parameter_default"])))
        print(f"warning_value_doc_undescribed_defualt: {len(self.__result['warning']['value']['doc_undescribed_parameter_default'])}")

        self.__result["warning"]["value"]["src_undescribed_default"] = \
            sorted(list(set(self.__result["warning"]["value"]["src_undescribed_parameter_default"])))
        print(f"warning_value_src_undescribed_defualt: {len(self.__result['warning']['value']['src_undescribed_parameter_default'])}")

        print(self.__type_compare_count)

        return self.__result

    def search_function(self, doc_function_symbol: Symbol) -> Optional[list[Function]]:
        source_code_function_list: Optional[list[Function]] = self.__source_code_result.search(doc_function_symbol)
        if source_code_function_list is None:
            # print(f"[Search Error] class {doc_class_symbol} method "
            #       f"{doc_method_symbol} does not exist in Source code.")
            self.__result["error"]["exist"]["function_not_exist"].append(f"{doc_function_symbol}")
            return None
        if not isinstance(source_code_function_list, list):
            # print(f"[Search Error] method {doc_method_symbol} is not a method. {type(source_code_function_list)}")
            self.__result["error"]["exist"]["function_not_exist"].append(f"{doc_function_symbol}")
            return None
        all_function_assert = [True] * len(source_code_function_list)
        for idx in range(len(source_code_function_list)):
            if not isinstance(source_code_function_list[idx], Function):
                # print(f"[Search Error] method {doc_method_symbol} is not a method. {type(function)}")
                self.__result["error"]["exist"]["function_not_exist"].append(f"{doc_function_symbol}")
                all_function_assert[idx] = False
        result = list()
        for idx in range(len(source_code_function_list)):
            if all_function_assert[idx]:
                result.append(source_code_function_list[idx])
        return result

    def search_method(self, doc_class_symbol: Symbol, doc_method_symbol: Symbol) -> Optional[list[Function]]:
        source_code_function_list: Optional[list[Function]] = self.__source_code_result.search(doc_method_symbol)
        if source_code_function_list is None:
            # print(f"[Search Error] class {doc_class_symbol} method "
            #       f"{doc_method_symbol} does not exist in Source code.")
            self.__result["error"]["exist"]["function_not_exist"].append(f"{doc_class_symbol}:{doc_method_symbol}")
            return None
        if not isinstance(source_code_function_list, list):
            # print(f"[Search Error] method {doc_method_symbol} is not a method. {type(source_code_function_list)}")
            self.__result["error"]["exist"]["function_not_exist"].append(f"{doc_class_symbol}:{doc_method_symbol}")
            return None
        all_function_assert = [True] * len(source_code_function_list)
        for idx in range(len(source_code_function_list)):
            if not isinstance(source_code_function_list[idx], Function):
                # print(f"[Search Error] method {doc_method_symbol} is not a method. {type(function)}")
                self.__result["error"]["exist"]["function_not_exist"].append(f"{doc_class_symbol}:{doc_method_symbol}")
                all_function_assert[idx] = False
        result = list()
        for idx in range(len(source_code_function_list)):
            if all_function_assert[idx]:
                result.append(source_code_function_list[idx])
        return result

    def compare_class(self, doc_class: ClassObject, source_code_class: ClassObject) -> None:
        # for source_code_parameter in source_code_class.param_list:  # Source code에 있는 파라미터가 정확한 파라미터라고 가정.
        #     if source_code_parameter.symbol.name == 'self':  # filtering method self.
        #         continue
        #     searched_doc_parameter: Optional[Parameter] = None
        #     for doc_parameter in doc_class.param_list:
        #         if doc_parameter.symbol == source_code_parameter.symbol:
        #             self.compare_parameter(doc_class, doc_parameter, source_code_parameter, False)
        #             searched_doc_parameter = doc_parameter
        #             break
        #     if searched_doc_parameter is None:
        #         print(f"[Parameter Exist Error] class {doc_class.symbol} parameter "
        #               f"{source_code_parameter.symbol} does not exist in Document.")
        #         self.__result["error"]["exist"]["parameter_not_exist"]\
        #             .append(f"{doc_class.symbol}:{source_code_parameter.symbol}")
        #     else:
        #         pass
        for doc_method in doc_class.method_list:
            source_code_function_list: Optional[list[Function]] = self.search_method(doc_class.symbol, doc_method.symbol)
            if source_code_function_list is None:
                continue
            self.compare_method(doc_method, source_code_function_list)

    def compare_function(self, doc_function: Function, source_code_function_list: list[Function]) -> None:
        if len(source_code_function_list) > 1:
            return
            # # overloaded functions
            # is_parameter_exist_ok = False
            # right_source_code_function: Optional[Function] = None
            # for source_code_function in source_code_function_list:
            #     is_all_parameter_ok = True
            #     for source_code_parameter in source_code_function.param_list:
            #         is_parameter_exist = False
            #         for doc_parameter in doc_function.param_list:
            #             if doc_parameter.symbol == source_code_parameter.symbol:
            #                 is_parameter_exist = True
            #                 break
            #         is_all_parameter_ok = is_all_parameter_ok and is_parameter_exist  # 전부 다 참이어야 함
            #     if is_all_parameter_ok:
            #         right_source_code_function = source_code_function
            #     is_parameter_exist_ok = is_parameter_exist_ok or is_all_parameter_ok  # 하나만 참이어도 됨
            # if not is_parameter_exist_ok:
            #     print(f"[Parameter Exist Error] overloaded function {doc_function.symbol} has something wrong.")
            # else:
            #     for source_code_parameter in right_source_code_function.param_list:
            #         for doc_parameter in doc_function.param_list:
            #             if doc_parameter.symbol == source_code_parameter.symbol:
            #                 self.compare_parameter(doc_function, doc_parameter, source_code_parameter, True)
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
                    # print(f"[Parameter Exist Error] function {doc_function.symbol} parameter "
                    #       f"{source_code_parameter.symbol} does not exist in Document.")
                    self.__result["error"]["exist"]["parameter_not_exist"] \
                        .append(f"{doc_function.symbol}:{source_code_parameter.symbol}")
                else:
                    pass
            doc_type = doc_function.return_type
            source_code_type = source_code_function_list[0].return_type

            if source_code_type == Type.none_type() and doc_type != Type.none_type():
                self.__result["warning"]["type"]["src_undescribed_return_type"].append(f"{doc_function.symbol}")
                return

            if doc_type == Type.none_type() and source_code_type != Type.none_type():
                self.__result["warning"]["type"]["doc_undescribed_return_type"].append(f"{doc_function.symbol}")
                return

            compare_result = self.compare_type(doc_function, doc_type, source_code_type)
            # if compare_result[0] != 'Match':
            #     # if is_overloaded:
            #     #     return
            if compare_result[0] == 'Error':
                if self.__print_with_type:
                    self.__result["error"]["type"]["return_not_matched"].append(f"{doc_function.symbol}:{source_code_type}-{doc_type}")
                else:
                    self.__result["error"]["type"]["return_not_matched"].append(f"{doc_function.symbol}")
            elif compare_result[0] == 'Warning':
                error_msg = compare_result[1]
                doc_or_src = "doc" if error_msg.split(" ")[0] == "Doc" else "src"
                if self.__print_with_type:
                    self.__result["warning"]["type"][f"{doc_or_src}_return_generic_type_is_not_specified"].append(f"{doc_function.symbol}:{source_code_type}-{doc_type}")
                else:
                    self.__result["warning"]["type"][f"{doc_or_src}_return_generic_type_is_not_specified"].append(f"{doc_function.symbol}")
            else:
                # if self.__print_with_type:
                #     self.__result["warning"]["type"]["return_not_matched"].append(f"{doc_function.symbol}:{source_code_type}-{doc_type}")
                # else:
                #     self.__result["warning"]["type"]["return_not_matched"].append(f"{doc_function.symbol}")
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
                # print(f"[Parameter Exist Error] method {doc_method.symbol} parameter "
                #       f"{source_code_parameter.symbol} does not exist in Document.")
                self.__result["error"]["exist"]["parameter_not_exist"] \
                    .append(f"{doc_method.symbol}:{source_code_parameter.symbol}")
        doc_type = doc_method.return_type
        source_code_type = source_code_method_list[0].return_type
        compare_result = self.compare_type(doc_method, doc_type, source_code_type)

        if source_code_type == Type.none_type() and doc_type != Type.none_type():
            self.__result["warning"]["type"]["src_undescribed_return_type"].append(f"{doc_method.symbol}")
            return

        if doc_type == Type.none_type() and source_code_type != Type.none_type():
            self.__result["warning"]["type"]["doc_undescribed_return_type"].append(f"{doc_method.symbol}")
            return

        # if compare_result[0] != 'Match':
        #     # if is_overloaded:
        #     #     return
        if compare_result[0] == 'Error':
            if self.__print_with_type:
                self.__result["error"]["type"]["return_not_matched"].append(f"{doc_method.symbol}:{source_code_type}-{doc_type}")
            else:
                self.__result["error"]["type"]["return_not_matched"].append(f"{doc_method.symbol}")
        elif compare_result[0] == 'Warning':
            error_msg = compare_result[1]
            doc_or_src = "doc" if error_msg.split(" ")[0] == "Doc" else "src"
            if self.__print_with_type:
                self.__result["warning"]["type"][f"{doc_or_src}_return_generic_type_is_not_specified"].append(f"{doc_method.symbol}:{source_code_type}-{doc_type}")
            else:
                self.__result["warning"]["type"][f"{doc_or_src}_return_generic_type_is_not_specified"].append(f"{doc_method.symbol}")
        else:
            # if self.__print_with_type:
            #     self.__result["warning"]["type"]["return_not_matched"].append(f"{doc_method.symbol}:{source_code_type}-{doc_type}")
            # else:
            #     self.__result["warning"]["type"]["return_not_matched"].append(f"{doc_method.symbol}")
            pass

    def compare_parameter(
            self,
            doc: Union[ClassObject, Function],
            doc_parameter: Parameter,
            source_code_parameter: Parameter,
            is_overloaded: bool
    ) -> None:
        """
        1. optional 유무 비교 규칙
            1. 만약 document type에 optional이 붙어있고, source code type에 optional이 붙어있지 않을 때
                1. 만약 document type에 optional을 떼고 source code type과 비교했을 때 타입이 다르다면 -> Error
                2. 만약 document type에 optional을 떼고 source code type과 비교했을 때 타입이 같고, document에 default value가 명시되어 있다면 -> Pass
                3. 만약 document type에 optional을 떼고 source code type과 비교했을 때 타입이 같고, document에 default value가 명시되어 있지 않다면 -> Error
            2. 만약 source code type에 optional이 붙어있고, document type에 optional이 붙어있지 않을 때 -> Error
        """
        if source_code_parameter.default == Value.none_value() and doc_parameter.default != Value.none_value():
            self.__result["warning"]["value"]["src_undescribed_parameter_default"].append(f"{doc.symbol}:{doc_parameter.symbol}")
        elif doc_parameter.default == Value.none_value() and source_code_parameter.default != Value.none_value():
            # print(f"[Parameter Type Warning] {'class' if isinstance(doc, ClassObject) else 'function'} {doc.symbol}"
            #       f" parameter {doc_parameter.symbol}:{doc_parameter.value_type} Document Type is not described.")
            self.__result["warning"]["value"]["doc_undescribed_parameter_default"].append(f"{doc.symbol}:{doc_parameter.symbol}")
        else:
            self.compare_value(doc, doc_parameter, doc_parameter.default, source_code_parameter.default)

        if source_code_parameter.value_type == Type.none_type() and doc_parameter.value_type != Type.none_type():
            self.__result["warning"]["type"]["src_undescribed_parameter_type"].append(f"{doc.symbol}:{doc_parameter.symbol}")
            return

        if doc_parameter.value_type == Type.none_type() and source_code_parameter.value_type != Type.none_type():
            # print(f"[Parameter Type Warning] {'class' if isinstance(doc, ClassObject) else 'function'} {doc.symbol}"
            #       f" parameter {doc_parameter.symbol}:{doc_parameter.value_type} Document Type is not described.")
            self.__result["warning"]["type"]["doc_undescribed_parameter_type"].append(f"{doc.symbol}:{doc_parameter.symbol}")
            return

        doc_type = doc_parameter.value_type
        source_code_type = source_code_parameter.value_type

        """
        # Optional 처리
        OPTIONAL_SYMBOL = Symbol("Optional")
        # 만약 doc에 optional이 붙어있고, 코드에 optional 이 붙어있지 않을 때
        if isinstance(doc_type, GenericType) and doc_type.symbol == OPTIONAL_SYMBOL \
                and source_code_type.symbol != OPTIONAL_SYMBOL:
            # doc에 optional을 떼고 코드와 비교했을 때 타입이 다르면 -> 에러
            compare_result = self.compare_type(doc, source_code_type, doc_type.generic_list[0])
            if compare_result[0] == 'Error':
                # print(f"[Parameter Type {compare_result[0]}] "
                #       f"{'class' if isinstance(doc, ClassObject) else 'overloaded function' if is_overloaded else 'function'}"
                #       f" {doc.symbol} "
                #       f"parameter {doc_parameter.symbol}:{doc_parameter.value_type} "
                #       f"does not same with {source_code_parameter.value_type} in Source code."
                #       f": {compare_result[1]}, type mismatch error without optional.")
                if self.__print_with_type:
                    self.__result["error"]["type"]["parameter_not_matched"].append(f"{doc.symbol}:{doc_parameter.symbol}:{source_code_type}-{doc_type}-{doc_parameter.default}")
                else:
                    self.__result["error"]["type"]["parameter_not_matched"].append(f"{doc.symbol}:{doc_parameter.symbol}")
                return
            elif compare_result[0] == 'Warning':
                if self.__print_with_type:
                    self.__result["warning"]["type"]["parameter_generic_type_is_not_specified"].append(f"{doc.symbol}:{source_code_type}-{doc_type}")
                else:
                    self.__result["warning"]["type"]["parameter_generic_type_is_not_specified"].append(f"{doc.symbol}:{doc_parameter.symbol}")
            elif compare_result[0] == 'Match':
                return
            # doc에 default value가 명시되어 있지 않다면 -> 에러
            if doc_parameter.default == Value.none_value():
                # print(f"[Parameter Type Error] "
                #       f"{'class' if isinstance(doc, ClassObject) else 'overloaded function' if is_overloaded else 'function'}"
                #       f" {doc.symbol} "
                #       f"parameter {doc_parameter.symbol}:{doc_parameter.value_type} "
                #       f"does not same with {source_code_parameter.value_type} in Source code."
                #       f": Doc type has optional, but there is no default value.")
                if self.__print_with_type:
                    self.__result["error"]["type"]["optional"]["on_parameter"].append(f"{doc.symbol}:{doc_parameter.symbol}:{source_code_type}-{doc_type}")
                else:
                    self.__result["error"]["type"]["optional"]["on_parameter"].append(f"{doc.symbol}:{doc_parameter.symbol}")
                return

        # 만약 코드에 Optional이 붙어있고, doc에 optional이 붙어있지 않을 때 -> 에러
        if doc_type.symbol != OPTIONAL_SYMBOL and isinstance(source_code_type, GenericType) \
                and source_code_type.symbol == OPTIONAL_SYMBOL:
            # print(f"[Parameter Type Error] "
            #       f"{'class' if isinstance(doc, ClassObject) else 'overloaded function' if is_overloaded else 'function'}"
            #       f" {doc.symbol} "
            #       f"parameter {doc_parameter.symbol}:{doc_parameter.value_type} "
            #       f"does not same with {source_code_parameter.value_type} in Source code."
            #       f": Source code type has Optional, but Doc type doesn't have optional.")
            if self.__print_with_type:
                self.__result["error"]["type"]["optional"]["on_parameter"].append(f"{doc.symbol}:{doc_parameter.symbol}:{source_code_type}-{doc_type}")
            else:
                self.__result["error"]["type"]["optional"]["on_parameter"].append(f"{doc.symbol}:{doc_parameter.symbol}")
            return
        """

        if isinstance(doc_type, GenericType) and doc_type.symbol == Symbol("DocumentOptional"):
            if doc_parameter.default == Value.none_value() or source_code_parameter.default == Value.none_value():
                self.__result["error"]["type"]["optional_wrong_used"].append(f"{doc.symbol}:{doc_parameter.symbol}")
            doc_type = doc_type.generic_list[0]  # Remove DocumentOptional to compare with source code type

        # Common case, not optional

        compare_result = self.compare_type(doc, doc_type, source_code_type)

        if compare_result[0] != 'Match':
            # if is_overloaded:
            #     return
            # print(f"[Parameter Type {compare_result[0]}] "
            #       f"{'class' if isinstance(doc, ClassObject) else 'overloaded function' if is_overloaded else 'function'}"
            #       f" {doc.symbol} "
            #       f"parameter {doc_parameter.symbol}:{doc_parameter.value_type} "
            #       f"does not same with {source_code_parameter.value_type} in Source code."
            #       f": {compare_result[1]}")
            if compare_result[0] == 'Error':
                if self.__print_with_type:
                    self.__result["error"]["type"]["parameter_not_matched"].append(f"{doc.symbol}:{doc_parameter.symbol}:{source_code_type}-{doc_type}")
                else:
                    self.__result["error"]["type"]["parameter_not_matched"].append(f"{doc.symbol}:{doc_parameter.symbol}")
            elif compare_result[0] == 'Warning':
                error_msg = compare_result[1]
                print(error_msg.split(" ")[0])
                doc_or_src = "doc" if error_msg.split(" ")[0] == "Doc" else "src"
                if self.__print_with_type:
                    self.__result["warning"]["type"][f"{doc_or_src}_parameter_generic_type_is_not_specified"].append(f"{doc.symbol}:{source_code_type}-{doc_type}")
                else:
                    self.__result["warning"]["type"][f"{doc_or_src}_parameter_generic_type_is_not_specified"].append(f"{doc.symbol}:{doc_parameter.symbol}")
            else:
                # if self.__print_with_type:
                #     self.__result["warning"]["type"]["parameter_not_matched"].append(f"{doc.symbol}:{doc_parameter.symbol}:{source_code_type}-{doc_type}")
                # else:
                #     self.__result["warning"]["type"]["parameter_not_matched"].append(f"{doc.symbol}:{doc_parameter.symbol}")
                pass


    def flatten_nested_union(self, target_type: GenericType) -> list[Type]:
        UNION_SYMBOL = Symbol("Union")
        if target_type.symbol != UNION_SYMBOL:
            raise "It is not union type."

        union_types: list[Type] = list()

        for t in target_type.generic_list:
            if t.symbol == UNION_SYMBOL and isinstance(t, GenericType):
                union_types.extend(self.flatten_nested_union(t))
                continue
            union_types.append(t)

        return union_types

    def compare_type(
            self,
            doc: Union[ClassObject, Function],
            doc_type: Optional[Type],
            source_code_type: Optional[Type]
    ) -> tuple[str, str]:
        """
        1. Union
            1. 만약 document type과 source code type에 Union이 붙어있을 때
                1. Nested Union이 있다면 모두 꺼내고, Union 안에 있는 타입은 순서에 상관없이 존재한다면 -> Pass
                2. Union 안에 비교하는 타입이 없다면 -> Error
        2. Type symbol이 다르다면 -> Error
        :return: (Error type, Message)
        """
        self.__type_compare_count += 1

        UNION_SYMBOL = Symbol("Union")
        # OPTIONAL_SYMBOL = Symbol("Optional")

        if not isinstance(doc_type, Type) or not isinstance(source_code_type, Type):
            return "Error", "doc_type or source_code_type is not a Type instance"

        # 만약 document type과 source code type에 Union이 붙어있을 때
        if (isinstance(doc_type, GenericType) and isinstance(source_code_type, GenericType) and
                doc_type.symbol == UNION_SYMBOL and source_code_type.symbol == UNION_SYMBOL):
            doc_type_union_list = self.flatten_nested_union(doc_type)
            source_code_type_union_list = self.flatten_nested_union(source_code_type)

            if len(doc_type_union_list) != len(source_code_type_union_list):
                return "Error", "Generic type count is not matched"

            # source code type = Union[int, int]
            # doc type = Union[int, str]
            # 일 때 제대로 동작하지 않음 -> 고쳐 -> 해결
            # 그리고 Generic list 안의 type에 대하여 warning 이어도 error로 처리하는 중 -> 고쳐

            # print(doc.symbol.name)
            # for t in doc_type_union_list:
            #     print(t, end=', ')
            # print()
            # for t in source_code_type_union_list:
            #     print(t, end=', ')
            # print()

            matched_count = 0
            max_error = 0
            for doc_union_type in doc_type_union_list:
                min_error = 2  # 0: Match, 1: Warning, 2: Error
                for source_union_type in source_code_type_union_list:
                    compare_result = self.compare_type(doc, doc_union_type, source_union_type)
                    if compare_result[0] == 'Error':
                        min_error = min(min_error, 2)
                    if compare_result[0] != 'Error':
                        if compare_result[0] == 'Warning':
                            min_error = min(min_error, 1)
                        else:
                            min_error = min(min_error, 0)
                    # if min_error:
                    #     break
                max_erorr = max(max_error, min_error)
                if min_error < 2:  # if there is matched or warning type exist.
                    matched_count += 1

            if matched_count != len(source_code_type_union_list):
                print(f"doc_type: {doc.symbol.name}, source_code_type: {doc.symbol.name}: union error")
                return "Error", "Some union type is not matched"

            if max_erorr == 1:
                return "Warning", "Doc"  # 임시 msg

            return "Match", ""

        if isinstance(source_code_type, GenericType):
            if not isinstance(doc_type, GenericType):
                if source_code_type.symbol == doc_type.symbol:
                    return "Warning", "Doc generic type is not specified"
                else:
                    return "Error", "Type in generic list symbol is not matched"
            else:
                if source_code_type.symbol != doc_type.symbol:
                    return "Error", "Type symbol is not matched"
                for source_code_t, doc_t in zip(source_code_type.generic_list, doc_type.generic_list):
                    compare_result = self.compare_type(doc, doc_t, source_code_t)
                    if compare_result[0] != 'Match':
                        return compare_result

            return "Match", ""

        if isinstance(doc_type, GenericType) and not isinstance(source_code_type, GenericType):
            if source_code_type.symbol == doc_type.symbol:
                return "Warning", "Source code generic type is not specified"
            else:
                return "Error", "Type in generic list symbol is not matched"

        if doc_type.symbol != source_code_type.symbol:
            return "Error", "Type symbol is not matched"

        return "Match", ""

    def compare_value(self, doc: Union[ClassObject, Function],
            doc_parameter: Parameter, doc_value: Value, source_code_value: Value) -> None:

        if str(doc_value) != str(source_code_value):
            if self.__print_with_type:
                self.__result["error"]["value"]["not_matched"].append(f"{doc.symbol}:{doc_parameter.symbol}:{doc_value}-{source_code_value}")
            else:
                self.__result["error"]["value"]["not_matched"].append(f"{doc.symbol}:{doc_parameter.symbol}")
        pass

    # def compare_symbol(self, doc_symbol: Symbol, source_code_symbol: Symbol) -> None:
    #     pass

# TODO: Remove duplicated class mapping
# TODO: Write default value error, warning rules, Write type warning rule, Write format warning rules.
