import git
from pathlib import Path


base_path = Path(__file__).parent.parent
apps_dir = base_path / "apps"


class UserApp:
    def __init__(self, git_url, git_dir):
        self.git_url = git_url
        self.git_dir = git_dir

    def deploy(self):
        if (self.git_dir / ".git").exists():
            repo = git.Repo(self.git_dir)
            repo.remotes.origin.pull()
        else:
            # repo = git.Repo.clone_from(self.git_url, self.git_dir)
            raise Exception("App dir doesn't exist")


def get_gh_app(repo_owner, repo_name):
    git_url = get_repo_url(repo_owner, repo_name)
    git_dir = get_repo_dir(repo_owner, repo_name)
    return UserApp(git_url=git_url, git_dir=git_dir)


def get_repo_url(owner_name, repo_name):
    return f"https://github.com/{owner_name}/{repo_name}"


def get_app_by_name(app_name):
    app_dir = apps_dir / app_name
    if app_dir.is_dir():
        return UserApp(None, app_dir)

    return None


def get_repo_dir(owner_name, repo_name):
    apps_dir.mkdir(exist_ok=True)

    return apps_dir / owner_name
