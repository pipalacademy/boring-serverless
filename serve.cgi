#!/usr/bin/env python3

import os
import sys
import yaml
from pathlib import Path
from wsgiref.handlers import CGIHandler


this_path = Path(__file__).parent
PYTHON_PACKAGES_PATH = os.getenv("PYTHON_PACKAGES_PATH", this_path / "venv/lib/python3.9/site-packages")


def get_base_dir():
    config = get_config()

    base_dir = config.get("base_directory", "apps")

    return (this_path / base_dir).resolve()


def get_config():
    with open(this_path / "config.yml") as f:
        config = yaml.safe_load(f)

    return config


def get_root(hostname):
    first, _ = hostname.split(".", maxsplit=1)

    base_path = get_base_dir()
    return str(base_path / first)


def respond_404():
    # headers
    print("Status: 404 Not Found")
    print("Content-Type: text/html")
    print()

    # body
    print("<h1>Not Found</h1>")


if __name__ == "__main__":
    hostname = os.getenv("SERVER_NAME")

    if PYTHON_PACKAGES_PATH:
        sys.path.insert(0, str(PYTHON_PACKAGES_PATH))

    sys.path.insert(0, str(get_root(hostname)))

    try:
        from train_ride.app import app
    except ImportError:
        respond_404()
        exit(0)

    CGIHandler().run(app)
