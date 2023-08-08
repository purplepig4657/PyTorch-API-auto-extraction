from typing import Tuple
from bs4 import BeautifulSoup, Tag, ResultSet

from src.common.model.class_object import ClassObject
from src.common.model.function import Function
from src.common.model.library import Library
from src.common.model.symbol import Symbol
from src.common.constant.pytorch_doc_constant import PyTorchDocConstant
from src.extraction.document.common.selector_string_builder import SelectorStringBuilder
from src.extraction.document.model.class_object_doc import ClassObjectDoc
from src.extraction.document.model.function_doc import FunctionDoc
from src.extraction.repository.pytorch_html_code_api import PyTorchHtmlCodeApi


class LibraryDoc(Library):
    __pytorch_html_code_api: PyTorchHtmlCodeApi

    __additional_doc_soup: list[BeautifulSoup]

    def __init__(self, pytorch_html_code_api: PyTorchHtmlCodeApi, library_name: Symbol, library_soup: BeautifulSoup):
        self.__pytorch_html_code_api = pytorch_html_code_api
        self.__additional_doc_soup = self.__extract_additional_doc_table(library_soup)
        function_name_list, function_tag_list = self.__extract_function_name_list_and_tag_list(library_soup)
        class_name_list, class_tag_list = self.__extract_class_name_list_and_tag_list(library_soup)

        function_list: list[Function] = self.__extract_functions(function_name_list, function_tag_list)
        class_list: list[ClassObject] = self.__extract_classes(class_name_list, class_tag_list)

        super().__init__(library_name, class_list, function_list)

    # noinspection PyMethodMayBeStatic
    def __extract_additional_doc_table(self, soup: BeautifulSoup) -> list[BeautifulSoup]:
        # Warning: This code is highly dependent on the PyTorch documentation HTML structure.
        # No need to delve deeply this code.
        doc_tables: ResultSet[Tag] = soup.select(
            SelectorStringBuilder(class_literal=PyTorchDocConstant.TORCH_DOC_TABLE_LITERAL).build()
        )
        all_links_in_doc_tables: list[str] = list[str]()

        for doc_table in doc_tables:
            tr_tags: ResultSet[Tag] = doc_table.find_all(name="tr")
            for tr_tag in tr_tags:
                td_tag: Tag = tr_tag.find(name="td", recursive=False)
                if td_tag is None:
                    continue

                a_tags: ResultSet[Tag] = td_tag.find_all(name="a")
                if len(a_tags) == 0:
                    # raise RuntimeError("There is no link", doc_table.text)
                    # There is several cases that table having functions and classes don't have 'a' tag (link).
                    continue

                for a_tag in a_tags:
                    all_links_in_doc_tables.append(PyTorchDocConstant.ROOT_URL + a_tag.get("href"))

        return list(map(self.__url_to_soup, all_links_in_doc_tables))

    # noinspection PyMethodMayBeStatic
    def __extract_doc_table_function_tag_list(self, soup_list: list[BeautifulSoup]) -> list[Tag]:
        # Warning: This code is highly dependent on the PyTorch documentation HTML structure.
        # No need to delve deeply this code.
        torch_function_list: list[Tag] = list[Tag]()
        for soup in soup_list:
            torch_functions: ResultSet[Tag] = soup.select(
                SelectorStringBuilder(class_literal=PyTorchDocConstant.TORCH_FUNCTION_LITERAL).build()
            )
            torch_function_list.extend(torch_functions)
        return torch_function_list

    # noinspection PyMethodMayBeStatic
    def __extract_doc_table_class_tag_list(self, soup_list: list[BeautifulSoup]) -> list[Tag]:
        # Warning: This code is highly dependent on the PyTorch documentation HTML structure.
        # No need to delve deeply this code.
        torch_class_list: list[Tag] = list[Tag]()
        for soup in soup_list:
            torch_classes: ResultSet[Tag] = soup.select(
                SelectorStringBuilder(class_literal=PyTorchDocConstant.TORCH_CLASS_LITERAL).build()
            )
            torch_class_list.extend(torch_classes)
        return torch_class_list

    # noinspection PyMethodMayBeStatic
    def __extract_function_name_list_and_tag_list(self, soup: BeautifulSoup) -> Tuple[list[Symbol], list[Tag]]:
        # Warning: This code is highly dependent on the PyTorch documentation HTML structure.
        # No need to delve deeply this code.
        torch_functions: ResultSet[Tag] = soup.select(
            SelectorStringBuilder(class_literal=PyTorchDocConstant.TORCH_FUNCTION_LITERAL).build()
        )
        torch_functions.extend(self.__extract_doc_table_function_tag_list(self.__additional_doc_soup))
        name_list: list[Symbol] = list[Symbol]()
        tag_list: list[Tag] = list[Tag]()
        if len(torch_functions) == 0:
            return name_list, tag_list
        for torch_function in torch_functions:
            torch_function_object: Tag = torch_function.find(
                attrs={'class', PyTorchDocConstant.TORCH_OBJECT_LITERAL},
                recursive=False
            )
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

    # noinspection PyMethodMayBeStatic
    def __extract_class_name_list_and_tag_list(self, soup: BeautifulSoup) -> Tuple[list[Symbol], list[Tag]]:
        # Warning: This code is highly dependent on the PyTorch documentation HTML structure.
        # No need to delve deeply this code.
        torch_classes: ResultSet[Tag] = soup.select(
            SelectorStringBuilder(class_literal=PyTorchDocConstant.TORCH_CLASS_LITERAL).build()
        )
        torch_classes.extend(self.__extract_doc_table_class_tag_list(self.__additional_doc_soup))
        name_list: list[Symbol] = list[Symbol]()
        tag_list: list[Tag] = list[Tag]()
        if len(torch_classes) == 0:
            return name_list, tag_list
        for torch_class in torch_classes:
            torch_class_object: Tag = torch_class.find(
                attrs={'class', PyTorchDocConstant.TORCH_OBJECT_LITERAL},
                recursive=False
            )
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

    # noinspection PyMethodMayBeStatic
    def __url_to_soup(self, url: str) -> BeautifulSoup:
        html_code: str = self.__pytorch_html_code_api.get_html_code_by_url(url)
        return BeautifulSoup(html_code, 'html.parser')
