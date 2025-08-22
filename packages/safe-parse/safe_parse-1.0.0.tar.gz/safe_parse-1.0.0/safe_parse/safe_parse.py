from typing import Any, Dict


class SafeParse:
    """
    A class that provides dot notation access to dictionary/JSON data.
    Returns None if a field doesn't exist and handles nested objects.
    """

    def __init__(self, data: Dict[str, Any]) -> None:
        self._data = data

    def __getattr__(self, name: str) -> Any:
        if name.startswith('_'):
            raise AttributeError(
                f"'{self.__class__.__name__}' object has no attribute '{name}'")
        value = self._data.get(name)
        if value is None:
            return SafeNone()
        elif isinstance(value, dict):
            return SafeParse(value)
        else:
            return value

    def get(self, key: str, default: Any = None) -> Any:
        value = self._data.get(key, default)
        if isinstance(value, dict):
            return SafeParse(value)
        return value

    def __repr__(self) -> str:
        return f"<class __name__='SafeParse'>"

    def __str__(self) -> str:
        return str(self._data)

    def to_dict(self) -> Dict[str, Any]:
        return self._data

    def keys(self):
        return self._data.keys()

    def values(self):
        return self._data.values()

    def items(self):
        return self._data.items()

    def __contains__(self, key: str) -> bool:
        return key in self._data


class SafeNone:
    """
    A class that handles attribute access on None values.
    Always returns None for any attribute access.
    """

    def __getattr__(self, name: str) -> 'SafeNone':
        return SafeNone()

    def __bool__(self) -> bool:
        return False

    def __str__(self) -> str:
        return "None"

    def __repr__(self) -> str:
        return "None"

    def __eq__(self, other: Any) -> bool:
        return other is None or isinstance(other, SafeNone)
