import pytest

import apiautomationtools.batch_generation.batch_generation as bg

pytestmark = pytest.mark.batch_generation


def test_generate_bad_urls_sub_value():
    # using the ';' to denote the start of the path arguments.
    url = "https://httpbin.org/get;/houseId/1b/2c?param=value1&another_param=2"
    bad_urls = bg.generate_bad_urls(url, "0")
    expected_urls = [
        "https://httpbin.org/get/houseId/0a/2c?param=value1&another_param=2",
        "https://httpbin.org/get/houseId/1b/0a?param=value1&another_param=2",
        "https://httpbin.org/get/houseId/1b/2c?param=aaaaa0&another_param=2",
        "https://httpbin.org/get/houseId/1b/2c?param=value1&another_param=0",
        "https://httpbin.org/get/houseId/0a/0a?param=aaaaa0&another_param=0",
    ]
    assert bad_urls == expected_urls


def test_generate_bad_urls_replacements():
    url = "https://httpbin.org/get/houseId/1b/2c?param=value1&another_param=2"
    bad_urls = bg.generate_bad_urls(url, replacements=["2c", "9f"])
    expected_urls = [
        "https://httpbin.org/get/houseId/1b/9f?param=value1&another_param=2"
    ]
    assert bad_urls == expected_urls


def test_generate_bad_urls_no_query_params():
    url = "https://httpbin.org/get/houseId/1b/2c?param=value1&another_param=2"
    bad_urls = bg.generate_bad_urls(url, "0", include_query_params=False)
    expected_urls = [
        "https://httpbin.org/get/houseId/0a/2c?param=value1&another_param=2",
        "https://httpbin.org/get/houseId/1b/0a?param=value1&another_param=2",
        "https://httpbin.org/get/houseId/0a/0a?param=value1&another_param=2",
    ]
    assert bad_urls == expected_urls


def test_generate_bad_urls_full():
    url = "https://httpbin.org/get/houseId/1b/2c?param1=value1&another_param=2"
    bad_urls = bg.generate_bad_urls(url, "0", full=True)
    expected_urls = [
        "https://httpbin.org/get/houseId/1b/2c?param1=value1&another_param=2",
        "https://httpbin.org/aaa/houseId/1b/2c?param1=value1&another_param=2",
        "https://httpbin.org/get/aaaaaaa/1b/2c?param1=value1&another_param=2",
        "https://httpbin.org/get/houseId/0a/2c?param1=value1&another_param=2",
        "https://httpbin.org/get/houseId/1b/0a?param1=value1&another_param=2",
        "https://httpbin.org/get/houseId/1b/2c?aaaaa0=value1&another_param=2",
        "https://httpbin.org/get/houseId/1b/2c?param1=aaaaa0&another_param=2",
        "https://httpbin.org/get/houseId/1b/2c?param1=value1&aaaaaaa_aaaaa=2",
        "https://httpbin.org/get/houseId/1b/2c?param1=value1&another_param=0",
        "https://httpbin.org/aaa/aaaaaaa/0a/0a?aaaaa0=aaaaa0&aaaaaaa_aaaaa=0",
    ]
    assert bad_urls == expected_urls
