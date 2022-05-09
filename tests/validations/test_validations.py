import os

import pytest

from apiautomationtools.validations.validations import Validations

pytestmark = pytest.mark.validations

root_dir = os.path.dirname(__file__)


def test_validate_references():
    validations = Validations(root_dir=root_dir)
    actual_path = f"{root_dir}/get_example_scrubbed.csv"
    mismatches = validations.validate_references(actual_path)
    assert not mismatches
    validations.logging.delete_run_info()


def test_validate_references_mismatch(safe=True):
    validations = Validations(root_dir=root_dir)
    actual_path = f"{root_dir}/get_example_scrubbed_mismatch.csv"
    mismatches = validations.validate_references(actual_path, safe=safe)

    assert mismatches
    assert mismatches[0]

    fields = [
        "values",
        "skipped_keys",
        "unscrubbed_refs",
        "actual_refs",
        "expected_refs",
    ]
    assert all(field in mismatches[0] for field in fields)

    expected_mismatches = [{"key": "ACTUAL_CODE", "d1": "404", "d2": "999"}]
    assert str(mismatches[0]["values"]) == str(expected_mismatches)

    validations.logging.delete_run_info()


def test_validate_references_mismatch_not_safe():
    try:
        test_validate_references_mismatch(safe=False)
        raise AssertionError
    except Exception as e:
        if type(e) is AssertionError:
            assert False
    Validations(root_dir=root_dir).logging.delete_run_info()


def test_fail_no_debug():
    validations = Validations(root_dir=root_dir)
    log_file_path = validations.logging.log_file_path

    try:
        validations.fail("Error message")
    except:
        with open(log_file_path, "r") as f:
            logs = f.read()
        assert "Error message" in logs
        assert "Debugging the raise.\n" not in logs

    validations.logging.delete_run_info()


def test_fail_debug():
    validations = Validations(root_dir=root_dir, debug=True)
    log_file_path = validations.logging.log_file_path
    validations.fail("Error message")

    with open(log_file_path, "r") as f:
        logs = f.read()
    assert "Error message" in logs
    assert "Debugging the raise.\n" in logs

    validations.logging.delete_run_info()
