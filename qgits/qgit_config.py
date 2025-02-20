"""Configuration module for qgit CLI and GUI."""

class QGitConfig:
    """Shared configuration for qgit CLI and GUI."""
    
    MENU_ITEMS = [
        ("commit", "Stage and commit changes", "コ"),        # Commit (コミット)
        ("sync", "Pull and push changes", "同"),            # Sync (同期)
        ("save", "Commit and sync in one step", "保"),      # Save (保存)
        ("all", "Stage, commit, and push everything", "全"), # All (全て)
        ("first", "Initialize new repository", "初"),        # First/Initialize (初期化)
        ("reverse", "Untrack sensitive files", "戻"),       # Reverse/Return (戻る)
        ("benedict", "Scan for risky files", "検"),         # Scan/Search (検索)
        ("expel", "Untrack all files", "追"),               # Expel (追放)
        ("doctor", "Health check", "医"),                   # Doctor (医者)
        ("help", "Show detailed help", "助"),               # Help (助け)
        ("quit", "Exit qgit", "出")                         # Exit (出る)
    ]

    HELP_SECTIONS = [
        ("Commands", [
            ("コ commit", "Stage and commit changes", "Stage and commit all modified files with an optional message."),
            ("同 sync", "Pull and push changes", "Pull and push changes from/to the current branch."),
            ("保 save", "Commit and sync in one step", "Commit all changes and sync with remote in one step."),
            ("全 all", "Stage, commit, and push", "Stage, commit, and optionally push all changes."),
            ("初 first", "Initialize new repository", "Initialize a new git repository and set up GitHub remote."),
            ("戻 reverse", "Untrack files", "Untrack specified files from git while preserving them locally."),
            ("検 benedict", "Scan for risky files", "Scan codebase for potentially risky files and update .gitignore."),
            ("追 expel", "Untrack all files", "Untrack all currently tracked files while preserving them locally."),
            ("撤 undo", "Undo operations", "Safely undo recent git operations."),
            ("写 snapshot", "Create snapshot", "Create a temporary commit of current changes."),
            ("統 stats", "View analytics", "Advanced repository analytics and team insights."),
            ("医 doctor", "Health check", "Perform a comprehensive health check of the Git repository."),
        ]),
        ("Options", [
            ("-m, --message", "Specify commit message", "Set a custom commit message instead of using the default."),
            ("-p, --push", "Push after commit", "Automatically push changes after successful commit."),
            ("--arnold", "Auto-benedict completion", "Automatically handle gitignore and reverse files after scanning."),
            ("--force, -f", "Force operation", "Skip safety checks and proceed with the operation."),
            ("--dry-run, -d", "Simulate operation", "Show what would happen without making changes."),
            ("--no-backup", "Skip backup", "Skip creating backup branch during undo."),
            ("--interactive, -i", "Interactive mode", "Choose which operations to undo interactively."),
            ("--keep-changes", "Preserve changes", "Preserve working directory changes during undo."),
            ("--remote-safe", "Remote safety", "Fail if operation would affect remote branches."),
            ("--no-tag", "Skip tagging", "Skip creating a reference tag for snapshots."),
            ("--stash", "Use stash", "Create snapshot as stash instead of commit."),
            ("--branch NAME", "New branch", "Create snapshot on new branch."),
            ("--expire DAYS", "Auto-expire", "Auto-expire snapshot after N days."),
            ("--include-untracked", "Include untracked", "Include untracked files in snapshot."),
            ("--author", "Filter by author", "Filter stats for specific author."),
            ("--team", "Team insights", "Show team collaboration insights."),
            ("--files", "File stats", "Show file-level statistics."),
            ("--fix", "Auto-fix issues", "Attempt to automatically fix identified issues."),
            ("--verbose", "Detailed output", "Show detailed diagnostic information."),
            ("--check-remote", "Remote checks", "Include remote repository checks."),
            ("--check-lfs", "LFS checks", "Include Git LFS configuration checks."),
            ("--check-hooks", "Hook checks", "Include Git hooks validation."),
        ]),
        ("Examples", [
            ("Basic Commit", "qgit commit", "Stage and commit all changes with default message."),
            ("Custom Message", "qgit commit -m 'Fix bug #123'", "Commit with a specific message."),
            ("Quick Sync", "qgit sync", "Pull and push changes in one command."),
            ("Complete Push", "qgit all -m 'Complete feature' -p", "Stage, commit, and push everything."),
            ("New Repo", "qgit first", "Initialize a new repository in current directory."),
            ("Security Scan", "qgit benedict", "Scan project for sensitive files."),
            ("Quick Undo", "qgit undo", "Safely undo last operation."),
            ("Create Snapshot", "qgit snapshot -m 'WIP' --expire 7", "Create temporary snapshot that expires in 7 days."),
            ("Team Stats", "qgit stats --team", "View team collaboration insights."),
            ("Health Check", "qgit doctor --verbose", "Run detailed repository health check."),
        ]),
        ("Shortcuts", [
            ("Navigation", "↑/↓", "Move between items"),
            ("", "←/→", "Switch between tabs"),
            ("", "Tab", "Next section"),
            ("", "Shift+Tab", "Previous section"),
            ("Actions", "Enter", "Select/Execute"),
            ("", "Space", "Toggle/Expand"),
            ("", "q/Esc", "Back/Quit"),
            ("Search", "/", "Start search"),
            ("", "n", "Next search result"),
            ("", "N", "Previous search result"),
            ("Scrolling", "PgUp/PgDn", "Page up/down"),
            ("", "Home/End", "Top/Bottom"),
        ])
    ]

    @classmethod
    def get_cli_help_text(cls):
        """Generate help text for CLI display."""
        help_text = """
Griffin's QGit - Quick Git Operations
==================================\n"""
        
        for section_name, items in cls.HELP_SECTIONS:
            if section_name == "Shortcuts":  # Skip shortcuts in CLI help
                continue
                
            help_text += f"\n{section_name}:\n"
            help_text += "-" * (len(section_name) + 1) + "\n"
            
            for item in items:
                if len(item) == 3:
                    command, short_desc, long_desc = item
                    help_text += f"{command.ljust(15)} {short_desc}\n"
                    if long_desc:
                        help_text += " " * 15 + f"({long_desc})\n"
                else:
                    category, shortcut, desc = item
                    if category:
                        help_text += f"{category.ljust(15)} {shortcut}\n"
                        if desc:
                            help_text += " " * 15 + f"({desc})\n"
        
        return help_text
