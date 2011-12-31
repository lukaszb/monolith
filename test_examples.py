import io
import os
import sys
from monolith.compat import unittest

EXAMPLES_DIR = os.path.abspath('examples')
sys.path.insert(0, EXAMPLES_DIR)

from git import get_manager


class TestGitManager(unittest.TestCase):

    def setUp(self):
        self.stdout = io.StringIO()
        self.manager = get_manager(stdout=self.stdout)

    def test_execute_add(self):
        self.manager.execute('add foo bar'.split())
        self.assertEqual(self.manager.stdout.getvalue(), '\n'.join((
            'A foo',
            'A bar',
            '',
        )))

if __name__ == '__main__':
    unittest.main()

