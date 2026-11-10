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


def patch_myst_hydration_and_lang(js_code: str) -> tuple[str, int]:
    """Aligns compiled MyST React bundles with localized <html lang>, search .sr-only, and switcher host."""
    count = 0
    lang_target = 'lang:"en"'
    lang_repl = 'lang:(typeof document!="undefined"&&document.documentElement.getAttribute("lang"))||"en"'
    if lang_target in js_code:
        js_code = js_code.replace(lang_target, lang_repl)
        count += 1

    search_target = '(0,$e.jsx)("span",{className:"myst-search-text-placeholder hidden sm:block grow",children:"Search"})'
    search_repl = (
        '(0,$e.jsx)("span",{className:"sr-only",children:(typeof document!="undefined"&&'
        'document.querySelector(".myst-search-bar .sr-only")?.textContent)||"Search"}),'
        + search_target
    )
    if search_target in js_code and 'document.querySelector(".myst-search-bar .sr-only")' not in js_code:
        js_code = js_code.replace(search_target, search_repl)
        count += 1

    theme_target = '(0,ft.jsx)(c4,{className:"w-8 h-8 ml-3"})'
    theme_repl = (
        '(0,ft.jsx)("div",{id:"softcloud-lang-switcher-root","data-sc-lang-switcher":"1",'
        '"data-sc-base-url":(typeof document!="undefined"&&'
        'document.getElementById("softcloud-lang-switcher-root")?.getAttribute("data-sc-base-url"))||""}),'
        + theme_target
    )
    if theme_target in js_code and 'id:"softcloud-lang-switcher-root"' not in js_code:
        js_code = js_code.replace(theme_target, theme_repl)
        count += 1

    dc_target = 'function Dc(l,t){return l==="textarea"||l==="noscript"||(t&&t.id==="softcloud-lang-switcher-root")'
    dc_target_orig = 'function Dc(l,t){return l==="textarea"||l==="noscript"'
    dc_repl = (
        'function Dc(l,t){return l==="textarea"||l==="noscript"||'
        '(t&&(t.id==="softcloud-lang-switcher-root"||(typeof t.className=="string"&&t.className.includes("sc-wa-host"))))'
    )
    if dc_target in js_code and 'sc-wa-host' not in js_code:
        js_code = js_code.replace(dc_target, dc_repl)
        count += 1
    elif dc_target_orig in js_code and 't.id==="softcloud-lang-switcher-root"' not in js_code:
        js_code = js_code.replace(dc_target_orig, dc_repl)
        count += 1

    lh_target = 'if(l.nodeName.toLowerCase()!==t.toLowerCase()){if(!a&&(l.nodeName!=="INPUT"||l.type!=="hidden"))break}'
    lh_repl = (
        'if(l.nodeName.toLowerCase()!==t.toLowerCase()&&!(n&&typeof n.className=="string"&&'
        'n.className.includes("sc-wa-host")&&l.nodeName.startsWith("WA-"))){'
        'if(!a&&(l.nodeName!=="INPUT"||l.type!=="hidden"))break}'
    )
    if lh_target in js_code and 'l.nodeName.startsWith("WA-")' not in js_code:
        js_code = js_code.replace(lh_target, lh_repl)
        count += 1

    return js_code, count


def patch_myst_storage_resilience(js_code: str) -> tuple[str, int]:
    """Guards MyST/Remix browser storage accesses against SecurityError when storage is blocked."""
    count = 0

    # 1. Theme hook useState read in MyST layout (prevents render crash caught by Root ErrorBoundary)
    js_code, n = re.subn(
        r"let ([A-Za-z_$][\w$]*)=([A-Za-z_$][\w$]*)\(\),([A-Za-z_$][\w$]*)=localStorage\.getItem\(([A-Za-z_$][\w$]*)\);",
        r"let \1=\2(),\3=null;try{\3=localStorage.getItem(\4)}catch{}",
        js_code,
    )
    count += n

    # 2. Theme hook useEffect write in MyST layout
    js_code, n = re.subn(
        r"([A-Za-z_$][\w$]*)\(([A-Za-z_$][\w$]*)\)&&\(([A-Za-z_$][\w$]*)\?localStorage\.setItem\(([A-Za-z_$][\w$]*),\2\):([A-Za-z_$][\w$]*)\(\2\)\)",
        r"\1(\2)&&(\3?(()=>{try{localStorage.setItem(\4,\2)}catch{}})():\5(\2))",
        js_code,
    )
    count += n

    # 3. Pre-paint theme <script> generator (must stay aligned with inline HTML script for hydration)
    js_code, n = re.subn(
        r"let ([A-Za-z_$][\w$]*)=`localStorage\.getItem\(\$\{JSON\.stringify\(([A-Za-z_$][\w$]*)\)\}\)`,",
        r"let \1=`(()=>{try{return localStorage.getItem(${JSON.stringify(\2)})}catch{return null}})()`,",
        js_code,
    )
    count += n

    # 4. Announcement banner localStorage read/write
    js_code, n = re.subn(
        r"(?<!return )localStorage\.getItem\(`myst-dismissed-banner-\$\{([A-Za-z_$][\w$]*)\}`\)",
        r"(()=>{try{return localStorage.getItem(`myst-dismissed-banner-${\1}`)}catch{return null}})()",
        js_code,
    )
    count += n

    js_code, n = re.subn(
        r'(?<!try\{)localStorage\.setItem\(`myst-dismissed-banner-\$\{([A-Za-z_$][\w$]*)\}`,"true"\)',
        r'(()=>{try{localStorage.setItem(`myst-dismissed-banner-${\1}`,"true")}catch{}})()',
        js_code,
    )
    count += n

    # 5. Remix ScrollRestoration sessionStorage setItem & catch-block removeItem
    js_code, n = re.subn(
        r"(?<!try\{)sessionStorage\.setItem\(([^(),]+),JSON\.stringify\(([^()]+)\)\)",
        r"(()=>{try{sessionStorage.setItem(\1,JSON.stringify(\2))}catch{}})()",
        js_code,
    )
    count += n

    js_code, n = re.subn(
        r"catch\(([A-Za-z_$][\w$]*)\)\{console\.error\(\1\),sessionStorage\.removeItem\(([A-Za-z_$][\w$]*)\)\}",
        r"catch(\1){try{sessionStorage.removeItem(\2)}catch{}}",
        js_code,
    )
    count += n

    return js_code, count


def patch_html_storage_resilience(html_code: str) -> tuple[str, int]:
    """Guards inline MyST/Remix <script> storage calls in static HTML against SecurityError."""
    count = 0

    theme_target = 'const savedTheme = localStorage.getItem("myst:theme");'
    theme_repl = 'const savedTheme = (()=>{try{return localStorage.getItem("myst:theme")}catch{return null}})();'
    if theme_target in html_code:
        html_code = html_code.replace(theme_target, theme_repl)
        count += 1

    html_code, n = re.subn(
        r"catch\(([A-Za-z_$][\w$]*)\)\{console\.error\(\1\),sessionStorage\.removeItem\(([A-Za-z_$][\w$]*)\)\}",
        r"catch(\1){try{sessionStorage.removeItem(\2)}catch{}}",
        html_code,
    )
    count += n

    return html_code, count


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
                    mod_content, hyd_count = patch_myst_hydration_and_lang(mod_content)
                    mod_content, str_count = patch_myst_storage_resilience(mod_content)

                    if dbg_count > 0 or map_count > 0 or hyd_count > 0 or str_count > 0:
                        with open(fpath, "w", encoding="utf-8") as f:
                            f.write(mod_content)
                        js_patched += 1
                        rel = os.path.relpath(fpath, html_dir)
                        print(
                            f"[OK] Patched {rel} (stripped {dbg_count} debug call(s), "
                            f"{map_count} sourcemap directive(s), {hyd_count} hydration patch(es), "
                            f"{str_count} storage guard(s))"
                        )

                except Exception as e:
                    print(f"[WARN] Error processing JS {fpath}: {e}", file=sys.stderr)

            # Process CSS bundles to fix unresolved /myst_assets_folder/_assets/ references
            elif fname.endswith(".css"):
                try:
                    with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                    if "/myst_assets_folder/_assets/" in content:
                        content = content.replace("/myst_assets_folder/_assets/", "/build/_assets/")
                        with open(fpath, "w", encoding="utf-8") as f:
                            f.write(content)
                except Exception as e:
                    print(f"[WARN] Error processing CSS {fpath}: {e}", file=sys.stderr)

            # Process HTML pages to inject early console.debug filter
            elif fname.endswith(".html"):
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        content = f.read()

                    orig_content = content
                    if "__thebe_debug_filtered" not in content and "<head" in content:
                        content = re.sub(r"(<head[^>]*>)", r"\1" + INLINE_HEAD_FILTER, content, count=1)

                    content = re.sub(
                        r'(id="softcloud-lang-switcher-root"[^>]*></div>)\s+(<button)',
                        r"\1\2",
                        content,
                    )
                    content, _ = patch_html_storage_resilience(content)

                    if content != orig_content:
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
