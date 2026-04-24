from abc import ABC, abstractmethod


class PyTorchHtmlCodeApi(ABC):

    @abstractmethod
    def get_html_code_by_url(self, url: str) -> str:
        pass

    @abstractmethod
    def prefetch_api_reference(self, root_url: str) -> None:
        pass
