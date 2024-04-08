import requests
import os
import git


def get_branches(repo_url):
    parts = repo_url.strip("/").split("/")
    if len(parts) != 5 or parts[0] != "https:" or parts[2] != "github.com":
        raise ValueError("Invalid GitHub repository URL")

    username, repo_name = parts[3], parts[4]

    api_url = f"https://api.github.com/repos/{username}/{repo_name.rstrip('.git')}/branches"
    response = requests.get(api_url)

    if response.status_code == 200:
        branches = [branch['name'] for branch in response.json()]
        return branches
    else:
        response.raise_for_status()


def get_git_executable_path():
    # Check if Git executable path is set via environment variable
    git_executable_path = os.environ.get('GIT_PYTHON_GIT_EXECUTABLE')
    if git_executable_path:
        return git_executable_path

    # Check common installation directories for Git
    common_git_paths = [
        '/usr/bin/git',  # Linux
        '/usr/local/bin/git',  # Linux
        'C://Program Files//Git//cmd//git.exe',  # Windows
        'C://Program Files//Git//bin//git.exe',  # Windows
    ]
    for path in common_git_paths:
        if os.path.exists(path):
            return path

    # If not found, return None or handle accordingly
    return None


def checkout_branch(repo_url, branch_name, path):
    # Specify the path to the Git executable
    git_executable_path = get_git_executable_path()
    if git_executable_path:
        git.Git().custom_environment(GIT_PYTHON_GIT_EXECUTABLE=git_executable_path)
    else:
        raise ValueError("Git executable path not found.")

    # Clone the repository
    repo = git.Repo.clone_from(repo_url, path)

    # Checkout the specified branch
    repo.git.checkout(branch_name)