import click

from modules.backend import update_redis_variable_loop


@click.command()
def run():
    update_redis_variable_loop()
