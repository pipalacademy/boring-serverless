import git
import yaml
from pathlib import Path

from flask import Flask, request


app = Flask(__name__)
this_path = Path(__file__).parent


def get_config():
    with open(this_path / "config.yml") as f:
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

    try:
        deploy_app(repo_owner, repo_name)
    except git.exc.GitError as e:
        return {"status": "git_problem", "message": str(e)}, 400

    return {"status": "ok"}


def deploy_app(owner_name, repo_name):
    repo_url = get_repo_url(owner_name, repo_name)
    repo_dir = get_repo_dir(owner_name, repo_name)

    if (repo_dir / ".git").exists():
        repo = git.Repo(repo_dir)
        repo.remotes.origin.pull()
    else:
        repo = git.Repo.clone_from(repo_url, repo_dir)


def get_repo_url(owner_name, repo_name):
    return f"https://github.com/{owner_name}/{repo_name}"


def get_repo_dir(owner_name, repo_name):
    base_dir = this_path / "apps"
    base_dir.mkdir(exist_ok=True)

    return base_dir / owner_name
