"""
Milestone 1: given a GitHub URL, clone it, find the Python files, print them.
Run: python main.py https://github.com/user/project
"""

import sys

from ingestion.github import clone_repository, cleanup_repository
from ingestion.file_loader import scan_repository
from ingestion.chunker import chunk_files


def main(repo_url: str) -> None:
    print(f"Cloning {repo_url} ...")
    local_path = clone_repository(repo_url)

    try:
        print("Scanning for Python files ...")
        files = scan_repository(local_path)
        print(f"Found {len(files)} Python files\n")

        print("Chunking files ...")
        chunks = chunk_files(files)
        print(f"Created {len(chunks)} chunks\n")

        for c in chunks:
            print(f"📄 {c['file']}  lines {c['start_line']}-{c['end_line']}")

    finally:
        # Always clean up the temp clone, even if scanning throws an error.
        cleanup_repository(local_path)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py <github_repo_url>")
        sys.exit(1)

    main(sys.argv[1])
