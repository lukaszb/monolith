import io
import argparse
from monolith.compat import unittest
from monolith.cli.completion import CompletionCommand


class TestCompletionCommand(unittest.TestCase):

    def test_get_env_var_name(self):
        command = CompletionCommand('foo')
        self.assertEqual(command.get_env_var_name(), 'FOO_AUTO_COMPLETE')

    def test_get_completion_snippet(self):
        command = CompletionCommand('foo')
        command.template = '%(prog_name)s | %(ENV_VAR_NAME)s'
        self.assertEqual(command.get_completion_snippet(),
            'foo | FOO_AUTO_COMPLETE')

    def test_handle(self):
        stream = io.StringIO()
        command = CompletionCommand('foo', stream)
        command.template = 'bar'
        command.handle(argparse.Namespace())
        self.assertEqual(stream.getvalue(), 'bar')

