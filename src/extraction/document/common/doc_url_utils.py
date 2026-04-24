from __future__ import annotations

from urllib.parse import urljoin, urlparse, urlunparse

from bs4 import BeautifulSoup, Tag
from typing import Optional

from src.common.constant.pytorch_doc_constant import PyTorchDocConstant


class DocUrlUtils:
    @staticmethod
    def normalize(url: str, base_url: Optional[str] = None) -> str:
        absolute_url = urljoin(base_url, url) if base_url is not None else url
        parsed = urlparse(absolute_url)
        path = parsed.path or "/"
        normalized = parsed._replace(fragment="", query="", path=path)
        return urlunparse(normalized)

    @staticmethod
    def is_internal_doc_url(url: str) -> bool:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"}:
            return False
        if parsed.netloc != "docs.pytorch.org":
            return False
        return parsed.path.startswith(f"/docs/{PyTorchDocConstant.DOC_VERSION_PATH}/")

    @staticmethod
    def is_html_doc_url(url: str) -> bool:
        parsed = urlparse(url)
        return parsed.path.endswith(".html") or parsed.path.endswith("/")

    @classmethod
    def is_reference_api_doc_url(cls, url: str) -> bool:
        parsed = urlparse(url)
        excluded_prefixes = [
            f"/docs/{PyTorchDocConstant.DOC_VERSION_PATH}/user_guide/",
            f"/docs/{PyTorchDocConstant.DOC_VERSION_PATH}/notes/",
            f"/docs/{PyTorchDocConstant.DOC_VERSION_PATH}/community/",
            f"/docs/{PyTorchDocConstant.DOC_VERSION_PATH}/tutorials/",
            f"/docs/{PyTorchDocConstant.DOC_VERSION_PATH}/install",
        ]
        return not any(parsed.path.startswith(prefix) for prefix in excluded_prefixes)

    @classmethod
    def normalize_if_internal_doc_url(cls, url: str, base_url: Optional[str] = None) -> Optional[str]:
        normalized = cls.normalize(url, base_url)
        if not cls.is_internal_doc_url(normalized):
            return None
        if not cls.is_html_doc_url(normalized):
            return None
        if not cls.is_reference_api_doc_url(normalized):
            return None
        return normalized

    @classmethod
    def extract_reference_api_urls(cls, root_url: str, root_soup: BeautifulSoup) -> list[str]:
        anchor = root_soup.find("a", string=lambda text: text is not None and text.strip() == "Reference API")
        if anchor is None:
            return []

        nav_item = anchor.find_parent("li")
        if nav_item is None:
            return []

        result: list[str] = []
        seen: set[str] = set()
        for child_anchor in nav_item.find_all("a"):
            href = child_anchor.get("href")
            if href is None or child_anchor == anchor:
                continue
            normalized = cls.normalize_if_internal_doc_url(href, root_url)
            if normalized is None or normalized in seen:
                continue
            seen.add(normalized)
            result.append(normalized)
        return result

    @classmethod
    def extract_descendant_doc_urls(cls, current_url: str, soup: BeautifulSoup) -> list[str]:
        main_tag = soup.find("main")
        if main_tag is None:
            main_tag = soup

        result: list[str] = []
        seen: set[str] = set()
        for anchor in main_tag.find_all("a", href=True):
            normalized = cls.normalize_if_internal_doc_url(anchor["href"], current_url)
            if normalized is None or normalized == cls.normalize(current_url):
                continue
            if normalized in seen:
                continue
            seen.add(normalized)
            result.append(normalized)
        return result

    @classmethod
    def extract_page_definition_links(cls, current_url: str, soup: BeautifulSoup) -> list[str]:
        result: list[str] = []
        seen: set[str] = set()

        table_selectors = [
            f"table.{PyTorchDocConstant.TORCH_DOC_TABLE_LITERAL.replace(' ', '.')}",
            f"table.{PyTorchDocConstant.TORCH_DOC_TABLE_LITERAL_ALTERNATIVE}",
        ]

        for selector in table_selectors:
            for table_tag in soup.select(selector):
                for anchor in table_tag.find_all("a", href=True):
                    normalized = cls.normalize_if_internal_doc_url(anchor["href"], current_url)
                    if normalized is None or normalized in seen:
                        continue
                    seen.add(normalized)
                    result.append(normalized)

        return result

    @staticmethod
    def has_class(tag: Optional[Tag], class_name: str) -> bool:
        if tag is None:
            return False
        return class_name in tag.get("class", [])
