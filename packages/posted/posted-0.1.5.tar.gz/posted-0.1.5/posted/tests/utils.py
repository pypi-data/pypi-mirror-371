import subprocess
from time import sleep


def run_cmd(cmd: str, run_in_background: bool = False):
    cmd_args = cmd.split(" ")

    if run_in_background:
        process = subprocess.Popen(cmd_args, stdout=subprocess.DEVNULL)
        return process

    result = subprocess.run(cmd_args, stdout=subprocess.PIPE)
    return result.stdout.decode() if result.stdout else None


def service_is_running(service_container_name: str):
    output = run_cmd(f"docker ps -q -f name={service_container_name}")
    return bool(output)


def start_service(
    service_container_name: str, docker_compose_filepath: str, *, wait: float = 2.0
):
    """
    Start a docker service container.

    :param service_container_name: The name of the service container.
    :param docker_compose_filepath: The path to the docker-compose file.
    :param wait: The time to wait after starting the container, in seconds.
    """
    print("\n")
    print(f"========================== Running container ==========================")
    run_cmd(
        f"docker-compose -f {docker_compose_filepath} -p {service_container_name} up -d"
    )
    sleep(wait)
    print(f"========================== Container running ==========================")


def stop_service(service_container_name: str, docker_compose_filepath: str):
    """
    Stop a docker service container.

    :param service_container_name: The name of the service container.
    :param docker_compose_filepath: The path to the docker-compose file.
    """
    print("\n")
    print(f"========================== Stopping container ==========================")
    run_cmd(
        f"docker-compose -f {docker_compose_filepath} -p {service_container_name} stop"
    )
    print(f"========================== Container stopped ===========================")
