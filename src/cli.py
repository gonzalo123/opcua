import logging

import click

from commands import setup_commands

for logger_name in ['asyncua', ]:
    logging.getLogger(logger_name).setLevel(logging.WARNING)

logging.basicConfig(
    format='%(asctime)s [%(levelname)s] %(message)s',
    level='INFO',
    datefmt='%d/%m/%Y %X')


@click.group()
def cli():
    pass


setup_commands(cli)

if __name__ == "__main__":
    cli()
