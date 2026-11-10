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


if __name__ == "__main__":
    unittest.main()
