import click
from core import start_curve , stop_curve 
import targets
import os
import config_generator
import pkg_resources
import sys
import subprocess

logo = r"""
     _                _
    / \    _ __  ___ | |__
   / _ \  | '__|/ __|| '_ \
  / ___ \ | |  | (__ | | | |
 /_/   \_\|_|   \___||_| |_|

"""
@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx):
    if ctx.invoked_subcommand is None:
        click.echo( """Curve (The Intelligent Prompt Gateway) CLI""")
        click.echo(logo)
        click.echo(ctx.get_help())

# Command to build curve and server Docker images
CURVEGW_DOCKERFILE = "./curve /Dockerfile"
MODEL_SERVER_DOCKERFILE = "./server/Dockerfile"

@click.command()
def build():
    """Build Curve from source. Must be in root of cloned repo."""
    # Check if /curve /Dockerfile exists
    if os.path.exists(CURVEGW_DOCKERFILE):
        click.echo("Building curve image...")
        try:
            subprocess.run(["docker", "build", "-f", CURVEGW_DOCKERFILE, "-t", "curve:latest", "."], check=True)
            click.echo("curve image built successfully.")
        except subprocess.CalledProcessError as e:
            click.echo(f"Error building curve image: {e}")
            sys.exit(1)
    else:
        click.echo("Error: Dockerfile not found in /curve ")
        sys.exit(1)

    # Check if /server/Dockerfile exists
    if os.path.exists(MODEL_SERVER_DOCKERFILE):
        click.echo("Building server image...")
        try:
            subprocess.run(["docker", "build", "-f", MODEL_SERVER_DOCKERFILE, "-t", "server:latest", "./server"], check=True)
            click.echo("server image built successfully.")
        except subprocess.CalledProcessError as e:
            click.echo(f"Error building server image: {e}")
            sys.exit(1)
    else:
        click.echo("Error: Dockerfile not found in /server")
        sys.exit(1)

    click.echo("All images built successfully.")

@click.command()
@click.argument('file', required=False)  # Optional file argument
@click.option('-path', default='.', help='Path to the directory containing curve_config.yml')
def up(file, path):
    """Starts Curve."""
    if file:
        # If a file is provided, process that file
        curve_config_file = os.path.abspath(file)
    else:
        # If no file is provided, use the path and look for curve_config.yml
        curve_config_file = os.path.abspath(os.path.join(path, "curve_config.yml"))

    # Check if the file exists
    if not os.path.exists(curve_config_file):
        print(f"Error: {curve_config_file} does not exist.")
        return

    print(f"Processing config file: {curve_config_file}")
    curve _schema_config = pkg_resources.resource_filename(__name__, "config/curve_config_schema.yaml")

    print(f"Validating {curve_config_file}")

    try:
        config_generator.validate_prompt_config(curve_config_file=curve_config_file, curve_config_schema_file=curve _schema_config)
    except Exception as e:
        print("Exiting curve up")
        sys.exit(1)

    print("Starting Curve gateway and Curve model server services via docker ")
    start_curve (curve_config_file)

@click.command()
def down():
    """Stops Curve."""
    stop_curve ()

@click.command()
@click.option('-f', '--file', type=click.Path(exists=True), required=True, help="Path to the Python file")
def generate_prompt_targets(file):
    """Generats prompt_targets from python methods.
       Note: This works for simple data types like ['int', 'float', 'bool', 'str', 'list', 'tuple', 'set', 'dict']:
       If you have a complex pydantic data type, you will have to flatten those manually until we add support for it."""

    print(f"Processing file: {file}")
    if not file.endswith(".py"):
        print("Error: Input file must be a .py file")
        sys.exit(1)

    targets.generate_prompt_targets(file)

main.add_command(up)
main.add_command(down)
main.add_command(build)
main.add_command(generate_prompt_targets)

if __name__ == '__main__':
    main()
