import os

import apiautomationtools.helpers.directory_helpers as dh
from apiautomationtools.client import AsyncRequests
from apiautomationtools.pytest import ApiPytestHelper


class APIBasePytestExample(ApiPytestHelper):
    root_dir = os.path.dirname(__file__)

    def setup_class(self):
        self.async_requests = AsyncRequests(root_dir=self.root_dir)
        ApiPytestHelper.setup_class(self)

    def test_setup(self):
        # pytest.ini cmd arguments
        self.debug = "Some value"

        for k, v in self.__dict__.items():
            setattr(APIBasePytestExample, k, v)

    def teardown_class(self):
        self.csv_path = self.async_requests.csv_path
        ApiPytestHelper.teardown_class(self)

        run_info_path = self.async_requests.logging.run_info_path
        expanded_dir = dh.expand_directory(run_info_path)
        files = [
            "/".join(e.split("/")[-2:]) if e.split("/")[-1] else e.split("/")[-2]
            for e in expanded_dir
        ]
        expected_files = [
            "run_info",
            "run_info/run_errors",
            "run_errors/pytest",
            "pytest/api_pytest",
            "api_pytest/get_example_errors.csv",
            "run_info/run_logs",
            "run_logs/pytest",
            "pytest/api_pytest",
            "api_pytest/fail",
            "api_pytest/pass",
            "pass/get_example.log",
            "pass/get_example.csv",
            "pass/get_example_scrubbed.csv",
        ]
        assert files == expected_files

        self.async_requests.logging.delete_run_info()
        assert not os.path.exists(run_info_path)
