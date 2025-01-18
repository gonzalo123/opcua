import click

from modules.opcua import server


@click.command()
def run():
    server()
