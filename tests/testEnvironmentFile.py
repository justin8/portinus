import unittest
from pathlib import Path
from unittest.mock import patch
import shutil

from portinus import EnvironmentFile

class testEnvironmentFile(unittest.TestCase):
    
    def setUp(self):
        self.test_dir = Path(__file__).absolute().parent
        self.test_data_dir = Path(self.test_dir).joinpath("testdata")
        self.real_environment_file = str(self.test_data_dir.joinpath('real_app/environmentfile'))

    def test_init_no_file(self):
        env = EnvironmentFile('foo')
        self.assertFalse(env)

    def test_init_non_existent_file(self):
        non_existent_file = str(self.test_data_dir.joinpath('i-dont-exist'))
        try:
            EnvironmentFile('foo', source_environment_file=non_existent_file)
        except FileNotFoundError:
            pass

    def test_init_good_file(self):
        env = EnvironmentFile('foo', source_environment_file=self.real_environment_file)
        self.assertTrue(env)

    @patch('os.remove')
    def test_remove(self, fake_remove):
        env = EnvironmentFile('foo')
        env.remove()
        fake_remove.assert_called_with(env.path)

    @patch('os.remove', side_effect=FileNotFoundError)
    def test_remove_no_file(self, fake_remove):
        env = EnvironmentFile('foo')
        try:
            env.remove()
        except FileNotFoundError:
            pass
        fake_remove.assert_called_with(env.path)

    @patch('os.remove')
    def test_remove_with_source(self, fake_remove):
        env = EnvironmentFile('foo', source_environment_file=self.real_environment_file)
        env.remove()
        fake_remove.assert_called_with(env.path)

    @patch.object(shutil, 'copy')
    def test_ensure(self, fake_copy):
        env = EnvironmentFile('foo', source_environment_file=self.real_environment_file)
        env.ensure()
        self.assertTrue(env)
        self.assertTrue(fake_copy.called)

    @patch.object(EnvironmentFile, 'remove')
    def test_ensure_no_source(self, fake_remove):
        env = EnvironmentFile('foo')
        env.ensure()
        self.assertTrue(fake_remove.called)

