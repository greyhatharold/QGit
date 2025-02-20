#!/usr/bin/env python3

"""Utility functions for qgit operations."""

import os
import fnmatch
from typing import Dict, List, Any, Tuple
from pathlib import Path
from datetime import datetime

def detect_risky_files(directory: str = '.', batch_size: int = 1000) -> Tuple[Dict[str, List[Dict[str, Any]]], int]:
    """Scan directory for potentially risky files.
    
    Args:
        directory: Directory to scan
        batch_size: Number of files to process in each batch
        
    Returns:
        Tuple of (scan results by category, total files scanned)
    """
    risky_patterns = {
        'secrets': [
            '*.pem', '*.key', '*.cert', '*.p12', '*.pfx',  # Certificates and keys
            '*password*', '*secret*', '*credential*',       # Common secret patterns
            '*.env', '.env.*', '.env',                     # Environment files
            '*config*.json', '*config*.yaml', '*config*.yml',  # Config files
            '*auth*', '*token*',                           # Auth-related files
            'id_rsa', 'id_dsa', '*.pub',                   # SSH keys
        ],
        'large_files': [
            '*.zip', '*.tar.gz', '*.tar', '*.rar',        # Archives
            '*.iso', '*.img', '*.dmg',                    # Disk images
            '*.mp4', '*.mov', '*.avi', '*.mkv',          # Videos
            '*.jpg', '*.jpeg', '*.png', '*.gif',         # Images
            '*.pdf', '*.doc', '*.docx', '*.ppt',         # Documents
            '*.bin', '*.exe', '*.dll',                   # Binaries
        ],
        'development': [
            '__pycache__/', '*.pyc', '*.pyo',            # Python cache
            'node_modules/', 'bower_components/',         # JS dependencies
            'vendor/', 'packages/',                       # Package directories
            '.venv/', 'venv/', 'env/',                   # Virtual environments
            'build/', 'dist/', '*.egg-info/',            # Build artifacts
            '.gradle/', 'target/',                       # Build directories
            '*.log', 'logs/', '*.debug',                 # Log files
            '.DS_Store', 'Thumbs.db',                    # OS files
            '*.swp', '*.swo', '*~',                      # Editor files
            '*.sqlite', '*.db', '*.sqlite3',             # Databases
            '.idea/', '.vscode/', '*.sublime-*',         # IDE files
        ]
    }

    results = {category: [] for category in risky_patterns}
    file_count = 0
    batch = []

    def process_batch(batch: List[str]) -> None:
        for filepath in batch:
            try:
                size = os.path.getsize(filepath)
                for category, patterns in risky_patterns.items():
                    for pattern in patterns:
                        if fnmatch.fnmatch(filepath, pattern):
                            results[category].append({
                                'path': filepath,
                                'size': size,
                                'pattern': pattern
                            })
                            break
            except OSError:
                continue

    for root, dirs, files in os.walk(directory):
        # Skip .git directory
        if '.git' in dirs:
            dirs.remove('.git')

        for file in files:
            filepath = os.path.join(root, file)
            batch.append(filepath)
            file_count += 1

            if len(batch) >= batch_size:
                process_batch(batch)
                batch = []

    # Process remaining files
    if batch:
        process_batch(batch)

    return results, file_count

def format_size(size: int) -> str:
    """Format file size in human readable format.
    
    Args:
        size: Size in bytes
        
    Returns:
        Formatted size string
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024:
            return f"{size:.1f}{unit}"
        size /= 1024
    return f"{size:.1f}PB"

def format_category_emoji(category: str) -> str:
    """Get emoji for file category.
    
    Args:
        category: Category name
        
    Returns:
        Emoji string for category
    """
    emoji_map = {
        'secrets': '🔒',
        'large_files': '📦',
        'development': '⚙️'
    }
    return emoji_map.get(category, '📄')

def group_files_by_pattern(files: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Group files by their matching pattern.
    
    Args:
        files: List of file information dictionaries
        
    Returns:
        Dictionary mapping patterns to lists of matching files
    """
    groups = {}
    for file_info in files:
        pattern = file_info['pattern']
        if pattern not in groups:
            groups[pattern] = []
        groups[pattern].append(file_info)
    return groups

def generate_gitignore_from_scan(scan_results: Dict[str, List[Dict[str, Any]]]) -> str:
    """Generate .gitignore content from scan results.
    
    Args:
        scan_results: Results from repository scan
        
    Returns:
        Generated .gitignore content
    """
    patterns = set()
    for category, files in scan_results.items():
        for file_info in files:
            pattern = file_info['pattern']
            # Convert glob pattern to git pattern if needed
            if pattern.startswith("*."):
                pattern = pattern[1:]  # Remove leading *
            patterns.add(pattern)
    
    # Sort patterns for consistency
    sorted_patterns = sorted(patterns)
    
    # Generate .gitignore content with categories
    content = [
        "# Generated by qgit benedict",
        "# https://github.com/qgit/qgit",
        "",
        "# Secrets and credentials",
        "*.pem",
        "*.key",
        "*.cert",
        "*.env",
        ".env*",
        "*password*",
        "*secret*",
        "*credential*",
        "id_rsa",
        "id_dsa",
        "",
        "# Development artifacts",
        "__pycache__/",
        "*.pyc",
        "node_modules/",
        "bower_components/",
        ".venv/",
        "venv/",
        "env/",
        "build/",
        "dist/",
        "*.egg-info/",
        "",
        "# Logs and databases",
        "*.log",
        "logs/",
        "*.sqlite",
        "*.db",
        "*.sqlite3",
        "",
        "# IDE files",
        ".idea/",
        ".vscode/",
        "*.sublime-*",
        "",
        "# OS files",
        ".DS_Store",
        "Thumbs.db",
        "",
        "# Additional patterns from scan"
    ]
    
    # Add any patterns not already included
    existing_patterns = set(p.strip() for p in content if not p.startswith('#') and p.strip())
    additional_patterns = [p for p in sorted_patterns if p not in existing_patterns]
    
    if additional_patterns:
        content.extend(additional_patterns)
    
    return "\n".join(content)

def check_tracked_files(file_patterns: List[str] = None) -> Dict[str, Dict[str, Any]]:
    """Check for problematic files that are being tracked."""
    if file_patterns is None:
        file_patterns = [
            "*.db", "*.sqlite3",          # Database files
            "*.log", "logs/",             # Log files
            "__pycache__/", "*.pyc",      # Python cache
            ".env", ".venv/", "venv/",    # Virtual environments
            ".DS_Store",                  # macOS files
            "node_modules/",              # Node.js modules
            "*.cache", ".cache/",         # Cache files
        ]

    try:
        from .qgit_core import run_command
        # Get list of tracked files
        tracked_files = run_command("git ls-files").split('\n')
        
        problematic_files = {}
        for pattern in file_patterns:
            # Convert git pattern to Python glob pattern
            if pattern.startswith("*"):
                pattern = f".{pattern}"
            
            matches = [f for f in tracked_files if fnmatch.fnmatch(f, pattern)]
            
            for file in matches:
                try:
                    size = os.path.getsize(file)
                    problematic_files[file] = {
                        'size': size,
                        'pattern': pattern
                    }
                except OSError:
                    continue

        return problematic_files

    except Exception as e:
        print(f"Error checking tracked files: {str(e)}")
        return {} 