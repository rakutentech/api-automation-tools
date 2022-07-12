import os

import pytest

import apiautomationtools.helpers.directory_helpers as dh
from apiautomationtools.client import AsyncRequests

pytestmark = pytest.mark.client

root_dir = f"{os.path.dirname(__file__)}/{__name__.split('.')[-1]}"
expected_form_data = """[(<MultiDict('name': 'field1')>, {}, 'value1'), (<MultiDict('name': 'file', 'filename': 'test_dict_as_form_data.py')>, {'Content-Type': 'text/html'}, <_io.BufferedReader name='root_dir/tests/client/aiohttp/test_dict_as_form_data.py'>)]"""
expected_form_data = expected_form_data.replace("root_dir", dh.get_root_dir())


def test_dict_as_form_data():
    pytest.async_requests = AsyncRequests(root_dir=root_dir)
    form_data = pytest.async_requests.dict_as_form_data(field1="value1", file=__file__)
    assert str(form_data._fields) == expected_form_data


def test_dict_as_form_data_kwargs():
    body = {"field1": "value1", "file": __file__}
    form_data = pytest.async_requests.dict_as_form_data(**body)
    assert str(form_data._fields) == expected_form_data

    pytest.async_requests.logging.delete_run_info(root_dir)
    path = pytest.async_requests.logging.log_file_path
    assert not os.path.exists(path)
