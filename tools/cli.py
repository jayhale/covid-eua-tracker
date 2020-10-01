import click

from .scrape import scrape
from .transform import transform


@click.group()
@click.option('--yaml-output', type=click.File('a+'), default='euas.yaml')
@click.pass_context
def cli(ctx, yaml_output):
    ctx.obj = {'yaml_output': yaml_output}


cli.add_command(scrape)
cli.add_command(transform)
