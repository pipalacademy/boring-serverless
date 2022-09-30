import traceback
import yaml
from flask import Flask, flash, redirect, request, render_template, url_for

from . import HamrError, base_path, create_app, get_app_by_name, get_apps


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


@app.route("/apps/create", methods=["GET", "POST"])
def create_new_app():
    if request.method == "POST":
        app_name = request.form.get("app_name")
        git_url = request.form.get("git_url")

        if not app_name:
            return "app_name is required", 400

        if not git_url:
            return "git_url is required", 400

        try:
            create_app(app_name=app_name, git_url=git_url)
        except HamrError as e:
            tb = traceback.format_exc()
            message = format_flash_error(e, tb)
            flash(message, "error")
            return redirect(
                url_for("create_new_app", app_name=app_name, git_url=git_url))
        else:
            message = f"App {app_name} was created"
            flash(message, "success")
            return redirect("/")
    else:
        return render_template("create_app.html", args=request.args)


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
