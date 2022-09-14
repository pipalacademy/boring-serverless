import yaml
from git.exc import GitError

from flask import Flask

from . import base_path, get_app_by_name


app = Flask(__name__)


def get_config():
    with open(base_path / "config.yml") as f:
        config = yaml.safe_load(f)

    return config


@app.route("/")
def health_check():
    return "Works!\n"


@app.route("/apps/<app_name>/deploy", methods=["POST"])
def deploy(app_name):
    app = get_app_by_name(app_name)
    if app is None:
        return {
            "status": "app_not_found",
            "message": f"App with name {app_name} not found"
        }

    app.deploy()
    return {"status": "ok"}
