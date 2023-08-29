import os

import requests

from src.extraction.repository.pytorch_html_code_api import PyTorchHtmlCodeApi


class PyTorchHtmlCodeApiImpl(PyTorchHtmlCodeApi):

    __FILE_PATH = os.path.dirname(os.path.abspath(__file__))
    __DATA_DIRECTORY = os.path.join(__FILE_PATH, "cache")

    def get_html_code_by_url(self, url: str) -> str:
        is_cached = True
        uri = url.replace('/', '-').replace('.', '')
        try:
            with open(os.path.join(self.__DATA_DIRECTORY, uri + ".txt"), 'r') as f:
                html = f.read()
        except FileNotFoundError:
            is_cached = False

        if is_cached:
            return html

        response: requests.Response = requests.get(url)
        if response.status_code == 200:
            html: str = response.text
            with open(os.path.join(self.__DATA_DIRECTORY, uri + ".txt"), 'w') as f:
                f.write(html)
            return html
        else:
            try:
                raise RuntimeError(f"request failed with status code: {response.status_code}")
            except RuntimeError:
                print(f"url: {url}")
                print(f"status_code: {response.status_code}")
                return "<html></html>"
