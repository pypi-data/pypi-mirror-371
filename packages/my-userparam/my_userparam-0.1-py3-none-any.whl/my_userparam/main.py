#!/usr/bin/env python3

import sys
import typer
import logging
import logging.handlers
from termcolor import colored

from rich.console import Console
from .typers import alias, ssh, ssh_keys, totp


class CLILogHandler(logging.StreamHandler):
    def __init__(self, stream):
        logging.StreamHandler.__init__(self, stream)

    def handle(self, record):

        msg = record.msg % record.args

        if record.levelname == 'DEBUG':
            s = colored(f'DEBUG:  {msg}\n', 'white')
        if record.levelname == 'INFO':
            s = colored(f'INFO:  {msg}\n', 'green', attrs=['bold'])
        if record.levelname == 'WARNING':
            s = colored(f'WARNING:  {msg}\n', 'yellow', attrs=['bold'])
        if record.levelname == 'ERROR':
            s = colored(f'ERROR !  {msg}\n', 'red', attrs=['bold'])

        s += "\n"

        self.stream.write(s)

log = logging.getLogger()
log.setLevel(logging.INFO)
stdout = CLILogHandler(sys.stdout)
stdout.setLevel(logging.INFO)
log.handlers = [stdout]

console = Console()
app = typer.Typer(no_args_is_help=True, add_completion=False, context_settings={"help_option_names": ["-h", "--help"]},)
app.add_typer(alias.app, name='alias')
app.add_typer(ssh.app, name='ssh')
app.add_typer(ssh_keys.app, name='ssh_keys')
app.add_typer(totp.app, name='totp')

if __name__ == "__main__":
    app()
