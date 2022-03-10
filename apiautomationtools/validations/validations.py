import os
import re
import difflib
from glob import iglob

from apiautomationtools.logging import Logger
import apiautomationtools.reporting.response_csv as rc
import apiautomationtools.helpers.directory_helpers as dir_help
import apiautomationtools.helpers.dictionary_helpers as dict_help


class Validations(object):
    """
    This is the class that hold all the ways we gather and use information for validations.
    """
    def __init__(self, debug=False):
        """
        The constructor for Validations.

        Args:
            debug (bool): Whether to catch exceptions in the fail method.
        """
        self.debug = debug
        self.logging = Logger()
        self.logger = self.logging.logger

        app_dir = dir_help.get_src_app_dir()
        project_dir = dir_help.get_root_dir()
        refs_dir = f'{project_dir}/validations/{app_dir}'
        refs_dir = os.path.dirname(refs_dir)
        self.refs_paths = [ref for ref in iglob(f'{refs_dir}//**', recursive=True) if '.csv' in ref]

    def validate_references(self, actual_refs, expected_refs=None, safe=True):
        """
        This validates stored json responses. Unfortunately if actual_refs is a string
        the expected_refs must be passed.

        Args:
            actual_refs (str|dict): The actual(current) refs or path to validate.
            expected_refs (None|str|dict): The expected(stored) refs or path to use as a reference.
            safe (bool): Whether to raise an error on mismatches.

        Returns:
            mismatches (dict): A record of any mismatching keys and or values.
        """
        self.logger.info(f'Validating references for {actual_refs}.')

        live_file = None
        if type(actual_refs) is str:
            live_file = actual_refs.split('/')[-1]
            actual_refs = rc.csv_to_dict(actual_refs)

        if type(expected_refs) is not dict:
            expected_refs = expected_refs or next((r for r in self.refs_paths if live_file == r.split('/')[-1]), [])
            if expected_refs:
                expected_refs = rc.csv_to_dict(expected_refs)

        if len(actual_refs) != len(expected_refs):
            message = f"Test completed HOWEVER, verification isn't possible as the " \
                      f"actual and expected reference files aren't the same size."
            self.fail(message)
        unscrubbed_refs = rc.csv_to_dict(self.logging.log_file_path.replace('.log', '.csv'))

        mismatches = []
        for i in range(len(unscrubbed_refs)):
            u_refs = unscrubbed_refs[i]
            a_refs = actual_refs[i]
            e_refs = expected_refs[i]
            errors = dict_help.async_compare_dictionaries(a_refs, e_refs, exclusive_keys=['ACTUAL_CODE', 'JSON'])

            e_values = errors.get('values')
            if e_values:
                differ = difflib.Differ()
                e_val_copy = e_values[:]
                for e in e_val_copy:
                    if 'json.' in e['key'].lower() and re.findall(r'[._](url|icon|manifest)', e['key'].lower()):
                        diffs = differ.compare(e['d1'], e['d2'])
                        diffs = [re.sub(r'[-+]\s+', '', d) for d in diffs if '- ' in d or '+ ' in d]
                        diffs = ''.join(diffs)
                        if 'stg' in diffs and 'dev' in diffs:
                            e_values = [ev for ev in e_values if ev != e]

            if errors.get('keys') or e_values:
                errors['unscrubbed_refs'] = u_refs
                errors['actual_refs'] = a_refs
                errors['expected_refs'] = e_refs
                mismatches.append(errors)

        if len(mismatches) > 0 and not safe:
            self.fail(f'Validated references with mismatches {mismatches}.')

        self.logger.info(f'Validated references for {actual_refs}.')
        return mismatches

    def fail(self, error_message, exception=Exception):
        """
        This fails a test.
        Note: If self.debug mode is True put a breakpoint on line 111 to pause at the exception.

        Args:
            error_message (str): The failure message to log.
            exception (None|exception): The python exception to raise.
        """
        self.logger.error(error_message)
        if not self.debug:
            raise exception(error_message)
        else:
            try:
                raise exception(error_message)
            except exception:
                self.logger.error('Debugging the raise.\n')
