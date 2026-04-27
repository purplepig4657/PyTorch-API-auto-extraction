import os

import requests
from bs4 import BeautifulSoup

from src.common.library_spec import LibrarySpec, get_library_spec
from src.extraction.document.common.doc_url_utils import DocUrlUtils
from src.extraction.repository.pytorch_html_code_api import PyTorchHtmlCodeApi


class PyTorchHtmlCodeApiImpl(PyTorchHtmlCodeApi):

    _FILE_PATH = os.path.dirname(os.path.abspath(__file__))

    def __init__(self, library_spec: LibrarySpec | None = None) -> None:
        self.__library_spec = get_library_spec("pytorch") if library_spec is None else library_spec
        self.__session = requests.Session()
        self.__data_directory = os.path.join(self._FILE_PATH, f"cache-{self.__library_spec.key}-{self.__library_spec.version}")
        os.makedirs(self.__data_directory, exist_ok=True)

    def get_html_code_by_url(self, url: str) -> str:
        normalized_url = DocUrlUtils.normalize(url)
        is_cached = True
        uri = self.__url_to_cache_key(normalized_url)
        try:
            with open(os.path.join(self.__data_directory, uri + ".txt"), 'r', encoding="utf-8") as f:
                html = f.read()
        except FileNotFoundError:
            is_cached = False

        if is_cached:
            return html

        response: requests.Response = self.__session.get(normalized_url, timeout=30)
        if response.status_code == 200:
            html: str = response.text
            with open(os.path.join(self.__data_directory, uri + ".txt"), 'w', encoding="utf-8") as f:
                f.write(html)
            return html
        else:
            try:
                raise RuntimeError(f"request failed with status code: {response.status_code}")
            except RuntimeError:
                print(f"url: {normalized_url}")
                print(f"status_code: {response.status_code}")
                return "<html></html>"

    def prefetch_api_reference(self, root_url: str) -> None:
        normalized_root_url = DocUrlUtils.normalize(root_url)
        root_html = self.get_html_code_by_url(normalized_root_url)
        root_soup = BeautifulSoup(root_html, "html.parser")

        queued_urls = DocUrlUtils.extract_reference_api_urls(normalized_root_url, root_soup, self.__library_spec)
        visited_urls: set[str] = {normalized_root_url}

        while queued_urls:
            current_url = queued_urls.pop(0)
            if current_url in visited_urls:
                continue

            visited_urls.add(current_url)
            current_html = self.get_html_code_by_url(current_url)
            current_soup = BeautifulSoup(current_html, "html.parser")

            discovered_urls = DocUrlUtils.extract_page_definition_links(current_url, current_soup, self.__library_spec)

            for discovered_url in discovered_urls:
                if discovered_url in visited_urls or discovered_url in queued_urls:
                    continue
                queued_urls.append(discovered_url)

    @staticmethod
    def __url_to_cache_key(url: str) -> str:
        return url.replace("/", "-").replace(".", "")
