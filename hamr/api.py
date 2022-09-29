import traceback
import yaml
from flask import Flask, flash, redirect, render_template

from . import HamrError, base_path, get_app_by_name, get_apps


app = Flask(__name__)
app.secret_key = "hello, world!"


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


@app.route("/apps/<app_name>/sync", methods=["POST"])
def sync_app(app_name):
    app = get_app_by_name(app_name)
    try:
        app.sync()
    except HamrError as e:
        tb = traceback.format_exc()
        message = format_flash_error(e, tb)
        flash(message, "error")
    else:
        message = f"App {app_name} was successfully synced"
        flash(message, "success")

    return redirect("/")


@app.route("/apps/<app_name>/delete", methods=["POST"])
def delete_app(app_name):
    app = get_app_by_name(app_name)
    try:
        app.delete()
    except HamrError as e:
        tb = traceback.format_exc()
        message = format_flash_error(e, tb)
        flash(message, "error")
    else:
        message = f"App {app_name} was deleted"
        flash(message, "success")

    return redirect("/")


@app.route("/apps/check_for_updates", methods=["POST"])
def check_for_updates():
    updates_available = 0
    for app in get_apps():
        if app.is_update_available(fetch=True):
            updates_available += 1

    flash(f"{updates_available} new updates available", "info")
    return redirect("/")


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


def format_flash_error(e, tb=None):
    tb_class = "notification is-danger is-light"

    message = f"<strong>An error occured: </strong>{e}</div>"
    if tb:
        message += f'<pre class="{tb_class}"><code>{tb}</code></pre>'
    return message
