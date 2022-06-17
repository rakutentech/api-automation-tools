import os
import time

import pytest

from apiautomationtools.client import HttpxRequests

pytestmark = pytest.mark.client

root_dir = f"{os.path.dirname(__file__)}/{__name__.split('.')[-1]}"
headers = {}
url = "https://httpbin.org/get"


def test_request(batch=None, delay=0, report=True, **kwargs):
    pytest.async_requests = HttpxRequests(root_dir=root_dir)

    batch = batch or {"method": "get", "headers": headers, "url": url}
    response = pytest.async_requests.request(
        batch, delay=delay, report=report, **kwargs
    )

    assert response.get("duration")

    responses = response.get("responses")
    assert responses

    response_fields = [
        "description",
        "code_mismatch",
        "batch_number",
        "index",
        "method",
        "expected_code",
        "actual_code",
        "json",
        "url",
        "server_headers",
        "response_seconds",
        "delay_seconds",
        "utc_time",
        "headers",
    ]
    for field in response_fields:
        assert responses[0].get(field, "missing") != "missing"

    assert responses[0].get("actual_code") == "200"
    assert responses[0].get("json")

    stream_path = kwargs.get("stream_path")
    if stream_path:
        assert os.path.exists(stream_path)

    pytest.async_requests.logging.delete_run_info(root_dir)
    path = pytest.async_requests.logging.log_file_path
    assert not os.path.exists(path)

    assert pytest.async_requests.client is None


def test_request_multiple():
    batch = [
        {"method": "get", "headers": headers, "url": url},
        {"method": "get", "headers": headers, "url": url},
    ]
    test_request(batch)


def test_request_delay():
    start = time.perf_counter()
    test_request(delay=2)
    stop = time.perf_counter() - start
    assert stop >= 2


def test_request_content_stream():
    stream_path = f"{root_dir}/streamed_content.txt"
    test_request(stream_path=stream_path)


def test_no_request_report():
    test_request(report=False)
    assert not os.path.exists(pytest.async_requests.csv_path)
