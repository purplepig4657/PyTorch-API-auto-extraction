from __future__ import annotations

from urllib.parse import urljoin, urlparse, urlunparse

from bs4 import BeautifulSoup, Tag
from typing import Optional

from src.common.library_spec import LibrarySpec


class DocUrlUtils:
    @staticmethod
    def normalize(url: str, base_url: Optional[str] = None) -> str:
        absolute_url = urljoin(base_url, url) if base_url is not None else url
        parsed = urlparse(absolute_url)
        path = parsed.path or "/"
        normalized = parsed._replace(fragment="", query="", path=path)
        return urlunparse(normalized)

    @staticmethod
    def is_internal_doc_url(url: str, library_spec: LibrarySpec) -> bool:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"}:
            return False
        if parsed.netloc != library_spec.doc_host:
            return False
        return parsed.path.startswith(library_spec.doc_path_prefix)

    @staticmethod
    def is_html_doc_url(url: str) -> bool:
        parsed = urlparse(url)
        return parsed.path.endswith(".html") or parsed.path.endswith("/")

    @classmethod
    def is_reference_api_doc_url(cls, url: str, library_spec: LibrarySpec) -> bool:
        parsed = urlparse(url)
        return not any(parsed.path.startswith(prefix) for prefix in library_spec.excluded_doc_prefixes)

    @classmethod
    def normalize_if_internal_doc_url(
            cls,
            url: str,
            library_spec: LibrarySpec,
            base_url: Optional[str] = None
    ) -> Optional[str]:
        normalized = cls.normalize(url, base_url)
        if not cls.is_internal_doc_url(normalized, library_spec):
            return None
        if not cls.is_html_doc_url(normalized):
            return None
        if not cls.is_reference_api_doc_url(normalized, library_spec):
            return None
        return normalized

    @classmethod
    def extract_reference_api_urls(
            cls,
            root_url: str,
            root_soup: BeautifulSoup,
            library_spec: LibrarySpec
    ) -> list[str]:
        if library_spec.key == "numpy":
            return cls.__extract_numpy_reference_api_urls(root_url, root_soup, library_spec)
        return cls.__extract_pytorch_reference_api_urls(root_url, root_soup, library_spec)

    @classmethod
    def __extract_pytorch_reference_api_urls(
            cls,
            root_url: str,
            root_soup: BeautifulSoup,
            library_spec: LibrarySpec
    ) -> list[str]:
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
            normalized = cls.normalize_if_internal_doc_url(href, library_spec, root_url)
            if normalized is None or normalized in seen:
                continue
            seen.add(normalized)
            result.append(normalized)
        return result

    @classmethod
    def __extract_numpy_reference_api_urls(
            cls,
            root_url: str,
            root_soup: BeautifulSoup,
            library_spec: LibrarySpec
    ) -> list[str]:
        heading = next(
            (tag for tag in root_soup.find_all(["h1", "h2", "h3"]) if "Python API" in tag.get_text(" ", strip=True)),
            None
        )
        if heading is None or heading.parent is None:
            return []

        result: list[str] = []
        seen: set[str] = set()
        for anchor in heading.parent.find_all("a", href=True):
            normalized = cls.normalize_if_internal_doc_url(anchor["href"], library_spec, root_url)
            if normalized is None or normalized == cls.normalize(root_url) or normalized in seen:
                continue
            seen.add(normalized)
            result.append(normalized)
        return result

    @classmethod
    def extract_descendant_doc_urls(cls, current_url: str, soup: BeautifulSoup, library_spec: LibrarySpec) -> list[str]:
        main_tag = soup.find("main")
        if main_tag is None:
            main_tag = soup

        result: list[str] = []
        seen: set[str] = set()
        for anchor in main_tag.find_all("a", href=True):
            normalized = cls.normalize_if_internal_doc_url(anchor["href"], library_spec, current_url)
            if normalized is None or normalized == cls.normalize(current_url):
                continue
            if normalized in seen:
                continue
            seen.add(normalized)
            result.append(normalized)
        return result

    @classmethod
    def extract_page_definition_links(
            cls,
            current_url: str,
            soup: BeautifulSoup,
            library_spec: LibrarySpec
    ) -> list[str]:
        result: list[str] = []
        seen: set[str] = set()

        for selector in library_spec.doc_table_selectors:
            for table_tag in soup.select(selector):
                for anchor in table_tag.find_all("a", href=True):
                    normalized = cls.normalize_if_internal_doc_url(anchor["href"], library_spec, current_url)
                    if normalized is None or normalized in seen:
                        continue
                    seen.add(normalized)
                    result.append(normalized)

        if library_spec.key == "numpy":
            for descendant_url in cls.extract_descendant_doc_urls(current_url, soup, library_spec):
                parsed = urlparse(descendant_url)
                if "/generated/" not in parsed.path and not parsed.path.startswith(f"{library_spec.doc_path_prefix}routines"):
                    continue
                if descendant_url in seen:
                    continue
                seen.add(descendant_url)
                result.append(descendant_url)

        return result

    @staticmethod
    def has_class(tag: Optional[Tag], class_name: str) -> bool:
        if tag is None:
            return False
        return class_name in tag.get("class", [])
