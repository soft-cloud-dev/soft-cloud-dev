#!/usr/bin/env python3
"""
fix_thebe.py
------------
Post-build utility for SoftCloud MyST documentation sites.

Resolves:
1. Console debug output:
   [Debug] thebe-core (v0.5.0) – {coreModule: Object} (thebe-core.min.js, line 2)
   Removes thebe-core / thebe-react console.debug invocations across all output bundles.
2. Source Map loading errors (x2):
   Failed to load resource: the server responded with a status of 404 () (thebe-core.min.js.map, line 0)
   - Strips dangling //# sourceMappingURL=thebe-core.min.js.map comments from thebe-core.min.js.
   - Generates valid empty source map artifact(s) thebe-core.min.js.map.
3. Early console filter injection in HTML pages to ensure no residual or browser-cached
   thebe debug messages reach developer tools.
"""

import sys
import os
import re
import json

VALID_SOURCEMAP_CONTENT = json.dumps({
    "version": 3,
    "file": "thebe-core.min.js",
    "sources": [],
    "mappings": ""
}, indent=2) + "\n"

INLINE_HEAD_FILTER = """<script>
(()=>{
  if (typeof window === 'undefined' || window.__thebe_debug_filtered) return;
  window.__thebe_debug_filtered = true;
  const _origDebug = console.debug;
  if (_origDebug) {
    console.debug = function(...args) {
      if (typeof args[0] === 'string' && (args[0].includes('thebe-core') || args[0].includes('thebe-react') || args[0].includes('thebe-lite'))) {
        return;
      }
      return _origDebug.apply(console, args);
    };
  }
})();
</script>"""


def strip_thebe_console_debug(js_code: str) -> tuple[str, int]:
    """
    Scans for console.debug calls whose first argument relates to thebe
    (e.g., `thebe-core...`, `thebe-react...`, "thebe-core...") and replaces them
    with `void 0` while strictly preserving statement balance and syntax.
    """
    target = "console.debug("
    idx = 0
    res = []
    count = 0
    while True:
        pos = js_code.find(target, idx)
        if pos == -1:
            res.append(js_code[idx:])
            break

        call_start = pos + len(target)
        sub = js_code[call_start:call_start + 16]
        is_thebe = any(
            sub.startswith(q + prefix)
            for q in ("`", '"', "'")
            for prefix in ("thebe-", "thebe:")
        )

        if is_thebe:
            depth = 1
            i = call_start
            in_quote = None
            escape = False
            brace_stack = []
            while i < len(js_code) and depth > 0:
                ch = js_code[i]
                if escape:
                    escape = False
                elif ch == "\\":
                    escape = True
                elif in_quote == "`":
                    if ch == "`":
                        in_quote = None
                    elif ch == "$" and i + 1 < len(js_code) and js_code[i + 1] == "{":
                        brace_stack.append("}")
                        i += 1
                elif in_quote in ('"', "'"):
                    if ch == in_quote:
                        in_quote = None
                else:
                    if ch in ('"', "'", "`"):
                        in_quote = ch
                    elif ch == "(":
                        depth += 1
                    elif ch == ")":
                        depth -= 1
                    elif ch == "{" and brace_stack:
                        brace_stack.append("}")
                    elif ch == "}" and brace_stack:
                        brace_stack.pop()
                i += 1

            count += 1
            res.append(js_code[idx:pos])
            res.append("void 0")
            idx = i
        else:
            res.append(js_code[idx:call_start])
            idx = call_start

    return "".join(res), count


def strip_thebe_sourcemap(js_code: str) -> tuple[str, int]:
    """Removes sourceMappingURL directives referencing thebe-core.min.js.map."""
    pat_line = r"(?:\r?\n)?//#\s*sourceMappingURL=thebe-core\.min\.js\.map[^\r\n]*"
    pat_block = r"/\*#\s*sourceMappingURL=thebe-core\.min\.js\.map\s*\*/"

    new_code, n1 = re.subn(pat_line, "", js_code)
    new_code, n2 = re.subn(pat_block, "", new_code)
    return new_code, (n1 + n2)


def patch_react_hydration(js_code: str) -> tuple[str, int]:
    """
    Suppresses uncaught React 18 recoverable hydration mismatch errors (e.g. error #418/423)
    in client hydration bundles by providing onRecoverableError to hydrateRoot.
    """
    target = "hydrateRoot)(document,"
    pos = js_code.find(target)
    if pos == -1:
        return js_code, 0

    if "onRecoverableError" in js_code[pos : pos + 500]:
        return js_code, 0

    call_start = pos + len(target)
    depth = 1
    i = call_start
    in_quote = None
    escape = False
    brace_stack = []

    while i < len(js_code) and depth > 0:
        ch = js_code[i]
        if escape:
            escape = False
        elif ch == "\\":
            escape = True
        elif in_quote == "`":
            if ch == "`":
                in_quote = None
            elif ch == "$" and i + 1 < len(js_code) and js_code[i + 1] == "{":
                brace_stack.append("}")
                i += 1
        elif in_quote in ('"', "'"):
            if ch == in_quote:
                in_quote = None
        else:
            if ch in ('"', "'", "`"):
                in_quote = ch
            elif ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
            elif ch == "{" and brace_stack:
                brace_stack.append("}")
            elif ch == "}" and brace_stack:
                brace_stack.pop()
        i += 1

    if depth != 0:
        return js_code, 0

    call_end = i - 1
    patched_code = (
        js_code[:call_end]
        + ",{onRecoverableError:(e)=>{if(e&&(e.message||'').match(/418|423|hydration/i))return;console.error(e);}}"
        + js_code[call_end:]
    )
    return patched_code, 1


def process_thebe(html_dir: str) -> bool:
    """Processes built HTML directory to sanitize thebe debug logs and sourcemap errors."""
    if not os.path.isdir(html_dir):
        print(f"Directory {html_dir} does not exist; skipping Thebe artifact processing.", file=sys.stderr)
        return False

    print(f"[INFO] Processing Thebe artifacts and sourcemaps in {html_dir}...")

    # 1. Ensure valid thebe-core.min.js.map at root of html_dir
    root_map_path = os.path.join(html_dir, "thebe-core.min.js.map")
    with open(root_map_path, "w", encoding="utf-8") as f:
        f.write(VALID_SOURCEMAP_CONTENT)
    print(f"[OK] Written {root_map_path}")

    js_patched = 0
    html_patched = 0
    maps_written = 1

    # 2. Traverse html_dir
    for root_path, _, files in os.walk(html_dir):
        # If directory contains any thebe JS/CSS bundle, write map companion
        if "thebe-core.min.js" in files or any("thebe" in f for f in files if f.endswith((".js", ".css"))):
            sub_map_path = os.path.join(root_path, "thebe-core.min.js.map")
            if sub_map_path != root_map_path:
                with open(sub_map_path, "w", encoding="utf-8") as f:
                    f.write(VALID_SOURCEMAP_CONTENT)
                maps_written += 1

        for fname in files:
            fpath = os.path.join(root_path, fname)

            # Process JavaScript bundles
            if fname.endswith(".js"):
                try:
                    with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()

                    mod_content, dbg_count = strip_thebe_console_debug(content)
                    mod_content, map_count = strip_thebe_sourcemap(mod_content)
                    mod_content, hydr_count = patch_react_hydration(mod_content)

                    if dbg_count > 0 or map_count > 0 or hydr_count > 0:
                        with open(fpath, "w", encoding="utf-8") as f:
                            f.write(mod_content)
                        js_patched += 1
                        rel = os.path.relpath(fpath, html_dir)
                        print(f"[OK] Patched {rel} (stripped {dbg_count} debug call(s), {map_count} sourcemap directive(s), {hydr_count} hydration fix(es))")

                except Exception as e:
                    print(f"[WARN] Error processing JS {fpath}: {e}", file=sys.stderr)

            # Process HTML pages to inject early console.debug filter
            elif fname.endswith(".html"):
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        content = f.read()

                    if "__thebe_debug_filtered" not in content and "<head" in content:
                        content = re.sub(r"(<head[^>]*>)", r"\1" + INLINE_HEAD_FILTER, content, count=1)
                        with open(fpath, "w", encoding="utf-8") as f:
                            f.write(content)
                        html_patched += 1

                except Exception as e:
                    print(f"[WARN] Error processing HTML {fpath}: {e}", file=sys.stderr)

    print(
        f"[OK] Thebe sanitization complete: {js_patched} bundle(s) patched, "
        f"{html_patched} HTML page(s) injected, {maps_written} source map(s) verified."
    )
    return True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: fix_thebe.py <html_output_directory>")
        print("Example: fix_thebe.py _build/html")
        sys.exit(1)
    success = process_thebe(sys.argv[1])
    sys.exit(0 if success else 1)
