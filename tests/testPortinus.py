from pathlib import Path
from unittest.mock import patch, mock_open
import shutil
import unittest

import portinus
from portinus.portinus import Service, ComposeSource, EnvironmentFile

test_dir = Path(__file__).absolute().parent
test_data_dir = Path(test_dir).joinpath("testdata")


class testComposeSource(unittest.TestCase):
    
    def setUp(self):
        self.real_app = str(test_data_dir.joinpath('real_app'))
        self.empty_dir = str(test_data_dir.joinpath('empty_dir'))
        self.non_existent_dir = str(test_data_dir.joinpath('i-dont-exist'))

    def test_init_no_file(self):
        cs = ComposeSource('foo')

    def test_init_non_existent_source(self):
        with self.assertRaises(FileNotFoundError):
            ComposeSource('foo', source=self.non_existent_dir)

    def test_init_empty_source(self):
        with self.assertRaises(FileNotFoundError):
            ComposeSource('foo', source=self.empty_dir)

    def test_init_existent_source(self):
        cs = ComposeSource('foo', source=self.real_app)

    @patch('shutil.rmtree')
    def test_remove_no_source(self, fake_rmtree):
        cs = ComposeSource('foo')
        cs.remove()
        self.assertTrue(fake_rmtree.called)
        fake_rmtree.called_with(1)

    @patch('shutil.rmtree', side_effect=FileNotFoundError)
    def test_remove_exception(self, fake_rmtree):
        cs = ComposeSource('foo')
        cs.remove()
        self.assertTrue(fake_rmtree.called)

    @patch('shutil.rmtree')
    def test_remove_with_source(self, fake_rmtree):
        cs = ComposeSource('foo', source=self.real_app)
        cs.remove()
        self.assertTrue(fake_rmtree.called)

    def test_ensure_no_source(self):
        cs = ComposeSource('foo')
        with self.assertRaises(IOError):
            cs.ensure()

    @patch.object(ComposeSource, 'remove')
    @patch.object(ComposeSource, '_ensure_service_script')
    @patch('shutil.copytree')
    def test_ensure_with_source(self, fake_copytree, fake__ensure_service_script, fake_remove):
        cs = ComposeSource('foo', source=self.real_app)
        cs.ensure()
        self.assertTrue(fake_remove.called)
        self.assertTrue(fake_copytree.called)
        self.assertTrue(fake__ensure_service_script.called)

    @patch('shutil.copy')
    @patch('os.chmod')
    def test__ensure_service_script(self, fake_chmod, fake_shutil_copy):
        cs = ComposeSource('foo')
        cs._ensure_service_script()
        fake_chmod.called_with(cs.service_script, 0o755)
        self.assertEqual(fake_shutil_copy.called, 1)


class testEnvironmentFile(unittest.TestCase):
    
    def setUp(self):
        self.real_environment_file = str(test_data_dir.joinpath('real_app/environmentfile'))

    def test_init_no_file(self):
        env = EnvironmentFile('foo')
        self.assertFalse(env)

    def test_init_non_existent_file(self):
        non_existent_file = str(test_data_dir.joinpath('i-dont-exist'))
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

class testService(unittest.TestCase):
    
    def setUp(self):
        pass
