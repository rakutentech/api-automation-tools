from apiautomationtools.client import AsyncRequests
from apiautomationtools.pytest import ApiPytestHelper


class APIBasePytestExample(ApiPytestHelper):
    def setup_class(self):
        self.async_requests = AsyncRequests()
        ApiPytestHelper.setup_class(self)

    def test_setup(self, test_debug):
        # pytest.ini cmd arguments
        self.debug = test_debug

        for k, v in self.__dict__.items():
            setattr(APIBasePytestExample, k, v)

    def teardown_class(self):
        self.csv_path = self.async_requests.csv_path
        ApiPytestHelper.teardown_class(self)
