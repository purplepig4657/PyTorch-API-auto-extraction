from src.common.model.source_code.package import Package


class Result:
    __root_package: Package

    def __init__(self, root_package: Package):
        self.__root_package = root_package

    @property
    def root_package(self) -> Package:
        return self.__root_package
