from typing import Optional, Tuple
from bs4 import BeautifulSoup, Tag, ResultSet

from src.common.model.class_object import ClassObject
from src.common.model.function import Function
from src.common.model.document.library import Library
from src.common.model.symbol import Symbol
from src.common.constant.pytorch_doc_constant import PyTorchDocConstant
from src.extraction.document.common.doc_url_utils import DocUrlUtils
from src.extraction.document.model.class_object_doc import ClassObjectDoc
from src.extraction.document.model.function_doc import FunctionDoc
from src.extraction.repository.pytorch_html_code_api import PyTorchHtmlCodeApi


class LibraryDoc(Library):
    __pytorch_html_code_api: PyTorchHtmlCodeApi

    def __init__(self, pytorch_html_code_api: PyTorchHtmlCodeApi, library_name: Symbol, library_soup: BeautifulSoup):
        self.__pytorch_html_code_api = pytorch_html_code_api
        related_soup_list = self.__extract_related_doc_soup_list(library_soup)
        function_name_list, function_tag_list = self.__extract_function_name_list_and_tag_list(related_soup_list)
        class_name_list, class_tag_list = self.__extract_class_name_list_and_tag_list(related_soup_list)

        function_list: list[Function] = self.__extract_functions(function_name_list, function_tag_list)
        class_list: list[ClassObject] = self.__extract_classes(class_name_list, class_tag_list)

        super().__init__(library_name, class_list, function_list)

    def __extract_related_doc_soup_list(self, library_soup: BeautifulSoup) -> list[BeautifulSoup]:
        related_soup_list: list[BeautifulSoup] = [library_soup]
        visited_url_set: set[str] = set()
        queued_url_list: list[str] = []

        base_url = self.__extract_canonical_url(library_soup)
        if base_url is None:
            return related_soup_list

        visited_url_set.add(base_url)
        queued_url_list.extend(DocUrlUtils.extract_page_definition_links(base_url, library_soup))

        while queued_url_list:
            current_url = queued_url_list.pop(0)
            if current_url in visited_url_set:
                continue

            visited_url_set.add(current_url)
            current_soup = self.__url_to_soup(current_url)
            related_soup_list.append(current_soup)

            discovered_url_list = DocUrlUtils.extract_page_definition_links(current_url, current_soup)

            for discovered_url in discovered_url_list:
                if discovered_url in visited_url_set or discovered_url in queued_url_list:
                    continue
                queued_url_list.append(discovered_url)

        return related_soup_list

    def __extract_function_name_list_and_tag_list(self, soup_list: list[BeautifulSoup]) -> Tuple[list[Symbol], list[Tag]]:
        name_list: list[Symbol] = []
        tag_list: list[Tag] = []
        seen_name_set: set[str] = set()
        for soup in soup_list:
            torch_functions: ResultSet[Tag] = soup.select(f".{PyTorchDocConstant.TORCH_FUNCTION_LITERAL.replace(' ', '.')}")
            torch_methods: ResultSet[Tag] = soup.select(f".{PyTorchDocConstant.TORCH_METHOD_LITERAL.replace(' ', '.')}")
            for torch_function in list(torch_functions) + list(torch_methods):
                torch_function_object: Tag = self.__extract_definition_object(torch_function)
                if torch_function_object is None:
                    continue
                torch_function_name: str = torch_function_object.get("id")
                if torch_function_name is None or torch_function_name in seen_name_set:
                    continue
                seen_name_set.add(torch_function_name)
                name_list.append(Symbol(torch_function_name))
                tag_list.append(torch_function)
        return name_list, tag_list

    def __extract_functions(self, function_name_list: list[Symbol], function_tag_list: list[Tag]) -> list[Function]:
        function_list: list[Function] = []
        for name, tag in zip(function_name_list, function_tag_list):
            function_list.append(FunctionDoc(name, tag))
        return function_list

    def __extract_class_name_list_and_tag_list(self, soup_list: list[BeautifulSoup]) -> Tuple[list[Symbol], list[Tag]]:
        name_list: list[Symbol] = []
        tag_list: list[Tag] = []
        seen_name_set: set[str] = set()
        for soup in soup_list:
            torch_classes: ResultSet[Tag] = soup.select(f".{PyTorchDocConstant.TORCH_CLASS_LITERAL.replace(' ', '.')}")
            for torch_class in torch_classes:
                torch_class_object: Tag = self.__extract_definition_object(torch_class)
                if torch_class_object is None:
                    continue
                torch_class_name: str = torch_class_object.get("id")
                if torch_class_name is None or torch_class_name in seen_name_set:
                    continue
                seen_name_set.add(torch_class_name)
                name_list.append(Symbol(torch_class_name))
                tag_list.append(torch_class)
        return name_list, tag_list

    def __extract_classes(self, class_name_list: list[Symbol], class_tag_list: list[Tag]) -> list[ClassObject]:
        class_list: list[ClassObject] = []
        for name, tag in zip(class_name_list, class_tag_list):
            class_list.append(ClassObjectDoc(name, tag))
        return class_list

    def __url_to_soup(self, url: str) -> BeautifulSoup:
        html_code: str = self.__pytorch_html_code_api.get_html_code_by_url(url)
        return BeautifulSoup(html_code, 'html.parser')

    @staticmethod
    def __extract_definition_object(definition_tag: Tag) -> Optional[Tag]:
        for child in definition_tag.find_all(recursive=False):
            if DocUrlUtils.has_class(child, PyTorchDocConstant.TORCH_OBJECT_LITERAL):
                return child
        return None

    @staticmethod
    def __extract_canonical_url(soup: BeautifulSoup) -> Optional[str]:
        canonical_tag = soup.find("link", rel="canonical")
        if canonical_tag is None:
            return None
        href = canonical_tag.get("href")
        if href is None:
            return None
        return DocUrlUtils.normalize_if_internal_doc_url(href)
