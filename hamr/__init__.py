import shutil
from pathlib import Path

import git
from git.exc import GitError, InvalidGitRepositoryError


base_path = Path(__file__).parent.parent
APPS_DIR = base_path / "apps"


class HamrError(Exception):
    pass


class UserApp:
    def __init__(self, name, git_url=None, git_dir=None):
        self.name = name
        self.app_root = APPS_DIR / name
        self.git_dir = git_dir or self.app_root / "app"
        self.git_url = git_url

        if not self.git_url and is_valid_git_dir(self.git_dir):
            self.git_url = get_origin_url(self.git_dir)

    @property
    def version(self):
        return get_version(self.git_dir) if is_valid_git_dir(self.git_dir) else None

    def _git_pull(self):
        git.Repo(self.git_dir).remotes.origin.pull()

    def _is_updatable(self):
        if is_valid_git_dir(self.git_dir):
            return "origin" in git.Repo(self.git_dir).remotes
        else:
            return False

    def sync(self):
        # since all apps as of now are git-based, we git-pull
        try:
            self._git_pull()
        except GitError as e:
            raise HamrError("git pull failed") from e

    def delete(self):
        try:
            shutil.rmtree(self.app_root)
        except OSError as e:
            raise HamrError("deleting app directory failed") from e

    def is_update_available(self, fetch=False):
        """Checks for updates

        If fetch is true, this will try to fetch changes from the remote
        server, which may take a longer time.
        """
        if not self._is_updatable():
            return False

        repo = git.Repo(self.git_dir)
        branch = repo.head.ref
        branch_name = branch.name
        origin = repo.remotes.origin
        if fetch and branch_name in origin.refs:
            origin.fetch()
        remote_branch = branch_name in origin.refs and origin.refs[branch_name]
        return remote_branch and remote_branch.commit != branch.commit

    def deploy(self):
        if self._is_updatable():
            self.sync()
        else:
            # self.git_clone()
            raise HamrError("App dir doesn't exist")


def get_apps():
    apps = []

    # get sub directories
    for appdir in APPS_DIR.glob("*/"):
        apps.append(get_app_by_name(appdir.name))

    return apps


def get_app_by_name(app_name):
    return UserApp(name=app_name)


def create_app(app_name, git_url):
    """Creates a new app, pulling it from git url and setting up
    necessary directories.
    """
    app = UserApp(name=app_name, git_url=git_url)
    try:
        git.Repo.clone_from(app.git_url, app.git_dir)
    except GitError as e:
        raise HamrError("git clone failed") from e

    try:
        init_app_dirs(app.app_root)
    except OSError as e:
        raise HamrError("couldn't initialize app dirs") from e

    return app


def is_valid_git_dir(path):
    try:
        _ = git.Repo(path)
    except InvalidGitRepositoryError:
        return False
    else:
        return True


def init_app_dirs(app_root):
    """Creates necessary directories

    Note: this doesn't create a `site` directory because it
    is a special directory.
    If it exists, then the web server must only serve files
    from that directory and not run any dynamic scripts.
    """
    (app_root / "bin").mkdir(exist_ok=True)
    (app_root / "logs").mkdir(exist_ok=True)
    (app_root / "public").mkdir(exist_ok=True)
    (app_root / "private").mkdir(exist_ok=True)
    (app_root / "tmp").mkdir(exist_ok=True)


def get_version(git_dir):
    repo = git.Repo(git_dir)
    return repo.head.commit.hexsha[:7] if repo.head.is_valid() else None


def get_origin_url(git_dir):
    repo = git.Repo(git_dir)
    return "origin" in repo.remotes and next(repo.remotes.origin.urls) or None
