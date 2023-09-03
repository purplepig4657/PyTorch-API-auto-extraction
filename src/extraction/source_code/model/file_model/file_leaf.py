class FileLeaf:
    __name: str
    __content: str

    def __init__(self, name: str, content: str):
        self.__name = name
        self.__content = content

    @property
    def name(self) -> str:
        return self.__name

    @property
    def content(self) -> str:
        return self.__content
