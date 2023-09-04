import os
from typing import Optional

from src.extraction.source_code.model.file_model.file_leaf import FileLeaf
from src.extraction.source_code.model.file_model.file_tree import FileTree
from src.extraction.source_code.repository.pytorch_source_code_repository import PyTorchSourceCodeRepository


class PyTorchSourceCodeRepositoryImpl(PyTorchSourceCodeRepository):

    __FILE_PATH = os.path.dirname(os.path.abspath(__file__))
    __PYTORCH_SOURCE_CODE_DIRECTORY = os.path.join(__FILE_PATH, "pytorch-2.0.0/torch")

    @staticmethod
    def __is_python_file(file_name: str) -> bool:
        ext: list[str] = file_name.split(".")
        if len(ext) == 0:
            return False
        ext: str = ext[-1]
        return ext == 'py'

    def get_source_code_tree(
            self,
            target_directory: str = __PYTORCH_SOURCE_CODE_DIRECTORY
    ) -> Optional[FileTree]:
        current_directory: str = os.getcwd()
        target_directory_name: str = target_directory.split('/')[-1]
        os.chdir(target_directory)

        directory_list = [f for f in os.listdir() if os.path.isdir(f)]
        python_file_list = [f for f in os.listdir() if os.path.isfile(f) and self.__is_python_file(f)]

        file_tree_list: list[FileTree] = list[FileTree]()
        file_leaf_list: list[FileLeaf] = list[FileLeaf]()

        for directory in directory_list:
            target_uri: str = os.path.join(os.getcwd(), directory)
            file_tree_list.append(self.get_source_code_tree(target_uri))

        for python_file in python_file_list:
            target_uri: str = os.path.join(os.getcwd(), python_file)
            target_name: str = python_file.split('.')[0]
            try:
                with open(target_uri, 'r') as f:
                    source_code: str = f.read()
                    file_leaf: FileLeaf = FileLeaf(target_name, source_code)
            except FileNotFoundError:
                return None
            file_leaf_list.append(file_leaf)

        result_file_tree: FileTree = FileTree(target_directory_name, file_tree_list, file_leaf_list)

        os.chdir(current_directory)

        return result_file_tree
