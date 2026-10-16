"""softcloud_security.py
Security policies and URL/attribute validation with exact JS parity.
"""

from __future__ import annotations

import re
from typing import Tuple
from urllib.parse import urlsplit

CONTROL_CHARS_REGEX = re.compile(r"[\x00-\x1f\x7f]")
HTML_CHARS_REGEX = re.compile(r"[<>\"']")
BACKSLASH_REGEX = re.compile(r"\\")

ALLOWED_SCHEMES_LINK = {"http", "https", "mailto"}
ALLOWED_SCHEMES_MEDIA = {"http", "https"}


def validate_url(url: str, context: str = "link") -> Tuple[bool, str]:
    """Validate a URL according to SoftCloud security policy.
    
    Args:
        url: The URL string to test.
        context: 'link' (default) or 'media'.
        
    Returns:
        (is_valid, reason)
    """
    if not isinstance(url, str) or not url.strip():
        return False, "URL must be a non-empty string"

    trimmed = url.strip()

    # 1. Control characters
    if CONTROL_CHARS_REGEX.search(trimmed):
        return False, "URL contains forbidden control characters"

    # 2. Backslashes
    if BACKSLASH_REGEX.search(trimmed):
        return False, "URL contains forbidden backslashes"

    # 3. HTML characters
    if HTML_CHARS_REGEX.search(trimmed):
        return False, "URL contains forbidden HTML characters"

    # 4. Protocol-relative
    if trimmed.startswith("//"):
        return False, "Protocol-relative URLs are forbidden"

    # 5. Scheme extraction
    scheme_match = re.match(r"^([a-zA-Z][a-zA-Z0-9+.-]*):", trimmed)
    if scheme_match:
        scheme = scheme_match.group(1).lower()

        if context == "media":
            if scheme not in ALLOWED_SCHEMES_MEDIA:
                return False, f"Scheme '{scheme}:' is not permitted for media"
        else:
            if scheme not in ALLOWED_SCHEMES_LINK:
                return False, f"Scheme '{scheme}:' is not permitted for links"

        if scheme == "mailto":
            email_part = trimmed[7:]
            if not email_part or email_part.startswith("?") or email_part.startswith("#"):
                return False, "Malformed mailto URL"
            return True, ""

        # For http / https
        try:
            parsed = urlsplit(trimmed)
            if parsed.scheme.lower() != scheme:
                return False, "Parsed protocol mismatch"
            if not parsed.hostname:
                return False, "Missing hostname in absolute URL"
            if parsed.username or parsed.password:
                return False, "Credentials in URL are forbidden"
            return True, ""
        except Exception:
            return False, "Malformed absolute URL"

    # Relative URLs
    first_slash = trimmed.find("/")
    colon_index = trimmed.find(":")
    if colon_index != -1 and (first_slash == -1 or colon_index < first_slash):
        return False, "Unknown or unsupported URL scheme"

    return True, ""


def sanitize_rel(rel: str | None, target: str | None) -> str:
    """Ensure noopener noreferrer is present for _blank targets."""
    parts = set(rel.split()) if rel else set()
    if target == "_blank":
        parts.add("noopener")
        parts.add("noreferrer")
    return " ".join(sorted(parts))
