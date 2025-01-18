from .backend import run as backend
from .client import run as client
from .server import run as server


def setup_commands(cli):
    cli.add_command(cmd=server, name='server')
    cli.add_command(cmd=client, name='client')
    cli.add_command(cmd=backend, name='backend')
