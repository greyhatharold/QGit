#!/usr/bin/env python3
"""Core functionality for QGit - Quick Git Operations.

This module provides the core Git operations used by both the CLI and GUI interfaces.
It includes functions for running Git commands, checking repository status, and performing
common Git workflows like committing, syncing, and pushing changes.
"""

import os
from typing import List, Optional

from .qgit_git import GitCommand
from .qgit_errors import (
    GitCommandError, GitConfigError, GitRepositoryError,
    GitStateError, GitNetworkError, FileOperationError,
    format_error
)

def run_command(command: str) -> str:
    """Execute a shell command and return its output.
    
    Args:
        command: The shell command to execute
        
    Returns:
        The command output as string
        
    Raises:
        GitCommandError: If the command fails
        GitNetworkError: If the command fails due to network issues
        GitStateError: If the repository is in an invalid state
    """
    return GitCommand.run(command)

def get_current_branch() -> str:
    """Get the name of the current Git branch.
    
    Returns:
        The name of the current branch
        
    Raises:
        GitRepositoryError: If not in a Git repository
        GitStateError: If the repository is in an invalid state
    """
    return GitCommand.get_current_branch()

def get_staged_files() -> List[str]:
    """Get list of staged files.
    
    Returns:
        List of filenames that are currently staged
        
    Raises:
        GitRepositoryError: If not in a Git repository
        GitStateError: If the repository is in an invalid state
    """
    return GitCommand.get_staged_files()

def get_modified_files() -> List[str]:
    """Get list of modified files.
    
    Returns:
        List of filenames that have been modified but not staged
        
    Raises:
        GitRepositoryError: If not in a Git repository
        GitStateError: If the repository is in an invalid state
    """
    return GitCommand.get_modified_files()

def is_git_repo() -> bool:
    """Check if current directory is a git repository.
    
    Returns:
        True if current directory is a git repo, False otherwise
    """
    return GitCommand.is_repo()

def format_size(size: int) -> str:
    """Format file size in a human-readable way.
    
    Args:
        size: Size in bytes
        
    Returns:
        Formatted string with appropriate unit (B, KB, MB, GB, TB)
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} TB"

def quick_commit(message: Optional[str] = None) -> bool:
    """Perform a quick commit with optional message.
    
    Stages and commits all modified files in one step.
    
    Args:
        message: Optional commit message. If None, uses "Automated commit"
        
    Returns:
        True if commit was successful, False if no changes to commit
        
    Raises:
        GitCommandError: If the commit operation fails
        GitStateError: If the repository is in an invalid state
    """
    try:
        modified = get_modified_files()
        if not modified or modified == ['']:
            print("No modified files to commit.")
            return False

        # Stage all modified files
        GitCommand.stage_files()
        
        # If no message provided, generate one based on changed files
        if not message:
            message = "Automated commit"

        # Commit changes
        GitCommand.commit(message)
        print(f"Committed changes with message: {message}")
        return True
        
    except (GitCommandError, GitStateError) as e:
        print(format_error(e))
        return False

def sync_branch() -> None:
    """Sync current branch with remote.
    
    Pulls latest changes from remote and pushes local changes.
    This ensures the local and remote branches are synchronized.
    
    Raises:
        GitCommandError: If sync operations fail
        GitNetworkError: If there are network issues
        GitStateError: If the repository is in an invalid state
    """
    try:
        current_branch = get_current_branch()
        
        # Pull latest changes
        print(f"Pulling latest changes from {current_branch}...")
        GitCommand.pull()
        
        # Push changes
        print(f"Pushing changes to {current_branch}...")
        GitCommand.push()
        
    except (GitCommandError, GitNetworkError, GitStateError) as e:
        print(format_error(e))
        raise

def all_in_one(message: Optional[str] = None, push: bool = False) -> None:
    """Stage, commit, and optionally push all changes.
    
    A convenience function that combines staging, committing and pushing into one step.
    
    Args:
        message: Optional commit message. If None, uses "Automated commit"
        push: Whether to push changes after committing
        
    Raises:
        GitCommandError: If any Git operation fails
        GitNetworkError: If push fails due to network issues
        GitStateError: If the repository is in an invalid state
        GitRepositoryError: If not in a Git repository
    """
    # First check if we're in a git repository
    if not is_git_repo():
        raise GitRepositoryError(
            "Not a Git repository. Please run 'qgit first' to initialize one or 'git init' manually.",
            command=None,
            error_output=None
        )

    try:
        # Check for any changes (untracked, modified, or staged)
        untracked = GitCommand.get_untracked_files()
        modified = get_modified_files()
        staged = get_staged_files()

        if not any([f for f in untracked + modified + staged if f]):
            print("No changes to commit.")
            return

        # Add all untracked and modified files
        print("Adding all changes...")
        GitCommand.stage_files()
        
        # Commit changes
        if not message:
            message = "Automated commit"
        
        GitCommand.commit(message)
        print(f"Committed changes with message: {message}")
        
        if push:
            print("Pushing changes to remote...")
            current_branch = get_current_branch()
            GitCommand.push("origin", current_branch)
            print("All changes have been staged, committed, and pushed!")
        else:
            print("All changes have been staged and committed!")
            
    except (GitCommandError, GitNetworkError, GitStateError) as e:
        print(format_error(e))
        raise

def first() -> None:
    """Initialize a new Git repository and set up GitHub remote.
    
    This function:
    1. Initializes a new Git repository if one doesn't exist
    2. Creates a README.md if it doesn't exist
    3. Makes an initial commit
    4. Optionally sets up GitHub remote if GITHUB_TOKEN is available
    
    Raises:
        GitCommandError: If Git operations fail
        GitStateError: If repository is in an invalid state
        FileOperationError: If file operations fail
    """
    try:
        # Check if already a git repo
        if is_git_repo():
            print("Repository already initialized!")
            return

        # Initialize new repository
        print("Initializing new Git repository...")
        GitCommand.run("git init")

        # Create README.md if it doesn't exist
        if not os.path.exists("README.md"):
            print("Creating README.md...")
            try:
                with open("README.md", "w") as f:
                    f.write("# New Repository\n\nInitialized with qgit first command.")
            except IOError as e:
                raise FileOperationError("Failed to create README.md", str(e))

        # Stage and commit
        print("Creating initial commit...")
        GitCommand.stage_files()
        GitCommand.commit("Initial commit", allow_empty=True)

        # Set up GitHub remote if token is available
        github_token = os.getenv('GITHUB_TOKEN')
        if github_token:
            print("GitHub token found. You can now create and link a GitHub repository.")
            print("Use: git remote add origin https://github.com/USERNAME/REPO.git")
        else:
            print("\nTip: Set GITHUB_TOKEN environment variable to enable GitHub integration.")

        print("\n✨ Repository initialized successfully!")
        print("Next steps:")
        print("1. Add your project files")
        print("2. Use 'qgit commit' to commit changes")
        print("3. Set up a remote repository and use 'qgit sync' to synchronize")

    except (GitCommandError, GitStateError) as e:
        print(format_error(e))
        raise
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise