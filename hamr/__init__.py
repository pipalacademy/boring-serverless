import git
from pathlib import Path


base_path = Path(__file__).parent.parent
APPS_DIR = base_path / "apps"


class UserApp:
    def __init__(self, name, git_url, git_dir):
        self.name = name
        self.app_root = APPS_DIR / name
        self.git_url = git_url
        self.git_dir = git_dir
        self.version = get_version(self.git_dir) if self.git_dir else None

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

    def git_clone(self):
        git.Repo.clone_from(self.git_url, self.git_dir)

    def git_pull(self):
        git.Repo(self.git_dir).remotes.origin.pull()

    def git_fetch(self):
        git.Repo(self.git_dir).remotes.origin.fetch()

    def is_update_available(self):
        repo = git.Repo(self.git_dir)
        branch = repo.head.ref
        branch_name = branch.name
        origin = repo.remotes.origin
        remote_branch = branch_name in origin.refs and origin.refs[branch_name]
        return remote_branch and remote_branch.commit != branch.commit

    def deploy(self):
        # TODO: check should be whether remote origin exists
        if (self.git_dir / ".git").exists():
            self.git_pull()
        else:
            # self.git_clone()
            raise Exception("App dir doesn't exist")


def get_apps():
    apps = []

    # get sub directories
    for appdir in APPS_DIR.glob("*/"):
        apps.append(get_app_from_dir(appdir))

    return apps


def get_gh_app(repo_owner, repo_name):
    git_url = get_repo_url(repo_owner, repo_name)
    git_dir = get_repo_dir(repo_owner, repo_name)
    return UserApp(git_url=git_url, git_dir=git_dir)


def get_repo_url(owner_name, repo_name):
    return f"https://github.com/{owner_name}/{repo_name}"


def get_app_by_name(app_name):
    app_dir = APPS_DIR / app_name
    if app_dir.is_dir():
        return get_app_from_dir(app_dir)

    return None


def get_app_from_dir(app_dir):
    git_dir = app_dir
    repo = git.Repo(git_dir)
    git_url = (None if repo.bare or not repo.remotes
               else next(repo.remote("origin").urls))

    return UserApp(name=app_dir.name, git_url=git_url, git_dir=git_dir)


def get_repo_dir(owner_name, repo_name):
    APPS_DIR.mkdir(exist_ok=True)

    return APPS_DIR / owner_name


def get_version(git_dir):
    repo = git.Repo(git_dir)
    return repo.head.commit.hexsha[:7] if repo.head.is_valid() else None
