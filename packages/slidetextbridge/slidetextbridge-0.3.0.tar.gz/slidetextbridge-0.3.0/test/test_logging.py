import sys
import tempfile
import unittest
import logging
from unittest.mock import MagicMock, patch

from slidetextbridge.core.logging import HideSameLogFilter

class _TestFilter(logging.Filter):
    def __init__(self):
        super().__init__()
        self.records = []

    def filter(self, record):
        self.records.append(record)
        return False

class TestHideSameLogFilter(unittest.TestCase):

    def test_all(self):
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)
        logger.addFilter(HideSameLogFilter(2))

        f = _TestFilter()
        logger.addFilter(f)

        logger.info('A')
        logger.info('B')
        logger.info('B')
        logger.info('C')
        logger.info('D')
        logger.info('B')
        logger.info('D')

        records = [r.msg for r in f.records]
        self.assertEqual(records, ['A', 'B', 'C', 'D', 'B'])

if __name__ == '__main__':
    unittest.main()
