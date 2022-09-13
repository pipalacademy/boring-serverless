import yaml
from git.exc import GitError

from flask import Flask, request

from . import base_path, get_gh_app


app = Flask(__name__)


def get_config():
    with open(base_path / "config.yml") as f:
        config = yaml.safe_load(f)

    return config


@app.route("/")
def health_check():
    return "Works!\n"


@app.route("/deploy", methods=["POST"])
def deploy():
    if "repo_owner" not in request.json or "repo_name" not in request.json:
        return {
            "status": "bad_request",
            "message": "repo_owner or repo_name missing in request",
        }

    repo_owner, repo_name = request.json.get("repo_owner"), request.json.get("repo_name")

    allowed_repos = get_config().get("whitelisted_repos", [])
    if (full_repo_name := f"{repo_owner}/{repo_name}") not in allowed_repos:
        return {
            "status": "not_allowed",
            "message": f"repository {full_repo_name} is not whitelisted",
        }, 403

    app = get_gh_app(repo_owner, repo_name)
    try:
        app.deploy()
    except GitError as e:
        return {"status": "git_problem", "message": str(e)}, 400

    return {"status": "ok"}
