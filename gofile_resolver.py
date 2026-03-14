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
import time
import requests

# Default modpack GoFile content ID (from https://gofile.io/d/Ke5wvh)
DEFAULT_CONTENT_ID = "Ke5wvh"

GOFILE_API_BASE = "https://api.gofile.io"
_GOFILE_WT_FALLBACK = "4fd6sg89d7s6"

# Module-level cache — only create a guest token once per process
_cached_guest_token = None
_cached_wt = None
_session = None  # requests.Session with browser headers


def _get_session():
    """Return a shared requests.Session with browser-like headers."""
    global _session
    if _session is None:
        _session = requests.Session()
        _session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Origin": "https://gofile.io",
            "Referer": "https://gofile.io/",
        })
    return _session


def _get_website_token(timeout=10):
    """Fetch the GoFile website token (wt) from their config JS, with caching."""
    global _cached_wt
    if _cached_wt:
        return _cached_wt
    try:
        resp = _get_session().get(
            "https://gofile.io/dist/js/config.js", timeout=timeout
        )
        resp.raise_for_status()
        match = re.search(r'appdata\.wt\s*=\s*["\']([^"\']+)["\']', resp.text)
        if match:
            _cached_wt = match.group(1)
            return _cached_wt
    except Exception:
        pass
    _cached_wt = _GOFILE_WT_FALLBACK
    return _cached_wt


def _create_guest_token(timeout=15):
    """
    Create a GoFile guest account and return its token.
    Retries up to 3 times with exponential backoff on 429 responses.
    """
    sess = _get_session()
    last_exc = None
    for attempt in range(3):
        try:
            resp = sess.post(f"{GOFILE_API_BASE}/accounts", timeout=timeout)
            if resp.status_code == 429:
                time.sleep(2 ** (attempt + 1))
                continue
            resp.raise_for_status()
            data = resp.json()
            if data.get("status") != "ok":
                raise RuntimeError(f"GoFile accounts API returned: {data}")
            # Persist the guest token as a cookie so subsequent calls use it
            token = data["data"]["token"]
            sess.cookies.set("accountToken", token, domain="gofile.io")
            return token
        except (requests.exceptions.ConnectTimeout,
                requests.exceptions.ConnectionError) as e:
            last_exc = e
            wait = 2 ** (attempt + 1)
            time.sleep(wait)
        except requests.exceptions.HTTPError as e:
            if e.response is not None and e.response.status_code == 429:
                time.sleep(2 ** (attempt + 1))
                continue
            raise
    raise RuntimeError(f"GoFile /accounts unreachable after 3 retries: {last_exc}")


def _get_or_create_guest_token(timeout=15):
    """Return cached guest token or create a new one."""
    global _cached_guest_token
    if not _cached_guest_token:
        _cached_guest_token = _create_guest_token(timeout=timeout)
    return _cached_guest_token


def resolve_gofile_url(content_id, timeout=15):
    """
    Resolve a GoFile content ID to a direct download URL.

    1. Fetch wt from config.js (cached).
    2. Create / reuse a guest token (cached per process).
    3. GET /contents/{id} with Authorization + X-Website-Token headers.
    4. Walk children to find the first file link.
    """
    global _cached_guest_token

    wt = _get_website_token(timeout=timeout)
    token = _get_or_create_guest_token(timeout=timeout)
    sess = _get_session()

    last_exc = None
    resp = None
    for attempt in range(3):
        try:
            resp = sess.get(
                f"{GOFILE_API_BASE}/contents/{content_id}",
                headers={
                    "Authorization": f"Bearer {token}",
                    "X-Website-Token": wt,
                },
                params={"wt": wt},
                timeout=timeout,
            )
            if resp.status_code == 401:
                # Token stale — refresh and retry
                _cached_guest_token = None
                token = _get_or_create_guest_token(timeout=timeout)
                continue
            if resp.status_code == 429:
                time.sleep(2 ** (attempt + 1))
                continue
            resp.raise_for_status()
            break
        except (requests.exceptions.ConnectTimeout,
                requests.exceptions.ConnectionError) as e:
            last_exc = e
            time.sleep(2 ** (attempt + 1))
    else:
        raise RuntimeError(
            f"GoFile /contents/{content_id} unreachable after 3 retries: {last_exc}"
        )

    data = resp.json()
    if data.get("status") != "ok":
        raise RuntimeError(f"GoFile contents API error: {data}")

    return _extract_download_link(data["data"])


def _extract_download_link(content):
    """Recursively walk GoFile content dict and return the first download link."""
    ctype = content.get("type", "")

    if ctype == "file":
        link = content.get("link") or content.get("directLink")
        if link:
            return link
        raise RuntimeError("GoFile file node has no link field")

    if ctype == "folder":
        children = content.get("children", {})
        child_iter = children.values() if isinstance(children, dict) else children
        for child in child_iter:
            try:
                return _extract_download_link(child)
            except RuntimeError:
                continue
        raise RuntimeError("No downloadable files found in GoFile folder")

    raise RuntimeError(f"Unknown GoFile content type: {ctype!r}")


def resolve_gofile_share_url(share_url, timeout=15):
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
