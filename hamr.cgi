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
        setup_env(self.app_root)
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
            app_root = get_root(hostname)

            if not app_root.is_dir():
                return self.not_found_app

            app_dir = app_root / "app"
            os.chdir(app_dir)
            sys.path.insert(0, str(app_dir))

            try:
                from wsgi import app
            finally:
                # restoring stdout, stderr streams because importing
                # may have had side effects, and stdout/stderr are
                # crucial for CGI and logging to behave correctly.
                # see https://github.com/pipalacademy/hamr/issues/20
                sys.stdout = sys.__stdout__
                sys.stderr = sys.__stderr__

            return app

    def __call__(self, environ, start_response):
        sys.stdout = sys.__stderr__
        try:
            return self.app(environ, start_response)
        finally:
            sys.stdout = sys.__stdout__


def main():
    app = Serverless()
    CGIHandler().run(app)


if __name__ == "__main__":
    main()
