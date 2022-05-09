import os
from datetime import datetime

import pytest

import apiautomationtools.helpers.directory_helpers as dh
from apiautomationtools.logging.logger import Logger

pytestmark = pytest.mark.logging


def test_logging(root_dir=None, by_time=False, deletion_path=None):
    logging = Logger().get_logger(root_dir=root_dir, by_time=by_time)
    logging.info("This is an example log message.")
    path = Logger().log_file_path
    assert os.path.exists(path)

    run_info_path = Logger().run_info_path
    expanded_dir = dh.expand_directory(run_info_path)
    files = [
        "/".join(e.split("/")[-2:]) if e.split("/")[-1] else e.split("/")[-2]
        for e in expanded_dir
    ]
    expected_files = [
        "run_info",
        "run_info/run_logs",
        "run_logs/logging",
        "logging/fail",
        "logging/pass",
        "pass/logger.log",
    ]

    if not by_time:
        assert files == expected_files
    else:
        assert files != expected_files
        assert datetime.now().strftime("%Y-%m-%d_%H:") in str(files)

    Logger().delete_run_info(deletion_path)
    assert not os.path.exists(path)


def test_logging_custom_root():
    root_dir = os.path.dirname(__file__) + "/custom_root"
    test_logging(root_dir, deletion_path=root_dir)


def test_logging_by_time():
    test_logging(by_time=True)


def test_logging_custom_root_by_time_():
    root_dir = os.path.dirname(__file__)
    test_logging(root_dir=root_dir, by_time=True)
