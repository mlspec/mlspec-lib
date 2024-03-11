#!/bin/bash

# Function to merge and delete branches
merge_and_delete() {
    # Get the current branch name
    current_branch=$(git rev-parse --abbrev-ref HEAD)

    # Merge all branches into the current branch
    git checkout "$current_branch"
    git fetch origin
    git pull origin "$current_branch"
    git fetch --all
    git pull --all
    git merge --no-ff "$1"

    # Delete the branch locally
    git branch -d "$1"

    # Delete the branch remotely
    git push origin --delete "$1"
}

# Get the list of branches
branches=$(git branch -r --merged | grep -v HEAD | grep -v master | sed 's/origin\///')

# Loop through each branch
for branch in $branches; do
    # Merge and delete the branch
    merge_and_delete "$branch"
done

echo "All branches merged and deleted successfully."

