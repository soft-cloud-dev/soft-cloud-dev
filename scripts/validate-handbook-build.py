#!/usr/bin/env python3
"""Verify the compiled Executable Handbook, not just its source Markdown.

Runs after MyST builds and after the multilingual site is assembled.
No browser, live server, or network access is required.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from urllib.parse import urlsplit

from bs4 import BeautifulSoup


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    page = root / "index.html"
    if not page.is_file():
        return ["Missing compiled root handbook route (/)"]

    soup = BeautifulSoup(page.read_text(encoding="utf-8"), "html.parser")
    source = soup.select_one(".sc-handbook")
    if source is None:
        return ["Compiled handbook is missing its .sc-handbook container"]

    for selector in (".sc-handbook__hero", ".sc-handbook__intro",
                     ".sc-handbook__verification", ".sc-handbook__routes",
                     ".sc-handbook__projects"):
        if source.select_one(selector) is None:
            errors.append(f"Compiled handbook missing {selector}")

    # MyST headings can contain an anchor element. BeautifulSoup's tag.string
    # becomes None for those headings, even though the visible heading exists.
    headline = next(
        (heading for heading in source.find_all(["h1", "h2"])
         if "Engineering knowledge you can reproduce." in heading.get_text(" ", strip=True)),
        None,
    )
    if headline is None:
        errors.append("Handbook headline is missing")
    if len(source.select(".sc-handbook__route")) != 3:
        errors.append("Expected exactly three handbook starting-point rows")

    links = [(a.get_text(" ", strip=True), a.get("href", "")) for a in source.find_all("a")]
    for text in ("Start with a guide", "Browse notebooks", "Open verification notebook",
                 "Publish your first page", "Reproduce an environment check",
                 "Find a reusable UI pattern", "Explore SoftCloud projects",
                 "FreeIPA"):
        if not any(text.lower() in label.lower() for label, _ in links):
            errors.append(f"Handbook action link missing: {text}")

    for text, href in links:
        parsed = urlsplit(href)
        if href.startswith(("javascript:", "data:")):
            errors.append(f"Unsafe link in handbook: {text}")
        if not href or parsed.scheme or parsed.netloc or href.startswith("#"):
            continue
        local_path = parsed.path
        if not local_path.startswith("/"):
            continue
        route = root / local_path.lstrip("/")
        if route.is_file():
            continue
        if not ((route / "index.html").is_file() or (root / (local_path.lstrip("/") + ".html")).is_file()):
            errors.append(f"Handbook link target has no compiled route: {text} ({href})")

    # The theme may fingerprint the CSS during build. Verify that the compiled
    # assets contain the actual design rules rather than assuming a fixed name.
    css_found = False
    for css_path in root.rglob("*.css"):
        if css_path.stat().st_size > 8_000_000:
            continue
        if ".sc-handbook__hero" in css_path.read_text(encoding="utf-8", errors="replace"):
            css_found = True
            break
    if not css_found:
        errors.append("Compiled site is missing the handbook design CSS")

    for code in ("en", "pl", "de", "es", "fr"):
        sub = root if code == "en" else root / code
        doc = sub / "index.html"
        if not doc.is_file():
            errors.append(f"[{code}] Missing localized homepage: {doc}")
            continue
        localized = BeautifulSoup(doc.read_text(encoding="utf-8"), "html.parser")
        if localized.select_one(".sc-handbook") is None:
            errors.append(f"[{code}] Missing handbook container")
        if len(localized.select(".sc-handbook__route")) != 3:
            errors.append(f"[{code}] Expected three starting points")
        html = localized.find("html")
        if not html or html.get("lang") != code:
            errors.append(f"[{code}] Incorrect document language")
        header = localized.select_one("nav.myst-top-nav-bar")
        if header is None:
            errors.append(f"[{code}] Missing top navbar")
            continue
        prefix = "" if code == "en" else f"/{code}"
        links = {a.get("href", "").rstrip("/") for a in header.find_all("a")}
        for slug in ("guides", "notebooks", "ui-library", "projects"):
            expected = f"{prefix}/{slug}"
            if expected not in links:
                errors.append(f"[{code}] Missing localized navbar destination {expected}")
            if not (sub / slug / "index.html").is_file() and not (sub / f"{slug}.html").is_file():
                errors.append(f"[{code}] Missing localized page for {slug}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify-dir", default="_build/html")
    args = parser.parse_args()
    root = Path(args.verify_dir).resolve()
    errors = validate(root)
    if errors:
        for message in errors:
            print(f"[FAIL] {message}", file=sys.stderr)
        return 1
    print("[OK] Executable Handbook compiled route, CSS, sections, and actions verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
