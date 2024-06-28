# https://python-type-challenges.zeabur.app/
#
#

from typing import Tuple, ClassVar, Awaitable, Callable, TypeVar, Literal, \
    LiteralString, Iterable, TypedDict, NotRequired, Required, Self, Unpack


# ======================== INTERMEDIATE ==========================

def await_func():
    # `run_async` takes an awaitable integer.
    pass


def callable_func():
    # Define a callable type that accepts a string argument and returns None.
    # *The parameter name can be arbitrary.*
    pass


class Foo:
    # Class `Foo` has a class variable `bar`, which is an integer.
    bar: ClassVar[int]


def run_async_func(arg: Awaitable[int]):
    # `run_async` takes an awaitable integer.
    return arg


A = TypeVar("A", bound=Callable)


def decorator_func(func: A) -> A:
    # Define a decorator that wraps a function and returns a function with the same signature.
    return func


def emptytuple_func(args: Tuple[()]):
    # should accept an empty tuple argument.
    return args


B = TypeVar("B")


def generic_func(arg1: B, arg2: B) -> B:
    # The function accepts two arguments and returns a value, they all have the same type.
    return arg1


C = TypeVar("C", int, str)  # must be an int or str


def generic2_func(arg1: C, arg2: C) -> C:
    # The function accepts two arguments and returns a value, they all have the same type.
    # The type can only be str or int (or their subclasses).
    return arg1


D = TypeVar("D", bound=int)  # may be int or relative (9)subtype


def generic3_func(arg1: D) -> D:
    # The function accepts two arguments and returns a value, they all have the same type.
    # The type can only be str or int (or their subclasses).
    return arg1


class Foo2:
    # Class has an instance variable `bar`, which is an integer.
    bar: int


def literal_func(arg1: Literal['left', 'right']):
    # only accepts literal 'left' and 'right' as its argument.
    return arg1


def literalstring_func(sql: LiteralString, parameters: Iterable[str] = ...):
    # Annotate a function `execute_query` which runs SQL, but also can prevent SQL injection attacks.
    ...  # like pass op


class Foo3:
    # should return an instance of the same type as the current enclosed class.
    def return_self(self) -> Self:
        return self


class Student(TypedDict):
    # Define a class `Student` that represents a dictionary with three keys:
    # - name, a string
    # - age, an integer
    # - school, a string
    name: str
    age: int
    school: str


class Student2(TypedDict):
    # Define a class `Student` that represents a dictionary with three keys:
    # - name, a string
    # - age, an integer
    # - school, a string, optional
    name: str
    age: int
    school: NotRequired[str]


class Person(TypedDict, total=False):
    # total=False means that instances of the Person class can have additional keys that are not defined in the class.
    # Define a class `Person` that represents a dictionary with five string keys:
    #     name, age, gender, address, email
    #
    # The value of each key must be the specified type:
    #     name - str, age - int, gender - str, address - str, email - str
    #
    # Note: Only `name` is required
    name: Required[str]
    age: int
    gender: str
    address: str
    email: str


class Person2(TypedDict):
    name: str
    age: int


def unpack_func(**arg: Unpack[Person2]):
    # expects two keyword arguments - `name` of type `str`, and `age` of type `int`
    return arg
