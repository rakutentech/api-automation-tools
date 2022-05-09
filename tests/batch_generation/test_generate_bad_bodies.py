import pytest

import apiautomationtools.batch_generation.batch_generation as bg

pytestmark = pytest.mark.batch_generation


def test_generate_bad_bodies_sub_value():
    body = {"field1": "value1", "field2": "2", "file": "file", "file2": "file2"}
    bad_bodies = bg.generate_bad_bodies(body, "0")
    expected_bodies = [
        {"aaaaa0": "value1", "field2": "2", "file": "file", "file2": "file2"},
        {"field1": "aaaaa0", "field2": "2", "file": "file", "file2": "file2"},
        {"field1": "value1", "aaaaa0": "2", "file": "file", "file2": "file2"},
        {"field1": "value1", "field2": "0", "file": "file", "file2": "file2"},
        {"field1": "value1", "field2": "2", "file": "file", "file2": "file2"},
        {"aaaaa0": "0", "file": "file", "file2": "file2"},
    ]
    assert bad_bodies == expected_bodies


def test_generate_bad_bodies_replacements():
    body = {"field1": "value1", "field2": "2", "file": "file", "file2": "file2"}
    bad_bodies = bg.generate_bad_bodies(body, replacements=["value1", "9f"])
    expected_bodies = [
        {"field1": "9f", "field2": "2", "file": "file", "file2": "file2"}
    ]
    assert bad_bodies == expected_bodies


def test_generate_bad_bodies_full():
    body = {"field1": "value1", "field2": "2", "file": "file", "file2": "file2"}
    bad_bodies = bg.generate_bad_bodies(body, "0", full=True)
    expected_bodies = [
        {"aaaaa0": "value1", "field2": "2", "file": "file", "file2": "file2"},
        {"field1": "aaaaa0", "field2": "2", "file": "file", "file2": "file2"},
        {"field1": "value1", "aaaaa0": "2", "file": "file", "file2": "file2"},
        {"field1": "value1", "field2": "0", "file": "file", "file2": "file2"},
        {"field1": "value1", "field2": "2", "file": "file", "file2": "file2"},
        {"aaaaa0": "0", "file": "file", "file2": "file2"},
    ]
    assert bad_bodies == expected_bodies


def test_generate_bad_bodies_original_keys():
    body = {"field1": "value1", "field2": "2", "file": "file", "file2": "file2"}
    bad_bodies = bg.generate_bad_bodies(body, "0", original_keys=True)
    expected_bodies = [
        {"field1": "aaaaa0", "field2": "2", "file": "file", "file2": "file2"},
        {"field1": "value1", "field2": "0", "file": "file", "file2": "file2"},
        {"field1": "value1", "field2": "2", "file": "file", "file2": "file2"},
    ]
    assert bad_bodies == expected_bodies
