import pytest

import apiautomationtools.batch_generation.batch_generation as bg

pytestmark = pytest.mark.batch_generation


def test_generate_batch():
    # using the ';' to denote the start of the path arguments.
    url = "https://httpbin.org/get;/houseId/1b"
    batch = bg.generate_batch(method="get", headers={"key1": "value1"}, url=url)

    expected_batch = [
        {
            "code": "200",
            "description": "good",
            "method": "get",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
        },
        {
            "code": "400",
            "description": "invalid",
            "method": "get",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/999a",
        },
        {
            "code": "401",
            "description": "not auth",
            "method": "get",
            "headers": {"key1": "aaaaa0"},
            "url": "https://httpbin.org/get/houseId/1b",
        },
        {
            "code": "404",
            "description": "not found",
            "method": "get",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/0a",
        },
    ]
    assert str(batch) == str(expected_batch)


def test_generate_batch_description():
    description = "Basic batch"
    url = "https://httpbin.org/get/houseId/1b"
    batch = bg.generate_batch(
        method="get", headers={"key1": "value1"}, url=url, description=description
    )

    expected_batch = [
        {
            "code": "200",
            "description": "Basic batch good",
            "method": "get",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
        },
        {
            "code": "400",
            "description": "Basic batch invalid",
            "method": "get",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/999a",
        },
        {
            "code": "401",
            "description": "Basic batch not auth",
            "method": "get",
            "headers": {"key1": "aaaaa0"},
            "url": "https://httpbin.org/get/houseId/1b",
        },
        {
            "code": "404",
            "description": "Basic batch not found",
            "method": "get",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/0a",
        },
    ]
    assert str(batch) == str(expected_batch)


def test_generate_batch_fr_pairs():
    url = "https://httpbin.org/get/houseId/1b"
    batch = bg.generate_batch(
        method="get", headers={"key1": "value1"}, url=url, fr_pairs=["1b", "9z"]
    )

    expected_batch = [
        {
            "code": "200",
            "description": "good",
            "method": "get",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
        },
        {
            "code": "400",
            "description": "invalid",
            "method": "get",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/999a",
        },
        {
            "code": "401",
            "description": "not auth",
            "method": "get",
            "headers": {"key1": "aaaaa0"},
            "url": "https://httpbin.org/get/houseId/1b",
        },
        {
            "code": "403",
            "description": "forbidden",
            "method": "get",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/9z",
        },
        {
            "code": "404",
            "description": "not found",
            "method": "get",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/0a",
        },
    ]
    assert str(batch) == str(expected_batch)


def test_generate_batch_bad_header_count():
    url = "https://httpbin.org/get/houseId/1b"
    batch = bg.generate_batch(
        method="get",
        headers={"key1": "value1", "key2": "value2"},
        url=url,
        bad_header_count=2,
    )

    expected_batch = [
        {
            "code": "200",
            "description": "good",
            "method": "get",
            "headers": {"key1": "value1", "key2": "value2"},
            "url": "https://httpbin.org/get/houseId/1b",
        },
        {
            "code": "400",
            "description": "invalid",
            "method": "get",
            "headers": {"key1": "value1", "key2": "value2"},
            "url": "https://httpbin.org/get/houseId/999a",
        },
        {
            "code": "401",
            "description": "not auth",
            "method": "get",
            "headers": {"key1": "aaaaa0", "key2": "value2"},
            "url": "https://httpbin.org/get/houseId/1b",
        },
        {
            "code": "401",
            "description": "not auth",
            "method": "get",
            "headers": {"key1": "value1", "key2": "aaaaa0"},
            "url": "https://httpbin.org/get/houseId/1b",
        },
        {
            "code": "404",
            "description": "not found",
            "method": "get",
            "headers": {"key1": "value1", "key2": "value2"},
            "url": "https://httpbin.org/get/houseId/0a",
        },
    ]
    assert str(batch) == str(expected_batch)


def test_generate_batch_include_query_params():
    url = "https://httpbin.org/get/houseId/1b?query=value1&query=value2"
    batch = bg.generate_batch(
        method="get", headers={"key1": "value1"}, url=url, include_query_params=True
    )

    expected_batch = [
        {
            "code": "200",
            "description": "good",
            "method": "get",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b?query=value1&query=value2",
        },
        {
            "code": "400",
            "description": "invalid",
            "method": "get",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/999a?query=value1&query=value2",
        },
        {
            "code": "400",
            "description": "invalid",
            "method": "get",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b?query=aaaaa999&query=value2",
        },
        {
            "code": "400",
            "description": "invalid",
            "method": "get",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b?query=value1&query=aaaaa999",
        },
        {
            "code": "400",
            "description": "invalid",
            "method": "get",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/999a?query=aaaaa999&query=aaaaa999",
        },
        {
            "code": "401",
            "description": "not auth",
            "method": "get",
            "headers": {"key1": "aaaaa0"},
            "url": "https://httpbin.org/get/houseId/1b?query=value1&query=value2",
        },
        {
            "code": "404",
            "description": "not found",
            "method": "get",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/0a?query=value1&query=value2",
        },
        {
            "code": "404",
            "description": "not found",
            "method": "get",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b?query=aaaaa0&query=value2",
        },
        {
            "code": "404",
            "description": "not found",
            "method": "get",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b?query=value1&query=aaaaa0",
        },
        {
            "code": "404",
            "description": "not found",
            "method": "get",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/0a?query=aaaaa0&query=aaaaa0",
        },
    ]
    assert str(batch) == str(expected_batch)


def test_generate_batch_include_not_including_query_params():
    url = "https://httpbin.org/get/houseId/1b?query=value1&query=value2"
    batch = bg.generate_batch(
        method="get", headers={"key1": "value1"}, url=url, include_query_params=False
    )

    expected_batch = [
        {
            "code": "200",
            "description": "good",
            "method": "get",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b?query=value1&query=value2",
        },
        {
            "code": "400",
            "description": "invalid",
            "method": "get",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/999a?query=value1&query=value2",
        },
        {
            "code": "401",
            "description": "not auth",
            "method": "get",
            "headers": {"key1": "aaaaa0"},
            "url": "https://httpbin.org/get/houseId/1b?query=value1&query=value2",
        },
        {
            "code": "404",
            "description": "not found",
            "method": "get",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/0a?query=value1&query=value2",
        },
    ]
    assert str(batch) == str(expected_batch)


def test_generate_batch_all_true():
    url = "https://httpbin.org/get/houseId/1b?query=value1&query=value2"
    batch = bg.generate_batch(
        method="get", headers={"key1": "value1"}, url=url, full=True
    )

    expected_batch = [
        {
            "code": "200",
            "description": "good",
            "method": "get",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b?query=value1&query=value2",
        },
        {
            "code": "400",
            "description": "invalid",
            "method": "get",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b?query=value1&query=value2",
        },
        {
            "code": "400",
            "description": "invalid",
            "method": "get",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/aaa/houseId/1b?query=value1&query=value2",
        },
        {
            "code": "400",
            "description": "invalid",
            "method": "get",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/aaaaaaa/1b?query=value1&query=value2",
        },
        {
            "code": "400",
            "description": "invalid",
            "method": "get",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/999a?query=value1&query=value2",
        },
        {
            "code": "400",
            "description": "invalid",
            "method": "get",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b?aaaaa=value1&aaaaa=value2",
        },
        {
            "code": "400",
            "description": "invalid",
            "method": "get",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b?query=aaaaa999&query=value2",
        },
        {
            "code": "400",
            "description": "invalid",
            "method": "get",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b?query=value1&query=aaaaa999",
        },
        {
            "code": "400",
            "description": "invalid",
            "method": "get",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/aaa/aaaaaaa/999a?aaaaa=aaaaa999&aaaaa=aaaaa999",
        },
        {
            "code": "401",
            "description": "not auth",
            "method": "get",
            "headers": {"key1": "aaaaa0"},
            "url": "https://httpbin.org/get/houseId/1b?query=value1&query=value2",
        },
        {
            "code": "404",
            "description": "not found",
            "method": "get",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b?query=value1&query=value2",
        },
        {
            "code": "404",
            "description": "not found",
            "method": "get",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/aaa/houseId/1b?query=value1&query=value2",
        },
        {
            "code": "404",
            "description": "not found",
            "method": "get",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/aaaaaaa/1b?query=value1&query=value2",
        },
        {
            "code": "404",
            "description": "not found",
            "method": "get",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/0a?query=value1&query=value2",
        },
        {
            "code": "404",
            "description": "not found",
            "method": "get",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b?aaaaa=value1&aaaaa=value2",
        },
        {
            "code": "404",
            "description": "not found",
            "method": "get",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b?query=aaaaa0&query=value2",
        },
        {
            "code": "404",
            "description": "not found",
            "method": "get",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b?query=value1&query=aaaaa0",
        },
        {
            "code": "404",
            "description": "not found",
            "method": "get",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/aaa/aaaaaaa/0a?aaaaa=aaaaa0&aaaaa=aaaaa0",
        },
    ]
    assert str(batch) == str(expected_batch)


def test_generate_batch_json_body():
    url = "https://httpbin.org/get/houseId/1b"
    body = {"field1": "value1", "field2": 2}
    batch = bg.generate_batch(
        method="post", headers={"key1": "value1"}, url=url, json=body
    )

    expected_batch = [
        {
            "code": "201",
            "description": "good",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "json": {"field1": "value1", "field2": 2},
        },
        {
            "code": "400",
            "description": "invalid",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/999a",
            "json": {"field1": "value1", "field2": 2},
        },
        {
            "code": "400",
            "description": "invalid",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "json": {"aaaaa999": "value1", "field2": 2},
        },
        {
            "code": "400",
            "description": "invalid",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "json": {"field1": "aaaaa999", "field2": 2},
        },
        {
            "code": "400",
            "description": "invalid",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "json": {"field1": "value1", "aaaaa999": 2},
        },
        {
            "code": "400",
            "description": "invalid",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "json": {"field1": "value1", "field2": 999},
        },
        {
            "code": "400",
            "description": "invalid",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "json": {"aaaaa999": 999},
        },
        {
            "code": "401",
            "description": "not auth",
            "method": "post",
            "headers": {"key1": "aaaaa0"},
            "url": "https://httpbin.org/get/houseId/1b",
            "json": {"field1": "value1", "field2": 2},
        },
        {
            "code": "404",
            "description": "not found",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/0a",
            "json": {"field1": "value1", "field2": 2},
        },
        {
            "code": "404",
            "description": "not found",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "json": {"aaaaa0": "value1", "field2": 2},
        },
        {
            "code": "404",
            "description": "not found",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "json": {"field1": "aaaaa0", "field2": 2},
        },
        {
            "code": "404",
            "description": "not found",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "json": {"field1": "value1", "aaaaa0": 2},
        },
        {
            "code": "404",
            "description": "not found",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "json": {"field1": "value1", "field2": 0},
        },
        {
            "code": "404",
            "description": "not found",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "json": {"aaaaa0": 0},
        },
    ]
    assert str(batch) == str(expected_batch)


def test_generate_batch_data_body():
    url = "https://httpbin.org/get/houseId/1b"
    body = {"field1": "value1", "field2": 2}
    batch = bg.generate_batch(
        method="post", headers={"key1": "value1"}, url=url, data=body
    )

    expected_batch = [
        {
            "code": "201",
            "description": "good",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "data": {"field1": "value1", "field2": 2},
        },
        {
            "code": "400",
            "description": "invalid",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/999a",
            "data": {"field1": "value1", "field2": 2},
        },
        {
            "code": "400",
            "description": "invalid",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "data": {"aaaaa999": "value1", "field2": 2},
        },
        {
            "code": "400",
            "description": "invalid",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "data": {"field1": "aaaaa999", "field2": 2},
        },
        {
            "code": "400",
            "description": "invalid",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "data": {"field1": "value1", "aaaaa999": 2},
        },
        {
            "code": "400",
            "description": "invalid",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "data": {"field1": "value1", "field2": 999},
        },
        {
            "code": "400",
            "description": "invalid",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "data": {"aaaaa999": 999},
        },
        {
            "code": "401",
            "description": "not auth",
            "method": "post",
            "headers": {"key1": "aaaaa0"},
            "url": "https://httpbin.org/get/houseId/1b",
            "data": {"field1": "value1", "field2": 2},
        },
        {
            "code": "404",
            "description": "not found",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/0a",
            "data": {"field1": "value1", "field2": 2},
        },
        {
            "code": "404",
            "description": "not found",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "data": {"aaaaa0": "value1", "field2": 2},
        },
        {
            "code": "404",
            "description": "not found",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "data": {"field1": "aaaaa0", "field2": 2},
        },
        {
            "code": "404",
            "description": "not found",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "data": {"field1": "value1", "aaaaa0": 2},
        },
        {
            "code": "404",
            "description": "not found",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "data": {"field1": "value1", "field2": 0},
        },
        {
            "code": "404",
            "description": "not found",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "data": {"aaaaa0": 0},
        },
    ]
    assert str(batch) == str(expected_batch)


def test_generate_batch_body_and_unsafe_json_bodies():
    url = "https://httpbin.org/get/houseId/1b"
    body = {"field1": "value1", "field2": 2}
    batch = bg.generate_batch(
        method="post",
        headers={"key1": "value1"},
        url=url,
        json=body,
        unsafe_bodies=True,
    )
    expected_batch = [
        {
            "code": "201",
            "description": "good",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "json": {"field1": "value1", "field2": 2},
        },
        {
            "code": "400",
            "description": "invalid",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/999a",
            "json": {"field1": "value1", "field2": 2},
        },
        {
            "code": "400",
            "description": "invalid",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "json": {"aaaaa999": "value1", "field2": 2},
        },
        {
            "code": "400",
            "description": "invalid",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "json": {"field1": "aaaaa999", "field2": 2},
        },
        {
            "code": "400",
            "description": "invalid",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "json": {"field1": "value1", "aaaaa999": 2},
        },
        {
            "code": "400",
            "description": "invalid",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "json": {"field1": "value1", "field2": 999},
        },
        {
            "code": "400",
            "description": "invalid",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "json": {"aaaaa999": 999},
        },
        {
            "code": "401",
            "description": "not auth",
            "method": "post",
            "headers": {"key1": "aaaaa0"},
            "url": "https://httpbin.org/get/houseId/1b",
            "json": {"field1": "value1", "field2": 2},
        },
        {
            "code": "404",
            "description": "not found",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/0a",
            "json": {"field1": "value1", "field2": 2},
        },
        {
            "code": "404",
            "description": "not found",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "json": {"aaaaa0": "value1", "field2": 2},
        },
        {
            "code": "404",
            "description": "not found",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "json": {"field1": "aaaaa0", "field2": 2},
        },
        {
            "code": "404",
            "description": "not found",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "json": {"field1": "value1", "aaaaa0": 2},
        },
        {
            "code": "404",
            "description": "not found",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "json": {"field1": "value1", "field2": 0},
        },
        {
            "code": "404",
            "description": "not found",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "json": {"aaaaa0": 0},
        },
        {
            "code": "???",
            "description": "unsafe bodies",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "json": {"field1": "value1  '--", "field2": "2  '--"},
        },
        {
            "code": "???",
            "description": "unsafe bodies",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "json": {"field1": "value1 '+OR+1=1--", "field2": "2 '+OR+1=1--"},
        },
        {
            "code": "???",
            "description": "unsafe bodies",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "json": {"field1": "value1  '--", "field2": "2  '--"},
        },
        {
            "code": "???",
            "description": "unsafe bodies",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "json": {
                "field1": "value1 ' and substr(version(),1,10) = 'PostgreSQL' and '1  -> OK",
                "field2": "2 ' and substr(version(),1,10) = 'PostgreSQL' and '1  -> OK",
            },
        },
        {
            "code": "???",
            "description": "unsafe bodies",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "json": {"field1": "value1  '--", "field2": "2  '--"},
        },
        {
            "code": "???",
            "description": "unsafe bodies",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "json": {
                "field1": "value1 SELECT version() --",
                "field2": "2 SELECT version() --",
            },
        },
        {
            "code": "???",
            "description": "unsafe bodies",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "json": {"field1": "value1  '--", "field2": "2  '--"},
        },
        {
            "code": "???",
            "description": "unsafe bodies",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "json": {
                "field1": "value1 select database_to_xml(true,true,'');",
                "field2": "2 select database_to_xml(true,true,'');",
            },
        },
        {
            "code": "???",
            "description": "unsafe bodies",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "json": {"field1": "value1  '--", "field2": "2  '--"},
        },
        {
            "code": "???",
            "description": "unsafe bodies",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "json": {
                "field1": "value1 UNION SELECT * FROM information_schema.tables --",
                "field2": "2 UNION SELECT * FROM information_schema.tables --",
            },
        },
        {
            "code": "???",
            "description": "unsafe bodies",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "json": {"field1": "value1 '+OR+1=1--", "field2": "2 '+OR+1=1--"},
        },
        {
            "code": "???",
            "description": "unsafe bodies",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "json": {
                "field1": "value1 SELECT version() --",
                "field2": "2 SELECT version() --",
            },
        },
        {
            "code": "???",
            "description": "unsafe bodies",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "json": {"field1": "value1 '+OR+1=1--", "field2": "2 '+OR+1=1--"},
        },
        {
            "code": "???",
            "description": "unsafe bodies",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "json": {
                "field1": "value1 select database_to_xml(true,true,'');",
                "field2": "2 select database_to_xml(true,true,'');",
            },
        },
        {
            "code": "???",
            "description": "unsafe bodies",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "json": {"field1": "value1 '+OR+1=1--", "field2": "2 '+OR+1=1--"},
        },
        {
            "code": "???",
            "description": "unsafe bodies",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "json": {
                "field1": "value1 UNION SELECT * FROM information_schema.tables --",
                "field2": "2 UNION SELECT * FROM information_schema.tables --",
            },
        },
        {
            "code": "???",
            "description": "unsafe bodies",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "json": {
                "field1": "value1 ' and substr(version(),1,10) = 'PostgreSQL' and '1  -> OK",
                "field2": "2 ' and substr(version(),1,10) = 'PostgreSQL' and '1  -> OK",
            },
        },
        {
            "code": "???",
            "description": "unsafe bodies",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "json": {
                "field1": "value1 SELECT version() --",
                "field2": "2 SELECT version() --",
            },
        },
        {
            "code": "???",
            "description": "unsafe bodies",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "json": {
                "field1": "value1 ' and substr(version(),1,10) = 'PostgreSQL' and '1  -> OK",
                "field2": "2 ' and substr(version(),1,10) = 'PostgreSQL' and '1  -> OK",
            },
        },
        {
            "code": "???",
            "description": "unsafe bodies",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "json": {
                "field1": "value1 select database_to_xml(true,true,'');",
                "field2": "2 select database_to_xml(true,true,'');",
            },
        },
        {
            "code": "???",
            "description": "unsafe bodies",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "json": {
                "field1": "value1 ' and substr(version(),1,10) = 'PostgreSQL' and '1  -> OK",
                "field2": "2 ' and substr(version(),1,10) = 'PostgreSQL' and '1  -> OK",
            },
        },
        {
            "code": "???",
            "description": "unsafe bodies",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "json": {
                "field1": "value1 UNION SELECT * FROM information_schema.tables --",
                "field2": "2 UNION SELECT * FROM information_schema.tables --",
            },
        },
        {
            "code": "???",
            "description": "unsafe bodies",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "json": {
                "field1": "value1 SELECT version() --",
                "field2": "2 SELECT version() --",
            },
        },
        {
            "code": "???",
            "description": "unsafe bodies",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "json": {
                "field1": "value1 select database_to_xml(true,true,'');",
                "field2": "2 select database_to_xml(true,true,'');",
            },
        },
        {
            "code": "???",
            "description": "unsafe bodies",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "json": {
                "field1": "value1 SELECT version() --",
                "field2": "2 SELECT version() --",
            },
        },
        {
            "code": "???",
            "description": "unsafe bodies",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "json": {
                "field1": "value1 UNION SELECT * FROM information_schema.tables --",
                "field2": "2 UNION SELECT * FROM information_schema.tables --",
            },
        },
        {
            "code": "???",
            "description": "unsafe bodies",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "json": {
                "field1": "value1 select database_to_xml(true,true,'');",
                "field2": "2 select database_to_xml(true,true,'');",
            },
        },
        {
            "code": "???",
            "description": "unsafe bodies",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "json": {
                "field1": "value1 UNION SELECT * FROM information_schema.tables --",
                "field2": "2 UNION SELECT * FROM information_schema.tables --",
            },
        },
    ]
    assert str(batch) == str(expected_batch)


def test_generate_batch_body_and_unsafe_data_bodies():
    url = "https://httpbin.org/get/houseId/1b"
    body = {"field1": "value1", "field2": 2}
    batch = bg.generate_batch(
        method="post",
        headers={"key1": "value1"},
        url=url,
        data=body,
        unsafe_bodies=True,
    )
    expected_batch = [
        {
            "code": "201",
            "description": "good",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "data": {"field1": "value1", "field2": 2},
        },
        {
            "code": "400",
            "description": "invalid",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/999a",
            "data": {"field1": "value1", "field2": 2},
        },
        {
            "code": "400",
            "description": "invalid",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "data": {"aaaaa999": "value1", "field2": 2},
        },
        {
            "code": "400",
            "description": "invalid",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "data": {"field1": "aaaaa999", "field2": 2},
        },
        {
            "code": "400",
            "description": "invalid",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "data": {"field1": "value1", "aaaaa999": 2},
        },
        {
            "code": "400",
            "description": "invalid",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "data": {"field1": "value1", "field2": 999},
        },
        {
            "code": "400",
            "description": "invalid",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "data": {"aaaaa999": 999},
        },
        {
            "code": "401",
            "description": "not auth",
            "method": "post",
            "headers": {"key1": "aaaaa0"},
            "url": "https://httpbin.org/get/houseId/1b",
            "data": {"field1": "value1", "field2": 2},
        },
        {
            "code": "404",
            "description": "not found",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/0a",
            "data": {"field1": "value1", "field2": 2},
        },
        {
            "code": "404",
            "description": "not found",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "data": {"aaaaa0": "value1", "field2": 2},
        },
        {
            "code": "404",
            "description": "not found",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "data": {"field1": "aaaaa0", "field2": 2},
        },
        {
            "code": "404",
            "description": "not found",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "data": {"field1": "value1", "aaaaa0": 2},
        },
        {
            "code": "404",
            "description": "not found",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "data": {"field1": "value1", "field2": 0},
        },
        {
            "code": "404",
            "description": "not found",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "data": {"aaaaa0": 0},
        },
        {
            "code": "???",
            "description": "unsafe bodies",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "data": {"field1": "value1  '--", "field2": "2  '--"},
        },
        {
            "code": "???",
            "description": "unsafe bodies",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "data": {"field1": "value1 '+OR+1=1--", "field2": "2 '+OR+1=1--"},
        },
        {
            "code": "???",
            "description": "unsafe bodies",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "data": {"field1": "value1  '--", "field2": "2  '--"},
        },
        {
            "code": "???",
            "description": "unsafe bodies",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "data": {
                "field1": "value1 ' and substr(version(),1,10) = 'PostgreSQL' and '1  -> OK",
                "field2": "2 ' and substr(version(),1,10) = 'PostgreSQL' and '1  -> OK",
            },
        },
        {
            "code": "???",
            "description": "unsafe bodies",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "data": {"field1": "value1  '--", "field2": "2  '--"},
        },
        {
            "code": "???",
            "description": "unsafe bodies",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "data": {
                "field1": "value1 SELECT version() --",
                "field2": "2 SELECT version() --",
            },
        },
        {
            "code": "???",
            "description": "unsafe bodies",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "data": {"field1": "value1  '--", "field2": "2  '--"},
        },
        {
            "code": "???",
            "description": "unsafe bodies",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "data": {
                "field1": "value1 select database_to_xml(true,true,'');",
                "field2": "2 select database_to_xml(true,true,'');",
            },
        },
        {
            "code": "???",
            "description": "unsafe bodies",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "data": {"field1": "value1  '--", "field2": "2  '--"},
        },
        {
            "code": "???",
            "description": "unsafe bodies",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "data": {
                "field1": "value1 UNION SELECT * FROM information_schema.tables --",
                "field2": "2 UNION SELECT * FROM information_schema.tables --",
            },
        },
        {
            "code": "???",
            "description": "unsafe bodies",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "data": {"field1": "value1 '+OR+1=1--", "field2": "2 '+OR+1=1--"},
        },
        {
            "code": "???",
            "description": "unsafe bodies",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "data": {
                "field1": "value1 SELECT version() --",
                "field2": "2 SELECT version() --",
            },
        },
        {
            "code": "???",
            "description": "unsafe bodies",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "data": {"field1": "value1 '+OR+1=1--", "field2": "2 '+OR+1=1--"},
        },
        {
            "code": "???",
            "description": "unsafe bodies",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "data": {
                "field1": "value1 select database_to_xml(true,true,'');",
                "field2": "2 select database_to_xml(true,true,'');",
            },
        },
        {
            "code": "???",
            "description": "unsafe bodies",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "data": {"field1": "value1 '+OR+1=1--", "field2": "2 '+OR+1=1--"},
        },
        {
            "code": "???",
            "description": "unsafe bodies",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "data": {
                "field1": "value1 UNION SELECT * FROM information_schema.tables --",
                "field2": "2 UNION SELECT * FROM information_schema.tables --",
            },
        },
        {
            "code": "???",
            "description": "unsafe bodies",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "data": {
                "field1": "value1 ' and substr(version(),1,10) = 'PostgreSQL' and '1  -> OK",
                "field2": "2 ' and substr(version(),1,10) = 'PostgreSQL' and '1  -> OK",
            },
        },
        {
            "code": "???",
            "description": "unsafe bodies",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "data": {
                "field1": "value1 SELECT version() --",
                "field2": "2 SELECT version() --",
            },
        },
        {
            "code": "???",
            "description": "unsafe bodies",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "data": {
                "field1": "value1 ' and substr(version(),1,10) = 'PostgreSQL' and '1  -> OK",
                "field2": "2 ' and substr(version(),1,10) = 'PostgreSQL' and '1  -> OK",
            },
        },
        {
            "code": "???",
            "description": "unsafe bodies",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "data": {
                "field1": "value1 select database_to_xml(true,true,'');",
                "field2": "2 select database_to_xml(true,true,'');",
            },
        },
        {
            "code": "???",
            "description": "unsafe bodies",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "data": {
                "field1": "value1 ' and substr(version(),1,10) = 'PostgreSQL' and '1  -> OK",
                "field2": "2 ' and substr(version(),1,10) = 'PostgreSQL' and '1  -> OK",
            },
        },
        {
            "code": "???",
            "description": "unsafe bodies",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "data": {
                "field1": "value1 UNION SELECT * FROM information_schema.tables --",
                "field2": "2 UNION SELECT * FROM information_schema.tables --",
            },
        },
        {
            "code": "???",
            "description": "unsafe bodies",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "data": {
                "field1": "value1 SELECT version() --",
                "field2": "2 SELECT version() --",
            },
        },
        {
            "code": "???",
            "description": "unsafe bodies",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "data": {
                "field1": "value1 select database_to_xml(true,true,'');",
                "field2": "2 select database_to_xml(true,true,'');",
            },
        },
        {
            "code": "???",
            "description": "unsafe bodies",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "data": {
                "field1": "value1 SELECT version() --",
                "field2": "2 SELECT version() --",
            },
        },
        {
            "code": "???",
            "description": "unsafe bodies",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "data": {
                "field1": "value1 UNION SELECT * FROM information_schema.tables --",
                "field2": "2 UNION SELECT * FROM information_schema.tables --",
            },
        },
        {
            "code": "???",
            "description": "unsafe bodies",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "data": {
                "field1": "value1 select database_to_xml(true,true,'');",
                "field2": "2 select database_to_xml(true,true,'');",
            },
        },
        {
            "code": "???",
            "description": "unsafe bodies",
            "method": "post",
            "headers": {"key1": "value1"},
            "url": "https://httpbin.org/get/houseId/1b",
            "data": {
                "field1": "value1 UNION SELECT * FROM information_schema.tables --",
                "field2": "2 UNION SELECT * FROM information_schema.tables --",
            },
        },
    ]
    assert str(batch) == str(expected_batch)
