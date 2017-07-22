import unittest
from unittest import mock
from unittest.mock import MagicMock, patch, PropertyMock

import systemd_unit
from jinja2 import Template
from systemd_unit import Unit
from portinus import restart

class testRestart(unittest.TestCase):

    @patch("subprocess.check_output")
    def setUp(self, mock_check_output):
        self.name = "foo"
        self.restart_schedule = "daily"
        self.notimer = restart.Timer(self.name, restart_schedule=None)
        self.timer = restart.Timer(self.name, restart_schedule=self.restart_schedule)

    def test_bool(self):
        self.assertFalse(self.notimer)
        self.assertTrue(self.timer)

    @patch("subprocess.check_output")
    def test_generate_service_file(self, fake_check_output):
        service_name = Unit(self.name).service_name
        template = "qwe {{ name }} {{service_name}}"
        expected_output = "qwe {} {}".format(self.name, service_name)
        with patch("portinus.get_template", return_value=Template(template)) as fake_get_template:
            output = self.timer._generate_service_file()
            fake_get_template.assert_called_with("restart.service")
            self.assertEqual(output, expected_output)

    @patch("subprocess.check_output")
    def test_generate_timer_file(self, fake_check_output):
        template = "qwe {{ name }} {{restart_schedule}}"
        expected_output = "qwe {} {}".format(self.name, self.restart_schedule)
        with patch("portinus.get_template", return_value=Template(template)) as fake_get_template:
            output = self.timer._generate_timer_file()
            fake_get_template.assert_called_with("restart.timer")
            self.assertEqual(output, expected_output)

    @patch.object(restart.Timer, "remove")
    def test_ensure_remove(self, fake_remove):
        self.notimer.ensure()
        fake_remove.assert_called_with()

    @patch.object(restart.Timer, "_generate_service_file", return_value="qwe")
    @patch.object(restart.Timer, "_generate_timer_file", return_value="qwe")
    @patch.object(systemd_unit.Unit, "ensure")
    def test_ensure_create(self,
                           fake_unit_ensure,
                           fake_generate_timer_file,
                           fake_generate_service_file):
        self.timer.ensure()
        fake_generate_timer_file.assert_called_with()
        fake_generate_service_file.assert_called_with()

    @patch.object(systemd_unit.Unit, "remove")
    def test_remove_timer(self, fake_remove):
        self.timer.remove()
        # Called once for the timer and once for the service.
        # Just checking count to keep it simple
        self.assertEqual(fake_remove.call_count, 2)

    @patch.object(systemd_unit.Unit, "remove")
    def test_remove_notimer(self, fake_remove):
        self.notimer.remove()
        # Called once for the timer and once for the service.
        # Just checking count to keep it simple
        self.assertEqual(fake_remove.call_count, 2)
