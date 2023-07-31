from bs4 import BeautifulSoup, Tag, ResultSet

from src.common.model.library import Library
from src.common.model.result import Result
from src.extraction.document.model.library_doc import LibraryDoc
from src.extraction.repository.pytorch_html_code_api import PyTorchHtmlCodeApi
from src.extraction.document.common.selector_string_builder import SelectorStringBuilder


class ResultDoc(Result):
    __pytorch_html_code_api: PyTorchHtmlCodeApi

    # PyTorch documentation traits
    __ROOT_URL = "https://pytorch.org/docs/stable/"
    __TORCH_MENU_LITERAL = "pytorch-menu"
    __TORCH_API_MENU_NUMBER = 4

    def __init__(self, pytorch_html_code_api: PyTorchHtmlCodeApi, root_url: str = None) -> None:
        self.__pytorch_html_code_api = pytorch_html_code_api
        library_url_list: list[str] = self.__extract_library_url_list(self.__ROOT_URL if root_url is None else root_url)
        library_soup_list: list[BeautifulSoup] = self.__convert_url_list_to_soup(library_url_list)
        library_list: list[Library] = self.__extract_libraries(library_soup_list)
        super().__init__(library_list=library_list)

    def __extract_library_url_list(self, root_url: str) -> list[str]:
        # Warning: This code is highly dependent on the PyTorch documentation HTML structure.
        # No need to delve deeply this code. Just extract PyTorch library url from PyTorch API menu.
        root_html_soup: BeautifulSoup = self.__url_to_soup(root_url)
        nav_tag: Tag = root_html_soup.select_one(SelectorStringBuilder(class_literal=self.__TORCH_MENU_LITERAL).build())
        ul_tag_list: ResultSet[Tag] = nav_tag.find_all(name="ul", recursive=False)
        api_tag: Tag = ul_tag_list[self.__TORCH_API_MENU_NUMBER]
        library_tags: ResultSet[Tag] = api_tag.find_all(name="li")
        result: list[str] = list[str]()
        for library in library_tags:
            result.append(self.__ROOT_URL + library.find(name="a").get('href'))
        return result

    # noinspection PyMethodMayBeStatic
    def __convert_url_list_to_soup(self, url_list: list[str]) -> list[BeautifulSoup]:
        return list(map(self.__url_to_soup, url_list))

    # noinspection PyMethodMayBeStatic
    def __extract_libraries(self, soup_list: list[BeautifulSoup]) -> list[Library]:
        library_list: list[Library] = list[Library]()
        for soup in soup_list:
            library_list.append(LibraryDoc(soup))
        return library_list

    # noinspection PyMethodMayBeStatic
    def __url_to_soup(self, url: str) -> BeautifulSoup:
        html_code: str = self.__pytorch_html_code_api.get_html_code_by_url(url)
        return BeautifulSoup(html_code, 'html.parser')
