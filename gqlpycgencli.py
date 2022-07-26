import click

from gqlpycgen import do_remote


@click.group()
@click.pass_context
def cli(ctx):
    pass


@cli.command('generate')
@click.option('-r', '--remote-url', default="http://localhost:4000/graphql", help='URL for the remote graphQL service to load the schema from.')
@click.option('-o', '--output', default="imported.py", help='file path to write the output to.')
@click.option('-p', '--py35backport', default=False, help='if set then the generated code is supported in python 3.5')
@click.pass_context
def generate(ctx, remote_url, output, py35backport):
    do_remote(remote_url, output, py36plus=(not py35backport))
