import logging
import os
import re
from datetime import datetime
from shutil import rmtree
from typing import Any

import __main__ as main

import apiautomationtools.helpers.directory_helpers as dh


class Logger(object):
    """
    This is a wrapper around the logging module.
    """

    logger: Any = None
    root_dir: None | str = None
    log_dir: None | str = None
    log_file_path: None | str = None
    run_info_path: None | str = None

    @classmethod
    def get_logger(cls, root_dir: None | str = None, by_time: bool = False) -> Any:
        """
        This gets the logger.

        Args:
            by_time: Whether to keep all successive runs by time.
            root_dir: The specified root directory.

        Returns:
            logger: The logger to use for logging.
        """
        if cls.logger is None:
            cls.logger = logging

        cls.root_dir = root_dir or dh.get_root_dir()
        cls.log_file_path = cls.get_log_path(by_time)
        log_file_path_split = cls.log_file_path.split("/")
        index = log_file_path_split.index("run_info")
        cls.run_info_path = "/".join(log_file_path_split[: index + 1]).replace(
            "//", "/"
        )
        cls.set_logger_handler(filename=cls.log_file_path)

        return cls.logger

    @classmethod
    def get_log_path(cls, by_time: bool = False) -> str:
        """
        This gets the logging directories and file paths.

        Args:
            by_time: Whether to keep all successive runs by time.

        Returns:
            log_file_path: The path of the log file to write to.
        """
        calling_test = (
            os.environ.get("PYTEST_CURRENT_TEST")
            or getattr(main, "__file__", None)
            or getattr(main, "path", None)
        )
        calling_test = calling_test.replace(f"{cls.root_dir}/", "")
        calling_test = calling_test.split("::")[0]

        file_path = f"{cls.root_dir}/{calling_test}"
        file_path_split = file_path.split("/")
        tests_index = next(
            (
                i
                for i in range(len(file_path_split) - 1, -1, -1)
                if "tests" in file_path_split[i]
            ),
            None,
        )
        file_path_split[tests_index] = "/run_info/run_logs/"
        file_path = "/".join(file_path_split)
        if "/run_info/run_logs/" not in file_path:
            file_path = file_path.replace(
                calling_test, f"/run_info/run_logs/{calling_test}"
            )

        cls.log_dir = "/".join(file_path.split("/")[:-1])
        log_dir_path_pass = f"{cls.log_dir}/pass"
        log_dir_path_fail = f"{cls.log_dir}/fail"
        dh.safe_mkdirs(log_dir_path_pass)
        dh.safe_mkdirs(log_dir_path_fail)

        filename = re.sub(r"test_|.py", "", file_path.split("/")[-1])
        if by_time:
            filename += f"_{datetime.now().strftime('%Y-%m-%d_%H:%M:%S')}"

        return f"{log_dir_path_pass}/{filename}.log"

    @classmethod
    def set_logger_handler(cls, **kwargs: Any):
        """
        This (re)sets the logging handler.

        Args:
            kwargs: See the logging basicConfig function for more param details.

        Returns:
            logging: The updated logging module.
        """
        stock_kwargs = {
            "level": logging.INFO,
            "filemode": "w",
            "filename": "stock_log_file.log",
            "format": "%(asctime)s | %(levelname)s |  %(name)s | %(message)s",
        }
        stock_kwargs.update(kwargs)

        cls.logger.root.handlers = []
        cls.logger._handlerList = []
        cls.logger.basicConfig(**stock_kwargs)

    @classmethod
    def delete_run_info(cls, path: None | str = None):
        """
        This deletes the run info folder.

        Args:
            path: A custom path that contains logs to be deleted.
        """
        path = path or cls.run_info_path
        rmtree(path)
