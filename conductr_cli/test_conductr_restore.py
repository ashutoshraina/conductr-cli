import os
from unittest import TestCase, mock
from unittest.mock import patch, MagicMock, call

from conductr_cli.bundle_core_info import BundleCoreInfo
from conductr_cli.conductr_restore import unpack_backup, process_bundle


class TestConductrRestore(TestCase):
    @patch('tempfile.mkdtemp')
    @patch('shutil.unpack_archive')
    def test_unpack_backup(self, archive_mock, tmp_mock):
        backup = MagicMock()
        tmp_mock.return_value = "something"
        result = unpack_backup(backup)

        archive_mock.assert_called_once_with(backup, tmp_mock.return_value)
        self.assertEqual(tmp_mock.return_value, result)

    @patch('conductr_cli.control_protocol.load_bundle')
    @patch('requests_toolbelt.MultipartEncoder')
    @patch('conductr_cli.bundle_utils.conf')
    def test_process_bundle(self, mock_conf, mock_encoder, mock_load_bundle):
        mock_args = MagicMock()
        mock_conf.return_value = 'hello'
        mock_encoder.return_value = MagicMock()
        bundle_info = BundleCoreInfo('1', 'b_name', '1234', '5678')
        open_mock = mock.mock_open()

        with patch('builtins.open', open_mock):
            process_bundle(mock_args, 'yolo', bundle_info)

        calls = [call(os.path.join('yolo', 'b_name-1234.zip'), 'rb'),
                 call(os.path.join('yolo', 'b_name-5678.zip'), 'rb')]
        open_mock.assert_has_calls(calls)

        conf_calls = [call(os.path.join('yolo', 'b_name-1234.zip')),
                      call(os.path.join('yolo', 'b_name-5678.zip'))]
        mock_conf.assert_has_calls(conf_calls)

        mock_load_bundle.assert_called_once_with(mock_args, mock_encoder.return_value)

    @patch('conductr_cli.control_protocol.load_bundle')
    @patch('requests_toolbelt.MultipartEncoder')
    @patch('conductr_cli.bundle_utils.conf')
    def test_process_bundle_with_no_configuration(self, mock_conf, mock_encoder, mock_load_bundle):
        mock_args = MagicMock()
        mock_conf.return_value = 'hello'
        mock_encoder.return_value = MagicMock()
        bundle_info = BundleCoreInfo('1', 'b_name', '1234', '')
        open_mock = mock.mock_open()

        with patch('builtins.open', open_mock):
            process_bundle(mock_args, 'yolo', bundle_info)

        open_mock.assert_called_once_with(os.path.join('yolo', 'b_name-1234.zip'), 'rb')
        mock_conf.assert_called_once_with(os.path.join('yolo', 'b_name-1234.zip'))

        mock_load_bundle.assert_called_once_with(mock_args, mock_encoder.return_value)
