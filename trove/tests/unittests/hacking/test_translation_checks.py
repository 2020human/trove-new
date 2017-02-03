#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from trove.hacking import translation_checks as tc
from trove.tests.unittests import trove_testtools


class HackingTestCase(trove_testtools.TestCase):

    def assertLinePasses(self, func, *args):
        def check_callable(f, *args):
            return next(f(*args))
        self.assertRaises(StopIteration, check_callable, func, *args)

    def assertLineFails(self, func, *args):
        self.assertIsInstance(next(func(*args)), tuple)

    def test_factory(self):
        def check_callable(fn):
            self.assertTrue(hasattr(fn, '__call__'))
        self.assertIsNone(tc.factory(check_callable))

    def test_log_translations(self):
        expected_marks = {
            'error': '_',
            'info': '_',
            'warning': '_',
            'critical': '_',
            'exception': '_',
        }
        logs = expected_marks.keys()
        debug = "LOG.debug('OK')"
        self.assertEqual(
            0, len(list(tc.validate_log_translations(debug, debug, 'f'))))
        for log in logs:
            bad = 'LOG.%s("Bad")' % log
            self.assertEqual(
                1, len(list(tc.validate_log_translations(bad, bad, 'f'))))
            ok = 'LOG.%s(_("OK"))' % log
            self.assertEqual(
                0, len(list(tc.validate_log_translations(ok, ok, 'f'))))
            ok = "LOG.%s('OK')    # noqa" % log
            self.assertEqual(
                0, len(list(tc.validate_log_translations(ok, ok, 'f'))))
            ok = "LOG.%s(variable)" % log
            self.assertEqual(
                0, len(list(tc.validate_log_translations(ok, ok, 'f'))))
            # Do not do validations in tests
            ok = 'LOG.%s("OK - unit tests")' % log
            self.assertEqual(
                0, len(list(tc.validate_log_translations(ok, ok,
                                                         'f/tests/f'))))

            for mark in tc._all_hints:
                stmt = "LOG.%s(%s('test'))" % (log, mark)
                self.assertEqual(
                    0 if expected_marks[log] == mark else 1,
                    len(list(tc.validate_log_translations(stmt, stmt, 'f'))))

    def test_no_translate_debug_logs(self):
        for hint in tc._all_hints:
            bad = "LOG.debug(%s('bad'))" % hint
            self.assertEqual(
                1, len(list(tc.no_translate_debug_logs(bad, 'f'))))

    def test_check_localized_exception_messages(self):
        f = tc.check_raised_localized_exceptions
        self.assertLineFails(f, "     raise KeyError('Error text')", '')
        self.assertLineFails(f, ' raise KeyError("Error text")', '')
        self.assertLinePasses(f, ' raise KeyError(_("Error text"))', '')
        self.assertLinePasses(f, ' raise KeyError(_ERR("Error text"))', '')
        self.assertLinePasses(f, " raise KeyError(translated_msg)", '')
        self.assertLinePasses(f, '# raise KeyError("Not translated")', '')
        self.assertLinePasses(f, 'print("raise KeyError("Not '
                                 'translated")")', '')

    def test_check_localized_exception_message_skip_tests(self):
        f = tc.check_raised_localized_exceptions
        self.assertLinePasses(f, "raise KeyError('Error text')",
                              'neutron_lib/tests/unit/mytest.py')
