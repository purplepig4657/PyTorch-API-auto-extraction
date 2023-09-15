from src.common.model.source_code.module import Module
from src.common.model.source_code.package import Package
from src.common.model.symbol import Symbol
from src.extraction.source_code.model.file_model.file_leaf import FileLeaf
from src.extraction.source_code.model.file_model.file_tree import FileTree
from src.extraction.source_code.model.module_source_code import ModuleSourceCode


class PackageSourceCode(Package):

    __package_file_tree: FileTree

    def __init__(self, package_file_tree: FileTree):
        self.__package_file_tree = package_file_tree
        symbol: Symbol = Symbol(package_file_tree.name)
        package_list = self.__extract_all_package_list()
        module_list = self.__extract_all_module_list()
        super().__init__(symbol, package_list, module_list)

    def __extract_all_package_list(self) -> list[Package]:
        package_list: list[Package] = list[Package]()
        directories: list[FileTree] = self.__package_file_tree.directories
        for directory in directories:
            package_list.append(PackageSourceCode(directory))

        return package_list

    def __extract_all_module_list(self) -> list[Module]:
        module_list: list[Module] = list[Module]()
        files: list[FileLeaf] = self.__package_file_tree.files
        for file in files:
            module_list.append(ModuleSourceCode(file))
        return module_list
