"""
Handles getting a GitHub repository onto local disk so we can read its files.
"""

import shutil
import tempfile

from git import Repo


def clone_repository(repo_url: str) -> str:
    """
    Clones a GitHub repo into a fresh temp directory and returns the local path.

    repo_url: full https URL, e.g. "https://github.com/user/project"
    """
    # Make a brand-new empty folder on disk. We don't reuse folders because
    # a leftover clone from a previous repo could confuse the file scanner.
    local_path = tempfile.mkdtemp(prefix="repo_")

    # depth=1 = "shallow clone": only grab the latest snapshot of the code,
    # not the full commit history. We don't need history for RAG, and it's
    # much faster + smaller.
    Repo.clone_from(repo_url, local_path, depth=1)

    return local_path


def cleanup_repository(local_path: str) -> None:
    """Deletes the cloned repo from disk once we're done indexing it."""
    shutil.rmtree(local_path, ignore_errors=True)
