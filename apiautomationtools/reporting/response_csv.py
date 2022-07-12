import ast
import csv
import json
import os
import re

import numpy as np

import apiautomationtools.helpers.json_helpers as jh


def read_csv(csv_path: None | str) -> list[list]:
    """

    Args:
        csv_path: The path to the csv file. If path is None the default one is found and used.
    Returns:
        data: The rows of a csv file.
    """
    with open(csv_path, "r") as csv_file:
        data = [r for r in csv.reader(csv_file)]

    return [
        [
            ast.literal_eval(i)
            if not (re.findall(r"MultiDict", i) or re.findall(r"BufferedReader", i))
            and re.findall(r"[\[{]", i)
            else i
            for i in d
        ]
        for d in data
        if d
    ]


def _scrub_specific_field(data_json: str, field: str) -> str:
    """
    This scrubs a specific field for alphanumerical data.

    Args:
        data_json: The JSON to scrub.
        field: The field in the json to scrub.

    Returns:
        data_json: The scrubbed JSON.
    """
    original_response = json.dumps(json.loads(data_json)[field])
    scrubbed_response = original_response[:]

    targets = re.findall(
        r"([A-Za-z]+[\d@]+[\w@]*|[\d@]+[A-Za-z]+[\w@]*|\d+)", scrubbed_response
    )
    targets.sort(key=len, reverse=True)

    for t in targets:
        if "test" not in t.lower() or "app" not in t.lower():
            scrubbed_response = scrubbed_response.replace(t, "0" * len(t))

    scrubbed_response = re.sub(
        r"\\+", "", re.sub(r'(?!\B"[^"]*)0+(?![^"]*"\B)', "0", scrubbed_response)
    )

    return data_json.replace(original_response, scrubbed_response)


def scrub_data(data: dict, regex: None | str = None) -> dict:
    """
    This removes id's from a response report object.

    Args:
        data: A response report object.
        regex: The regex to locate anything (id's) for scrubbing (defaults to uuid's).

    Returns:
        data: A scrubbed response report object.
    """
    regex = (
        regex
        or r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
    )

    data_json = {k: jh.ensure_serializable(v) for k, v in data.items()}
    data_json = json.dumps(data_json)
    ids = list(set(re.findall(regex, str(data))))
    if ids:
        uuid_rep = re.sub(r"[^-]", "0", ids[0])
        data_json = re.sub("|".join(ids), uuid_rep, data_json)

    headers = data.get("HEADERS") or data.get("headers")
    if headers:
        header_reps = [
            [v, "0" * len(v)]
            for k, v in headers.items()
            if len(re.findall(r"\d", str(v))) > 1
        ]
        for h in header_reps:
            data_json = data_json.replace(h[0], h[1])

    if data.get("json") and "2" == data["actual_code"][0]:
        data_json = _scrub_specific_field(data_json, "json")

    if data.get("json") and "4" == data["actual_code"][0]:
        targets = re.findall(r'"(.+?)"', str(data["json"]))
        targets = [
            [t, re.findall(r"([A-Za-z]+[\d@]+[\w@]*|[\d@]+[A-Za-z]+[\w@]*|\d+)", t)]
            for t in targets
        ]
        reps = [[t[0], re.sub("|".join(t[1]), "0", t[0])] for t in targets if t[1]]
        for r in reps:
            data_json = data_json.replace(r[0], r[1])

    if data.get("body"):
        data_json = _scrub_specific_field(data_json, "body")

    return json.loads(data_json)


def csv_to_dict(csv_data: str | list, scrub: bool = False) -> list[dict]:
    """

    Args:
        csv_data: The path to the csv file to be read in or the data itself.
        scrub: Whether to remove sensitive info from the data.

    Returns:
        data: The csv file represented as a dictionary.
    """
    if type(csv_data) is str:
        csv_data = read_csv(csv_data)

    data = [dict(zip(csv_data[0], r)) for r in csv_data[1:] if r]
    if scrub:
        data = [scrub_data(d) for d in data]
    return data


def create_csv_report(csv_path: str, _return: dict, scrub: bool = False):
    """
    This writes the results of each batch of requests to a csv report file.

    Args:
        csv_path: The path to store the csv report.
        _return: The _return from a batch request.
        scrub: Whether to remove sensitive info from the data.
    """
    responses = _return["responses"]

    for r in responses:
        r["server_headers"] = {k: v for k, v in r["server_headers"].items()}

        kwargs = r.get("kwargs", {})
        r["body"] = kwargs.pop("json", {}) or kwargs.pop("data", {})
        if "FormData" in str(type(r["body"])):
            r["body"] = r["body"]._fields
        elif type(r["body"]) is dict:
            update = {
                k: v.name
                for k, v in r["body"].items()
                if "BufferedReader" in str(type(v))
            }
            r["body"].update(update)

        r["response_seconds"] = r.pop("response_seconds")
        r["delay_seconds"] = r.pop("delay_seconds")

    col_titles = [""]
    if not os.path.exists(csv_path):
        col_titles = [",".join(responses[0].keys()).upper().split(",")]

    csv_data = col_titles + [list(r.values()) for r in responses]
    add_rows_to_csv_report(csv_path, csv_data)

    if scrub:
        scrubbed_csv_path = csv_path.replace(".csv", "_scrubbed.csv")

        scrubbed_responses = [
            {k: v if k != "curl" else "" for k, v in r.copy().items()}
            for r in responses
        ]
        scrubbed_responses = [scrub_data(r) for r in scrubbed_responses]

        col_titles = [""]
        if not os.path.exists(scrubbed_csv_path):
            col_titles = [",".join(responses[0].keys()).upper().split(",")]

        csv_data = col_titles + [list(r.values()) for r in scrubbed_responses]
        add_rows_to_csv_report(scrubbed_csv_path, csv_data)


def add_rows_to_csv_report(csv_path: None | str, csv_data: list[list]):
    """
    This adds a row(s) to an existing csv report

    Args:
        csv_path: The path to the csv file. If path is None the default one is found and used.
        csv_data: The column to add to the report.
    """
    if type(csv_data) is not list:
        csv_data = [[csv_data]]

    with open(csv_path, "a+") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerows(csv_data)


def delete_last_n_rows_from_csv_report(csv_path: None | str, rows: int = 1):
    """
    This removes the last n row(s) from an existing csv report.

    Args:
        csv_path: The path to the csv file. If path is None the default one is found and used.
        rows: The last n rows to remove.
    """
    with open(csv_path, "r") as csv_file:
        data = [r for r in csv.reader(csv_file)]

    with open(csv_path, "w") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerows(data[:-rows])


def add_column_to_csv_report(csv_path: str, column: list):
    """
    This adds a column to an existing csv report

    Args:
        csv_path: The path to the csv file.
        column: The column to add to the report.
    """
    rows = read_csv(csv_path)

    rows_no_newlines = np.array([r for r in rows if r])
    normalized_column = np.array(
        [column[0]] + [""] * (len(rows_no_newlines) - len(column)) + column[1:]
    )
    new_rows = np.column_stack([rows_no_newlines, normalized_column]).tolist()

    newline_indices = [i for i in range(len(rows)) if not rows[i]]
    for ni in newline_indices:
        new_rows.insert(ni, [])

    with open(csv_path, "w") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerows(new_rows)
