"""
gofile_resolver.py — Resolve a GoFile share link to a direct download URL.

Usage (standalone):
    python gofile_resolver.py [gofile_content_id]

    Example:
        python gofile_resolver.py Ke5wvh

    If no argument is provided, defaults to the modpack content ID (Ke5wvh).

Returns the first download URL found (printed to stdout).
Also importable: use resolve_gofile_url(content_id) -> str | None
"""

import sys
import requests

# Default modpack GoFile content ID (from https://gofile.io/d/Ke5wvh)
DEFAULT_CONTENT_ID = "Ke5wvh"

GOFILE_API_BASE = "https://api.gofile.io"


def _create_guest_token(timeout: int = 15) -> str:
    """Create a GoFile guest account and return its token."""
    resp = requests.post(f"{GOFILE_API_BASE}/accounts", timeout=timeout)
    resp.raise_for_status()
    data = resp.json()
    if data.get("status") != "ok":
        raise RuntimeError(f"GoFile accounts API error: {data}")
    token = data["data"]["token"]
    return token


def resolve_gofile_url(content_id: str, timeout: int = 15) -> str:
    """
    Resolve a GoFile content ID to a direct download URL.

    Steps:
      1. Create a guest account token (POST /accounts).
      2. Fetch content metadata (GET /contents/{content_id}).
      3. Walk the children to find the first downloadable file URL.

    Returns the direct download URL string.
    Raises RuntimeError if resolution fails.
    """
    # 1. Guest token
    token = _create_guest_token(timeout=timeout)

    # 2. Content metadata
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(
        f"{GOFILE_API_BASE}/contents/{content_id}",
        headers=headers,
        timeout=timeout,
    )
    resp.raise_for_status()
    data = resp.json()

    if data.get("status") != "ok":
        raise RuntimeError(f"GoFile contents API error: {data}")

    content = data["data"]

    # 3. Find the download link
    # GoFile content can be a folder (type="folder") with children,
    # or a file (type="file") with a direct "link" field.
    return _extract_download_link(content)


def _extract_download_link(content: dict) -> str:
    """Recursively walk GoFile content dict and return the first download link."""
    ctype = content.get("type", "")

    if ctype == "file":
        link = content.get("link") or content.get("directLink")
        if link:
            return link
        raise RuntimeError("GoFile file node has no link field")

    if ctype == "folder":
        children = content.get("children", {})
        # children can be a dict {id: child_obj} or a list
        if isinstance(children, dict):
            child_iter = children.values()
        else:
            child_iter = children

        for child in child_iter:
            try:
                return _extract_download_link(child)
            except RuntimeError:
                continue

        raise RuntimeError("No downloadable files found in GoFile folder")

    raise RuntimeError(f"Unknown GoFile content type: {ctype!r}")


def resolve_gofile_share_url(share_url: str, timeout: int = 15) -> str:
    """
    Convenience wrapper: accepts a full GoFile share URL like
    https://gofile.io/d/Ke5wvh and returns the direct download URL.
    """
    # Extract content ID from URL
    content_id = share_url.rstrip("/").split("/")[-1]
    return resolve_gofile_url(content_id, timeout=timeout)


if __name__ == "__main__":
    content_id = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CONTENT_ID
    print(f"Resolving GoFile content ID: {content_id}", file=sys.stderr)
    try:
        url = resolve_gofile_url(content_id)
        print(url)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
