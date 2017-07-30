import unittest
from pathlib import Path
from unittest.mock import patch

from portinus import ComposeSource

class testComposeSource(unittest.TestCase):
    
    def setUp(self):
        self.test_dir = Path(__file__).absolute().parent
        self.test_data_dir = Path(self.test_dir).joinpath("testdata")
        self.real_app = str(self.test_data_dir.joinpath('real_app'))
        self.empty_dir = str(self.test_data_dir.joinpath('empty_dir'))
        self.non_existent_dir = str(self.test_data_dir.joinpath('i-dont-exist'))

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
