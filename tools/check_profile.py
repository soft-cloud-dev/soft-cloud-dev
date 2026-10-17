import json
import os
import re
import sys
from importlib.metadata import version
from pathlib import Path

import yaml
from jupyter_client.kernelspec import KernelSpecManager

def require(condition, message):
    if not condition:
        raise SystemExit(message)

root = Path.cwd().resolve()
require(sys.implementation.name == "cpython", "CPython required")
require(sys.version_info[:3] == (3, 12, 14), "Python 3.12.14 required")
require(sys.prefix != sys.base_prefix, "Activate the project virtualenv")
for package, expected in {
    "jupyter-book": "2.1.7", "ipykernel": "7.3.0", "PyYAML": "6.0.3"
}.items():
    require(version(package) == expected, f"Wrong version: {package}")
require(version("jupyter-server"), "Jupyter Server required")
for name in ("JUPYTER_BASE_URL", "JUPYTER_TOKEN", "READTHEDOCS_CANONICAL_URL"):
    require(not os.environ.get(name), f"Unexpected environment override: {name}")
require("BASE_URL" in os.environ, "Set BASE_URL explicitly; empty is valid")
base = os.environ["BASE_URL"]
require(base == "" or (base.startswith("/") and not base.startswith("//")
        and not base.endswith("/") and not any(c in base for c in "?#\n\r")),
        "BASE_URL must be empty or a path prefix such as /docs")

kernel_dir = Path(sys.prefix) / "share/jupyter/kernels/jb2-python"
spec = json.loads((kernel_dir / "kernel.json").read_text())
require(Path(spec["argv"][0]).absolute() == Path(sys.executable).absolute(),
        "Kernel does not launch this environment's Python")
resolved = KernelSpecManager().get_kernel_spec("jb2-python")
require(Path(resolved.resource_dir).resolve() == kernel_dir.resolve(),
        "Another kernelspec overrides the project kernel")

def local_file(value):
    require(isinstance(value, str), "Source path must be a string")
    path = root / value
    require(not Path(value).is_absolute(), f"Absolute source path: {value}")
    require(path.resolve().is_relative_to(root), f"External path: {value}")
    require(path.is_file(), f"Missing source or asset: {value}")
    return path

config = yaml.safe_load(Path("myst.yml").read_text())
require(isinstance(config, dict) and config.get("version") == 1,
        "Expected myst.yml version: 1")
require("extends" not in config, "Configuration inheritance needs a profile extension")
project = config.get("project", {})
allowed_plugins = ["assets/plugins/myst-webawesome.mjs"]
plugins = project.get("plugins") or []
require(isinstance(plugins, list) and all(p in allowed_plugins for p in plugins),
        "Custom plugins need a profile extension")
for p in plugins:
    local_file(p)
require(not project.get("exclude"), "Project exclusions are not accepted")
toc = project.get("toc")
require(isinstance(toc, list) and toc, "Explicit nonempty project.toc required")
site = config.get("site", {})
require(site.get("template") == "book-theme", "Expected book-theme selector")
local_file(site.get("options", {}).get("logo"))
files = []

def walk(entries):
    require(isinstance(entries, list), "TOC children must be a list")
    for entry in entries:
        require(isinstance(entry, dict), "TOC entry must be a mapping")
        require(set(entry) <= {"file", "title", "children"},
                "Unsupported TOC entry; use file/title/children")
        require("file" in entry or entry.get("children"), "Empty TOC entry")
        if "file" in entry:
            files.append(local_file(entry["file"]))
        if "children" in entry:
            walk(entry["children"])

walk(toc)
require(len({p.resolve() for p in files}) == len(files), "Duplicate TOC file")
for path in Path("notebooks").rglob("*.ipynb"):
    if ".ipynb_checkpoints" not in path.parts:
        require(path.resolve() in {p.resolve() for p in files},
                f"Notebook absent from TOC: {path}")

banned = {"skip-execution", "raises-exception"}

def check_controls(value, label):
    if isinstance(value, dict):
        execute = value.get("execute")
        if isinstance(execute, dict):
            require(execute.get("skip") in (None, False), f"Execution skipped: {label}")
        tags = value.get("tags", [])
        if isinstance(tags, (list, str)):
            require(not any(tag in tags for tag in banned), f"Forbidden tag: {label}")
        for child in value.values():
            check_controls(child, label)
    elif isinstance(value, list):
        for child in value:
            check_controls(child, label)

def check_kernel(metadata, label):
    expected = {"name": "jb2-python", "display_name": "Python (JB2)", "language": "python"}
    actual = metadata.get("kernelspec", {})
    require(all(actual.get(k) == v for k, v in expected.items()),
            f"Wrong or absent kernelspec: {label}")

check_controls(config, "myst.yml")
for path in files:
    if path.suffix == ".ipynb":
        notebook = json.loads(path.read_text())
        check_controls(notebook.get("metadata", {}), path)
        cells = notebook.get("cells", [])
        for cell in cells:
            check_controls(cell.get("metadata", {}), path)
        computational = any(c.get("cell_type") == "code" for c in cells)
        computational = computational or any(
            "{eval}" in "".join(c.get("source", []))
            or "{code-cell}" in "".join(c.get("source", []))
            for c in cells if c.get("cell_type") == "markdown")
        if computational:
            check_kernel(notebook.get("metadata", {}), path)
    elif path.suffix == ".md":
        text = path.read_text()
        front = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|\Z)", text, re.S)
        metadata = yaml.safe_load(front.group(1)) or {} if front else {}
        require(isinstance(metadata, dict), f"Invalid frontmatter: {path}")
        check_controls(metadata, path)
        if "{code-cell}" in text or "{eval}" in text:
            check_kernel(metadata, path)
            require(not any(tag in text for tag in banned),
                    f"Review executable Markdown execution controls: {path}")
require(not Path("_config.yml").exists() and not Path("_toc.yml").exists(),
        "Remove legacy configuration from this profile")
local_file("tools/generate_audio.py")
local_file("tools/build_locales.py")
local_file("tools/translate_sources.py")
local_file("tools/verify_locales.py")
local_file("widgets/voice-player.mjs")
local_file("widgets/language-switcher.mjs")
local_file("i18n/locales.yml")
local_file("i18n/glossary.yml")

locales_cfg = yaml.safe_load(Path("i18n/locales.yml").read_text())
require(isinstance(locales_cfg, dict) and bool(locales_cfg.get("schema_version") or locales_cfg.get("version") == 1),
        "Expected i18n/locales.yml schema_version")
default_locale = locales_cfg.get("default_locale", "en")
locales_map = locales_cfg.get("locales", {})
require(isinstance(locales_map, dict) and default_locale in locales_map,
        "Invalid locales mapping in i18n/locales.yml")

for loc_code, loc_info in locales_map.items():
    if not isinstance(loc_info, dict) or not loc_info.get("enabled", True):
        continue
    if loc_code != default_locale:
        src_dir = loc_info.get("source_dir", f"i18n/{loc_code}")
        prov_file = local_file(f"{src_dir}/provenance.json")
        prov_data = json.loads(prov_file.read_text())
        require(prov_data.get("locale") == loc_code, f"Provenance locale mismatch: {prov_file}")
        for en_file in files:
            rel_doc = en_file.relative_to(root).as_posix()
            # Untranslated component catalog files publish progressively. Existing
            # core documentation remains subject to strict locale validation.
            candidate = root / src_dir / rel_doc
            if rel_doc.startswith("components/") and not candidate.is_file():
                continue
            loc_path = local_file(f"{src_dir}/{rel_doc}")
            if loc_path.suffix == ".ipynb":
                notebook = json.loads(loc_path.read_text())
                check_controls(notebook.get("metadata", {}), loc_path)
                for cell in notebook.get("cells", []):
                    check_controls(cell.get("metadata", {}), loc_path)
                check_kernel(notebook.get("metadata", {}), loc_path)
            elif loc_path.suffix == ".md":
                text = loc_path.read_text()
                front = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|\Z)", text, re.S)
                metadata = yaml.safe_load(front.group(1)) or {} if front else {}
                require(isinstance(metadata, dict), f"Invalid frontmatter: {loc_path}")
                check_controls(metadata, loc_path)
                if "{code-cell}" in text or "{eval}" in text:
                    check_kernel(metadata, loc_path)
                    require(not any(tag in text for tag in banned),
                            f"Review executable Markdown execution controls: {loc_path}")

    loc_audio_dir = root / str(loc_info.get("audio_dir", "audio" if loc_code == default_locale else f"audio/{loc_code}"))
    if loc_audio_dir.is_dir():
        for manifest_path in sorted(loc_audio_dir.glob("*/manifest.json")):
            if manifest_path.parent.name in locales_map and loc_code == default_locale:
                continue
            manifest = json.loads(manifest_path.read_text())
            require(manifest.get("status") == "complete", f"Incomplete audio manifest: {manifest_path}")
            require(manifest.get("locale") == loc_code, f"Audio manifest locale mismatch in {manifest_path}")
            local_file(manifest.get("source_path", ""))
            local_file(str((manifest_path.parent / manifest.get("transcript_file", "")).relative_to(root)))
            for chunk in manifest.get("chunks", []):
                require(chunk.get("locale") == loc_code, f"Audio chunk locale mismatch in {manifest_path}")
                local_file(str((manifest_path.parent / chunk.get("audio_file", "")).relative_to(root)))

print(f"Preflight passed for {len(files)} TOC files across {len(locales_map)} locales")
