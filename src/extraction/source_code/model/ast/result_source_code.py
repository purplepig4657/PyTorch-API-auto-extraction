from typing import Union, Optional

from src.common.model.class_object import ClassObject
from src.common.model.function import Function
from src.common.model.source_code.module import Module
from src.common.model.source_code.package import Package
from src.common.model.source_code.result import Result
from src.common.model.symbol import Symbol
from src.extraction.source_code.model.file_model.file_tree import FileTree
from src.extraction.source_code.model.ast.package_source_code import PackageSourceCode


class ResultSourceCode(Result):

    __root_tree: FileTree
    __root_package: Package

    def __init__(self, root_tree: FileTree):
        self.__root_tree = root_tree
        self.__root_package = self.__extract_root_package()
        self.__resolve_import()
        self.__resolve_class_inheritance()
        super().__init__(root_package=self.__root_package)

    def __extract_root_package(self) -> Package:
        root_package = PackageSourceCode("", self.__root_tree)
        return root_package

    def search(self, fully_qualified_name: Union[str, Symbol]) -> Optional[Union[Module, ClassObject, list[Function]]]:
        #  => Union[Module, ClassObject, list[Function]] -> 이렇게 바꾸는 거 고려해봐.  => overloading 있을 시 여러 개가
        #                                                   있을 수 있어서 여러 개 매칭해서 하나라도 맞으면 패스하도록 만들 수 있음.
        if type(fully_qualified_name) == Symbol:
            fully_qualified_name = fully_qualified_name.name
        name_split: list[str] = fully_qualified_name.split('.')
        if name_split[0] != "torch":
            return None
        if isinstance(self.__root_package, PackageSourceCode):
            root_package: PackageSourceCode = self.__root_package
            return root_package.search(name_split[1:])

    def __resolve_import(self) -> None:
        package_list: list[Package] = self.__root_package.package_list
        if isinstance(self.__root_package, PackageSourceCode):
            self.__root_package.resolve_import(['torch'], self.__root_package)

    def __resolve_class_inheritance(self) -> None:
        if isinstance(self.__root_package, PackageSourceCode):
            self.__root_package.resolve_class_inheritance()
