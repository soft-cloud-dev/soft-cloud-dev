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
from pathlib import Path

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
    lang_repl = 'lang:(typeof document!="undefined"&&document.documentElement.getAttribute("lang"))||"en"'
    js_code, n = re.subn(r'lang:(?:"en"|`en`)', lang_repl, js_code)
    count += n

    if 'document.querySelector(".myst-search-bar .sr-only")' not in js_code:
        search_pat = re.compile(
            r'\(0,([A-Za-z_$][\w$]*)\.jsx\)\((["`])span\2,'
            r'\{className:\2myst-search-text-placeholder hidden sm:block grow\2,children:\2Search\2\}\)'
        )
        js_code, n = search_pat.subn(
            lambda m: (
                f'(0,{m.group(1)}.jsx)("span",{{className:"sr-only",children:(typeof document!="undefined"&&'
                f'document.querySelector(".myst-search-bar .sr-only")?.textContent)||"Search"}}),'
                + m.group(0)
            ),
            js_code,
        )
        count += n

    if 'id:"softcloud-lang-switcher-root"' not in js_code:
        theme_pat = re.compile(
            r'\(0,([A-Za-z_$][\w$]*)\.jsx\)\(([A-Za-z_$][\w$]*),\{className:(["`])w-8 h-8 ml-3\3\}\)'
        )
        js_code, n = theme_pat.subn(
            lambda m: (
                f'(0,{m.group(1)}.jsx)("div",{{id:"softcloud-lang-switcher-root","data-sc-lang-switcher":"1",'
                f'"data-sc-base-url":(typeof document!="undefined"&&'
                f'document.getElementById("softcloud-lang-switcher-root")?.getAttribute("data-sc-base-url"))||""}}),'
                + m.group(0)
            ),
            js_code,
        )
        count += n

    if 'id:"softcloud-breadcrumbs-root"' not in js_code:
        bc_pat = re.compile(
            r'children:\[(!([A-Za-z_$][\w$]*)&&\(0,([A-Za-z_$][\w$]*)\.jsx\)\(([A-Za-z_$][\w$]*),'
            r'\{kind:([A-Za-z_$][\w$]*)\.kind,frontmatter:\{\.\.\.\5\.frontmatter,downloads:[A-Za-z_$][\w$]*\},'
            r'className:(["`])mb-8 pt-9\6)'
        )
        js_code, n = bc_pat.subn(
            lambda m: (
                f'children:[{m.group(5)}.slug&&{m.group(5)}.slug!=="index"&&'
                f'(0,{m.group(3)}.jsx)("div",{{id:"softcloud-breadcrumbs-root",className:"sc-breadcrumbs-host",'
                f'"data-sc-breadcrumbs":"1","data-sc-page-slug":{m.group(5)}.slug,'
                f'"data-sc-base-url":(typeof document!="undefined"&&'
                f'document.getElementById("softcloud-breadcrumbs-root")?.getAttribute("data-sc-base-url"))||'
                f'(typeof window!="undefined"&&window.__SC_ROOT_BASE_URL__)||""}}),'
                + m.group(1)
            ),
            js_code,
        )
        count += n

    js_code, wa_count = patch_myst_webawesome_hydration(js_code)
    js_code, nav_count = patch_myst_nav_drawer(js_code)
    return js_code, count + wa_count + nav_count


def patch_myst_nav_drawer(js_code: str) -> tuple[str, int]:
    """Patches MyST book-theme navigation drawer for modal dismissal, close button, route reset, and ARIA."""
    count = 0

    # 1. TopNav menu button: add type="button", aria-expanded, aria-controls, and hydration-safe localized label
    if 'aria-controls:"myst-primary-sidebar"' not in js_code:
        menu_btn_pat = re.compile(
            r'\(0,([A-Za-z_$][\w$]*)\.jsxs\)\((["`])button\2,\{'
            r'className:\2myst-top-nav-menu-button([^\2]*)\2,'
            r'onClick:\(\)=>\{([A-Za-z_$][\w$]*)\(!([A-Za-z_$][\w$]*)\)\},'
            r'children:\[(.*?),\(0,\1\.jsx\)\(\2span\2,\{className:\2sr-only\2,children:\2Open Menu\2\}\)\]\}\)'
        )
        js_code, n = menu_btn_pat.subn(
            lambda m: (
                f'(0,{m.group(1)}.jsxs)("button",{{type:"button",className:"myst-top-nav-menu-button{m.group(3)}",'
                f'"aria-expanded":{m.group(5)}?"true":"false","aria-controls":"myst-primary-sidebar",'
                f'onClick:()=>{{{m.group(4)}(!{m.group(5)})}},children:[{m.group(6)},'
                f'(0,{m.group(1)}.jsx)("span",{{className:"sr-only",children:(typeof document!="undefined"&&'
                f'document.querySelector(".myst-top-nav-menu-button .sr-only")?.textContent)||"Open Menu"}})]}})'
            ),
            js_code,
        )
        count += n

    # 2. Navigation overlay (sD): render backdrop even when hide_toc=true clears headings when nav is present
    if 'window.__scNavDrawerDismiss("backdrop")' not in js_code:
        sd_sig = re.search(
            r'nav:([A-Za-z_$][\w$]*),headings:([A-Za-z_$][\w$]*),footer:[^}]+\}\)=>\{let\[([A-Za-z_$][\w$]*),([A-Za-z_$][\w$]*)\]=([A-Za-z_$][\w$]*)\(\)',
            js_code,
        )
        nav_var = sd_sig.group(1) if sd_sig else "o"
        overlay_pat = re.compile(
            r'(\(0,([A-Za-z_$][\w$]*)\.jsxs\)\(\2\.Fragment,\{children:\[)'
            r'([A-Za-z_$][\w$]*)&&!([A-Za-z_$][\w$]*)&&([A-Za-z_$][\w$]*)&&'
            r'\(0,\2\.jsx\)\((["`])div\6,\{className:\6(myst-navigation-overlay[^\6]*)\6,style:\{marginTop:([A-Za-z_$][\w$]*)\},onClick:\(\)=>([A-Za-z_$][\w$]*)\(!1\)\}\)'
        )
        js_code, n = overlay_pat.subn(
            lambda m: (
                f'{m.group(1)}{m.group(3)}&&!{m.group(4)}&&({nav_var}||{m.group(5)})&&'
                f'(0,{m.group(2)}.jsx)("div",{{className:"{m.group(7)}","aria-hidden":"true",'
                f'style:{{marginTop:{m.group(8)}}},onClick:()=>{{typeof window!="undefined"&&window.__scNavDrawerDismiss?'
                f'window.__scNavDrawerDismiss("backdrop"):{m.group(9)}(!1)}}}})'
            ),
            js_code,
        )
        count += n

    # 3. PrimarySidebar (MS): add id, modal dialog ARIA while open, visible close button header, and state bridge
    oa_fn = None
    if 'data-sc-drawer-open' not in js_code:
        ms_pat = re.compile(
            r'(var\s+[A-Za-z_$][\w$]*=\(\{sidebarRef:([A-Za-z_$][\w$]*),nav:([A-Za-z_$][\w$]*),footer:[^,]+,navbarEnd:[^,]+,headings:[^,]+,hide_toc:([A-Za-z_$][\w$]*),mobileOnly:[^}]+\}\)=>\{.*?)'
            r'\[([A-Za-z_$][\w$]*)\]=([A-Za-z_$][\w$]*)\(\)'
            r'(.*?return)'
            r'(\(0,([A-Za-z_$][\w$]*)\.useEffect\)\(\(\)=>\{setTimeout\(\(\)=>\{[^}]+\},500\)\},\[[^\]]+\]\),)'
            r'([A-Za-z_$][\w$]*\?\(0,([A-Za-z_$][\w$]*)\.jsx\)\((["`])div\12,\{ref:\2,)'
            r'(.*?myst-primary-sidebar-pointer.*?children:\[)'
            r'(\(0,\11\.jsxs\)\(\12div\12,\{className:\12myst-primary-sidebar-nav )'
        )
        m_ms = ms_pat.search(js_code)
        if m_ms:
            oa_fn = m_ms.group(6)
            open_v = m_ms.group(5)
            nav_v = m_ms.group(3)
            hidetoc_v = m_ms.group(4)
            react_ns = m_ms.group(9)
            jsx_ns = m_ms.group(11)

            def _repl_ms(m: re.Match[str]) -> str:
                effects = (
                    f'(0,{react_ns}.useEffect)(()=>{{if(typeof window==="undefined")return;'
                    f'window.__scSetNavDrawerOpen=__scSetOpen;'
                    f'return()=>{{if(window.__scSetNavDrawerOpen===__scSetOpen)delete window.__scSetNavDrawerOpen}}}},[__scSetOpen]),'
                    f'(0,{react_ns}.useEffect)(()=>{{if(typeof window==="undefined")return;'
                    f'window.dispatchEvent(new CustomEvent("sc:nav-drawer-state",{{detail:{{open:{open_v}}}}}))}},[{open_v}]),'
                )
                sidebar_attrs = (
                    f'id:"myst-primary-sidebar","data-sc-drawer-open":{open_v}?"true":"false",'
                    f'"data-sc-hide-toc":{nav_v}&&{hidetoc_v}?"true":"false",'
                    f'role:{open_v}?"dialog":void 0,"aria-modal":{open_v}?"true":void 0,'
                    f'"aria-label":{open_v}?(typeof window!="undefined"&&window.__scGetNavDrawerLabel?window.__scGetNavDrawerLabel("drawer"):"Navigation menu"):void 0,'
                    f'tabIndex:{open_v}?-1:void 0,'
                )
                header = (
                    f'{open_v}&&(0,{jsx_ns}.jsxs)("div",{{className:"myst-primary-sidebar-header flex items-center justify-between px-4 py-3 border-b border-myst-border shrink-0 xl:hidden",'
                    f'children:[(0,{jsx_ns}.jsx)("span",{{className:"myst-primary-sidebar-title text-sm font-semibold text-myst-text",'
                    f'children:typeof window!="undefined"&&window.__scGetNavDrawerLabel?window.__scGetNavDrawerLabel("title"):"Menu"}}),'
                    f'(0,{jsx_ns}.jsx)("button",{{type:"button",className:"myst-drawer-close-button flex items-center justify-center w-10 h-10 rounded-lg text-myst-text-secondary hover:text-myst-text hover:bg-myst-surface focus-visible:outline outline-myst-focus-outline outline-2",'
                    f'"aria-label":typeof window!="undefined"&&window.__scGetNavDrawerLabel?window.__scGetNavDrawerLabel("close"):"Close menu",'
                    f'title:typeof window!="undefined"&&window.__scGetNavDrawerLabel?window.__scGetNavDrawerLabel("close"):"Close menu",'
                    f'onClick:()=>{{typeof window!="undefined"&&window.__scNavDrawerDismiss?window.__scNavDrawerDismiss("close-button"):__scSetOpen(!1)}},'
                    f'children:(0,{jsx_ns}.jsx)("svg",{{xmlns:"http://www.w3.org/2000/svg",viewBox:"0 0 24 24",fill:"none",stroke:"currentColor",strokeWidth:2,strokeLinecap:"round",strokeLinejoin:"round","aria-hidden":"true",width:"1.25rem",height:"1.25rem",children:(0,{jsx_ns}.jsx)("path",{{d:"M6 6L18 18M18 6L6 18"}})}})}})]}}),'
                )
                return f'{m.group(1)}[{open_v},__scSetOpen]={oa_fn}(){m.group(7)}{m.group(8)}{effects}{m.group(10)}{sidebar_attrs}{m.group(13)}{header}{m.group(14)}'

            js_code, n = ms_pat.subn(_repl_ms, js_code, count=1)
            count += n

    # 4. PrimarySidebar topnav items (qQ): close drawer when clicking any navigation link
    if 'window.__scNavDrawerDismiss("navigation")' not in js_code:
        if not oa_fn:
            m_oa = re.search(r'let\[[A-Za-z_$][\w$]*,[A-Za-z_$][\w$]*\]=([A-Za-z_$][\w$]*)\(\)', js_code)
            oa_fn = m_oa.group(1) if m_oa else "Oa"
        qq_pat = re.compile(
            r'(function\s+[A-Za-z_$][\w$]*\(\{item:([A-Za-z_$][\w$]*)\}\)\{var\s+[^;]+;let\s+([A-Za-z_$][\w$]*)=[A-Za-z_$][\w$]*\(\);)'
            r'(.*?myst-primary-sidebar-item-short.*?)(children:\2\.title\}\);)'
            r'(let\[([A-Za-z_$][\w$]*),([A-Za-z_$][\w$]*)\]=.*?myst-primary-sidebar-item-title.*?)'
            r'(onClick:\(\)=>\8\(!\7\))'
            r'(.*?myst-primary-sidebar-item-link.*?)(children:\w+\.title\})'
        )
        js_code, n = qq_pat.subn(
            lambda m: (
                f'{m.group(1)[:-1]},[,__scCloseNav]={oa_fn}();'
                f'{m.group(4)}onClick:()=>{{typeof window!="undefined"&&window.__scNavDrawerDismiss?window.__scNavDrawerDismiss("navigation"):__scCloseNav(!1)}},{m.group(5)}'
                f'{m.group(6)}onClick:()=>{{{m.group(8)}(!{m.group(7)}),{m.group(2)}.url&&(typeof window!="undefined"&&window.__scNavDrawerDismiss?window.__scNavDrawerDismiss("navigation"):__scCloseNav(!1))}}'
                f'{m.group(10)}onClick:()=>{{typeof window!="undefined"&&window.__scNavDrawerDismiss?window.__scNavDrawerDismiss("navigation"):__scCloseNav(!1)}},{m.group(11)}'
            ),
            js_code,
            count=1,
        )
        count += n

    return js_code, count


def patch_myst_webawesome_hydration(js_code: str) -> tuple[str, int]:
    """Align React's placeholder expectations with the server-rendered Web Awesome hosts."""
    count = 0
    dc_target = 'function Dc(l,t){return l==="textarea"||l==="noscript"||(t&&t.id==="softcloud-lang-switcher-root")'
    dc_target_orig = 'function Dc(l,t){return l==="textarea"||l==="noscript"'
    dc_repl = (
        'function Dc(l,t){return l==="textarea"||l==="noscript"||'
        '(t&&(t.id==="softcloud-lang-switcher-root"||t.id==="softcloud-breadcrumbs-root"||'
        '(typeof t.className=="string"&&t.className.includes("sc-wa-host"))))'
    )
    if dc_target in js_code and 'sc-wa-host' not in js_code:
        js_code = js_code.replace(dc_target, dc_repl)
        count += 1
    elif dc_target_orig in js_code and 't.id==="softcloud-lang-switcher-root"' not in js_code:
        js_code = js_code.replace(dc_target_orig, dc_repl)
        count += 1
    elif 'sc-wa-host' not in js_code:
        ud_pat = re.compile(
            r'function ([A-Za-z_$][\w$]*)\(([A-Za-z_$][\w$]*),([A-Za-z_$][\w$]*)\)'
            r'\{return \2===(["`])textarea\4\|\|\2===\4noscript\4(?!\|\|\()'
        )
        js_code, n = ud_pat.subn(
            lambda m: (
                f'function {m.group(1)}({m.group(2)},{m.group(3)}){{return '
                f'{m.group(2)}==={m.group(4)}textarea{m.group(4)}||{m.group(2)}==={m.group(4)}noscript{m.group(4)}||'
                f'({m.group(3)}&&({m.group(3)}.id==="softcloud-lang-switcher-root"||'
                f'{m.group(3)}.id==="softcloud-breadcrumbs-root"||'
                f'(typeof {m.group(3)}.className=="string"&&{m.group(3)}.className.includes("sc-wa-host"))))'
            ),
            js_code,
        )
        count += n

    lh_target = 'if(l.nodeName.toLowerCase()!==t.toLowerCase()){if(!a&&(l.nodeName!=="INPUT"||l.type!=="hidden"))break}'
    lh_repl = (
        'if(l.nodeName.toLowerCase()!==t.toLowerCase()&&!(n&&typeof n.className=="string"&&'
        'n.className.includes("sc-wa-host")&&l.nodeName.startsWith("WA-"))){'
        'if(!a&&(l.nodeName!=="INPUT"||l.type!=="hidden"))break}'
    )
    if lh_target in js_code and 'l.nodeName.startsWith("WA-")' not in js_code:
        js_code = js_code.replace(lh_target, lh_repl)
        count += 1
    elif '.nodeName.startsWith("WA-")' not in js_code:
        tf_pat = re.compile(
            r'function ([A-Za-z_$][\w$]*)\(([A-Za-z_$][\w$]*),([A-Za-z_$][\w$]*),([A-Za-z_$][\w$]*),([A-Za-z_$][\w$]*)\)'
            r'\{for\(;\2\.nodeType===1;\)\{var ([A-Za-z_$][\w$]*)=\4;'
            r'if\(\2\.nodeName\.toLowerCase\(\)!==\3\.toLowerCase\(\)\)'
            r'\{if\(!\5&&\(\2\.nodeName!==(["`])INPUT\7\|\|\2\.type!==\7hidden\7\)\)break\}'
        )
        js_code, n = tf_pat.subn(
            lambda m: (
                f'function {m.group(1)}({m.group(2)},{m.group(3)},{m.group(4)},{m.group(5)})'
                f'{{for(;{m.group(2)}.nodeType===1;){{var {m.group(6)}={m.group(4)};'
                f'if({m.group(2)}.nodeName.toLowerCase()!=={m.group(3)}.toLowerCase()&&'
                f'!({m.group(4)}&&typeof {m.group(4)}.className=="string"&&'
                f'{m.group(4)}.className.includes("sc-wa-host")&&{m.group(2)}.nodeName.startsWith("WA-"))){{'
                f'if(!{m.group(5)}&&({m.group(2)}.nodeName!=={m.group(7)}INPUT{m.group(7)}||'
                f'{m.group(2)}.type!=={m.group(7)}hidden{m.group(7)}))break}}'
            ),
            js_code,
        )
        count += n

    return js_code, count


def process_webawesome_hydration(html_dir: str) -> bool:
    """Apply the production component hydration rules without localized layout changes."""
    root = Path(html_dir)
    if not root.is_dir():
        print(f"Missing built fixture directory: {html_dir}", file=sys.stderr)
        return False
    patched = 0
    for bundle in sorted(root.rglob("*.js")):
        original = bundle.read_text(encoding="utf-8")
        updated, count = patch_myst_webawesome_hydration(original)
        if count:
            bundle.write_text(updated, encoding="utf-8")
            patched += 1
    print(f"[OK] Applied production Web Awesome hydration rules to {patched} fixture bundle(s)")
    return True


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

    # 1b. Storage helper & theme hook in Vite / React Router v7 book-theme (Hi/Ui)
    js_code, n = re.subn(
        r'function ([A-Za-z_$][\w$]*)\(([A-Za-z_$][\w$]*)\)\{if\(typeof window==(["`])object\3\)return \2\?window\.localStorage:window\.sessionStorage\}',
        r'function \1(\2){try{if(typeof window=="object")return \2?window.localStorage:window.sessionStorage}catch{}}',
        js_code,
    )
    count += n

    js_code, n = re.subn(
        r'(let ([A-Za-z_$][\w$]*)=[A-Za-z_$][\w$]*\([A-Za-z_$][\w$]*\),([A-Za-z_$][\w$]*)=)([A-Za-z_$][\w$]*)\.getItem\(([A-Za-z_$][\w$]*)\)',
        r'\1(()=>{try{return \4.getItem(\5)}catch{return null}})()',
        js_code,
    )
    count += n

    js_code, n = re.subn(
        r'([A-Za-z_$][\w$]*\(([A-Za-z_$][\w$]*)\)&&)([A-Za-z_$][\w$]*)\.setItem\(([A-Za-z_$][\w$]*),\2\)',
        r'\1(()=>{try{\3.setItem(\4,\2)}catch{}})()',
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

    js_code, n = re.subn(
        r"([A-Za-z_$][\w$]*)=`sessionStorage\.getItem\(\$\{JSON\.stringify\(([A-Za-z_$][\w$]*)\)\}\)`",
        r"\1=`(()=>{try{return sessionStorage.getItem(${JSON.stringify(\2)})}catch{return null}})()`",
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
        r'(?<!try\{)localStorage\.setItem\(`myst-dismissed-banner-\$\{([A-Za-z_$][\w$]*)\}`,(["`])true\2\)',
        r'(()=>{try{localStorage.setItem(`myst-dismissed-banner-${\1}`,"true")}catch{}})()',
        js_code,
    )
    count += n

    # 5. Remix ScrollRestoration sessionStorage setItem & catch-block removeItem
    js_code, n = re.subn(
        r"(?<!try\{)(?<!\.)sessionStorage\.setItem\(([^(),]+),JSON\.stringify\(([^()]+)\)\)",
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

    for storage_obj in ("localStorage", "sessionStorage"):
        theme_target = f'const savedTheme = {storage_obj}.getItem("myst:theme");'
        theme_repl = (
            f'const savedTheme = (()=>{{try{{return {storage_obj}.getItem("myst:theme")}}catch{{return null}}}})();'
        )
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
    success = (
        process_webawesome_hydration(sys.argv[1])
        if "--webawesome-only" in sys.argv[2:]
        else process_thebe(sys.argv[1])
    )
    sys.exit(0 if success else 1)
