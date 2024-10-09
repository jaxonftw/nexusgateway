import click
import targets
import os
import config_generator
import pkg_resources
import sys
import subprocess
from core import start_curve _modelserver, stop_curve _modelserver, start_curve , stop_curve 
from utils import get_llm_provider_access_keys, load_env_file_to_dict

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
        click.echo("""Curve (The Intelligent Prompt Gateway) CLI""")
        click.echo(logo)
        click.echo(ctx.get_help())


# Command to build curve and server Docker images
CURVEGW_DOCKERFILE = "./curve /Dockerfile"
MODEL_SERVER_BUILD_FILE = "./server/pyproject.toml"


@click.command()
def build():
    """Build Curve from source. Must be in root of cloned repo."""
    # Check if /curve /Dockerfile exists
    if os.path.exists(CURVEGW_DOCKERFILE):
        click.echo("Building curve image...")
        try:
            subprocess.run(
                [
                    "docker",
                    "build",
                    "-f",
                    CURVEGW_DOCKERFILE,
                    "-t",
                    "curve:latest",
                    ".",
                ],
                check=True,
            )
            click.echo("curve image built successfully.")
        except subprocess.CalledProcessError as e:
            click.echo(f"Error building curve image: {e}")
            sys.exit(1)
    else:
        click.echo("Error: Dockerfile not found in /curve ")
        sys.exit(1)

    click.echo("All images built successfully.")

    """Install the model server dependencies using Poetry."""
    # Check if pyproject.toml exists
    if os.path.exists(MODEL_SERVER_BUILD_FILE):
        click.echo("Installing model server dependencies with Poetry...")
        try:
            subprocess.run(
                ["poetry", "install", "--no-cache"],
                cwd=os.path.dirname(MODEL_SERVER_BUILD_FILE),
                check=True,
            )
            click.echo("Model server dependencies installed successfully.")
        except subprocess.CalledProcessError as e:
            click.echo(f"Error installing model server dependencies: {e}")
            sys.exit(1)
    else:
        click.echo(f"Error: pyproject.toml not found in {MODEL_SERVER_BUILD_FILE}")
        sys.exit(1)


@click.command()
@click.argument("file", required=False)  # Optional file argument
@click.option(
    "-path", default=".", help="Path to the directory containing curve_config.yml"
)
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

    print(f"Validating {curve_config_file}")
    curve _schema_config = pkg_resources.resource_filename(
        __name__, "config/curve_config_schema.yaml"
    )

    try:
        config_generator.validate_prompt_config(
            curve_config_file=curve_config_file,
            curve_config_schema_file=curve _schema_config,
        )
    except Exception as e:
        print("Exiting curve up")
        sys.exit(1)

    print("Starting Curve gateway and Curve model server services via docker ")

    # Set the CURVE_CONFIG_FILE environment variable
    env_stage = {}
    env = os.environ.copy()
    # check if access_keys are preesnt in the config file
    access_keys = get_llm_provider_access_keys(curve_config_file=curve_config_file)
    if access_keys:
        if file:
            app_env_file = os.path.join(
                os.path.dirname(os.path.abspath(file)), ".env"
            )  # check the .env file in the path
        else:
            app_env_file = os.path.abspath(os.path.join(path, ".env"))

        if not os.path.exists(
            app_env_file
        ):  # check to see if the environment variables in the current environment or not
            for access_key in access_keys:
                if env.get(access_key) is None:
                    print(f"Access Key: {access_key} not found. Exiting Start")
                    sys.exit(1)
                else:
                    env_stage[access_key] = env.get(access_key)
        else:  # .env file exists, use that to send parameters to Curve
            env_file_dict = load_env_file_to_dict(app_env_file)
            for access_key in access_keys:
                if env_file_dict.get(access_key) is None:
                    print(f"Access Key: {access_key} not found. Exiting Start")
                    sys.exit(1)
                else:
                    env_stage[access_key] = env_file_dict[access_key]

    with open(
        pkg_resources.resource_filename(__name__, "config/stage.env"), "w"
    ) as file:
        for key, value in env_stage.items():
            file.write(f"{key}={value}\n")

    env.update(env_stage)
    env["CURVE_CONFIG_FILE"] = curve_config_file

    start_curve _modelserver()
    start_curve (curve_config_file, env)


@click.command()
def down():
    """Stops Curve."""
    stop_curve _modelserver()
    stop_curve ()


@click.command()
@click.option(
    "-f",
    "--file",
    type=click.Path(exists=True),
    required=True,
    help="Path to the Python file",
)
def generate_prompt_targets(file):
    """Generats prompt_targets from python methods.
    Note: This works for simple data types like ['int', 'float', 'bool', 'str', 'list', 'tuple', 'set', 'dict']:
    If you have a complex pydantic data type, you will have to flatten those manually until we add support for it.
    """

    print(f"Processing file: {file}")
    if not file.endswith(".py"):
        print("Error: Input file must be a .py file")
        sys.exit(1)

    targets.generate_prompt_targets(file)


main.add_command(up)
main.add_command(down)
main.add_command(build)
main.add_command(generate_prompt_targets)

if __name__ == "__main__":
    main()
