"""
Walks a cloned repo on disk, skips folders/files we don't care about,
and reads the contents of the source files we do care about.
"""

from pathlib import Path

# Directories we never want to index — dependencies, build output, VCS internals.
# If we indexed these, most search results would be library code, not the
# user's actual code.
IGNORED_DIRS = {
    ".git",
    "node_modules",
    "venv",
    ".venv",
    "__pycache__",
    "dist",
    "build",
}

# MVP scope: Python only, per the recommended build order (add more languages later).
ALLOWED_EXTENSIONS = {".py"}


def scan_repository(repo_path: str) -> list[dict]:
    """
    Walks every file under repo_path and returns a list of dicts:
    [{"file": "src/auth.py", "content": "...", "language": "python"}, ...]

    "file" is a path relative to the repo root — that's what we'll later
    show the user as a source reference, so it needs to be readable, not
    an absolute /tmp/... path.
    """
    root = Path(repo_path)
    results = []

    # rglob("*") = recursively list every file and folder under root.
    for path in root.rglob("*"):

        # Skip anything that lives inside an ignored directory. We check
        # path.parts (the folder names in the path) against IGNORED_DIRS
        # rather than just the immediate parent, because a bad folder
        # could be nested several levels deep.
        if any(part in IGNORED_DIRS for part in path.parts):
            continue

        # Skip directories themselves — we only want files.
        if not path.is_file():
            continue

        # Skip anything that isn't a Python file for this MVP.
        if path.suffix not in ALLOWED_EXTENSIONS:
            continue

        # Some files can fail to decode as UTF-8 (rare, but happens with
        # odd encodings). Skip rather than crash the whole scan.
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

        results.append(
            {
                "file": str(path.relative_to(root)),
                "content": content,
                "language": "python",
            }
        )

    return results
