from copy import deepcopy

import pytest

import apiautomationtools.helpers.dictionary_helpers as dh

pytestmark = pytest.mark.helpers

test_dict_base = {
    "str1": "value1",
    "int1": 2,
    "list1": ["str1", "str2"],
    "list2": [0, 1],
}
test_dict = {**test_dict_base, **{"dict1": test_dict_base}}

changed_test_dict = deepcopy(test_dict)
changed_test_dict["str1"] = "diffValue1"
changed_test_dict.pop("int1")


def test_compare_dicts_no_mismatches():
    mismatches = dh.compare_dictionaries(test_dict, test_dict)
    assert str(mismatches) == str({})


def test_compare_dicts_mismatches():
    mismatches = dh.compare_dictionaries(test_dict, changed_test_dict)
    expected_mismatches = {
        "keys": [{"f1_not_in_f2": ["int1"]}],
        "values": [{"key": "str1", "d1": "value1", "d2": "diffValue1"}],
    }
    assert str(mismatches) == str(expected_mismatches)


def test_compare_dicts_skipped_keys():
    mismatches = dh.compare_dictionaries(
        test_dict, changed_test_dict, skipped_keys=["int1"]
    )
    mismatches["skipped_keys"] = sorted(mismatches["skipped_keys"])
    expected_mismatches = {
        "values": [{"key": "str1", "d1": "value1", "d2": "diffValue1"}],
        "skipped_keys": ["dict1.int1", "int1", "int1"],
    }
    assert str(mismatches) == str(expected_mismatches)


def test_compare_dicts_exclusive_keys():
    mismatches = dh.compare_dictionaries(
        test_dict, changed_test_dict, exclusive_keys=["list1"]
    )
    mismatches["skipped_keys"] = sorted(mismatches["skipped_keys"])
    expected_mismatches = {
        "skipped_keys": [
            "dict1.int1",
            "dict1.list2.0",
            "dict1.list2.1",
            "dict1.str1",
            "int1",
            "list2.0",
            "list2.1",
            "str1",
        ]
    }
    assert str(mismatches) == str(expected_mismatches)


def test_compare_dicts_normalize():
    changed_test_dict_casing = deepcopy(test_dict)
    changed_test_dict_casing["str1"] = "VALUE1"

    mismatches = dh.compare_dictionaries(
        test_dict, changed_test_dict_casing, normalize=True
    )
    assert str(mismatches) == str({})
