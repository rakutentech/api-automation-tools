import difflib
import os.path
import re
from glob import iglob
from typing import Any

import apiautomationtools.helpers.dictionary_helpers as dict_help
import apiautomationtools.helpers.directory_helpers as dir_help
import apiautomationtools.reporting.response_csv as rc
from apiautomationtools.logging import Logger


class Validations(object):
    """
    This is the class that hold all the ways we gather and use information for validations.
    """

    def __init__(self, debug: bool = False, root_dir: None | str = None):
        """
        The constructor for Validations.

        Args:
            debug: Whether to catch exceptions in the fail method.
            root_dir: The specified root directory.
        """
        self.debug = debug
        Logger().get_logger(root_dir=root_dir)
        self.logging = Logger()
        self.logger = self.logging.logger

        app_dir = dir_help.get_src_app_dir()
        project_dir = root_dir or dir_help.get_root_dir()
        refs_dir = next(
            (
                ref
                for ref in iglob(f"{project_dir}//**", recursive=True)
                if f"/validations/{app_dir}" in ref
            ),
            None,
        )
        self.refs_paths = [
            ref for ref in iglob(f"{refs_dir}//**", recursive=True) if ".csv" in ref
        ]

    def validate_references(
        self,
        actual_refs: str,
        expected_refs: None | str = None,
        safe: bool = True,
    ) -> list[dict]:
        """
        This validates stored json responses. Unfortunately if actual_refs is a string
        the expected_refs must be passed.

        Args:
            actual_refs: The actual (current) path of refs to validate.
            expected_refs: The expected (stored) path of refs to use as a reference.
            safe: Whether to raise an error on mismatches.

        Returns:
            mismatches: A record of any mismatching keys and or values.
        """
        self.logger.info(f"Validating references for {actual_refs}.")

        live_file = os.path.basename(actual_refs)
        _actual_refs = rc.csv_to_dict(actual_refs)

        _expected_refs = expected_refs or next(
            (r for r in self.refs_paths if os.path.basename(r) == live_file), []
        )
        if _expected_refs:
            _expected_refs = rc.csv_to_dict(_expected_refs)

        if len(_actual_refs) != len(_expected_refs):
            message = (
                f"Test completed HOWEVER, verification isn't possible as the "
                f"actual and expected reference files aren't the same size."
            )
            self.fail(message)

        unscrubbed_refs = rc.csv_to_dict(actual_refs.replace("_scrubbed.csv", ".csv"))

        mismatches = []
        for i in range(len(unscrubbed_refs)):
            u_refs = unscrubbed_refs[i]
            a_refs = _actual_refs[i]
            e_refs = _expected_refs[i]
            errors = dict_help.compare_dictionaries(
                a_refs, e_refs, exclusive_keys=["ACTUAL_CODE", "JSON"]
            )

            e_values = errors.get("values")
            if e_values:
                differ = difflib.Differ()
                e_val_copy = e_values[:]
                for e in e_val_copy:
                    if "json." in e["key"].lower() and re.findall(
                        r"[._](url|icon|manifest)", e["key"].lower()
                    ):
                        diffs = differ.compare(e["d1"], e["d2"])
                        diffs = [
                            re.sub(r"[-+]\s+", "", d)
                            for d in diffs
                            if "- " in d or "+ " in d
                        ]
                        diffs = "".join(diffs)
                        if "stg" in diffs and "dev" in diffs:
                            e_values = [ev for ev in e_values if ev != e]

            if errors.get("keys") or e_values:
                errors["unscrubbed_refs"] = u_refs
                errors["actual_refs"] = a_refs
                errors["expected_refs"] = e_refs
                mismatches.append(errors)

        if len(mismatches) > 0 and not safe:
            self.fail(f"Validated references with mismatches {mismatches}.")

        self.logger.info(f"Validated references for {actual_refs}.")
        return mismatches

    def fail(self, error_message: str, exception: Any = Exception):
        """
        This fails a test.
        Note: If self.debug mode is True put a breakpoint on line 111 to pause at the exception.

        Args:
            error_message: The failure message to log.
            exception: The python exception to raise.
        """
        self.logger.error(error_message)
        if not self.debug:
            raise exception(error_message)
        else:
            try:
                raise exception(error_message)
            except exception:
                self.logger.error("Debugging the raise.\n")
