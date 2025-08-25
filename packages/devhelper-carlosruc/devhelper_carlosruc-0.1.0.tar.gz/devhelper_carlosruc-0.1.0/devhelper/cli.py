# devhelper/cli.py
import click
from .tasks import create_file, list_files

@click.group()
def cli():
    """DevHelper CLI - Automate dev tasks"""
    pass

@cli.command()
@click.argument("filename")
def touch(filename):
    """Create an empty file"""
    create_file(filename)
    click.echo(f"Created file: {filename}")

@cli.command()
@click.argument("path", default=".")
def ls(path):
    """List files in a directory"""
    files = list_files(path)
    for f in files:
        click.echo(f)