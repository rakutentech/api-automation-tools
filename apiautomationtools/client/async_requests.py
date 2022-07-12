import asyncio
import time
from copy import deepcopy
from datetime import datetime, timezone
from operator import itemgetter
from typing import Any

import orjson
import pypeln as pl
from aiohttp import ClientSession, FormData, TCPConnector

import apiautomationtools.helpers.directory_helpers as dir_helpers
import apiautomationtools.reporting.response_csv as rc
from apiautomationtools.logging import Logger


class AsyncRequests(object):
    """
    Code minifier for batching async requests.
    """

    def __init__(self, root_dir: None | str = None):
        """
        This is the constructor for AsyncRequests.

        Args:
            root_dir: A specified root directory.
        """
        Logger().get_logger(root_dir=root_dir)
        self.logging = Logger()
        self.logger = self.logging.logger
        self.csv_path = self.logging.log_file_path.replace(".log", ".csv")

        self.batch_number = 0
        self._return = []
        self._return_history = []

    def dict_as_form_data(self, **kwargs: Any) -> FormData:
        """
        This converts a dictionary into form data for posting.

        Args:
            kwargs: The dictionary to convert.

        Returns:
            data: The data to be used as the value of a data parameter.
        """
        self.logger.info(f"Converting dictionary {kwargs}.")
        data = FormData()

        for key, value in kwargs.items():
            if "file" in key:
                if type(value) is not list:
                    value = [value]
                files = [dir_helpers.expand_directory(v) for v in value]
                for f1 in files:
                    for f2 in f1:
                        # Workaround - set content_type for mimetype issue
                        content_type = "text/html"
                        if f2.split(".")[-1].lower() in ["ico", "jpeg", "jpg", "png"]:
                            content_type = None
                        data.add_field(
                            key,
                            open(f2, "rb"),
                            filename=f2.split("/")[-1],
                            content_type=content_type,
                        )
            else:
                data.add_field(key, value)

        self.logger.info(f"Converted dictionary {kwargs} into {data}.")
        return data

    def build_request_info(
        self, data: list[dict] | dict, delay: int | float = 0, **kwargs: Any
    ) -> list:
        """
        This builds the object for making requests.

        Args:
            data: The list of info needed to make the request eg [{'url': ..., 'method': 'get'}].
            delay: How long to delay between requests.
            **kwargs: The additional params eg headers or data etc. See
                https://docs.aiohttp.org/en/stable/client_reference.html for more details.

        Returns:
            list: The prepped data and kwargs e.g. [data, kwargs]

        """
        if type(data) is not list:
            data = [data]

        agg_delay = 0
        for i in range(len(data)):
            agg_delay += delay
            d = data[i]
            f_data = d.pop("data", None)
            d = deepcopy(d)
            d["delay"] = round(agg_delay, 2)
            d["index"] = i

            if f_data:
                if "FormData" not in str(type(f_data)):
                    f_data = self.dict_as_form_data(**f_data)
                d["data"] = f_data
            data[i] = d

        kwargs = deepcopy(kwargs)
        return [data, kwargs]

    async def _request(self, session: ClientSession, data: dict, **kwargs: Any):
        """
        This makes the individual requests.

        Args:
            session: The request making session object.
            data: The info needed to make the request eg {'url': ..., 'method': 'get'}.
            **kwargs: The additional params eg headers or data etc. See
                https://docs.aiohttp.org/en/stable/client_reference.html for more details.
        """
        kwargs.update(data)

        description = kwargs.pop("description", None)
        code = kwargs.pop("code", None)
        method = kwargs.pop("method", "").lower()
        url = kwargs.pop("url", "")
        delay = kwargs.pop("delay", 0)
        stream_path = kwargs.pop("stream_path", "")
        index = kwargs.pop("index", 0)

        self.logger.info(f"Making the request with {data}.")
        not delay or await asyncio.sleep(delay)

        t0 = datetime.utcnow().replace(tzinfo=timezone.utc)
        async with session.request(method, url, ssl=False, **kwargs) as response:
            t1 = datetime.utcnow().replace(tzinfo=timezone.utc)
            response_seconds = round((t1 - t0).total_seconds(), 2)

            if stream_path:
                with open(stream_path, "wb") as fd:
                    async for content in response.content.iter_chunked(1024):
                        fd.write(content)

            try:
                _json = await response.json(loads=orjson.loads)
            except Exception:
                try:
                    _json = await response.text()
                except Exception:
                    _json = ""

            code_mismatch = ""
            if code and str(code).split("|")[0] != str(response.status):
                code_mismatch = "X"

            self._return += [
                {
                    "description": description,
                    "code_mismatch": code_mismatch,
                    "batch_number": self.batch_number,
                    "index": index + 1,
                    "method": response.method.upper(),
                    "expected_code": code,
                    "actual_code": str(response.status),
                    "json": _json,
                    "url": url,
                    "server_headers": response.headers,
                    "response_seconds": response_seconds,
                    "delay_seconds": delay,
                    "utc_time": t1.isoformat(),
                    "headers": kwargs.pop("headers"),
                    "kwargs": kwargs,
                }
            ]
            if stream_path:
                self._return[-1]["stream_path"] = stream_path

        self.logger.info(
            f"Made the request with {data} \n returning {self._return[-1]}."
        )

    async def each_request(self, data: list[dict], **kwargs: Any) -> Any:
        """
        The looping wrapper for _request.

        Args:
            data: The list of info needed to make the request eg [{'url': ..., 'method': 'get'}].
            **kwargs: The additional params eg headers or data etc. See
                https://docs.aiohttp.org/en/stable/client_reference.html for more details.
        """
        conn = TCPConnector(limit=1000)
        async with ClientSession(connector=conn) as session:
            return await pl.task.each(
                lambda d: self._request(session, d, **kwargs), data, workers=len(data)
            )

    def request(
        self,
        data: list[dict] | dict,
        delay: int | float = 0,
        report: bool = True,
        **kwargs: Any,
    ) -> dict:
        """
        The batch executor for the requests batch.

        Args:
            data: The list of info needed to make the request eg [{'url': ..., 'method': 'get'}].
            delay: How long to delay between requests.
            report: Whether to create or update a report with the current responses.
            **kwargs: The additional params eg headers or data etc. See
                https://docs.aiohttp.org/en/stable/client_reference.html for more details.
        Returns:
            responses: The global response object eg {'duration': ..., 'responses': ...}.
        """
        self.batch_number += 1
        data, kwargs = self.build_request_info(data, delay, **kwargs)

        each = self.each_request(data, **kwargs)
        t0 = time.time()
        asyncio.run(each)
        t1 = time.time()

        _return = {
            "duration": round(t1 - t0, 2),
            "responses": sorted(self._return, key=itemgetter("index")),
        }
        self._return_history.append(_return)
        self._return = []
        self.logger.info(f'The batch duration was {_return["duration"]} seconds.')

        if _return["responses"]:
            not report or rc.create_csv_report(self.csv_path, _return, scrub=True)
        return _return

    async def async_request(
        self,
        data: list[dict] | dict,
        delay: int | float = 0,
        report: bool = True,
        **kwargs: Any,
    ) -> dict:
        """
        The batch executor for the async requests batch.

        Args:
            data: The list of info needed to make the request eg [{'url': ..., 'method': 'get'}].
            delay: How long to delay between requests.
            report: Whether to create or update a report with the current responses.
            **kwargs: The additional params eg headers or data etc. See
                https://docs.aiohttp.org/en/stable/client_reference.html for more details.
        Returns:
            responses: The global response object eg {'duration': ..., 'responses': ...}.
        """
        self.batch_number += 1
        data, kwargs = self.build_request_info(data, delay, **kwargs)

        t0 = time.time()
        await self.each_request(data, **kwargs)
        t1 = time.time()

        _return = {
            "duration": round(t1 - t0, 2),
            "responses": sorted(self._return, key=itemgetter("index")),
        }
        self._return_history.append(_return)
        self._return = []
        self.logger.info(f'The batch duration was {_return["duration"]} seconds.')

        if _return["responses"]:
            not report or rc.create_csv_report(self.csv_path, _return, scrub=True)
        return _return
