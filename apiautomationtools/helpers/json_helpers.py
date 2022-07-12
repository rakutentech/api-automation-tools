import json
from typing import Any


def ensure_serializable(data: Any) -> Any:
    """
    This ensures data is serializable.

    Args:
        data: Any data to serialize.

    Returns:
        data: The serializable data.
    """
    try:
        json.dumps(data)
        return data
    except:
        return str(data)


def deserialize(text: str | bytes, other_exceptions: Any = None) -> dict | str | bytes:
    """
    This converts json to its pythonic object.

    Args:
        text: The string to convert.
        other_exceptions: Other exceptions to catch.

    Returns:
        data: The converted text or original text.
    """
    other_exceptions = other_exceptions or []
    if type(other_exceptions) is not list:
        other_exceptions = [other_exceptions]
    exceptions = [json.JSONDecodeError] + other_exceptions

    try:
        return json.loads(text)
    except tuple(exceptions):
        return text
