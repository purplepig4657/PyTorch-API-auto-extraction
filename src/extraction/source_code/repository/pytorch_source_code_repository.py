from abc import ABC, abstractmethod

from src.extraction.source_code.model.file_model.file_tree import FileTree


class PyTorchSourceCodeRepository:

    @abstractmethod
    def get_source_code_tree(self, target_directory: str = None) -> FileTree:
        pass
