import unittest
import sys
import os
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from arch_store.backend.aur_api import AurApi
from arch_store.backend.package_manager import PackageManager

class TestAurApi(unittest.TestCase):
    def test_search(self):
        api = AurApi()
        # Mock requests.get
        with patch('requests.Session.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {'results': [{'Name': 'test-package', 'Version': '1.0'}]}
            mock_get.return_value = mock_response
            
            results = api.search('test')
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0]['Name'], 'test-package')

class TestPackageManager(unittest.TestCase):
    def setUp(self):
        self.pm = PackageManager()

    @patch('subprocess.run')
    def test_is_installed(self, mock_run):
        mock_run.return_value.returncode = 0
        self.assertTrue(self.pm.is_installed('python'))
        
        mock_run.side_effect = subprocess.CalledProcessError(1, 'cmd')
        self.assertFalse(self.pm.is_installed('non-existent'))

    @patch('subprocess.run')
    def test_get_installed_version(self, mock_run):
        mock_run.return_value.stdout = "python 3.10.0"
        self.assertEqual(self.pm.get_installed_version('python'), '3.10.0')

    @patch('subprocess.run')
    def test_check_updates(self, mock_run):
        # Mock pacman -Qm and pacman -Q
        mock_run.side_effect = [
            MagicMock(stdout="test-package 1.0\n"), # pacman -Qm
            MagicMock(stdout="test-package 1.0\n")  # pacman -Q test-package
        ]
        
        # Mock AurApi
        with patch('arch_store.backend.aur_api.AurApi.get_info') as mock_info:
            mock_info.return_value = [{'Name': 'test-package', 'Version': '1.1'}]
            
            # Mock vercmp call inside check_updates
            # We need to be careful with side_effect order if check_updates calls subprocess multiple times
            # It calls pacman -Qm first. Then vercmp.
            
            # Let's just mock compare_versions to make it easier
            with patch.object(self.pm, 'compare_versions', return_value=-1):
                updates = self.pm.check_updates()
                self.assertEqual(len(updates), 1)
                self.assertEqual(updates[0]['Name'], 'test-package')

if __name__ == '__main__':
    import subprocess # Re-import for the test method usage
    unittest.main()
