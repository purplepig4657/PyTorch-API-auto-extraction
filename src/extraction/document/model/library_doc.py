from typing import Tuple
from bs4 import BeautifulSoup, Tag, ResultSet

from src.common.model.class_object import ClassObject
from src.common.model.function import Function
from src.common.model.library import Library
from src.common.model.symbol import Symbol
from src.extraction.document.common.selector_string_builder import SelectorStringBuilder
from src.extraction.document.model.class_object_doc import ClassObjectDoc
from src.extraction.document.model.function_doc import FunctionDoc


class LibraryDoc(Library):

    # PyTorch documentation traits
    __TORCH_CLASS_LITERAL = "py class"
    __TORCH_FUNCTION_LITERAL = "py function"
    __TORCH_OBJECT_LITERAL = "sig-object"

    def __init__(self, library_name: Symbol, library_soup: BeautifulSoup):
        function_name_list, function_tag_list = self.__extract_function_name_list_and_tag_list(library_soup)
        class_name_list, class_tag_list = self.__extract_class_name_list_and_tag_list(library_soup)

        function_list: list[Function] = self.__extract_functions(function_name_list, function_tag_list)
        class_list: list[ClassObject] = self.__extract_classes(class_name_list, class_tag_list)

        super().__init__(library_name, class_list, function_list)

    def __extract_function_name_list_and_tag_list(self, soup: BeautifulSoup) -> Tuple[list[Symbol], list[Tag]]:
        # Warning: This code is highly dependent on the PyTorch documentation HTML structure.
        # No need to delve deeply this code.
        torch_functions: ResultSet[Tag] = soup.select(SelectorStringBuilder(
            class_literal=self.__TORCH_FUNCTION_LITERAL).build()
        )
        name_list: list[Symbol] = list[Symbol]()
        tag_list: list[Tag] = list[Tag]()
        if len(torch_functions) == 0:
            return name_list, tag_list
        for torch_function in torch_functions:
            torch_function_object: Tag = torch_function.find(
                attrs={'class', self.__TORCH_OBJECT_LITERAL}, recursive=False)
            if torch_function_object is None:
                raise RuntimeError("Wrong document")
            torch_function_name: str = torch_function_object.get('id')
            name_list.append(Symbol(torch_function_name))
            tag_list.append(torch_function_object)
        return name_list, torch_functions

    # noinspection PyMethodMayBeStatic
    def __extract_functions(self, function_name_list: list[Symbol], function_tag_list: list[Tag]) -> list[Function]:
        function_list: list[Function] = list[Function]()
        for name, tag in zip(function_name_list, function_tag_list):
            function_list.append(FunctionDoc(name, tag))
        return function_list

    def __extract_class_name_list_and_tag_list(self, soup: BeautifulSoup) -> Tuple[list[Symbol], list[Tag]]:
        # Warning: This code is highly dependent on the PyTorch documentation HTML structure.
        # No need to delve deeply this code.
        torch_classes: ResultSet[Tag] = soup.select(SelectorStringBuilder(
            class_literal=self.__TORCH_CLASS_LITERAL).build()
        )
        name_list: list[Symbol] = list[Symbol]()
        tag_list: list[Tag] = list[Tag]()
        if len(torch_classes) == 0:
            return name_list, tag_list
        for torch_class in torch_classes:
            torch_class_object: Tag = torch_class.find(
                attrs={'class', self.__TORCH_OBJECT_LITERAL}, recursive=False)
            if torch_class_object is None:
                raise RuntimeError("Wrong document")
            torch_class_name: str = torch_class_object.get('id')
            name_list.append(Symbol(torch_class_name))
            tag_list.append(torch_class_object)
        return name_list, torch_classes

    # noinspection PyMethodMayBeStatic
    def __extract_classes(self, class_name_list: list[Symbol], class_tag_list: list[Tag]) -> list[ClassObject]:
        class_list: list[ClassObject] = list[ClassObject]()
        for name, tag in zip(class_name_list, class_tag_list):
            class_list.append(ClassObjectDoc(name, tag))
        return class_list
