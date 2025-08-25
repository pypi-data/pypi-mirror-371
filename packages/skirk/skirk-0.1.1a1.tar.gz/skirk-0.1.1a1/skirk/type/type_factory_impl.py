"""Type factory implementations module.

This module provides implementations of type factories for complex data types.
Type factories are used to convert string representations of data into their
corresponding Python objects.

The module includes factories for:
- dict: Converts a string to a dictionary
- list: Converts a string to a list
- set: Converts a string to a set
- tuple: Converts a string to a tuple
"""
import ast

from .base_type_factory import type_factory


@type_factory(dict)
def dict_factory(s: str) -> dict:
    """Convert a string to a dictionary.

    Args:
        s: A string representation of a dictionary.

    Returns:
        dict: The parsed dictionary.

    Raises:
        ValueError: If the parsed object is not a dictionary.
        SyntaxError: If the string is not a valid Python dictionary representation.
    """
    result = ast.literal_eval(s.strip())
    if not isinstance(result, dict):
        raise ValueError(f"Parsed object is not a dict, got {type(result).__name__}")
    return result


@type_factory(list)
def list_factory(s: str) -> list:
    """Convert a string to a list.

    Args:
        s: A string representation of a list.

    Returns:
        list: The parsed list.

    Raises:
        ValueError: If the parsed object is not a list.
        SyntaxError: If the string is not a valid Python list representation.
    """
    result = ast.literal_eval(s.strip())
    if not isinstance(result, list):
        raise ValueError(f"Parsed object is not a list, got {type(result).__name__}")
    return result


@type_factory(set)
def set_factory(s: str) -> set:
    """Convert a string to a set.

    Args:
        s: A string representation of a set.

    Returns:
        set: The parsed set.

    Raises:
        ValueError: If the parsed object is not a set.
        SyntaxError: If the string is not a valid Python set representation.
    """
    result = ast.literal_eval(s.strip())
    if not isinstance(result, set):
        raise ValueError(f"Parsed object is not a set, got {type(result).__name__}")
    return result


@type_factory(tuple)
def tuple_factory(s: str) -> tuple:
    """Convert a string to a tuple.

    Args:
        s: A string representation of a tuple.

    Returns:
        tuple: The parsed tuple.

    Raises:
        ValueError: If the parsed object is not a tuple.
        SyntaxError: If the string is not a valid Python tuple representation.
    """
    result = ast.literal_eval(s.strip())
    if not isinstance(result, tuple):
        raise ValueError(f"Parsed object is not a tuple, got {type(result).__name__}")
    return result