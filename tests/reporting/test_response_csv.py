import os

import orjson
import pytest

import apiautomationtools.reporting.response_csv as rc
from apiautomationtools.client.async_requests import AsyncRequests

pytestmark = pytest.mark.reporting

test_field = {"field": "Test12345"}


def request(root_dir=os.path.dirname(__file__)):
    url = "https://httpbin.org/get"
    batch = {"method": "get", "headers": {}, "url": url}

    async_requests = AsyncRequests(root_dir=root_dir)
    return async_requests, async_requests.request(batch)


def test_read_csv():
    async_requests, _ = request()
    response_csv = rc.read_csv(async_requests.csv_path)
    assert response_csv
    assert len(response_csv) == 2
    async_requests.logging.delete_run_info()


def test_scrub_field():
    data = {"new_field": "Test12345"}
    data_json = orjson.dumps(data).decode()
    scrubbed_data_json = rc._scrub_specific_field(data_json, "new_field")
    scrubbed_data = orjson.loads(scrubbed_data_json)
    assert scrubbed_data["new_field"] == "000000000"


def test_scrub_data():
    data = {
        "actual_code": "200",
        "headers": test_field,
        "body": test_field,
        "json": test_field,
    }
    scrubbed_data = rc.scrub_data(data)
    expected_scrubbed_data = {
        "actual_code": "200",
        "headers": {"field": "000000000"},
        "body": {"field": "000000000"},
        "json": {"field": "000000000"},
    }
    assert str(scrubbed_data) == str(expected_scrubbed_data)


def test_csv_to_dict_path():
    async_requests, _ = request()
    response_dict = rc.csv_to_dict(async_requests.csv_path)
    assert response_dict
    assert type(response_dict[0]) is dict
    async_requests.logging.delete_run_info()


def test_csv_to_dict_data():
    async_requests, _ = request()
    response_csv = rc.read_csv(async_requests.csv_path)
    response_dict = rc.csv_to_dict(response_csv)
    assert response_dict
    assert type(response_dict[0]) is dict
    async_requests.logging.delete_run_info()


def test_csv_to_dict_path_scrub_data():
    async_requests, _ = request()
    response_csv = rc.read_csv(async_requests.csv_path)
    response_csv[1][11] = test_field
    response_dict = rc.csv_to_dict(response_csv, scrub=True)

    assert response_dict
    assert type(response_dict[0]) is dict
    assert str(response_dict[0]["HEADERS"]) == str({"field": "000000000"})
    async_requests.logging.delete_run_info()


def test_create_csv_report(scrub=False, delete=True):
    async_requests, response = request()
    response["responses"][0]["headers"] = test_field

    path = f"{async_requests.logging.run_info_path}/test_csv.csv"
    rc.create_csv_report(path, response, scrub=scrub)
    assert os.path.exists(path)
    if scrub:
        path = path.replace(".csv", "_scrubbed.csv")
        assert os.path.exists(path)

    response_csv = rc.read_csv(path)
    response_dict = rc.csv_to_dict(response_csv)
    assert response_dict

    if delete:
        async_requests.logging.delete_run_info()

    return response, path, async_requests


def test_create_csv_report_scrub():
    test_create_csv_report(scrub=True)


def test_add_rows_to_csv_report(delete=True):
    _, path, async_requests = test_create_csv_report(delete=False)
    response_csv = rc.read_csv(path)
    rc.add_rows_to_csv_report(path, [response_csv[1]])
    response_csv = rc.read_csv(path)
    assert len(response_csv) == 3
    assert response_csv[1] == response_csv[2]

    if delete:
        async_requests.logging.delete_run_info()

    return path, async_requests


def test_delete_last_n_rows_from_csv_report():
    path, async_requests = test_add_rows_to_csv_report(delete=False)
    rc.delete_last_n_rows_from_csv_report(path, 2)
    response_csv = rc.read_csv(path)
    assert len(response_csv) == 1
    async_requests.logging.delete_run_info()


def test_add_column_to_csv_report():
    _, path, async_requests = test_create_csv_report(delete=False)
    rc.add_column_to_csv_report(path, ["New Column", "New Column Value"])
    response_csv = rc.read_csv(path)
    assert response_csv[0][-1] == "New Column"
    assert response_csv[1][-1] == "New Column Value"
    async_requests.logging.delete_run_info()
