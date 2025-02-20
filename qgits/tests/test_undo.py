import os
import pytest
import subprocess
from unittest.mock import patch, MagicMock
import tempfile
import shutil
from datetime import datetime

# Import the functions we want to test
from qgit import undo_operation, run_command, create_snapshot

class TestUndoOperation:
    @pytest.fixture
    def git_repo(self):
        """Create a temporary git repository for testing."""
        old_cwd = os.getcwd()
        with tempfile.TemporaryDirectory() as tmp_dir:
            os.chdir(tmp_dir)
            subprocess.run(["git", "init"], check=True)
            subprocess.run(["git", "config", "user.name", "Test User"], check=True)
            subprocess.run(["git", "config", "user.email", "test@example.com"], check=True)
            
            # Create initial commit
            with open("test.txt", "w") as f:
                f.write("initial content")
            subprocess.run(["git", "add", "test.txt"], check=True)
            subprocess.run(["git", "commit", "-m", "Initial commit"], check=True)
            
            yield tmp_dir
            
            os.chdir(old_cwd)

    def test_repository_validation(self, git_repo):
        """Test that undo checks for valid git repository."""
        # Test in git repo
        assert undo_operation(1) is True
        
        # Test outside git repo
        os.chdir("/tmp")
        assert undo_operation(1) is False

    def test_uncommitted_changes_backup(self, git_repo):
        """Test handling of uncommitted changes."""
        # Create uncommitted changes
        with open("test.txt", "a") as f:
            f.write("\nmore content")
        
        with patch('builtins.input', return_value='y'):
            with patch('qgit.create_snapshot') as mock_snapshot:
                undo_operation(1)
                mock_snapshot.assert_called_once()

    def test_backup_branch_creation(self, git_repo):
        """Test that backup branch is created correctly."""
        # Make a commit to undo
        with open("test.txt", "a") as f:
            f.write("\nmore content")
        subprocess.run(["git", "add", "test.txt"], check=True)
        subprocess.run(["git", "commit", "-m", "Test commit"], check=True)
        
        undo_operation(1)
        
        # Check for backup branch
        branches = subprocess.check_output(["git", "branch"], text=True)
        assert any(branch.strip().startswith("backup/undo_") for branch in branches.split('\n'))

    def test_remote_branch_detection(self, git_repo):
        """Test detection of operations affecting remote branches."""
        # Set up remote
        subprocess.run(["git", "remote", "add", "origin", "https://github.com/test/test.git"], check=True)
        
        # Simulate remote branch
        with patch('qgit.run_command') as mock_run:
            mock_run.return_value = "origin/main"
            with patch('builtins.input', return_value='n'):  # Reject the operation
                result = undo_operation(1)
                assert result is False  # Operation should be cancelled

    def test_operation_categorization(self, git_repo):
        """Test correct categorization of different operations."""
        # Create different types of operations
        operations = [
            ("commit", "git commit -m 'Regular commit'"),
            ("snapshot", "git commit -m 'SNAPSHOT: Test snapshot'"),
            ("merge", "git merge branch_name"),
        ]
        
        for op_type, command in operations:
            with patch('qgit.run_command') as mock_run:
                mock_run.return_value = f"HEAD {op_type} {command}"
                with patch('builtins.print') as mock_print:
                    undo_operation(1)
                    # Verify operation was correctly identified
                    mock_print.assert_any_call(f"\n1. Operation: {op_type.upper()}")

    def test_error_recovery(self, git_repo):
        """Test recovery mechanism when undo fails."""
        # Force an error during undo
        with patch('qgit.run_command') as mock_run:
            mock_run.side_effect = [
                "",  # git status
                "",  # create backup branch
                Exception("Simulated error")
            ]
            
            with patch('builtins.input', return_value='y'):  # Accept recovery
                result = undo_operation(1)
                assert result is False
                # Verify recovery was offered
                mock_run.assert_any_call("git branch backup/undo_")

    def test_remote_sync_status(self, git_repo):
        """Test detection of remote sync status after undo."""
        # Set up remote and create divergence
        subprocess.run(["git", "remote", "add", "origin", "https://github.com/test/test.git"], check=True)
        
        with patch('qgit.run_command') as mock_run:
            mock_run.return_value = "1\t0"  # 1 commit ahead, 0 behind
            result = undo_operation(1)
            assert result is True
            # Verify warning about being ahead of remote
            mock_run.assert_any_call("git rev-list --left-right --count origin/main...HEAD")

    def test_multiple_operation_undo(self, git_repo):
        """Test undoing multiple operations at once."""
        # Create multiple commits
        for i in range(3):
            with open("test.txt", "a") as f:
                f.write(f"\ncontent {i}")
            subprocess.run(["git", "add", "test.txt"], check=True)
            subprocess.run(["git", "commit", "-m", f"Commit {i}"], check=True)
        
        result = undo_operation(3)
        assert result is True
        
        # Verify commits were undone
        log = subprocess.check_output(["git", "log", "--oneline"], text=True)
        assert len(log.split('\n')) == 2  # Initial commit + empty line

    def test_snapshot_handling(self, git_repo):
        """Test proper handling of snapshot commits during undo."""
        # Create a snapshot
        create_snapshot("Test snapshot")
        
        result = undo_operation(1)
        assert result is True
        
        # Verify snapshot was removed
        log = subprocess.check_output(["git", "log", "--oneline"], text=True)
        assert "SNAPSHOT:" not in log

    def test_merge_conflict_handling(self, git_repo):
        """Test handling of merge conflicts during undo."""
        # Create a branch with conflicting changes
        subprocess.run(["git", "checkout", "-b", "test-branch"], check=True)
        with open("test.txt", "w") as f:
            f.write("branch content")
        subprocess.run(["git", "add", "test.txt"], check=True)
        subprocess.run(["git", "commit", "-m", "Branch commit"], check=True)
        
        subprocess.run(["git", "checkout", "main"], check=True)
        with open("test.txt", "w") as f:
            f.write("main content")
        subprocess.run(["git", "add", "test.txt"], check=True)
        subprocess.run(["git", "commit", "-m", "Main commit"], check=True)
        
        # Try to merge (will create conflict)
        try:
            subprocess.run(["git", "merge", "test-branch"], check=True)
        except subprocess.CalledProcessError:
            pass
        
        result = undo_operation(1)
        assert result is True
        
        # Verify we're not in a merge conflict state
        status = subprocess.check_output(["git", "status"], text=True)
        assert "You have unmerged paths" not in status

if __name__ == '__main__':
    pytest.main([__file__]) 