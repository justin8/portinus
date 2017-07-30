from unittest.mock import patch
import unittest

from jinja2 import Template
from pathlib import Path

import portinus

class TestMonitorInit(unittest.TestCase):

    def setUp(self):
        pass

    @patch('systemd_unit.Unit')
    def test_init(self, fake_unit):
        res = portinus.monitor.Service('foo')

    @patch('systemd_unit.Unit')
    @patch('portinus.get_template')
    def test__generate_service_file(self, fake_get_template, fake_unit):
        service = portinus.monitor.Service('foo')
        fake_get_template.return_value = Template("qwe {{name}} asd")
        expected_output = "qwe foo asd"
        output = service._generate_service_file()
        self.assertEqual(output, expected_output)

    @patch('systemd_unit.Unit')
    @patch('portinus.get_template')
    def test__generate_timer_file(self, fake_get_template, fake_unit):
        service = portinus.monitor.Service('foo')
        fake_get_template.return_value = Template("qwe {{name}} asd")
        expected_output = "qwe foo asd"
        output = service._generate_service_file()
        self.assertEqual(output, expected_output)
        
    @patch('systemd_unit.Unit')
    def test_ensure(self, fake_unit):
        service = portinus.monitor.Service('foo')
        service.ensure()
        self.assertEqual(fake_unit().ensure.call_count, 2)
        
    @patch('systemd_unit.Unit')
    def test_remove(self, fake_unit):
        service = portinus.monitor.Service('foo')
        service.remove()
        self.assertEqual(fake_unit().remove.call_count, 2)
