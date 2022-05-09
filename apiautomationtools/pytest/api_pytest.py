import json
import os
import re
import shutil
import sys
import traceback
from glob import iglob

import apiautomationtools.helpers.directory_helpers as dir_help
import apiautomationtools.reporting.response_csv as rc
from apiautomationtools.validations import Validations


class ApiPytestHelper(object):
    root_dir = dir_help.get_root_dir()
    csv_path = None
    tests_data = None
    credentials_data = None

    # Custom on-end options to be run as part of the teardown
    validate = True
    debug = False
    validations = None

    def set_data(self, _dir: str):
        data_dir = f"{self.root_dir}/{_dir}"
        files = [p for p in iglob(f"{data_dir}//**", recursive=True) if ".json" in p]
        data = {
            os.path.basename(f).split(".")[0]: {
                "data": dir_help.load_json(f),
                "path": f,
            }
            for f in files
        }
        setattr(ApiPytestHelper, f"{_dir}_data", data)

    def setup_class(self):
        self.set_data(self, "tests")
        self.set_data(self, "credentials")

    def teardown_class(self):
        last_value = sys.__dict__.get("last_value")
        if last_value and "exit" not in last_value.args[0]:
            trace = [
                t for t in traceback.format_tb(sys.last_traceback) if self.root_dir in t
            ]
            trace = "".join(trace + [f"\t{sys.last_value}"])
            self.api_testing.async_requests.logger.error(f"\n{trace}")

            log_file_path = self.api_testing.async_requests.logging.log_file_path
            new_csv_path = self.csv_path.replace("/pass/", "/fail/")

            shutil.move(log_file_path, log_file_path.replace("/pass/", "/fail/"))
            shutil.move(self.csv_path, new_csv_path)
            shutil.move(
                self.csv_path.replace(".csv", "_scrubbed.csv"),
                new_csv_path.replace(".csv", "_scrubbed.csv"),
            )
            self.csv_path = new_csv_path

            rc.add_rows_to_csv_report(self.csv_path, f"{trace}")
            rc.add_rows_to_csv_report(
                self.csv_path.replace(".csv", "_scrubbed.csv"), f"{trace}"
            )

        if self.validate and "/fail/" not in self.csv_path:
            if not getattr(ApiPytestHelper, "validations"):
                self.validations = Validations(debug=self.debug, root_dir=self.root_dir)

            mismatches = self.validations.validate_references(
                self.csv_path.replace(".csv", "_scrubbed.csv")
            )
            if mismatches:
                rows = []
                for m in mismatches:
                    headers = [""] + list(
                        dict.fromkeys(
                            list(m["actual_refs"].keys())
                            + list(m["expected_refs"].keys())
                        )
                    )
                    rows or rows.append(headers)

                    keys = list(
                        dict.fromkeys(
                            ["expected_refs", "actual_refs", "unscrubbed_refs"]
                            + list(m.keys())
                        )
                    )
                    rows += [
                        [k] + [m[k][h] if m[k].get(h) else "" for h in headers if h]
                        if type(m[k]) is dict
                        else [f"error_{k}"] + [json.dumps((m[k]))]
                        for k in keys
                        if "skip" not in k
                    ] + [""]

                error_file = re.sub(
                    r"/run_logs/",
                    "/run_errors/",
                    self.csv_path.replace(".csv", "_errors.csv"),
                )
                error_file = re.sub(r"/pass/|/fail/", "/", error_file)
                error_dir = "/".join(error_file.split("/")[:-1])
                dir_help.safe_mkdirs(error_dir)
                rc.add_rows_to_csv_report(error_file, rows)
