import click
import os
import pkg_resources
import sys
import subprocess
from cli import targets
from cli import config_generator
from cli.core import (
    start_curve _modelserver,
    stop_curve _modelserver,
    start_curve ,
    stop_curve ,
    stream_gateway_logs,
)
from cli.utils import get_llm_provider_access_keys, load_env_file_to_dict
from cli.consts import KATANEMO_DOCKERHUB_REPO
from cli.utils import getLogger
import multiprocessing
from huggingface_hub import snapshot_download
import joblib


log = getLogger(__name__)

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
@click.option(
    "--service",
    default="all",
    help="Optioanl parameter to specify which service to build. Options are server, curve",
)
def build(service):
    """Build Curve from source. Must be in root of cloned repo."""
    if service not in ["server", "curve", "all"]:
        print(f"Error: Invalid service {service}. Exiting")
        sys.exit(1)
    # Check if /curve /Dockerfile exists
    if service == "curve" or service == "all":
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
                        f"{KATANEMO_DOCKERHUB_REPO}:latest",
                        ".",
                        "--add-host=host.docker.internal:host-gateway",
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

    click.echo("curve image built successfully.")

    """Install the model server dependencies using Poetry."""
    if service == "server" or service == "all":
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
    "--path", default=".", help="Path to the directory containing curve_config.yaml"
)
@click.option(
    "--service",
    default="all",
    help="Service to start. Options are server, curve.",
)
def up(file, path, service):
    """Starts Curve."""
    if service not in ["all", "server", "curve"]:
        print(f"Error: Invalid service {service}. Exiting")
        sys.exit(1)

    if service == "server":
        start_curve _modelserver()
        return

    if file:
        # If a file is provided, process that file
        curve_config_file = os.path.abspath(file)
    else:
        # If no file is provided, use the path and look for curve_config.yaml
        curve_config_file = os.path.abspath(os.path.join(path, "curve_config.yaml"))

    # Check if the file exists
    if not os.path.exists(curve_config_file):
        print(f"Error: {curve_config_file} does not exist.")
        return

    print(f"Validating {curve_config_file}")
    curve _schema_config = pkg_resources.resource_filename(
        __name__, "../config/curve_config_schema.yaml"
    )

    try:
        config_generator.validate_prompt_config(
            curve_config_file=curve_config_file,
            curve_config_schema_file=curve _schema_config,
        )
    except Exception as e:
        print(f"Exiting curve up: {e}")
        sys.exit(1)

    log.info("Starging curve  model server and curve  gateway")

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
        pkg_resources.resource_filename(__name__, "../config/stage.env"), "w"
    ) as file:
        for key, value in env_stage.items():
            file.write(f"{key}={value}\n")

    env.update(env_stage)
    env["CURVE_CONFIG_FILE"] = curve_config_file

    if service == "curve":
        start_curve (curve_config_file, env)
    else:
        start_curve _modelserver()
        start_curve (curve_config_file, env)


@click.command()
@click.option(
    "--service",
    default="all",
    help="Service to down. Options are all, server, curve. Default is all",
)
def down(service):
    """Stops Curve."""

    if service not in ["all", "server", "curve"]:
        print(f"Error: Invalid service {service}. Exiting")
        sys.exit(1)
    if service == "server":
        stop_curve _modelserver()
    elif service == "curve":
        stop_curve ()
    else:
        stop_curve _modelserver()
        stop_curve ()


@click.command()
@click.option(
    "--f",
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


def stream_server_logs(follow):
    log_file = "~/curve_logs/modelserver.log"
    log_file_expanded = os.path.expanduser(log_file)
    stream_command = ["tail"]
    if follow:
        stream_command.append("-f")
    stream_command.append(log_file_expanded)
    subprocess.run(
        stream_command,
        check=True,
        stdout=sys.stdout,
        stderr=sys.stderr,
    )


@click.command()
@click.option(
    "--service",
    default="all",
    help="Service to monitor. By default it will monitor both gateway and model_serve",
)
@click.option("--follow", help="Follow the logs", is_flag=True)
def logs(service, follow):
    """Stream logs from curve  services."""

    if service not in ["all", "server", "curve"]:
        print(f"Error: Invalid service {service}. Exiting")
        sys.exit(1)
    curve_process = None
    if service == "curve" or service == "all":
        curve_process = multiprocessing.Process(
            target=stream_gateway_logs, args=(follow,)
        )
        curve_process.start()

    server_process = None
    if service == "server" or service == "all":
        server_process = multiprocessing.Process(
            target=stream_server_logs, args=(follow,)
        )
        server_process.start()

    if curve_process:
        curve_process.join()
    if server_process:
        server_process.join()


model_list = [
    "curvelaboratory/Curve-Guard-cpu",
    "curvelaboratory/Curve-Guard",
    "curvelaboratory/bge-large-en-v1.5",
]


@click.command()
def download_models():
    """Download required models from Hugging Face Hub in the cache directory"""
    for model in model_list:
        log.info(f"Downloading model: {model}")
        snapshot_download(repo_id=model)


main.add_command(up)
main.add_command(down)
main.add_command(build)
main.add_command(logs)
main.add_command(download_models)
main.add_command(generate_prompt_targets)

if __name__ == "__main__":
    main()
