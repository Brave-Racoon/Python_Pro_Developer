# https://python-type-challenges.zeabur.app/
#
#

from typing import Final, List, Tuple, TypeAlias, Union


# Create a new type called Vector, which is a list of float.
# Python 3.12
# type Vector = list[float]

# Python 3.11
Vector: TypeAlias = list[float]

# `a` should be an integer - see last challenge "variable"
a: int


# ======================== BASIC ==========================

def any_func(args):
    # Modify so it takes an argument of arbitrary type.
    return args


def dict_func(args: dict[str, str]):
    # should accept a dict argument, both keys and values are string.
    return args


# "final" challenge: `my_list` cannot be re-assigned to
llist: list = []
my_list: Final = llist


def kwargs_func(**kwargs: int | str):
    # takes keyword arguments of type integer or string.
    return kwargs


def list_func(arg1: List[str]):
    # foo should accept a list argument, whose elements are string.
    return arg1


def optional_func(arg1: None | int = None):
    # can accept an integer argument, None or no argument at all.
    return arg1


def return_func() -> int:
    # should return an integer argument.
    return 1


def tuple_func(args: Tuple[str, int]):
    # should accept a tuple argument, 1st item is a string, 2nd item is an integer.
    return args


def typealias_func(v: Vector):
    # Create a new type called Vector, which is a list of float.
    return v


def union_func(arg1: Union[str, int]):
    # should accept an argument that's either a string or integer.
    return arg1
