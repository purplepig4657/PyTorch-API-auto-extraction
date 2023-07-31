import requests

from src.extraction.repository.pytorch_html_code_api import PyTorchHtmlCodeApi


class PyTorchHtmlCodeApiImpl(PyTorchHtmlCodeApi):

    def get_html_code_by_url(self, url: str) -> str:
        response: requests.Response = requests.get(url)
        if response.status_code == 200:
            html: str = response.text
            return html
        else:
            raise RuntimeError(f"request failed with status code: {response.status_code}")