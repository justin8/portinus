from unittest.mock import patch, PropertyMock
import unittest
from pathlib import Path

import jinja2

import portinus

test_dir = Path(__file__).absolute().parent
test_data_dir = Path(test_dir).joinpath("testdata")
portinus_dir = str(test_data_dir.joinpath('portinus_dir'))

class testInit(unittest.TestCase):

    def setUp(self):
        pass

    @patch.object(portinus, 'service_dir')
    @patch('builtins.print')
    def test_list(self, fake_print, fake_service_dir):
        portinus.service_dir = portinus_dir
        portinus.list()
        self.assertEqual(str(fake_print.mock_calls[-2]),"call('bar')")
        self.assertEqual(str(fake_print.mock_calls[-1]),"call('baz')")

    def test_get_instance_dir(self):
        res = portinus.get_instance_dir('foo')

    def test_get_template(self):
        template = portinus.get_template('instance.service')
        self.assertTrue(isinstance(template, jinja2.Template))

class testApplication(unittest.TestCase):

    def setUp(self):
        pass

    @patch('subprocess.check_output')
    @patch.object(portinus.restart, 'Timer')
    @patch.object(portinus.monitor, 'Service')
    def test_init(self, fake_monitor_service, fake_restart_timer, fake_check_output):
        app = portinus.Application('foo')
        self.assertTrue(fake_restart_timer.called)
        self.assertTrue(fake_monitor_service.called)
