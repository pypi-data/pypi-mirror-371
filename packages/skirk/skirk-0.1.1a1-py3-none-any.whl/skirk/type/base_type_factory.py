"""Type factory module.

This module provides a mechanism for registering and retrieving type factories.
Type factories are functions that convert strings to specific Python types.

The module includes:
- A decorator for registering type factories
- A function for retrieving type factories
- Default factories for basic Python types (int, float, complex, bool, str)
"""
from collections.abc import Callable
from typing import Any, TypeVar

T = TypeVar("T")

__type_factories: dict[type, Callable[[str], Any]] = {
    int: int,
    float: float,
    complex: complex,
    bool: bool,
    str: str,
}

def type_factory(type_: type, override: bool = False) -> Callable[[Callable[[str], T]], Callable[[str], T]]:
    """Decorator for registering type factories.

    This decorator registers a function as a factory for converting strings to
    a specific type.

    Args:
        type_: The type for which the factory is being registered.
        override: Whether to override an existing factory for the same type.
            Defaults to False.

    Returns:
        Callable[[Callable[[str], T]], Callable[[str], T]]: A decorator function
            that registers the factory and returns the original function.

    Raises:
        ValueError: If a factory for the same type is already registered and
            override is False.
    """
    def wrapper(func: Callable[[str], T]) -> Callable[[str], T]:
        if type_ in __type_factories and not override:
            raise ValueError(f"Factory for {type_} already registered")
        __type_factories[type_] = func
        return func
    return wrapper

def get_type_factory(type_: type) -> Callable[[str], Any] | None:
    """Retrieve a type factory for the specified type.

    Args:
        type_: The type for which to retrieve the factory.

    Returns:
        Callable[[str], Any] | None: The factory function for the specified type,
            or None if no factory is registered.
    """
    return __type_factories.get(type_)