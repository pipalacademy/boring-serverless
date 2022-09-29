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
        self.git_url = git_url
        self.git_dir = git_dir or self.app_root

    @property
    def version(self):
        return get_version(self.git_dir) if is_valid_git_dir(self.git_dir) else None

    def init_dirs(self):
        """Creates necessary directories

        Note: this doesn't create a `site` directory because it
        is a special directory.
        If it exists, then the web server must only serve files
        from that directory and not run any dynamic scripts.
        """
        (self.app_root / "bin").mkdir(exists_ok=True)
        (self.app_root / "logs").mkdir(exists_ok=True)
        (self.app_root / "public").mkdir(exists_ok=True)
        (self.app_root / "private").mkdir(exists_ok=True)
        (self.app_root / "tmp").mkdir(exists_ok=True)

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
        apps.append(get_app_from_dir(appdir))

    return apps


def get_app_by_name(app_name):
    app_dir = APPS_DIR / app_name
    if app_dir.is_dir():
        return get_app_from_dir(app_dir)

    return None


def get_app_from_dir(app_dir):
    git_dir = app_dir

    if is_valid_git_dir(app_dir):
        repo = git.Repo(git_dir)
        if not repo.bare and "origin" in repo.remotes:
            origin = repo.remote("origin")
            git_url = next(origin.urls)
        else:
            git_url = None

        return UserApp(name=app_dir.name, git_url=git_url, git_dir=git_dir)
    else:
        return UserApp(name=app_dir.name)


def create_app(app_name, git_url):
    """Creates a new app, pulling it from git url and setting up
    necessary directories.
    """
    app = UserApp(name=app_name, git_url=git_url)
    try:
        git.Repo.clone_from(app.git_url, app.git_dir)
    except GitError as e:
        raise HamrError("git clone failed") from e
    return app


def is_valid_git_dir(path):
    try:
        _ = git.Repo(path)
    except InvalidGitRepositoryError:
        return False
    else:
        return True


def get_version(git_dir):
    repo = git.Repo(git_dir)
    return repo.head.commit.hexsha[:7] if repo.head.is_valid() else None
