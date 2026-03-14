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

import re
import sys
import requests

# Default modpack GoFile content ID (from https://gofile.io/d/Ke5wvh)
DEFAULT_CONTENT_ID = "Ke5wvh"

GOFILE_API_BASE = "https://api.gofile.io"
# GoFile website token — required by the API alongside the bearer token.
# Fetched dynamically from config.js; this value is the known fallback.
_GOFILE_WT_FALLBACK = "4fd6sg89d7s6"


def _get_website_token(timeout: int = 10) -> str:
    """Fetch the GoFile website token (wt) from their config JS."""
    try:
        resp = requests.get("https://gofile.io/dist/js/config.js", timeout=timeout)
        resp.raise_for_status()
        match = re.search(r'appdata\.wt\s*=\s*["\']([^"\']+)["\']', resp.text)
        if match:
            return match.group(1)
    except Exception:
        pass
    return _GOFILE_WT_FALLBACK


def _create_guest_token(timeout: int = 15) -> str:
    """Create a GoFile guest account and return its token."""
    resp = requests.post(f"{GOFILE_API_BASE}/accounts", timeout=timeout)
    resp.raise_for_status()
    data = resp.json()
    if data.get("status") != "ok":
        raise RuntimeError(f"GoFile accounts API error: {data}")
    return data["data"]["token"]


def resolve_gofile_url(content_id: str, timeout: int = 15) -> str:
    """
    Resolve a GoFile content ID to a direct download URL.

    Steps:
      1. Fetch the GoFile website token (wt) from config.js.
      2. Create a guest account token (POST /accounts).
      3. Fetch content metadata (GET /contents/{content_id}).
      4. Walk the children to find the first downloadable file URL.

    Returns the direct download URL string.
    Raises RuntimeError if resolution fails.
    """
    # 1. Website token (required by GoFile API alongside bearer token)
    wt = _get_website_token(timeout=timeout)

    # 2. Guest bearer token
    token = _create_guest_token(timeout=timeout)

    # 3. Content metadata — send both Authorization header and X-Website-Token header
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Website-Token": wt,
    }
    resp = requests.get(
        f"{GOFILE_API_BASE}/contents/{content_id}",
        headers=headers,
        params={"wt": wt},
        timeout=timeout,
    )
    resp.raise_for_status()
    data = resp.json()

    if data.get("status") != "ok":
        raise RuntimeError(f"GoFile contents API error: {data}")

    content = data["data"]

    # 4. Find the download link
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
        child_iter = children.values() if isinstance(children, dict) else children
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
