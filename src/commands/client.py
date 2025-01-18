import click

from modules.opcua import client


@click.command()
def run():
    client()
