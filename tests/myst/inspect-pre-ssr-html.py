#!/usr/bin/env python3
"""tests/myst/inspect-pre-ssr-html.py
Inspects generated HTML before SSR transformation to ensure placeholders
match the contract defined in Phase 3.
"""

import html
import json
import re
import sys
from pathlib import Path
from bs4 import BeautifulSoup


def inspect_html_dir(html_dir: Path) -> int:
    if not html_dir.is_dir():
        print(f"[FAIL] Directory does not exist: {html_dir}", file=sys.stderr)
        return 1

    html_files = list(html_dir.glob("**/*.html"))
    if not html_files:
        print(f"[FAIL] No HTML files found in: {html_dir}", file=sys.stderr)
        return 1

    total_hosts = 0
    components_found = set()

    for file_path in html_files:
        soup = BeautifulSoup(file_path.read_text(encoding="utf-8"), "html.parser")
        hosts = soup.find_all(class_=lambda c: c and "sc-wa-host" in c.split())

        for host in hosts:
            total_hosts += 1
            classes = host.get("class", [])

            # Must contain one component marker class
            comp_class = None
            for c in classes:
                if c in ("sc-wa-card", "sc-wa-callout", "sc-wa-button", "sc-wa-icon"):
                    comp_class = c
                    break

            if not comp_class:
                print(f"[FAIL] Host element missing component marker class: {host}", file=sys.stderr)
                return 1

            components_found.add(comp_class)

            # Must have exactly one direct sc-wa-meta child
            meta_elements = [
                child for child in host.find_all(recursive=False)
                if "sc-wa-meta" in child.get("class", [])
            ]
            if not meta_elements:
                # In some renderers it might be deeply nested or direct; check direct first
                meta_elements = host.find_all(class_=lambda c: c and "sc-wa-meta" in c.split())

            if len(meta_elements) != 1:
                print(f"[FAIL] Expected exactly 1 sc-wa-meta in {comp_class}, found {len(meta_elements)}", file=sys.stderr)
                return 1

            meta_span = meta_elements[0]
            raw_text = meta_span.get_text()
            try:
                meta = json.loads(raw_text)
            except Exception as e:
                print(f"[FAIL] Malformed JSON in metadata: '{raw_text}': {e}", file=sys.stderr)
                return 1

            if meta.get("schema_version") != "1.0.0":
                print(f"[FAIL] Invalid schema_version: {meta.get('schema_version')}", file=sys.stderr)
                return 1

    print(f"[OK] Pre-SSR inspection passed: {total_hosts} hosts verified across {len(html_files)} page(s). Found components: {sorted(components_found)}")
    return 0


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("tests/fixtures/webawesome-book/_build/html")
    sys.exit(inspect_html_dir(target))
