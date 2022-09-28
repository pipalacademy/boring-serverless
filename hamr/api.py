import yaml
from git.exc import GitError

from flask import Flask, render_template

from . import base_path, get_app_by_name, get_apps


app = Flask(__name__)


def get_config():
    with open(base_path / "config.yml") as f:
        config = yaml.safe_load(f)

    return config


@app.route("/api/")
def health_check():
    return "Works!\n"


@app.route("/")
def index():
    apps = get_apps()
    return render_template("index.html", apps=apps)


@app.route("/apps/<app_name>/deploy", methods=["POST"])
def deploy(app_name):
    # should the route for this endpoint be changed to begin with /api/ ?
    app = get_app_by_name(app_name)
    if app is None:
        return {
            "status": "app_not_found",
            "message": f"App with name {app_name} not found"
        }

    app.deploy()
    return {"status": "ok"}
