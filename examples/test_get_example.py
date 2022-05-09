from apiautomationtools.batch_generation.batch_generation import generate_batch
from examples.api_base_pytest_example import APIBasePytestExample


class TestGetExample(APIBasePytestExample):
    headers = {}
    url = "https://httpbin.org/get"

    def test_get_example(self):
        batch = {"method": "get", "headers": self.headers, "url": self.url}
        self.async_requests.request(batch)

    def test_get_example_batch_generator(self):
        self.url += "/someId/5678uyGHJIYUJHi8y-5678uyGHJIYUJHi8y"
        batch = generate_batch("get", self.headers, self.url)
        self.async_requests.request(batch)
