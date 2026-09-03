"""
Splits whole-file contents into smaller pieces ("chunks") that are small
enough to embed and send to an LLM, while keeping track of exactly where
each chunk came from (file + line numbers) so we can cite it later.
"""

CHUNK_SIZE = 60   # lines per chunk
CHUNK_OVERLAP = 10  # lines shared between consecutive chunks


def chunk_file(file: dict, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[dict]:
    """
    Splits a single file's content into overlapping chunks.

    file: {"file": "src/auth.py", "content": "...", "language": "python"}
    returns: [{"content", "file", "language", "start_line", "end_line"}, ...]
    """
    lines = file["content"].splitlines()
    chunks = []

    # Step size is smaller than chunk_size, which is what creates the overlap.
    # e.g. chunk_size=60, overlap=10 -> step=50, so chunk 2 starts at line 50
    # but chunk 1 ran through line 60 — lines 50-60 appear in both.
    #
    # Why overlap at all? If a function definition sits right at line 60,
    # a hard cut would split it in half across two chunks and neither chunk
    # alone would make sense. Overlap makes it much more likely the whole
    # function shows up intact in at least one chunk.
    step = chunk_size - overlap

    for start in range(0, len(lines), step):
        end = min(start + chunk_size, len(lines))
        chunk_lines = lines[start:end]

        # Skip chunks that are only blank lines (common at end of file).
        if not any(line.strip() for line in chunk_lines):
            continue

        chunks.append(
            {
                "content": "\n".join(chunk_lines),
                "file": file["file"],
                "language": file["language"],
                # +1 because splitlines() is 0-indexed but humans (and code
                # editors) count lines starting at 1.
                "start_line": start + 1,
                "end_line": end,
            }
        )

        # Stop once we've covered the last line — otherwise range() keeps
        # generating more starting points that produce empty/duplicate chunks.
        if end == len(lines):
            break

    return chunks


def chunk_files(files: list[dict], chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[dict]:
    """Runs chunk_file() over every file and flattens the results into one list."""
    all_chunks = []
    for file in files:
        all_chunks.extend(chunk_file(file, chunk_size, overlap))
    return all_chunks
