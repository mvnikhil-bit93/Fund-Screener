"""Manage only this repository's disposable, loopback-only PostgreSQL service."""

import argparse
import json
import os
import shutil
import subprocess
import time
from typing import Any

from ledger.db.migrate import bootstrap_roles, revision, upgrade

IMAGE = (
    "postgres:17-bookworm@sha256:839fbb5a4942a7758dd93e18b42ea5649807491a0545b5eeeb8f0b8bb11857a5"
)
NAME = "fund-screener-postgres"
LABEL = "io.fund-screener.local"
DEV_DSN = "postgresql://postgres@127.0.0.1:55432/fund_dev?hostaddr=127.0.0.1"
_SELECTORS = (
    "DOCKER_HOST",
    "DOCKER_CONTEXT",
    "DOCKER_TLS",
    "DOCKER_TLS_VERIFY",
    "DOCKER_CERT_PATH",
)


def docker(*arguments: str, required: bool = True) -> subprocess.CompletedProcess[str]:
    binary = shutil.which("docker")
    if binary is None:
        raise RuntimeError("Docker is required for the local PostgreSQL service")
    environment = {key: value for key, value in os.environ.items() if key not in _SELECTORS}
    return subprocess.run(  # noqa: S603 -- fixed executable, arguments built internally, no shell
        [binary, "--host=unix:///var/run/docker.sock", *arguments],
        env=environment,
        check=required,
        capture_output=True,
        text=True,
    )


def owned_container() -> dict[str, Any] | None:
    result = docker(
        "inspect",
        "--format",
        "{{json .Config.Labels}}|{{json .Config.Image}}|"
        "{{json .HostConfig.PortBindings}}|{{json .State.Running}}",
        NAME,
        required=False,
    )
    if result.returncode:
        if "No such object" in result.stderr or "No such container" in result.stderr:
            return None
        raise RuntimeError("Cannot inspect the managed local Docker daemon")
    labels, image, ports, running = map(json.loads, result.stdout.strip().split("|"))
    expected_ports = {"5432/tcp": [{"HostIp": "127.0.0.1", "HostPort": "55432"}]}
    if (
        not isinstance(labels, dict)
        or labels.get(LABEL) != "true"
        or image != IMAGE
        or ports != expected_ports
    ):
        raise RuntimeError("Refusing to modify a conflicting or unrecognized container")
    return {"running": running}


def ready() -> None:
    for _ in range(30):
        result = docker(
            "exec",
            NAME,
            "psql",
            "-U",
            "postgres",
            "-d",
            "fund_dev",
            "-At",
            "-c",
            "SELECT 1",
            required=False,
        )
        if result.returncode == 0 and result.stdout.strip() == "1":
            return
        time.sleep(1)
    raise RuntimeError("Local PostgreSQL did not pass its SQL readiness check")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("start", "stop", "status", "migrate"))
    action = parser.parse_args().action
    docker("info", "--format", "{{.ServerVersion}}")
    existing = owned_container()
    if action == "start":
        if existing is None:
            docker(
                "run",
                "--detach",
                "--name",
                NAME,
                "--label",
                f"{LABEL}=true",
                "--publish",
                "127.0.0.1:55432:5432",
                "--env",
                "POSTGRES_HOST_AUTH_METHOD=trust",
                "--env",
                "POSTGRES_DB=fund_dev",
                "--tmpfs",
                "/var/lib/postgresql/data:rw,mode=0700",
                IMAGE,
            )
        elif not existing["running"]:
            docker("start", NAME)
        ready()
        print("Local PostgreSQL is ready on 127.0.0.1:55432; data is disposable.")
    elif action == "stop":
        if existing is not None:
            docker("stop", NAME)
            docker("rm", NAME)
        print("Local PostgreSQL stopped; no other containers were touched.")
    elif action == "status":
        if existing is None or not existing["running"]:
            raise RuntimeError("Local PostgreSQL is not running; run make db-start")
        ready()
        print("Local PostgreSQL SQL readiness check passed.")
    else:
        if existing is None or not existing["running"]:
            raise RuntimeError("Start the managed local PostgreSQL service first")
        ready()
        # This helper only migrates its own local service. Ambient libpq
        # routing, services, or session options must not override that target.
        for name in (
            "PGHOST",
            "PGHOSTADDR",
            "PGPORT",
            "PGDATABASE",
            "PGUSER",
            "PGSERVICE",
            "PGSERVICEFILE",
            "PGOPTIONS",
        ):
            os.environ.pop(name, None)
        bootstrap_roles(DEV_DSN)
        upgrade(DEV_DSN)
        print(f"Local development database revision: {revision(DEV_DSN)}")


if __name__ == "__main__":
    main()
