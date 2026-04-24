from typing import Tuple
from bs4 import BeautifulSoup, Tag, ResultSet

from src.common.model.document.library import Library
from src.common.model.document.result import Result
from src.common.model.symbol import Symbol
from src.common.constant.pytorch_doc_constant import PyTorchDocConstant
from src.extraction.document.common.doc_url_utils import DocUrlUtils
from src.extraction.document.model.library_doc import LibraryDoc
from src.extraction.repository.pytorch_html_code_api import PyTorchHtmlCodeApi


class ResultDoc(Result):
    __pytorch_html_code_api: PyTorchHtmlCodeApi

    def __init__(self, pytorch_html_code_api: PyTorchHtmlCodeApi, root_url: str = None) -> None:
        self.__pytorch_html_code_api = pytorch_html_code_api
        resolved_root_url = PyTorchDocConstant.ROOT_URL if root_url is None else root_url
        self.__pytorch_html_code_api.prefetch_api_reference(resolved_root_url)
        library_name_list, library_url_list = self.__extract_library_name_list_and_url_list(resolved_root_url)
        library_soup_list: list[BeautifulSoup] = self.__convert_library_url_list_to_soup(library_url_list)
        library_list: list[Library] = self.__extract_libraries(library_name_list, library_soup_list)
        super().__init__(library_list=library_list)

    def __extract_library_name_list_and_url_list(self, root_url: str) -> Tuple[list[Symbol], list[str]]:
        root_html_soup: BeautifulSoup = self.__url_to_soup(root_url)
        library_tags: list[Tag] = []
        reference_api_anchor = root_html_soup.find("a", string=lambda text: text is not None and text.strip() == "Reference API")
        if reference_api_anchor is not None:
            reference_api_item = reference_api_anchor.find_parent("li")
            if reference_api_item is not None:
                library_tags = reference_api_item.find_all("a")

        url_list: list[str] = []
        name_list: list[Symbol] = []
        seen_url_list: set[str] = set()
        for library_tag in library_tags:
            href = library_tag.get("href")
            if href is None:
                continue
            url = DocUrlUtils.normalize_if_internal_doc_url(href, root_url)
            if url is None or url in seen_url_list:
                continue
            if library_tag == reference_api_anchor:
                continue

            library_name = library_tag.text.strip()
            if library_name == "":
                continue

            seen_url_list.add(url)
            name_list.append(Symbol(library_name))
            url_list.append(url)
        return name_list, url_list

    # noinspection PyMethodMayBeStatic
    def __convert_library_url_list_to_soup(self, library_url_list: list[str]) -> list[BeautifulSoup]:
        return list(map(self.__url_to_soup, library_url_list))

    # noinspection PyMethodMayBeStatic
    def __extract_libraries(
            self, library_name_list: list[Symbol],
            library_soup_list: list[BeautifulSoup]
    ) -> list[Library]:
        library_list: list[Library] = []
        for name, soup in zip(library_name_list, library_soup_list):
            library_list.append(LibraryDoc(self.__pytorch_html_code_api, name, soup))
        return library_list

    # noinspection PyMethodMayBeStatic
    def __url_to_soup(self, url: str) -> BeautifulSoup:
        html_code: str = self.__pytorch_html_code_api.get_html_code_by_url(url)
        return BeautifulSoup(html_code, 'html.parser')
