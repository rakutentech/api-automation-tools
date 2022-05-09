import orjson
import pytest

import apiautomationtools.helpers.json_helpers as jh

pytestmark = pytest.mark.helpers

test_dict = {"str1": "value1", "int1": 2, "list1": ["str1", "str2"], "list2": [0, 1]}


def test_ensure_serializable():
    data = jh.ensure_serializable(test_dict)
    assert str(data) == str(test_dict)


def test_ensure_not_serializable():
    bad_data = str
    data = jh.ensure_serializable(bad_data)
    assert data == str(bad_data)


def test_deserialize():
    test_dict_json = orjson.dumps(test_dict)
    data = jh.deserialize(test_dict_json)
    assert type(data) is dict
    assert str(data) == str(test_dict)


def test_not_deserialize():
    str_test_dict = str(test_dict)
    data = jh.deserialize(str_test_dict)
    assert type(data) is not dict
    assert data == str_test_dict
