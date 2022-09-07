#!/usr/bin/env python3

import os
import sys
import yaml
from pathlib import Path
from wsgiref.handlers import CGIHandler


# change this
this_path = Path("/home/dev/boring-serverless") # path to boring-serverless installation

apps_dir = this_path / "apps"

# change this
PYTHON_PACKAGES_PATH = os.getenv("PYTHON_PACKAGES_PATH", this_path / "venv/lib/python3.9/site-packages")


def get_root(hostname):
    first, _ = hostname.split(".", maxsplit=1)

    return str(apps_dir / first)


def respond_404():
    # headers
    print("Status: 404 Not Found")
    print("Content-Type: text/html")
    print()

    # body
    print("<h1>Not Found</h1>")


if __name__ == "__main__":
    if PYTHON_PACKAGES_PATH:
        sys.path.insert(0, str(PYTHON_PACKAGES_PATH))

    hostname = os.getenv("SERVER_NAME")
    sys.path.insert(0, str(get_root(hostname)))

    try:
        from train_ride.app import app
    except ImportError:
        respond_404()
        exit(0)

    CGIHandler().run(app)
