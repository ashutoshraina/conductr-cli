from unittest import TestCase
from unittest.mock import patch, MagicMock

from conductr_cli.conductr_restore import unpack_backup


class TestConductrRestore(TestCase):

    @patch('tempfile.mkdtemp')
    @patch('shutil.unpack_archive')
    def test_unpack_backup(self, archive_mock, tmp_mock):
        backup = MagicMock()
        tmp_mock.return_value = "something"
        result = unpack_backup(backup)

        archive_mock.assert_called_once_with(backup, tmp_mock.return_value)
        self.assertEqual(tmp_mock.return_value, result)
