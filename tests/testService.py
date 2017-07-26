import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

import systemd_unit

import portinus
from portinus import Service


class testService(unittest.TestCase):
    
    def setUp(self):
        self.test_dir = Path(__file__).absolute().parent
        self.test_data_dir = Path(self.test_dir).joinpath("testdata")
        self.real_app = str(self.test_data_dir.joinpath('real_app'))
        self.empty_dir = str(self.test_data_dir.joinpath('empty_dir'))
        self.non_existent_dir = str(self.test_data_dir.joinpath('i-dont-exist'))

    @patch.object(portinus, 'ComposeSource')
    @patch.object(systemd_unit, 'Unit')
    def test_init_no_source(self, fake_unit, fake_compose_source):
        service = Service('foo')
        fake_unit.assert_called_with('portinus-foo')
        fake_compose_source.assert_called_with('foo', None)

    @patch.object(portinus, 'ComposeSource')
    @patch.object(systemd_unit, 'Unit')
    def test_init_real_source(self, fake_unit, fake_compose_source):
        service = Service('foo', self.real_app)
        fake_unit.assert_called_with('portinus-foo')
        fake_compose_source.assert_called_with('foo', self.real_app)

    @patch.object(systemd_unit, 'Unit')
    @patch('os.path.isdir', return_value=True)
    def test_exists_non_existent_dir(self, fake_isdir, fake_unit):
        service = Service('foo')
        service.exists()
        self.assertTrue(fake_isdir.called)

    @patch.object(portinus.Service, 'exists', return_value=True)
    @patch.object(systemd_unit, 'Unit')
    @patch('subprocess.call')
    def test_compose(self, fake_call, fake_unit, fake_exists):
        service = Service('foo')
        service.compose(['ps'])
        fake_call.assert_called_with([service._source.service_script, 'ps'])

        service.compose(['logs', 'foo'])
        fake_call.assert_called_with([service._source.service_script, 'logs', 'foo'])

    @patch.object(systemd_unit, 'Unit')
    def test_stop(self, fake_unit):
        service = Service('foo')
        service._systemd_service = MagicMock()
        service.stop()
        self.assertTrue(service._systemd_service.stop.called)

    @patch('subprocess.check_output')
    def test_restart(self, fake_check_output):
        service = Service('foo')
        service._systemd_service.restart = MagicMock()
        service.restart()
        self.assertTrue(service._systemd_service.restart.called)

    @patch.object(systemd_unit, 'Unit')
    @patch.object(portinus.ComposeSource, 'remove')
    def test_remove(self, fake_compose_remove, fake_unit):
        service = Service('foo')
        service._systemd_service.remove = MagicMock()
        service.remove()
        self.assertTrue(fake_compose_remove.called)
        self.assertTrue(service._systemd_service.remove.called)

    @patch('subprocess.check_output')
    @patch.object(portinus.ComposeSource, 'ensure')
    @patch.object(systemd_unit.Unit, 'ensure')
    def test_ensure(self, fake_check_output, fake_compose_ensure, fake_unit_ensure):
        service = Service('foo')
        service.ensure()
        self.assertTrue(fake_compose_ensure.called)
        self.assertTrue(fake_unit_ensure.called)

    @patch('subprocess.check_output')
    def test__generate_service_file(self, fake_check_output):
        service = Service('foo')
        service_file = service._generate_service_file()
        if not '[Unit]' in service_file:
            raise(AssertionError('[Unit] not found in service_file'))
