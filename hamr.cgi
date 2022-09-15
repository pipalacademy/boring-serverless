#!./venv/bin/python

import fnmatch
import os
import sys
import yaml
from pathlib import Path
from wsgiref.handlers import CGIHandler


this_path = Path(__file__).parent # path to hamr installation
APPS_DIR = this_path / "apps"

API_HOSTNAME_PATTERNS = ["localhost", "hamr.*"]


def get_root(hostname):
    first, _ = hostname.split(".", maxsplit=1)

    return APPS_DIR / first


class Serverless:

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
            sys.path.insert(0, str(app_dir))

            from wsgi import app
            return app

    def __call__(self, environ, start_response):
        hostname = os.getenv("SERVER_NAME")

        app = self.get_app(hostname)
        return app(environ, start_response)


def main():
    app = Serverless()
    CGIHandler().run(app)


if __name__ == "__main__":
    main()
