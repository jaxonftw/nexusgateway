import subprocess
import os
import time
import sys
import glob
import docker
from cli.utils import getLogger
from cli.consts import (
    CURVEGW_DOCKER_IMAGE,
    CURVEGW_DOCKER_NAME,
    KATANEMO_LOCAL_MODEL_LIST,
    MODEL_SERVER_LOG_FILE,
    ACCESS_LOG_FILES,
)
from huggingface_hub import snapshot_download
from dotenv import dotenv_values


log = getLogger(__name__)


def start_curve_docker(client, curve_config_file, env):
    logs_path = "~/curve_logs"
    logs_path_abs = os.path.expanduser(logs_path)

    return client.containers.run(
        name=CURVEGW_DOCKER_NAME,
        image=CURVEGW_DOCKER_IMAGE,
        detach=True,  # Run in detached mode
        ports={
            "10000/tcp": 10000,
            "10001/tcp": 10001,
            "11000/tcp": 11000,
            "12000/tcp": 12000,
            "9901/tcp": 19901,
        },
        volumes={
            f"{curve_config_file}": {
                "bind": "/app/curve_config.yaml",
                "mode": "ro",
            },
            "/etc/ssl/cert.pem": {"bind": "/etc/ssl/cert.pem", "mode": "ro"},
            logs_path_abs: {"bind": "/var/log"},
        },
        environment={
            "OTEL_TRACING_HTTP_ENDPOINT": "http://host.docker.internal:4318/v1/traces",
            **env,
        },
        extra_hosts={"host.docker.internal": "host-gateway"},
        healthcheck={
            "test": ["CMD", "curl", "-f", "http://localhost:10000/healthz"],
            "interval": 5000000000,  # 5 seconds
            "timeout": 1000000000,  # 1 seconds
            "retries": 3,
        },
    )


def stream_gateway_logs(follow):
    """
    Stream logs from the curve  gateway service.
    """
    log.info("Logs from curve  gateway service.")

    options = ["docker", "logs", "curve"]
    if follow:
        options.append("-f")
    try:
        # Run `docker-compose logs` to stream logs from the gateway service
        subprocess.run(
            options,
            check=True,
            stdout=sys.stdout,
            stderr=sys.stderr,
        )

    except subprocess.CalledProcessError as e:
        log.info(f"Failed to stream logs: {str(e)}")


def stream_server_logs(follow):
    """
    Get the model server logs, check if the user wants to follow/tail them.
    """
    log_file_expanded = os.path.expanduser(MODEL_SERVER_LOG_FILE)

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


def stream_access_logs(follow):
    """
    Get the curve access logs
    """
    log_file_pattern_expanded = os.path.expanduser(ACCESS_LOG_FILES)
    log_files = glob.glob(log_file_pattern_expanded)

    stream_command = ["tail"]
    if follow:
        stream_command.append("-f")

    stream_command.extend(log_files)
    subprocess.run(
        stream_command,
        check=True,
        stdout=sys.stdout,
        stderr=sys.stderr,
    )


def start_curve (curve_config_file, env, log_timeout=120):
    """
    Start Docker Compose in detached mode and stream logs until services are healthy.

    Args:
        path (str): The path where the prompt_config.yml file is located.
        log_timeout (int): Time in seconds to show logs before checking for healthy state.
    """
    log.info("Starting curve  gateway")

    try:
        client = docker.from_env()

        container = start_curve_docker(client, curve_config_file, env)

        start_time = time.time()

        while True:
            container = client.containers.get(container.id)
            current_time = time.time()
            elapsed_time = current_time - start_time

            # Check if timeout is reached
            if elapsed_time > log_timeout:
                log.info(f"Stopping log monitoring after {log_timeout} seconds.")
                break

            container_status = container.attrs["State"]["Health"]["Status"]

            if container_status == "healthy":
                log.info("Container is healthy!")
                break
            else:
                log.info(f"Container health status: {container_status}")
                time.sleep(1)

    except docker.errors.APIError as e:
        log.info(f"Failed to start Curve: {str(e)}")


def stop_curve ():
    """
    Shutdown all Docker Compose services by running `docker-compose down`.

    Args:
        path (str): The path where the docker-compose.yml file is located.
    """
    log.info("Shutting down curve  gateway service.")

    try:
        subprocess.run(
            ["docker", "stop", "curve"],
        )
        subprocess.run(
            ["docker", "remove", "curve"],
        )

        log.info("Successfully shut down curve  gateway service.")

    except subprocess.CalledProcessError as e:
        log.info(f"Failed to shut down services: {str(e)}")


def download_models_from_hf():
    for model in KATANEMO_LOCAL_MODEL_LIST:
        log.info(f"Downloading model: {model}")
        snapshot_download(repo_id=model)


def start_curve _modelserver():
    """
    Start the model server. This assumes that the curve_modelserver package is installed locally

    """
    try:
        log.info("curve_modelserver restart")
        subprocess.run(
            ["curve_modelserver", "restart"], check=True, start_new_session=True
        )
        log.info("Successfull ran server")
    except subprocess.CalledProcessError as e:
        log.info(f"Failed to start server. Please check curve_modelserver logs")
        sys.exit(1)


def stop_curve _modelserver():
    """
    Stop the model server. This assumes that the curve_modelserver package is installed locally

    """
    try:
        subprocess.run(
            ["curve_modelserver", "stop"],
            check=True,
        )
        log.info("Successfull stopped the curve server")
    except subprocess.CalledProcessError as e:
        log.info(f"Failed to start server. Please check curve_modelserver logs")
        sys.exit(1)
