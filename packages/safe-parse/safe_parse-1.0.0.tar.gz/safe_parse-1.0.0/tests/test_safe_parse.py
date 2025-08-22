import pytest
from safe_parse import SafeParse, SafeNone


def test_existing_fields():
    data = {"a": 1, "b": "test"}
    obj = SafeParse(data)
    assert obj.a == 1
    assert obj.b == "test"


def test_missing_field_returns_SafeNone():
    data = {"a": 1}
    obj = SafeParse(data)
    assert isinstance(obj.missing, SafeNone)
    assert obj.missing == None
    assert not obj.missing


def test_nested_access():
    data = {"user": {"profile": {"name": "Alice"}}}
    obj = SafeParse(data)
    assert obj.user.profile.name == "Alice"
    assert isinstance(obj.user.profile.missing, SafeNone)
    assert obj.user.profile.missing == None


def test_get_method():
    data = {"x": 10}
    obj = SafeParse(data)
    assert obj.get("x") == 10
    assert obj.get("y", 42) == 42


def test_to_dict():
    data = {"foo": "bar"}
    obj = SafeParse(data)
    assert obj.to_dict() == data


def test_keys_values_items():
    data = {"a": 1, "b": 2}
    obj = SafeParse(data)
    assert set(obj.keys()) == {"a", "b"}
    assert set(obj.values()) == {1, 2}
    assert set(obj.items()) == {("a", 1), ("b", 2)}


def test_contains():
    data = {"a": 1}
    obj = SafeParse(data)
    assert "a" in obj
    assert "b" not in obj


def test_SafeNone_str_repr():
    none_obj = SafeNone()
    assert str(none_obj) == "None"
    assert repr(none_obj) == "None"
    assert none_obj == None
    assert none_obj == SafeNone()
    assert not none_obj
