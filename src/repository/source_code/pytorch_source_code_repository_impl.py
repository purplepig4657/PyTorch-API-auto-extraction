from src.extraction.source_code.model.file_model.file_tree import FileTree
from src.extraction.source_code.repository.pytorch_source_code_repository import PyTorchSourceCodeRepository


class PyTorchSourceCodeRepositoryImpl(PyTorchSourceCodeRepository):

    def get_torch_root_tree(self) -> FileTree:
        pass
