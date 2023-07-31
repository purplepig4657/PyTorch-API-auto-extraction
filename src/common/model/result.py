from src.common.model.library import Library


class Result:
    __library_list: list[Library]

    def __init__(self, library_list: list[Library]) -> None:
        self.__library_list = library_list

    @property
    def library_list(self) -> list[Library]:
        return self.__library_list

    def __str__(self) -> str:
        def str_lambda(x) -> str:
            return str(x).replace("\'", "").replace("\\", "")

        library_list_str = list(map(str_lambda, self.library_list))
        return str_lambda(f"{{ library_list: {library_list_str} }}")
