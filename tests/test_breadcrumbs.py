#!/usr/bin/env python3
"""Unit and mock-build tests for SoftCloud TOC-driven breadcrumb navigation."""

from __future__ import annotations

import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOLS_DIR = ROOT / "tools"
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

import build_locales as bl  # noqa: E402
import fix_seo_artifacts as fsa  # noqa: E402
import verify_locales as vl  # noqa: E402


class TestBreadcrumbNavigation(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.locales_cfg = bl.load_locales_config(ROOT)
        cls.base_myst = bl.load_yaml_file(ROOT / "myst.yml")

    def setUp(self) -> None:
        self.tmp_dir = Path(tempfile.mkdtemp(prefix="test_breadcrumbs_"))
        self.addCleanup(lambda: shutil.rmtree(self.tmp_dir, ignore_errors=True))

    def test_route_manifest_breadcrumbs_cover_all_locales_and_hierarchy(self) -> None:
        manifest = bl.build_route_manifest(ROOT, self.locales_cfg, self.base_myst)
        bc = manifest.get("breadcrumbs")
        self.assertIsInstance(bc, dict)
        self.assertEqual(set(bc.keys()), {"en", "pl", "de", "es", "fr"})

        # English homepage has no breadcrumb trail; subpages preserve myst.yml hierarchy
        en_trails = bc["en"]["trails"]
        self.assertNotIn("", en_trails)
        self.assertNotIn("index", en_trails)

        guides = bl._resolve_trail_from_manifest(manifest, "en", "guides")
        self.assertIsNotNone(guides)
        aria_label, key, items = guides
        self.assertEqual(aria_label, "Breadcrumbs")
        self.assertEqual(key, "en:guides")
        self.assertEqual(
            [(i["label"], i["href"], i["current"]) for i in items],
            [
                ("SoftCloud Hub", "/", False),
                ("Platform Engineering", None, False),
                ("Guides", "/guides", True),
            ],
        )

        # Component deep page links Web Awesome Components -> /components and keeps Navigation as non-link label
        crumb = bl._resolve_trail_from_manifest(manifest, "en", "components/navigation/breadcrumb")
        self.assertIsNotNone(crumb)
        self.assertEqual(
            [(i["label"], i["href"], i["current"]) for i in crumb[2]],
            [
                ("SoftCloud Hub", "/", False),
                ("Platform Engineering", None, False),
                ("Web Awesome Components", "/components", False),
                ("Navigation", None, False),
                ("Breadcrumb <wa-breadcrumb>", "/components/navigation/breadcrumb", True),
            ],
        )

        # Folder landing pages collapse without duplicating adjacent labels
        comp_index = bl._resolve_trail_from_manifest(manifest, "en", "components")
        self.assertIsNotNone(comp_index)
        self.assertEqual(
            [(i["label"], i["href"], i["current"]) for i in comp_index[2]],
            [
                ("SoftCloud Hub", "/", False),
                ("Platform Engineering", None, False),
                ("Web Awesome — Component Catalog", "/components", True),
            ],
        )

        # Alias resolution for index-1 -> components
        comp_alias = bl._resolve_trail_from_manifest(manifest, "en", "index-1")
        self.assertEqual(comp_alias, comp_index)

        # Portable alternatives folder links for children and collapses for itself
        portable_self = bl._resolve_trail_from_manifest(manifest, "en", "components/portable-alternatives")
        self.assertEqual(
            [(i["label"], i["href"], i["current"]) for i in portable_self[2]],
            [
                ("SoftCloud Hub", "/", False),
                ("Platform Engineering", None, False),
                ("Web Awesome Components", "/components", False),
                ("Portable Alternatives (Non-Core)", "/components/portable-alternatives", True),
            ],
        )
        bar_chart = bl._resolve_trail_from_manifest(manifest, "en", "components/data-viz/bar-chart")
        self.assertEqual(
            [(i["label"], i["href"], i["current"]) for i in bar_chart[2]],
            [
                ("SoftCloud Hub", "/", False),
                ("Platform Engineering", None, False),
                ("Web Awesome Components", "/components", False),
                ("Portable Alternatives (Non-Core)", "/components/portable-alternatives", False),
                ("Bar Chart: portable MyST alternative", "/components/data-viz/bar-chart", True),
            ],
        )

        # Localized trails use localized home route, folder titles, and aria-label
        pl_linux = bl._resolve_trail_from_manifest(manifest, "pl", "projects/linux")
        self.assertIsNotNone(pl_linux)
        self.assertEqual(pl_linux[0], "Nawigacja okruszkowa")
        self.assertEqual(
            [(i["label"], i["href"], i["current"]) for i in pl_linux[2]],
            [
                ("SoftCloud Hub", "/pl/", False),
                ("Systemy i laboratoria", "/pl/projects", False),
                ("Węzeł Linux", "/pl/projects/linux", True),
            ],
        )

        pl_projects = bl._resolve_trail_from_manifest(manifest, "pl", "projects")
        self.assertEqual(
            [(i["label"], i["href"], i["current"]) for i in pl_projects[2]],
            [
                ("SoftCloud Hub", "/pl/", False),
                ("Projekty", "/pl/projects", True),
            ],
        )

    def test_render_breadcrumbs_html_escapes_and_sanitizes(self) -> None:
        rendered = bl.render_breadcrumbs_html(
            [
                {"label": "Home", "href": "/", "current": False},
                {"label": "Bad Link", "href": "javascript:alert(1)", "current": False},
                {"label": "Protocol Rel", "href": "//evil.example/x", "current": False},
                {"label": "Breadcrumb <wa-breadcrumb>", "href": "/breadcrumb", "current": True},
            ],
            aria_label='Trail "Breadcrumbs"',
            rendered_key="en:breadcrumb",
        )
        self.assertIn('aria-label="Trail &quot;Breadcrumbs&quot;"', rendered)
        self.assertIn('class="sc-breadcrumbs not-prose"', rendered)
        self.assertIn('<ol class="sc-breadcrumbs__list">', rendered)
        self.assertIn('Breadcrumb &lt;wa-breadcrumb&gt;', rendered)
        self.assertNotIn("javascript:", rendered)
        self.assertNotIn("//evil.example", rendered)
        self.assertIn('aria-current="page"', rendered)

    def test_mock_multilingual_build_injects_and_verifies_breadcrumbs(self) -> None:
        out_dir = self.tmp_dir / "html"
        staging_dir = self.tmp_dir / "locales"
        rc = bl.main(
            [
                "--mock-html",
                "--output-dir",
                str(out_dir),
                "--staging-dir",
                str(staging_dir),
            ]
        )
        self.assertEqual(rc, 0)

        # Homepage omits breadcrumbs container, subpages render semantic breadcrumbs
        en_home = (out_dir / "index.html").read_text(encoding="utf-8")
        self.assertNotIn('id="softcloud-breadcrumbs-root"', en_home)
        self.assertIn("breadcrumbs.mjs", en_home)

        en_guides = (out_dir / "guides" / "index.html").read_text(encoding="utf-8")
        self.assertIn('id="softcloud-breadcrumbs-root"', en_guides)
        self.assertIn('aria-label="Breadcrumbs"', en_guides)
        self.assertIn('href="/"', en_guides)
        self.assertIn("Platform Engineering", en_guides)
        self.assertIn('aria-current="page">Guides</a>', en_guides)

        fr_linux = (out_dir / "fr" / "projects" / "linux" / "index.html").read_text(encoding="utf-8")
        self.assertIn('aria-label="Fil d&#x27;Ariane"', fr_linux)
        self.assertIn('href="/fr/"', fr_linux)
        self.assertIn('href="/fr/projects"', fr_linux)
        self.assertIn('aria-current="page">Nœud Linux</a>', fr_linux)

        # Verify idempotence of inject_breadcrumbs_into_html
        manifest = bl.json.loads((out_dir / "i18n" / "route-manifest.json").read_text(encoding="utf-8"))
        second_count = bl.inject_breadcrumbs_into_html(out_dir, manifest, self.locales_cfg)
        self.assertEqual(second_count, 0)

        # Run SEO post-processing + full verify_locales built artifact verification
        fsa.process_site("https://my.softcloud.dev", str(out_dir))
        errors = vl.verify_built_html_artifact(ROOT, out_dir)
        self.assertEqual(errors, [], f"verify_built_html_artifact failed: {errors}")


if __name__ == "__main__":
    unittest.main()
