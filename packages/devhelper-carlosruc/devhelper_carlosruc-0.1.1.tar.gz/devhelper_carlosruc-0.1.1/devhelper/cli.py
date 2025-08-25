# devhelper/cli.py
import click
from .tasks import create_file, list_files, generate_tree

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

@cli.command()
@click.argument("path", default=".")
def tree(path):
    """Generate directory tree (solution-aware if .sln exists)"""
    print("teste")
    click.echo(generate_tree(path))