from typing import Generic, Self, TypeVar, assert_never

from dataclasses import dataclass
from enum import StrEnum, auto


class BaseClass:
    base = "base"
    ...


class A(BaseClass):
    a = "a"
    ...


class B(BaseClass):
    b = "b"
    ...


class Option(StrEnum):
    A = auto()
    B = auto()


T = TypeVar("T", bound=BaseClass)


@dataclass
class Config(Generic[T]):

    value: T

    @classmethod
    def create(cls, option: Option) -> "Config":
        match option:
            case Option.A:
                return Config[A](A())
            case Option.B:
                return Config[B](B())
            case _:
                assert_never(option)


config = Config.create(Option.A)
print(config.value.a)
