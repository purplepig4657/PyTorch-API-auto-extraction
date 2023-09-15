from src.common.model.source_code.package import Package
from src.common.model.source_code.result import Result
from src.extraction.source_code.model.file_model.file_tree import FileTree
from src.extraction.source_code.model.package_source_code import PackageSourceCode


class ResultSourceCode(Result):
    __root_tree: FileTree

    def __init__(self, root_tree: FileTree):
        self.__root_tree = root_tree
        root_package: Package = self.__extract_root_package()
        super().__init__(root_package=root_package)

    def __extract_root_package(self) -> Package:
        root_package = PackageSourceCode(self.__root_tree)
        return root_package
