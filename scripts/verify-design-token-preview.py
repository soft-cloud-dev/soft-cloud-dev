#!/usr/bin/env python3
"""Validate rendered Design Tokens preview without relying on JavaScript execution."""

from __future__ import annotations

import sys
from pathlib import Path
from bs4 import BeautifulSoup


def validate(output: Path) -> None:
    if not output.is_dir():
        raise ValueError(f"Publication directory missing: {output}")

    stylesheet = output / "static" / "softcloud.css"
    if not stylesheet.is_file():
        raise ValueError("SoftCloud stylesheet was not staged")
    css = stylesheet.read_text(encoding="utf-8")
    if ".sc-token-preview-grid" not in css:
        raise ValueError("Design Tokens styling missing from staged CSS")

    candidates: list[Path] = []
    for path in output.rglob("*.html"):
        if "/pl/" in path.as_posix() or "/de/" in path.as_posix() or "/fr/" in path.as_posix() or "/es/" in path.as_posix():
            continue
        text = path.read_text(encoding="utf-8")
        if "Design Tokens &amp; Style Preview" in text or "Design Tokens & Style Preview" in text:
            if "sc-token-preview-grid" in text:
                candidates.append(path)

    if len(candidates) != 1:
        raise ValueError(f"Expected one English Design Tokens route, found {len(candidates)}: {candidates}")

    target = candidates[0]
    soup = BeautifulSoup(target.read_text(encoding="utf-8"), "html.parser")
    errors = []

    def check(condition: bool, label: str) -> None:
        if not condition:
            errors.append(label)

    panel = soup.select_one(".sc-token-preview-grid")
    check(panel is not None, "static preview grid missing")
    if panel is not None:
        check(len(panel.select(".sc-token-panel.wa-light")) == 1, "light preview absent")
        check(len(panel.select(".sc-token-panel.wa-dark")) == 1, "dark preview absent")

    for variant in ("brand", "neutral", "success", "warning", "danger"):
        check(len(soup.select(f".sc-token-color.sc-token-{variant}")) == 1, f"semantic color {variant} missing")

    check(len(soup.select(".sc-token-ramp-item")) == 5, "brand tint ramp missing")
    check(len(soup.select(".sc-token-types > div")) == 6, "typography samples missing")
    check(len(soup.select(".sc-token-spaces .sc-token-space")) == 7, "spacing scale missing")
    check(len(soup.select(".sc-token-radius")) == 4, "radius samples missing")
    check(len(soup.select(".sc-token-shadow")) == 3, "shadow samples missing")

    for tag, count in (("wa-card", 1), ("wa-callout", 1), ("wa-button", 2)):
        elements = soup.select(tag)
        check(len(elements) >= count, f"{tag} missing from published page")
        for el in elements:
            check(el.has_attr("did-ssr"), f"{tag} missing Lit SSR marker")
            check(bool(el.select_one('template[shadowrootmode="open"]')), f"{tag} missing open DSD template")

    check("document.createElement" not in target.read_text(encoding="utf-8"), "unwanted inline preview runtime")
    check(bool(soup.select('link[href*="softcloud.css"]')), "token styles not referenced from the page")

    if errors:
        raise ValueError(f"{target}: " + "; ".join(errors))
    print(f"[OK] Token preview verification passed: {target.relative_to(output)}")


if __name__ == "__main__":
    path = Path(sys.argv[1] if len(sys.argv) > 1 else "_build/html").resolve()
    try:
        validate(path)
    except ValueError as exc:
        print(f"[FAIL] {exc}", file=sys.stderr)
        raise SystemExit(1)
