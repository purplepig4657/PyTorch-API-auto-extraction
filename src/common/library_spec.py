from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class LibrarySpec:
    key: str
    version: str
    doc_root_url: str
    doc_host: str
    doc_path_prefix: str
    root_package_name: str
    source_code_directory: str
    class_literal: str = "py class"
    function_literal: str = "py function"
    method_literal: str = "py method"
    object_literal: str = "sig-object"
    parameter_from_box_literal: str = "sig-param"
    return_type_from_box_literal: str = "sig-return-typehint"
    doc_table_selectors: tuple[str, ...] = ("table.docutils.align-default", "table.autosummary")
    excluded_doc_prefixes: tuple[str, ...] = ()


_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SOURCE_ROOT = os.path.join(_PROJECT_ROOT, "repository", "source_code")


LIBRARY_SPECS: dict[str, LibrarySpec] = {
    "pytorch": LibrarySpec(
        key="pytorch",
        version="2.11.0",
        doc_root_url="https://docs.pytorch.org/docs/2.11/",
        doc_host="docs.pytorch.org",
        doc_path_prefix="/docs/2.11/",
        root_package_name="torch",
        source_code_directory=os.path.join(_SOURCE_ROOT, "pytorch-2.11.0", "torch"),
        excluded_doc_prefixes=(
            "/docs/2.11/user_guide/",
            "/docs/2.11/notes/",
            "/docs/2.11/community/",
            "/docs/2.11/tutorials/",
            "/docs/2.11/install",
        ),
    ),
    "numpy": LibrarySpec(
        key="numpy",
        version="2.4.0",
        doc_root_url="https://numpy.org/doc/2.4/reference/index.html",
        doc_host="numpy.org",
        doc_path_prefix="/doc/2.4/reference/",
        root_package_name="numpy",
        source_code_directory=os.path.join(_SOURCE_ROOT, "numpy-2.4.0", "numpy"),
        excluded_doc_prefixes=(
            "/doc/2.4/reference/c-api/",
            "/doc/2.4/reference/simd/",
            "/doc/2.4/reference/thread_safety.html",
            "/doc/2.4/reference/global_state.html",
            "/doc/2.4/reference/security.html",
            "/doc/2.4/reference/distutils_status_migration.html",
            "/doc/2.4/reference/distutils_guide.html",
        ),
    ),
}


def get_library_spec(library: str) -> LibrarySpec:
    try:
        return LIBRARY_SPECS[library]
    except KeyError as exc:
        raise ValueError(f"Unsupported library: {library}") from exc
