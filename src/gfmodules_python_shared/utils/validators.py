from typing import TypeVar, List

T = TypeVar("T")


def validate_sets_equal(list_1: List[T], list_2: List[T]) -> bool:
    return set(list_1) == set(list_2)
