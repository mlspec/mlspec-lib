import os
import subprocess

import requests
from dotenv import load_dotenv

load_dotenv()
# GitHub credentials
username = "aronchick"

# GitHub personal access token from the GH_TOKEN_SECRET environment variable
token = os.environ.get("GH_TOKEN_SECRET")
if token is None:
    raise ValueError("GH_TOKEN_SECRET environment variable not set")

# Repository information
repo_owner = "mlspec"
repo_name = "mlspec-lib"

# PR number to merge all open PRs into
pr_to_merge_into = "dependabot/pip/jupyter-lsp-2.2.2"


# PR number to exclude from merging
exclude_pr_number = "49"


# Function to merge a branch into a PR locally
def merge_branch_into_pr(branch_name, pr_number):
    # Checkout the branch locally
    subprocess.run(["git", "checkout", branch_name])

    # Merge the branch into the specified PR locally
    subprocess.run(["git", "fetch", "origin", branch_name])

    # Merge the branch into the specified PR locally with a commit message and no confirmation
    subprocess.run(
        [
            "git",
            "merge",
            f"origin/{branch_name}",
            "--no-ff",
            "-m",
            f"Merging {branch_name} into {pr_to_merge_into}",
        ]
    )

    # Commit the changes
    subprocess.run(
        ["git", "commit", "-m", f"Merging {branch_name} into {pr_to_merge_into}"]
    )

    # Push the changes to the remote branch
    subprocess.run(["git", "push", "origin", branch_name])

    # Delete the branch locally and remotely
    subprocess.run(["git", "branch", "-d", branch_name])

    # Delete the branch remotely
    subprocess.run(["git", "push", "origin", "--delete", branch_name])


# Get list of open PRs
url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/pulls"
params = {"state": "open"}
headers = {"Authorization": f"token {token}"}
response = requests.get(url, headers=headers, params=params)
open_prs = response.json()

# Exclude the most recent PR
if open_prs:
    exclude_pr_number = open_prs[0]["number"]

# Merge each branch into the specified PR locally
for pr in open_prs:
    pr_number = pr["number"]
    if pr_number != exclude_pr_number:
        branch_name = pr["head"]["ref"]
        merge_branch_into_pr(branch_name, pr_number)
