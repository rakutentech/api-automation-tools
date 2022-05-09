import os

import pytest

import apiautomationtools.helpers.directory_helpers as dh

pytestmark = pytest.mark.helpers

base_path = os.path.dirname(__file__)
test_dict = {"str1": "value1", "int1": 2, "list1": ["str1", "str2"], "list2": [0, 1]}


def test_safe_mkdirs():
    path = base_path + "/test_dir"
    dh.safe_mkdirs(path)
    assert os.path.exists(path)

    os.rmdir(path)
    assert not os.path.exists(path)


def test_make_json():
    path = base_path + "/test.json"
    dh.make_json(test_dict, path)
    assert os.path.exists(path)

    os.remove(path)
    assert not os.path.exists(path)


def test_make_json_append():
    path = base_path + "/test_append.json"
    dh.make_json(test_dict, path)
    assert os.path.exists(path)

    extra_dict = {"new_key": "new_value"}
    dh.make_json(extra_dict, path, append=True)
    assert os.path.exists(path)

    appended_dict = dh.load_json(path)
    assert str(appended_dict) == str({**test_dict, **extra_dict})

    os.remove(path)
    assert not os.path.exists(path)


def test_make_json_ascii():
    path = base_path + "/test_ascii.json"
    dh.make_json(test_dict, path, ensure_ascii=True)
    assert os.path.exists(path)

    os.remove(path)
    assert not os.path.exists(path)


def test_load_json():
    path = base_path + "/test_load.json"
    dh.make_json(test_dict, path)
    assert os.path.exists(path)

    loaded_dict = dh.load_json(path)
    assert str(loaded_dict) == str(test_dict)

    os.remove(path)
    assert not os.path.exists(path)


def test_find_reference_in_list_directory():
    references = [
        "/foo/apple.txt",
        "/foo/bar",
        "/foo/bar/orange.txt",
        "/foo/bar/py/peach.txt",
    ]
    reference = dh.find_reference_in_list("peach.txt", references)
    assert reference == references[-1]


def test_find_reference_in_list_file():
    references = [
        "/foo/apple.txt",
        "/foo/bar",
        "/foo/bar/orange.txt",
        "/foo/bar/py/peach.txt",
    ]
    reference = dh.find_reference_in_list("bar", references)
    assert reference == references[1]


def test_get_root_dir():
    root_dir = dh.get_root_dir()
    expected_root_dir = "/".join(__file__.split("/")[:-4])
    assert root_dir == expected_root_dir


def test_get_root_dir_root_checks():
    root_dir = dh.get_root_dir(root_checks=["bad_check"])
    expected_root_dir = "/".join(__file__.split("/")[:-4])
    assert root_dir == expected_root_dir


def test_get_src_app_dir():
    app_dir = dh.get_src_app_dir()
    assert app_dir == "helpers"


def test_expand_directory():
    expanded_dir = dh.expand_directory(base_path)
    assert len(expanded_dir) >= 3

    expected_files = ["directory_helpers", "test_directory_helpers.py", "__init__.py"]
    actual_files = [
        e.split("/")[-1] if e.split("/")[-1] else e.split("/")[-2] for e in expanded_dir
    ]
    assert actual_files == expected_files
