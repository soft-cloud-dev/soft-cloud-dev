#!/usr/bin/env python3
"""Unit tests for tools/fix_thebe.py post-build JS/HTML resilience patches."""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOLS_DIR = ROOT / "tools"
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

import fix_thebe as ft


class TestFixThebeStorageResilience(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = Path(tempfile.mkdtemp(prefix="test_fix_thebe_"))
        self.addCleanup(lambda: shutil.rmtree(self.tmp_dir, ignore_errors=True))

    def test_fixture_component_hydration_matches_hosts_without_changing_layout(self) -> None:
        bundle = self.tmp_dir / "runtime.js"
        code = (
            'const layout={lang:"en"};'
            'function Dc(l,t){return l==="textarea"||l==="noscript"||typeof t.children==="string"}'
            'function matches(l,t,n){let a=false;for(let i=0;i<1;i++){'
            'if(l.nodeName.toLowerCase()!==t.toLowerCase()){if(!a&&(l.nodeName!=="INPUT"||l.type!=="hidden"))break}'
            'return true}return false}'
        )
        bundle.write_text(code, encoding="utf-8")
        html = self.tmp_dir / "index.html"
        html.write_text('<html lang="en"><body>Fixture</body></html>', encoding="utf-8")
        css = self.tmp_dir / "style.css"
        css.write_text('body{color:red}', encoding="utf-8")
        command = [sys.executable, str(TOOLS_DIR / "fix_thebe.py"), str(self.tmp_dir), "--webawesome-only"]
        subprocess.run(command, check=True, capture_output=True, text=True)
        patched = bundle.read_text(encoding="utf-8")
        behavior = patched + (
            ';if(layout.lang!=="en")throw Error("layout changed");'
            'if(!Dc("div",{className:"sc-wa-host"}))throw Error("placeholder children mismatch");'
            'if(Dc("div",{}))throw Error("ordinary children accepted");'
            'if(!matches({nodeName:"WA-CARD"},"div",{className:"sc-wa-host"}))throw Error("component host mismatch");'
            'if(matches({nodeName:"WA-CARD"},"div",{}))throw Error("unrelated tag accepted");'
        )
        result = subprocess.run(["node", "-e", behavior], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(html.read_text(encoding="utf-8"), '<html lang="en"><body>Fixture</body></html>')
        self.assertEqual(css.read_text(encoding="utf-8"), 'body{color:red}')
        subprocess.run(command, check=True, capture_output=True, text=True)
        self.assertEqual(bundle.read_text(encoding="utf-8"), patched)

    def test_theme_hook_and_prepaint_script_are_guarded_and_idempotent(self) -> None:
        sample_js = (
            'function gD({ssrTheme:t,useLocalStorage:e}){let[r,n]=ac.default.useState(()=>{'
            'if(hg(t))return t;if(typeof window!="object")return null;'
            'let i=uee(),s=localStorage.getItem(k0);return e&&hg(s)?s:i});'
            'dee({setTheme:n});let o=(0,ac.useRef)(!1);'
            'return(0,ac.useEffect)(()=>{if(!o.current){o.current=!0;return}'
            'hg(r)&&(e?localStorage.setItem(k0,r):hD(r))},[r]),[r,n]}'
            'function WS({useLocalStorage:t}){let e=`localStorage.getItem(${JSON.stringify(k0)})`,'
            'r=`\n  const savedTheme = ${t?e:"null"};\n`;return r}'
        )

        patched, count = ft.patch_myst_storage_resilience(sample_js)
        self.assertEqual(count, 3)
        self.assertIn("try{s=localStorage.getItem(k0)}catch{}", patched)
        self.assertIn("try{localStorage.setItem(k0,r)}catch{}", patched)
        self.assertIn("try{return localStorage.getItem(${JSON.stringify(k0)})}catch{return null}", patched)

        # Second pass must be a no-op
        reparsed, second_count = ft.patch_myst_storage_resilience(patched)
        self.assertEqual(second_count, 0)
        self.assertEqual(reparsed, patched)

    def test_banner_and_scroll_restoration_are_guarded_and_idempotent(self) -> None:
        sample_js = (
            'vj(()=>{let M=g.current,b=localStorage.getItem(`myst-dismissed-banner-${y}`)==="true";'
            'm({visible:!b,height:0})},[y]);'
            'let w=()=>{localStorage.setItem(`myst-dismissed-banner-${y}`,"true"),m({visible:!1})};'
            'Uo(F.useCallback(()=>{if(s.state==="idle"){let u=o.key;_t[u]=window.scrollY}'
            'sessionStorage.setItem(r||sn,JSON.stringify(_t)),window.history.scrollRestoration="auto"},[]));'
            'try{let u=JSON.parse(sessionStorage.getItem(o)||"{}")[l]}'
            'catch(s){console.error(s),sessionStorage.removeItem(o)}'
        )

        patched, count = ft.patch_myst_storage_resilience(sample_js)
        self.assertEqual(count, 4)
        self.assertIn("catch{return null}", patched)
        self.assertIn('catch{}})()', patched)
        self.assertNotIn("console.error(s),sessionStorage.removeItem(o)", patched)
        self.assertIn("catch(s){try{sessionStorage.removeItem(o)}catch{}}", patched)

        reparsed, second_count = ft.patch_myst_storage_resilience(patched)
        self.assertEqual(second_count, 0)
        self.assertEqual(reparsed, patched)

    def test_html_inline_scripts_are_guarded_and_aligned_with_ws_bundle(self) -> None:
        sample_html = (
            "<html><head><script>\n"
            '  const savedTheme = localStorage.getItem("myst:theme");\n'
            "  const theme = window.matchMedia(\"(prefers-color-scheme: light)\").matches ? 'light' : 'dark';\n"
            "</script></head><body>"
            '<script>((a,s)=>{try{let u=JSON.parse(sessionStorage.getItem(a)||"{}")[s]}'
            'catch(l){console.error(l),sessionStorage.removeItem(a)}})("positions",null)</script>'
            "</body></html>"
        )

        patched, count = ft.patch_html_storage_resilience(sample_html)
        self.assertEqual(count, 2)
        self.assertIn(
            'const savedTheme = (()=>{try{return localStorage.getItem("myst:theme")}catch{return null}})();',
            patched,
        )
        self.assertIn("catch(l){try{sessionStorage.removeItem(a)}catch{}}", patched)

        reparsed, second_count = ft.patch_html_storage_resilience(patched)
        self.assertEqual(second_count, 0)
        self.assertEqual(reparsed, patched)

    def test_patched_theme_code_executes_without_throwing_when_storage_blocked(self) -> None:
        js_bundle = (
            'function gD({ssrTheme:t,useLocalStorage:e}){let[r,n]=ac.default.useState(()=>{'
            'if(hg(t))return t;if(typeof window!="object")return null;'
            'let i=uee(),s=localStorage.getItem(k0);return e&&hg(s)?s:i});'
            'dee({setTheme:n});let o=(0,ac.useRef)(!1);'
            'return(0,ac.useEffect)(()=>{if(!o.current){o.current=!0;return}'
            'hg(r)&&(e?localStorage.setItem(k0,r):hD(r))},[r]),[r,n]}'
            'function WS({useLocalStorage:t}){let e=`localStorage.getItem(${JSON.stringify(k0)})`,'
            'r=`const savedTheme = ${t?e:"null"};`;return r}'
        )
        patched_js, _ = ft.patch_myst_storage_resilience(js_bundle)

        node_script = (
            "const window = { matchMedia: () => ({ matches: true }) };\n"
            "Object.defineProperty(globalThis, 'localStorage', { get() { throw new Error('SecurityError'); } });\n"
            "const k0 = 'myst:theme';\n"
            "const hg = (v) => v === 'light' || v === 'dark';\n"
            "const uee = () => 'light';\n"
            "const dee = () => {};\n"
            "const hD = () => {};\n"
            "const effects = [];\n"
            "const ac = { default: { useState: (init) => [init(), () => {}] }, useRef: (v) => ({ current: v }), useEffect: (fn) => effects.push(fn) };\n"
            + patched_js + "\n"
            "const [theme] = gD({ ssrTheme: undefined, useLocalStorage: true });\n"
            "if (theme !== 'light') throw new Error('Expected fallback theme light, got ' + theme);\n"
            "effects[0](); effects[0]();\n"
            "const wsCode = WS({ useLocalStorage: true });\n"
            "const saved = new Function('localStorage', wsCode + '; return savedTheme;')(undefined);\n"
            "if (saved !== null) throw new Error('Expected savedTheme null, got ' + saved);\n"
        )
        res = subprocess.run(["node", "-e", node_script], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, msg=res.stderr or res.stdout)

    def test_process_thebe_end_to_end(self) -> None:
        shared_dir = self.tmp_dir / "build" / "_shared"
        shared_dir.mkdir(parents=True)
        chunk = shared_dir / "chunk-test.js"
        chunk.write_text(
            'let i=uee(),s=localStorage.getItem(k0);',
            encoding="utf-8",
        )
        html_file = self.tmp_dir / "index.html"
        html_file.write_text(
            '<html><head><script>const savedTheme = localStorage.getItem("myst:theme");</script></head><body></body></html>',
            encoding="utf-8",
        )

        self.assertTrue(ft.process_thebe(str(self.tmp_dir)))
        self.assertIn("try{s=localStorage.getItem(k0)}catch{}", chunk.read_text(encoding="utf-8"))
        self.assertIn("try{return localStorage.getItem(\"myst:theme\")}catch{return null}", html_file.read_text(encoding="utf-8"))

    def test_property_access_session_storage_is_not_corrupted(self) -> None:
        sample_js = "try{e.sessionStorage.setItem(wt,JSON.stringify(n))}catch(e){}"
        patched, count = ft.patch_myst_storage_resilience(sample_js)
        self.assertEqual(count, 0)
        self.assertEqual(patched, sample_js)

    def test_vite_react_router_v7_hydration_and_storage_patches_are_idempotent(self) -> None:
        bundle = (
            '(0,Z.jsxs)(`html`,{lang:`en`});'
            '[(0,import_jsx_runtime.jsx)(`span`,{className:`myst-search-text-placeholder hidden sm:block grow`,children:`Search`})];'
            '[(0,import_jsx_runtime.jsx)(ThemeButton,{className:`w-8 h-8 ml-3`})];'
            'function Ud(e,t){return e===`textarea`||e===`noscript`}'
            'function tf(e,t,n,r){for(;e.nodeType===1;){var i=n;if(e.nodeName.toLowerCase()!==t.toLowerCase()){if(!r&&(e.nodeName!==`INPUT`||e.type!==`hidden`))break}}}'
            'function Hi(e){if(typeof window==`object`)return e?window.localStorage:window.sessionStorage}'
            'let r=Bi(e),i=n.getItem(zi);Ae(r)&&n.setItem(zi,r);'
            'n=`sessionStorage.getItem(${JSON.stringify(zi)})`;'
            'localStorage.setItem(`myst-dismissed-banner-${n}`,`true`);'
        )
        patched, hyd_count = ft.patch_myst_hydration_and_lang(bundle)
        self.assertEqual(hyd_count, 5)
        self.assertIn('document.documentElement.getAttribute("lang")', patched)
        self.assertIn('document.querySelector(".myst-search-bar .sr-only")', patched)
        self.assertIn('id:"softcloud-lang-switcher-root"', patched)
        self.assertIn('sc-wa-host', patched)
        self.assertIn('e.nodeName.startsWith("WA-")', patched)

        patched, str_count = ft.patch_myst_storage_resilience(patched)
        self.assertEqual(str_count, 5)
        self.assertIn('try{if(typeof window=="object")return e?window.localStorage:window.sessionStorage}catch{}', patched)
        self.assertIn('(()=>{try{return n.getItem(zi)}catch{return null}})()', patched)
        self.assertIn('(()=>{try{n.setItem(zi,r)}catch{}})()', patched)
        self.assertIn('sessionStorage.getItem(${JSON.stringify(zi)})}catch{return null}', patched)
        self.assertIn('(()=>{try{localStorage.setItem(`myst-dismissed-banner-${n}`,"true")}catch{}})()', patched)

        again, hyd_again = ft.patch_myst_hydration_and_lang(patched)
        again, str_again = ft.patch_myst_storage_resilience(again)
        self.assertEqual(hyd_again, 0)
        self.assertEqual(str_again, 0)
        self.assertEqual(again, patched)

    def test_nav_drawer_patches_are_valid_and_idempotent(self) -> None:
        sample_bundle = (
            'function HQ({hideToc:t,hideSearch:e}){let[n,o]=Oa();'
            'return(0,ft.jsxs)("button",{className:"myst-top-nav-menu-button flex items-center",onClick:()=>{o(!n)},'
            'children:[(0,ft.jsx)(W_,{width:"1.5rem",height:"1.5rem"}),(0,ft.jsx)("span",{className:"sr-only",children:"Open Menu"})]})}'
            'function qQ({item:t}){var o,i,s;let e=zt();if(!((o=t.children)!=null&&o.length))'
            'return(0,fr.jsx)(tc,{nav:!0,to:(i=Ct(t.url,e))!=null?i:"",className:(0,Si.default)("myst-primary-sidebar-item-short","p-2"),children:t.title});'
            'let[r,n]=Js.default.useState(!1);return(0,fr.jsxs)(Vd,{className:"w-full",open:r,onOpenChange:n,children:['
            '(0,fr.jsxs)("div",{className:"myst-primary-sidebar-item",children:[(0,fr.jsx)(tc,{nav:!0,to:(s=Ct(t.url,e))!=null?s:"",className:"myst-primary-sidebar-item-title",onClick:()=>n(!r),children:t.title})]}),'
            '(0,fr.jsx)(Gd,{children:t.children.map(a=>(0,fr.jsx)(tc,{nav:!0,to:Ct(a.url,e)||"",className:"myst-primary-sidebar-item-link",children:a.title},a.url))})]})}'
            'var MS=({sidebarRef:t,nav:e,footer:r,navbarEnd:n,headings:o,hide_toc:i,mobileOnly:s})=>{let a=qi(),[p]=Oa(),g=Pr();'
            'return(0,Js.useEffect)(()=>{setTimeout(()=>{f.current&&(f.current.style.opacity="1")},500)},[f]),'
            'g?(0,fr.jsx)("div",{ref:t,className:(0,Si.default)("myst-primary-sidebar",{"lg:hidden":e&&i}),style:{top:a},children:(0,fr.jsxs)("div",{className:(0,Si.default)("myst-primary-sidebar-pointer"),children:[(0,fr.jsxs)("div",{className:"myst-primary-sidebar-nav flex-grow"})]})}):null};'
            'var sD=({nav:o,headings:i,mobileOnly:n})=>{let[c,u]=Oa(),f=qi();'
            'return(0,ss.jsxs)(ss.Fragment,{children:[c&&!n&&i&&(0,ss.jsx)("div",{className:"myst-navigation-overlay fixed inset-0",style:{marginTop:f},onClick:()=>u(!1)}),(0,ss.jsx)(MS,{})]})};'
        )
        patched, count = ft.patch_myst_nav_drawer(sample_bundle)
        self.assertEqual(count, 4)
        self.assertIn('"aria-controls":"myst-primary-sidebar"', patched)
        self.assertIn('c&&!n&&(o||i)&&', patched)
        self.assertIn('data-sc-drawer-open', patched)
        self.assertIn('myst-drawer-close-button', patched)
        self.assertIn('window.__scNavDrawerDismiss("navigation")', patched)

        patched_path = self.tmp_dir / "patched_nav.js"
        patched_path.write_text(patched, encoding="utf-8")
        node_check = subprocess.run(
            ["node", "--check", str(patched_path)],
            capture_output=True,
            text=True,
        )
        self.assertEqual(node_check.returncode, 0, node_check.stderr)

        reparsed, second_count = ft.patch_myst_nav_drawer(patched)
        self.assertEqual(second_count, 0)
        self.assertEqual(reparsed, patched)

    def test_fix_seo_artifacts_patches_menu_button_and_sidebar_attributes(self) -> None:
        from fix_seo_artifacts import fix_html_accessibility

        sample_html = (
            '<div class="myst-top-nav"><nav class="myst-top-nav-bar">'
            '<button class="myst-top-nav-menu-button w-10 h-10"><svg></svg><span class="sr-only">Open Menu</span></button>'
            '</nav></div>'
            '<div class="myst-primary-sidebar fixed lg:hidden hidden z-10">'
            '<div class="myst-primary-sidebar-pointer"><div class="myst-primary-sidebar-nav"></div></div>'
            '</div>'
        )
        patched_pl = fix_html_accessibility(sample_html, loc_code="pl")
        self.assertIn('type="button"', patched_pl)
        self.assertIn('aria-expanded="false"', patched_pl)
        self.assertIn('aria-controls="myst-primary-sidebar"', patched_pl)
        self.assertIn('<span class="sr-only">Otwórz menu</span>', patched_pl)
        self.assertEqual(patched_pl.count('id="myst-primary-sidebar"'), 1)
        self.assertEqual(patched_pl.count('data-sc-drawer-open="false"'), 1)
        self.assertIn('data-sc-hide-toc="true"', patched_pl)
        self.assertIn('<div class="myst-primary-sidebar-pointer">', patched_pl)

        re_patched = fix_html_accessibility(patched_pl, loc_code="pl")
        self.assertEqual(re_patched, patched_pl)


if __name__ == "__main__":
    unittest.main()
