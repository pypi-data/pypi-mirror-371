import sys
import tempfile
import unittest
import logging
from unittest.mock import MagicMock, patch

from slidetextbridge.core import main

@unittest.skipUnless(sys.version_info >= (3, 12), 'delete_on_close requires Python >= 3.12')
class TestMainFailure(unittest.TestCase):

    @patch('logging.getLogger')
    def test_empty_config(self, mock_logger):
        with tempfile.NamedTemporaryFile(mode='w', delete_on_close=False) as fc:
            fc.write('steps:')
            fc.close()

            mock_logger.return_value = MagicMock()
            mock_error = mock_logger.return_value.error

            with patch('sys.argv', ['test', '-c', fc.name]):
                ret = main.main()

            self.assertNotEqual(ret, 0)
            # TODO: Better message
            self.assertIn('Failed to start', mock_error.call_args_list[0][0][0])

    @patch('logging.getLogger')
    def test_src_connection_fail(self, mock_logger):
        with tempfile.NamedTemporaryFile(mode='w', delete_on_close=False) as fc:
            fc.write('''
            steps:
              - type: stdout
             ''')
            fc.close()

            mock_logger.return_value = MagicMock()
            mock_error = mock_logger.return_value.error

            with patch('sys.argv', ['test', '-c', fc.name]):
                ret = main.main()

            self.assertNotEqual(ret, 0)
            self.assertIn('Cannot connect to the source', mock_error.call_args_list[0][0][0])

    @patch('logging.getLogger')
    def test_no_type(self, mock_logger):
        with tempfile.NamedTemporaryFile(mode='w', delete_on_close=False) as fc:
            fc.write('''
            steps:
              - json: true
             ''')
            fc.close()

            mock_logger.return_value = MagicMock()
            mock_error = mock_logger.return_value.error

            with patch('sys.argv', ['test', '-c', fc.name]):
                ret = main.main()

            self.assertNotEqual(ret, 0)
            self.assertIn('A field "type" is missing.', mock_error.call_args_list[0][0][0])

    @patch('logging.getLogger')
    def test_wrong_type(self, mock_logger):
        with tempfile.NamedTemporaryFile(mode='w', delete_on_close=False) as fc:
            fc.write('''
            steps:
              - type: invalid-type
             ''')
            fc.close()

            mock_logger.return_value = MagicMock()
            mock_error = mock_logger.return_value.error

            with patch('sys.argv', ['test', '-c', fc.name]):
                ret = main.main()

            self.assertNotEqual(ret, 0)
            self.assertIn('No such type', mock_error.call_args_list[0][0][0])

    @patch('logging.getLogger')
    def test_wrong_step_field(self, mock_logger):
        with tempfile.NamedTemporaryFile(mode='w', delete_on_close=False) as fc:
            fc.write('''
            steps:
              - type: openlp
                invalid_field: 'error'
             ''')
            fc.close()

            mock_logger.return_value = MagicMock()
            mock_error = mock_logger.return_value.error

            with patch('sys.argv', ['test', '-c', fc.name]):
                ret = main.main()

            self.assertNotEqual(ret, 0)
            self.assertIn('Failed to start', mock_error.call_args_list[0][0][0])
            self.assertIn('is undefined', str(mock_error.call_args_list[0][0][1]))

    @patch('logging.getLogger')
    def test_wrong_src(self, mock_logger):
        with tempfile.NamedTemporaryFile(mode='w', delete_on_close=False) as fc:
            fc.write('''
            steps:
              - type: openlp
                name: name1
              - type: stdout
                src: test-invalid-name
             ''')
            fc.close()

            mock_logger.return_value = MagicMock()
            mock_error = mock_logger.return_value.error

            with patch('sys.argv', ['test', '-c', fc.name]):
                ret = main.main()

            self.assertNotEqual(ret, 0)
            self.assertIn('Cannot connect to the source.', mock_error.call_args_list[0][0][0])
            self.assertIn('test-invalid-name', str(mock_error.call_args_list[0][0][1]))
            self.assertIn('Failed to start', str(mock_error.call_args_list[1][0][0]))

class TestMainLogLevels(unittest.TestCase):
    @patch('logging.getLogger')
    def test_args_verbose(self, mock_logger):
        levels = (
                ([], logging.INFO),
                (['-v'], logging.DEBUG),
                (['-q'], logging.WARNING),
                (['-qq'], logging.ERROR),
                (['-qqq'], logging.CRITICAL),
        )
        for log_args, exp_level in levels:
            with (patch('logging.basicConfig') as basicConfig, patch('sys.argv', ['test'] + log_args)):
                basicConfig.side_effect = StopIteration('test: stop the code here')
                main.main()
                basicConfig.assert_called_once_with(level=exp_level)

if __name__ == '__main__':
    unittest.main()
