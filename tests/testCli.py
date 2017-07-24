from pathlib import Path
from unittest.mock import patch
import logging
import unittest


from click.testing import CliRunner

from portinus import cli
import portinus

test_dir = Path(__file__).absolute().parent
test_data_dir = Path(test_dir).joinpath("testdata")


class testCli(unittest.TestCase):

    def setUp(self):
        self.runner = CliRunner()

    @patch("portinus.list")
    def test_list(self, fake_list):
        result = self.runner.invoke(cli.list)
        self.assertFalse(result.exception)
        fake_list.assert_called_with()

    @patch.object(portinus, "Application")
    def test_stop_success(self, fake_application):
        result = self.runner.invoke(cli.stop, ["foo"])
        self.assertFalse(result.exception)
        self.assertEqual(str(fake_application.mock_calls[0]),
                         "call('foo')")
        self.assertEqual(str(fake_application.mock_calls[1]),
                         "call().service.stop()")

    @patch.object(portinus, "Application")
    def test_stop_no_input(self, fake_application):
        result = self.runner.invoke(cli.stop, [])
        self.assertTrue(result.exception)
        self.assertEqual(fake_application.mock_calls, [])

    @patch.object(portinus, "Application")
    def test_restart_success(self, fake_application):
        result = self.runner.invoke(cli.restart, ["foo"])
        self.assertFalse(result.exception)
        self.assertEqual(str(fake_application.mock_calls[0]),
                         "call('foo')")
        self.assertEqual(str(fake_application.mock_calls[1]),
                         "call().service.restart()")

    @patch.object(portinus, "Application")
    def test_restart_no_input(self, fake_application):
        result = self.runner.invoke(cli.restart, [])
        self.assertTrue(result.exception)
        self.assertEqual(fake_application.mock_calls, [])

    @patch.object(portinus, "Application")
    def test_remove_success(self, fake_application):
        result = self.runner.invoke(cli.remove, ["foo"])
        self.assertFalse(result.exception)
        self.assertEqual(str(fake_application.mock_calls[0]), "call('foo')")
        self.assertEqual(str(fake_application.mock_calls[1]), "call().remove()")

    @patch.object(portinus, "Application")
    def test_remove_no_input(self, fake_application):
        result = self.runner.invoke(cli.remove, [])
        self.assertTrue(result.exception)
        self.assertEqual(fake_application.mock_calls, [])

    @patch.object(portinus, "Application", side_effect=PermissionError)
    def test_remove_permission_error(self, fake_application):
        result = self.runner.invoke(cli.remove, ["foo"])
        self.assertTrue(result.exception)

    @patch.object(portinus, "Application")
    def test_compose_no_args(self, fake_application):
        result = self.runner.invoke(cli.compose, [])
        self.assertTrue(result.exception)
        self.assertEqual(fake_application.mock_calls, [])

    @patch.object(portinus, "Application")
    def test_compose_one_arg(self, fake_application):
        result = self.runner.invoke(cli.compose, ["foo"])
        self.assertTrue(result.exception)
        self.assertEqual(fake_application.mock_calls, [])

    @patch.object(portinus, "Application")
    def test_compose_2_args(self, fake_application):
        result = self.runner.invoke(cli.compose, ["foo", "ps"])
        self.assertFalse(result.exception)
        self.assertEqual(str(fake_application.mock_calls[0]),
                         "call('foo')")
        self.assertEqual(str(fake_application.mock_calls[1]),
                         "call().service.compose(('ps',))")

    @patch.object(portinus, "Application")
    def test_compose_5_args(self, fake_application):
        result = self.runner.invoke(cli.compose, ["foo", "logs", "bar", "baz", "qwe"])
        self.assertFalse(result.exception)
        self.assertEqual(str(fake_application.mock_calls[0]), "call('foo')")
        self.assertEqual(
            str(fake_application.mock_calls[1]),
            "call().service.compose(('logs', 'bar', 'baz', 'qwe'))"
        )

    @patch.object(portinus, "Application")
    def test_ensure_no_args(self, fake_application):
        result = self.runner.invoke(cli.ensure, [])
        self.assertTrue(result.exception)
        self.assertEqual(fake_application.mock_calls, [])

    @patch.object(portinus, "Application")
    def test_ensure_no_source(self, fake_application):
        result = self.runner.invoke(cli.ensure, ["foo"])
        self.assertTrue(result.exception)
        self.assertEqual(fake_application.mock_calls, [])

    @patch.object(portinus, "Application")
    def test_ensure_non_existent_dir(self, fake_application):
        non_existent_dir = str(test_data_dir.joinpath('i-dont-exist'))
        result = self.runner.invoke(cli.ensure,
                                    ['--source', non_existent_dir, 'foo'])
        self.assertTrue(result.exception)

    @patch.object(portinus, "Application")
    def test_ensure_success(self, fake_application):
        real_app = str(test_data_dir.joinpath('real_app'))
        result = self.runner.invoke(cli.ensure, ['--source', real_app, 'foo'])
        self.assertFalse(result.exception)

        # python 3.4 seems to re-arrange arguments,
        # so we test for the source and not the order
        expected_source = "source='{}'".format(real_app)
        create_call = str(fake_application.mock_calls[0])
        if not expected_source in create_call:
            raise AssertionError(
                "{} not found in {}".format(expected_source, create_call)
                )
        self.assertEqual(str(fake_application.mock_calls[1]),
                             "call().ensure()")

    @patch('logging.basicConfig')
    def test_set_log_level(self, fake_logging):
        cli.set_log_level(0)
        fake_logging.assert_called_with(level=logging.WARNING)

        cli.set_log_level(1)
        fake_logging.assert_called_with(level=logging.INFO)

        cli.set_log_level(2)
        fake_logging.assert_called_with(level=logging.DEBUG)

        cli.set_log_level(10)
        fake_logging.assert_called_with(level=logging.DEBUG)

