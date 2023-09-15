from typing import Tuple
from bs4 import BeautifulSoup, Tag, ResultSet

from src.common.model.document.library import Library
from src.common.model.document.result import Result
from src.common.model.symbol import Symbol
from src.common.constant.pytorch_doc_constant import PyTorchDocConstant
from src.extraction.document.model.library_doc import LibraryDoc
from src.extraction.repository.pytorch_html_code_api import PyTorchHtmlCodeApi
from src.extraction.document.common.selector_string_builder import SelectorStringBuilder


class ResultDoc(Result):
    __pytorch_html_code_api: PyTorchHtmlCodeApi

    # PyTorch documentation traits
    __TORCH_MENU_LITERAL = "pytorch-menu"
    __TORCH_API_MENU_NUMBER = 4

    def __init__(self, pytorch_html_code_api: PyTorchHtmlCodeApi, root_url: str = None) -> None:
        self.__pytorch_html_code_api = pytorch_html_code_api
        library_name_list, library_url_list = \
            self.__extract_library_name_list_and_url_list(PyTorchDocConstant.ROOT_URL if root_url is None else root_url)
        library_soup_list: list[BeautifulSoup] = self.__convert_library_url_list_to_soup(library_url_list)
        library_list: list[Library] = self.__extract_libraries(library_name_list, library_soup_list)
        super().__init__(library_list=library_list)

    def __extract_library_name_list_and_url_list(self, root_url: str) -> Tuple[list[Symbol], list[str]]:
        # Warning: This code is highly dependent on the PyTorch documentation HTML structure.
        # No need to delve deeply this code. Just extract PyTorch library url from PyTorch API menu.
        root_html_soup: BeautifulSoup = self.__url_to_soup(root_url)
        nav_tag: Tag = root_html_soup.select_one(SelectorStringBuilder(class_literal=self.__TORCH_MENU_LITERAL).build())
        ul_tag_list: ResultSet[Tag] = nav_tag.find_all(name="ul", recursive=False)
        api_tag: Tag = ul_tag_list[self.__TORCH_API_MENU_NUMBER]
        library_tags: ResultSet[Tag] = api_tag.find_all(name="li")

        url_list: list[str] = list[str]()
        name_list: list[Symbol] = list[Symbol]()
        for library in library_tags:
            a_tag: Tag = library.find(name="a")
            name_list.append(Symbol(a_tag.text))
            url_list.append(PyTorchDocConstant.ROOT_URL + a_tag.get("href"))

        return name_list, url_list

    # noinspection PyMethodMayBeStatic
    def __convert_library_url_list_to_soup(self, library_url_list: list[str]) -> list[BeautifulSoup]:
        return list(map(self.__url_to_soup, library_url_list))

    # noinspection PyMethodMayBeStatic
    def __extract_libraries(
            self, library_name_list: list[Symbol],
            library_soup_list: list[BeautifulSoup]
    ) -> list[Library]:
        library_list: list[Library] = list[Library]()
        for name, soup in zip(library_name_list, library_soup_list):
            library_list.append(LibraryDoc(self.__pytorch_html_code_api, name, soup))
        return library_list

    # noinspection PyMethodMayBeStatic
    def __url_to_soup(self, url: str) -> BeautifulSoup:
        html_code: str = self.__pytorch_html_code_api.get_html_code_by_url(url)
        return BeautifulSoup(html_code, 'html.parser')
