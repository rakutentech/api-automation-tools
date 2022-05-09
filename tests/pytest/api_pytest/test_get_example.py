import pytest

from tests.pytest.api_pytest.api_base_pytest_example import \
    APIBasePytestExample

pytestmark = pytest.mark.api_pytest


class TestGetExample(APIBasePytestExample):
    headers = {}
    url = "https://httpbin.org/get"

    def test_check_imported_data(self):
        expected_data = {"key1": "value1", "key2": {"key1": "value1"}}
        data = self.credentials_data["credentials"]["data"]
        assert str(data) == str(expected_data)

        data = self.tests_data["data"]["data"]
        assert str(data) == str(expected_data)

    def test_get_example_request(self):
        batch = {"method": "get", "headers": self.headers, "url": self.url}
        self.async_requests.request(batch)
