from typing import Union, TypeVar, Generic


T = TypeVar('T', bound=Union[int, str, None])


class Value(Generic[T]):
    __value: T

    def __init__(self, value: T) -> None:
        self.__value = value

    @property
    def value(self) -> T:
        return self.__value

    def __str__(self) -> str:
        if type(self.value) == int:
            return f"{self.value}"
        else:
            return f"\"{self.value}\""
