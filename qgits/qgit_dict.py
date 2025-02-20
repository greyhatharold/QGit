from typing import Dict, Any

# Dictionary containing help information and configuration for all qgit commands
# Each command has a description, usage pattern, and available options
QGIT_COMMANDS: Dict[str, Dict[str, Any]] = {
    'commit': {
        'description': 'Stage and commit all modified files',
        'usage': 'qgit commit [-m MESSAGE]',
        'options': {
            '-m, --message': 'Specify a custom commit message'
        }
    },
    'sync': {
        'description': 'Pull and push changes from/to the current branch', 
        'usage': 'qgit sync',
        'options': {}
    },
    'save': {
        'description': 'Commit all changes and sync with remote in one step',
        'usage': 'qgit save [-m MESSAGE]',
        'options': {
            '-m, --message': 'Specify a custom commit message'
        }
    },
    'all': {
        'description': 'Stage, commit, and optionally push all changes',
        'usage': 'qgit all [-m MESSAGE] [-p]',
        'options': {
            '-m, --message': 'Specify a custom commit message',
            '-p, --push': 'Push changes after committing'
        }
    },
    'first': {
        'description': 'Initialize a new git repository and set up GitHub remote',
        'usage': 'qgit first',
        'options': {}
    },
    'reverse': {
        'description': 'Untrack specified files from git while preserving them locally',
        'usage': 'qgit reverse [--patterns PATTERN...]',
        'options': {
            '--patterns': 'Specify custom file patterns to untrack'
        }
    },
    'benedict': {
        'description': 'Scan codebase for potentially risky files and update .gitignore',
        'usage': 'qgit benedict [--arnold]',
        'options': {
            '--arnold': 'Automatically update .gitignore and reverse tracked files'
        }
    },
    'expel': {
        'description': 'Untrack all currently tracked files while preserving them locally',
        'usage': 'qgit expel',
        'options': {}
    },
    'undo': {
        'description': 'Safely undo recent git operations',
        'usage': 'qgit undo [n] [options]',
        'options': {
            'n': 'Number of operations to undo (default: 1)',
            '--force, -f': 'Skip safety checks and confirmations', 
            '--dry-run, -d': 'Show what would be undone without making changes',
            '--no-backup': 'Skip creating backup branch',
            '--interactive, -i': 'Choose which operations to undo interactively',
            '--keep-changes': 'Preserve working directory changes during undo',
            '--remote-safe': 'Fail if undo would affect remote branches'
        }
    },
    'snapshot': {
        'description': 'Create a temporary commit of current changes',
        'usage': 'qgit snapshot [options]',
        'options': {
            '-m, --message': 'Optional snapshot description',
            '--no-tag': 'Skip creating a reference tag',
            '--push': 'Push snapshot to remote (useful for backups)',
            '--stash': 'Create as stash instead of commit',
            '--branch NAME': 'Create snapshot on new branch',
            '--expire DAYS': 'Auto-expire snapshot after N days',
            '--include-untracked': 'Include untracked files in snapshot'
        }
    },
    'stats': {
        'description': 'Advanced repository analytics and team insights',
        'usage': 'qgit stats [options]',
        'options': {
            '--author': 'Filter stats for specific author',
            '--from': 'Start date for analysis (YYYY-MM-DD)',
            '--to': 'End date for analysis (YYYY-MM-DD)',
            '--format': 'Output format (text/json)',
            '--team': 'Show team collaboration insights',
            '--files': 'Show file-level statistics'
        }
    },
    'doctor': {
        'description': 'Perform a comprehensive health check of the Git repository',
        'usage': 'qgit doctor',
        'options': {
            '--fix': 'Attempt to automatically fix identified issues',
            '--verbose': 'Show detailed diagnostic information',
            '--check-remote': 'Include remote repository checks',
            '--check-lfs': 'Include Git LFS configuration checks',
            '--check-hooks': 'Include Git hooks validation'
        }
    }
}

def get_command_help(command: str) -> Dict[str, Any]:
    """Get help information for a specific command.
    
    Args:
        command: Name of the command to get help for
        
    Returns:
        Dictionary containing description, usage and options for the command.
        Returns empty dict if command not found.
    """
    return QGIT_COMMANDS.get(command, {})

def get_all_commands() -> Dict[str, Dict[str, Any]]:
    """Get all command definitions.
    
    Returns:
        Dictionary containing help information for all available commands.
        Each command entry includes description, usage pattern and options.
    """
    return QGIT_COMMANDS
