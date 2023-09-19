from typing import Union, Optional

from src.common.model.class_object import ClassObject
from src.common.model.function import Function
from src.common.model.method import Method
from src.common.model.source_code.module import Module
from src.common.model.source_code.package import Package
from src.common.model.source_code.result import Result
from src.extraction.source_code.model.file_model.file_tree import FileTree
from src.extraction.source_code.model.package_source_code import PackageSourceCode


class ResultSourceCode(Result):

    __root_tree: FileTree
    __root_package: Package

    def __init__(self, root_tree: FileTree):
        self.__root_tree = root_tree
        self.__root_package = self.__extract_root_package()
        # self.__resolve_init_py()
        super().__init__(root_package=self.__root_package)

    def __extract_root_package(self) -> Package:
        root_package = PackageSourceCode(self.__root_tree)
        return root_package

    def search(self, fully_qualified_name: str) -> Optional[Union[Module, ClassObject, Function]]:
        name_split: list[str] = fully_qualified_name.split('.')
        if name_split[0] != "torch":
            return None
        if isinstance(self.__root_package, PackageSourceCode):
            root_package: PackageSourceCode = self.__root_package
            return root_package.search(name_split[1:])

    def __resolve_init_py(self) -> None:
        package_list: list[Package] = self.__root_package.package_list
        for package in package_list:
            package: PackageSourceCode = package
            package.resolve_init_py()

