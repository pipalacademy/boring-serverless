#!./venv/bin/python

import os
import sys
import yaml
from pathlib import Path
from wsgiref.handlers import CGIHandler


this_path = Path(__file__).parent # path to boring-serverless installation
apps_dir = this_path / "apps"

def get_root(hostname):
    first, _ = hostname.split(".", maxsplit=1)

    return str(apps_dir / first)


class Serverless:

    def not_found_app(self, environ, start_response):
        status = "404 Not Found"
        headers = [("Content-Type", "text/html")]
        body = b"<h1>Not Found</h1>"

        start_response(status, headers)
        return [body]

    def get_app(self, hostname):
        sys.path.insert(0, str(get_root(hostname)))

        try:
            from wsgi import app
            return app
        except ImportError:
            return self.not_found_app

    def __call__(self, environ, start_response):
        hostname = os.getenv("SERVER_NAME")

        app = self.get_app(hostname)
        return app(environ, start_response)


def main():
    app = Serverless()
    CGIHandler().run(app)


if __name__ == "__main__":
    main()
