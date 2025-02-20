#!/usr/bin/env python3
"""QGit command implementations for various Git operations.

This module contains the command classes that implement different Git operations
like scanning for sensitive files, generating repository statistics, and performing
health checks. Each command inherits from the base QGitCommand class.
"""

import os
import argparse
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict, Any

from .qgit_core import run_command, is_git_repo, get_current_branch
from .qgit_utils import format_size, detect_risky_files, format_category_emoji, group_files_by_pattern, generate_gitignore_from_scan, check_tracked_files
from .secret_sauce import SecretSauce
from .qgit_errors import (
    QGitError, GitCommandError, GitConfigError, GitRepositoryError,
    GitStateError, GitNetworkError, FileOperationError, format_error
)

class QGitCommand(ABC):
    """Base class for all qgit commands.
    
    Provides common functionality like status/error message handling and command execution.
    All concrete command classes should inherit from this.
    """
    
    def __init__(self):
        """Initialize command with name derived from class name and empty message lists."""
        self.name = self.__class__.__name__.lower().replace('command', '')
        self.description = self.__doc__ or "No description available"
        self.status_messages = []
        self.error_messages = []
    
    def add_status(self, message: str) -> None:
        """Add a status message to be displayed to the user.
        
        Args:
            message: Status message to add
        """
        self.status_messages.append(message)
    
    def add_error(self, message: str) -> None:
        """Add an error message to be displayed to the user.
        
        Args:
            message: Error message to add
        """
        self.error_messages.append(message)
    
    def handle_error(self, error: Exception) -> None:
        """Handle an error by formatting and storing it appropriately.
        
        Args:
            error: The exception to handle
        """
        formatted_error = format_error(error)
        self.add_error(formatted_error)
        
        # Re-raise certain critical errors
        if isinstance(error, (GitRepositoryError, GitStateError)):
            raise error
    
    def run_command(self, command: str) -> str:
        """Execute a shell command safely and return its output.
        
        Args:
            command: Shell command to execute
            
        Returns:
            Command output as string
            
        Raises:
            GitCommandError: If the command fails
            GitNetworkError: If there are network issues
            GitStateError: If the repository is in an invalid state
        """
        try:
            result = run_command(command)
            return result
        except (GitCommandError, GitNetworkError, GitStateError) as e:
            self.handle_error(e)
            raise
        except Exception as e:
            self.handle_error(e)
            raise GitCommandError(command, str(e))
    
    def verify_repository(self) -> None:
        """Verify that we're in a Git repository.
        
        Raises:
            GitRepositoryError: If not in a Git repository
        """
        if not is_git_repo():
            raise GitRepositoryError(
                "Not a Git repository. Please run 'qgit first' to initialize one or 'git init' manually.",
                command=None,
                error_output=None
            )
    
    @abstractmethod
    def execute(self, args: argparse.Namespace) -> bool:
        """Execute the command with given arguments.
        
        Args:
            args: Parsed command line arguments
            
        Returns:
            True if command executed successfully, False otherwise
            
        Raises:
            QGitError: Base class for all QGit errors
        """
        pass

class BenedictCommand(QGitCommand):
    """Scan codebase for potentially risky files and update .gitignore.
    
    Analyzes the repository for sensitive files like credentials, keys, and logs.
    Can automatically update .gitignore and untrack sensitive files.
    """
    
    def execute(self, args: argparse.Namespace) -> bool:
        """Execute the benedict scan command.
        
        Scans codebase, displays results by category, and optionally updates .gitignore.
        Can also automatically untrack sensitive files if --arnold flag is used.
        
        Args:
            args: Command arguments including arnold flag
            
        Returns:
            True if scan completed successfully, False otherwise
        """
        try:
            from .qgit_benedict import scan_repository, update_gitignore, reverse_tracking
            
            # Verify we're in a git repository
            self.verify_repository()
            
            # Delegate scanning to qgit_benedict
            results, total_files = scan_repository()
            
            # Handle .gitignore updates based on user choice
            should_update = args.arnold or input("\n📝 Would you like to update .gitignore with recommended patterns? (y/N): ").lower() == 'y'
            
            if should_update:
                success = update_gitignore(results, auto_commit=args.arnold)
                if not success:
                    return False
                
                # Handle automatic reverse operation with --arnold flag
                if args.arnold:
                    print("\n🔄 Initiating automatic reverse operation for tracked files...")
                    return reverse_tracking()
                else:
                    print("\n💡 Tip: Run 'qgit reverse' to untrack any already-tracked files matching these patterns")
                    print("   This will help ensure sensitive files are not tracked in git history")
            
            return True
            
        except Exception as e:
            self.handle_error(e)
            return False

class StatsCommand(QGitCommand):
    """Generate advanced repository analytics and team insights.
    
    Analyzes commit history, code churn, and team collaboration patterns.
    Can also generate "secret sauce" insights about repository health.
    """
    
    def execute(self, args: argparse.Namespace) -> bool:
        """Execute the stats generation command.
        
        Collects and displays commit stats, churn metrics, and team collaboration data.
        Also generates repository insights using SecretSauce.
        
        Args:
            args: Command arguments including author filter and team flag
            
        Returns:
            True if stats generated successfully, False otherwise
        """
        try:
            # Collect repository statistics
            commit_stats = self._collect_commit_stats(args.author)
            churn_stats = self._collect_churn_stats()
            team_stats = self._collect_team_stats() if args.team else None
            
            # Display collected statistics
            self._display_stats(commit_stats, churn_stats, team_stats)
            
            # Generate repository insights
            sauce = SecretSauce()
            repo_url = self.run_command("git config --get remote.origin.url")
            
            sauce_data = sauce.read_sauce()
            if not sauce_data:
                sauce_data = sauce.generate_sauce(
                    repo_url=repo_url,
                    commit_data=commit_stats['commits'],
                    authors_data=commit_stats['authors']
                )
            
            # Display additional insights
            self._display_secret_insights(sauce_data)
            
            return True
            
        except Exception as e:
            self.add_error(f"Error generating stats: {str(e)}")
            return False

class DoctorCommand(QGitCommand):
    """Perform a comprehensive health check of the Git repository.
    
    Runs multiple diagnostic checks to identify potential issues with:
    - Repository configuration
    - Remote connectivity
    - Large files
    - Branch status
    - Git hooks
    - .gitignore setup
    - LFS configuration
    - Submodules
    """
    
    def execute(self, args: argparse.Namespace) -> bool:
        """Execute the repository health check.
        
        Runs a series of diagnostic checks and displays results with recommendations.
        
        Args:
            args: Command arguments including verbose and fix flags
            
        Returns:
            True if health check completed, False if critical issues found
        """
        try:
            # Initialize doctor with command line options
            from .qgit_doctor import RepositoryDoctor
            doctor = RepositoryDoctor(
                verbose=args.verbose if hasattr(args, 'verbose') else False,
                fix=args.fix if hasattr(args, 'fix') else False
            )
            
            # Run all checks
            all_passed = doctor.run_all_checks()
            
            # Apply fixes if requested
            if hasattr(args, 'fix') and args.fix:
                fixes_applied, fixes_failed = doctor.apply_fixes()
                if fixes_applied > 0 or fixes_failed > 0:
                    print(f"\n🔧 Applied {fixes_applied} fix(es), {fixes_failed} failed")
                    # Run checks again to verify fixes
                    all_passed = doctor.run_all_checks()
            
            # Print final report
            doctor.print_report()
            
            return all_passed
            
        except Exception as e:
            self.add_error(f"Error during health check: {str(e)}")
            return False 