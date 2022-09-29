#!./venv/bin/python

import fnmatch
import os
import sys
import yaml
from pathlib import Path
from wsgiref.handlers import CGIHandler


this_path = Path(__file__).parent # path to hamr installation
APPS_DIR = this_path / "apps"
CONFIG_FILE = this_path / "config.yml"

API_HOSTNAME_PATTERNS = ["localhost", "hamr.*"]


def get_root(hostname):
    first, _ = hostname.split(".", maxsplit=1)

    return APPS_DIR / first


def get_config():
    if Path(CONFIG_FILE).is_file():
        with open(CONFIG_FILE) as f:
            return yaml.safe_load(f)


def inject_env_vars(config_key="env"):
    config = get_config()
    env_vars = config and config.get(config_key) or {}
    for (key, val) in env_vars.items():
        os.environ[key.upper()] = str(val)


def setup_env(app_root):
    os.environ["APP_ROOT"] = str(app_root)
    os.environ["TMPDIR"] = str(app_root / "tmp")

    inject_env_vars()
    if "HTTP_X_HAMR_TEST" in os.environ:
        inject_env_vars("test_env")


class Serverless:

    def __init__(self):
        hostname = os.getenv("SERVER_NAME")
        self.app_root = get_root(hostname).resolve()
        self.app = self.get_app(hostname)

    def not_found_app(self, environ, start_response):
        status = "404 Not Found"
        headers = [("Content-Type", "text/html")]
        body = b"<h1>Not Found</h1>"

        start_response(status, headers)
        return [body]

    def get_app(self, hostname):
        if any(fnmatch.fnmatch(hostname, pattern) for pattern in API_HOSTNAME_PATTERNS):
            sys.path.insert(0, str(this_path))

            from hamr.api import app
            return app
        else:
            app_dir = get_root(hostname)

            if not app_dir.is_dir():
                return self.not_found_app

            os.chdir(app_dir)
            sys.path.insert(0, str(app_dir / "app"))

            from wsgi import app
            return app

    def __call__(self, environ, start_response):
        return self.app(environ, start_response)


def main():
    app = Serverless()
    setup_env(app.app_root)
    CGIHandler().run(app)


if __name__ == "__main__":
    main()
