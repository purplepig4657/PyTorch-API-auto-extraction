from abc import ABC, abstractmethod

from src.extraction.source_code.model.file_model.file_tree import FileTree


class PyTorchSourceCodeRepository:

    @abstractmethod
    def get_torch_root_tree(self) -> FileTree:
        pass
