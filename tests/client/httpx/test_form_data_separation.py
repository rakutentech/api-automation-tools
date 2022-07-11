import os

import pytest

import apiautomationtools.helpers.directory_helpers as dh
from apiautomationtools.client import HttpxRequests

pytestmark = pytest.mark.client

root_dir = f"{os.path.dirname(__file__)}/{__name__.split('.')[-1]}"
expected_form_data = """{'data': {'field1': 'value1'}, 'files': [('file', <_io.BufferedReader name='root_dir/tests/client/httpx/test_form_data_separation.py'>)]}"""
expected_form_data = expected_form_data.replace("root_dir", dh.get_root_dir())


def test_dict_as_form_data():
    pytest.async_requests = HttpxRequests(root_dir=root_dir)
    form_data = pytest.async_requests.separate_form_data(field1="value1", file=__file__)
    assert str(form_data) == expected_form_data


def test_dict_as_form_data_kwargs():
    body = {"field1": "value1", "file": __file__}
    form_data = pytest.async_requests.separate_form_data(**body)
    assert str(form_data) == expected_form_data

    pytest.async_requests.logging.delete_run_info(root_dir)
    path = pytest.async_requests.logging.log_file_path
    assert not os.path.exists(path)
