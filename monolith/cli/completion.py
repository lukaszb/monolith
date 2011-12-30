from monolith.compat import unicode
from monolith.cli.base import BaseCommand


COMPLETION_TEMPLATE = '''
# %(prog_name)s bash completion start
_%(prog_name)s_completion()
{
    COMPREPLY=( $( COMP_WORDS="${COMP_WORDS[*]}" \\
                   COMP_CWORD=$COMP_CWORD \\
                   %(ENV_VAR_NAME)s=1 $1 ) )
}
complete -o default -F _%(prog_name)s_completion %(prog_name)s
# %(prog_name)s bash completion end

'''


class CompletionCommand(BaseCommand):
    help = ''.join((
        'Prints out shell snippet that once evaluated would allow '
        'this command utility to use completion abilities.',
    ))
    template = COMPLETION_TEMPLATE

    def get_env_var_name(self):
        return '_'.join((self.prog_name.upper(), 'AUTO_COMPLETE'))

    def get_completion_snippet(self):
        return self.template % {'prog_name': self.prog_name,
            'ENV_VAR_NAME': self.get_env_var_name()}

    def handle(self, namespace):
        self.stdout.write(unicode(self.get_completion_snippet()))

    def post_register(self, manager):
        manager.completion = True
        manager.completion_env_var_name = self.get_env_var_name()

