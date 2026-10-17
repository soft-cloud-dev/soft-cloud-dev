"""assets/python/softcloud_ui.py
Python API for Jupyter Notebooks producing Web Awesome SSR placeholder HTML conforming to schema 2.0.0.
"""

from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any, Optional

from softcloud_security import validate_url, sanitize_rel

SHARED_DIR = Path(__file__).resolve().parent.parent / "shared"
SCHEMA_PATH = SHARED_DIR / "component-schema.json"

try:
    SCHEMA = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
except Exception:
    SCHEMA = {"allowedComponents": ["wa-card", "wa-callout", "wa-button", "wa-icon"]}


class TrustedHTML:
    """Explicit container for trusted HTML content.
    Prevents accidental injection of author-controlled strings into raw HTML.
    """
    def __init__(self, content: str):
        if not isinstance(content, str):
            raise TypeError("TrustedHTML content must be a string")
        self._content = content

    def __html__(self) -> str:
        return self._content

    def __str__(self) -> str:
        return self._content

    def __repr__(self) -> str:
        return f"TrustedHTML({self._content!r})"


class HTMLOutput:
    """Wraps HTML output to render natively in Jupyter Notebooks via _repr_html_."""
    def __init__(self, raw_html: str):
        self._raw_html = raw_html

    def _repr_html_(self) -> str:
        return self._raw_html

    def __str__(self) -> str:
        return self._raw_html

    def __repr__(self) -> str:
        return self._raw_html


class UI:
    """Python notebook helper API matching the MyST Web Awesome placeholder contract."""

    @staticmethod
    def _create_placeholder(
        tag: str,
        comp_class: str,
        meta: dict[str, Any],
        body_html: str = "",
        extra_class: Optional[str] = None,
    ) -> HTMLOutput:
        classes = ["sc-wa-host", comp_class]
        if extra_class:
            classes.append(html.escape(extra_class, quote=True))

        meta_json = json.dumps(meta, ensure_ascii=False)
        # Escape metadata text inside span
        escaped_meta_json = html.escape(meta_json, quote=True)

        meta_span = f'<span class="sc-wa-meta" style="display:none">{escaped_meta_json}</span>'

        if tag == "span":
            output = f'<span class="{" ".join(classes)}">{meta_span}</span>'
        else:
            output = f'<div class="{" ".join(classes)}">{meta_span}{body_html}</div>'

        return HTMLOutput(output)

    @classmethod
    def icon(
        cls,
        name: str,
        family: Optional[str] = None,
        variant: Optional[str] = None,
        style: Optional[str] = None,
        label: Optional[str] = None,
        library: str = "default",
        class_name: Optional[str] = None,
    ) -> HTMLOutput:
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Icon name must be a non-empty string")

        clean_name = name.strip()
        # Canonical 2.0.0 icon normalization
        if clean_name == "info-circle":
            clean_name = "circle-info"

        canonical_family = family or "classic"
        canonical_variant = variant or "solid"

        if style == "brands" or family == "brands":
            canonical_family = "brands"
            canonical_variant = None
        elif style == "regular" or variant == "regular":
            canonical_family = family or "classic"
            canonical_variant = "regular"
        elif style == "solid":
            canonical_family = family or "classic"
            canonical_variant = "solid"

        meta: dict[str, Any] = {
            "schema_version": "2.0.0",
            "component": "wa-icon",
            "name": clean_name,
            "family": canonical_family,
        }
        if canonical_variant:
            meta["variant"] = canonical_variant
        if label:
            meta["label"] = label
        if class_name:
            meta["class"] = class_name

        return cls._create_placeholder("span", "sc-wa-icon", meta, extra_class=class_name)

    @classmethod
    def button(
        cls,
        label: str,
        href: Optional[str] = None,
        variant: str = "neutral",
        appearance: Optional[str] = None,
        size: Optional[str] = None,
        target: Optional[str] = None,
        rel: Optional[str] = None,
        disabled: bool = False,
        with_caret: bool = False,
        caret: bool = False,
        loading: bool = False,
        outline: bool = False,
        pill: bool = False,
        circle: bool = False,
        class_name: Optional[str] = None,
    ) -> HTMLOutput:
        if not isinstance(label, str):
            raise TypeError("Button label must be a string")

        canonical_variant = variant
        if canonical_variant == "primary":
            canonical_variant = "brand"
        elif canonical_variant == "default":
            canonical_variant = "neutral"

        canonical_appearance = appearance
        if canonical_appearance in ("text", "flat"):
            canonical_appearance = "plain"
        if outline:
            canonical_appearance = "outlined"

        final_classes = []
        if class_name:
            final_classes.append(class_name)
        if circle:
            final_classes.append("sc-button-circle")
        combined_class = " ".join(final_classes) if final_classes else None

        meta: dict[str, Any] = {
            "schema_version": "2.0.0",
            "component": "wa-button",
            "variant": canonical_variant,
        }
        if canonical_appearance:
            meta["appearance"] = canonical_appearance
        if size:
            size_map = {"small": "s", "medium": "m", "large": "l"}
            meta["size"] = size_map.get(size.strip().lower(), size.strip().lower())
        if target:
            meta["target"] = target
            rel = sanitize_rel(rel, target)
        if rel:
            meta["rel"] = rel
        if disabled:
            meta["disabled"] = True
        if with_caret or caret:
            meta["with-caret"] = True
        if loading:
            meta["loading"] = True
        if pill:
            meta["pill"] = True
        if combined_class:
            meta["class"] = combined_class

        if href is not None:
            is_valid, reason = validate_url(href, context="link")
            if not is_valid:
                raise ValueError(f"Button href violates URL policy: {reason}")
            meta["href"] = href

        escaped_label = html.escape(label, quote=True)
        return cls._create_placeholder(
            "div",
            "sc-wa-button",
            meta,
            body_html=escaped_label,
            extra_class=combined_class,
        )

    @classmethod
    def card_text(
        cls,
        text: str,
        header: Optional[str] = None,
        footer: Optional[str] = None,
        image: Optional[str] = None,
        image_alt: Optional[str] = None,
        appearance: str = "outlined",
        class_name: Optional[str] = None,
    ) -> HTMLOutput:
        if not isinstance(text, str):
            raise TypeError("Card text must be a string")
        escaped_body = f"<p>{html.escape(text, quote=True)}</p>"
        return cls._build_card(escaped_body, header, footer, image, image_alt, appearance, class_name)

    @classmethod
    def card_trusted_html(
        cls,
        html_obj: TrustedHTML,
        header: Optional[str] = None,
        footer: Optional[str] = None,
        image: Optional[str] = None,
        image_alt: Optional[str] = None,
        appearance: str = "outlined",
        class_name: Optional[str] = None,
    ) -> HTMLOutput:
        if not isinstance(html_obj, TrustedHTML):
            raise TypeError("Must pass TrustedHTML to card_trusted_html; use card_text for plain text")
        return cls._build_card(str(html_obj), header, footer, image, image_alt, appearance, class_name)

    @classmethod
    def _build_card(
        cls,
        body_html: str,
        header: Optional[str] = None,
        footer: Optional[str] = None,
        image: Optional[str] = None,
        image_alt: Optional[str] = None,
        appearance: str = "outlined",
        class_name: Optional[str] = None,
    ) -> HTMLOutput:
        canonical_appearance = appearance
        final_classes = []
        if class_name:
            final_classes.append(class_name)

        if canonical_appearance == "elevated":
            canonical_appearance = "filled-outlined"
            final_classes.append("sc-elevation")
        elif canonical_appearance == "flat":
            canonical_appearance = "plain"
        elif canonical_appearance == "default":
            canonical_appearance = "outlined"

        combined_class = " ".join(final_classes) if final_classes else None

        meta: dict[str, Any] = {
            "schema_version": "2.0.0",
            "component": "wa-card",
            "appearance": canonical_appearance,
        }
        if header:
            meta["header"] = header
        if footer:
            meta["footer"] = footer
        if image:
            is_valid, reason = validate_url(image, context="media")
            if not is_valid:
                raise ValueError(f"Card image violates URL policy: {reason}")
            meta["image"] = image
        if image_alt:
            meta["image_alt"] = image_alt
        if combined_class:
            meta["class"] = combined_class

        return cls._create_placeholder(
            "div",
            "sc-wa-card",
            meta,
            body_html=body_html,
            extra_class=combined_class,
        )

    @classmethod
    def callout_text(
        cls,
        text: str,
        title: Optional[str] = None,
        variant: str = "brand",
        appearance: str = "outlined",
        icon: Optional[str] = None,
        class_name: Optional[str] = None,
    ) -> HTMLOutput:
        if not isinstance(text, str):
            raise TypeError("Callout text must be a string")
        escaped_body = f"<p>{html.escape(text, quote=True)}</p>"
        return cls._build_callout(escaped_body, title, variant, appearance, icon, class_name)

    @classmethod
    def callout_trusted_html(
        cls,
        html_obj: TrustedHTML,
        title: Optional[str] = None,
        variant: str = "brand",
        appearance: str = "outlined",
        icon: Optional[str] = None,
        class_name: Optional[str] = None,
    ) -> HTMLOutput:
        if not isinstance(html_obj, TrustedHTML):
            raise TypeError("Must pass TrustedHTML to callout_trusted_html; use callout_text for plain text")
        return cls._build_callout(str(html_obj), title, variant, appearance, icon, class_name)

    @classmethod
    def _build_callout(
        cls,
        body_html: str,
        title: Optional[str] = None,
        variant: str = "brand",
        appearance: str = "outlined",
        icon: Optional[str] = None,
        class_name: Optional[str] = None,
    ) -> HTMLOutput:
        canonical_appearance = appearance
        if canonical_appearance == "soft":
            canonical_appearance = "filled-outlined"
        elif canonical_appearance == "solid":
            canonical_appearance = "filled"
        elif canonical_appearance == "outline":
            canonical_appearance = "outlined"
        elif canonical_appearance == "default":
            canonical_appearance = "outlined"

        meta: dict[str, Any] = {
            "schema_version": "2.0.0",
            "component": "wa-callout",
            "variant": variant,
            "appearance": canonical_appearance,
        }
        if title:
            meta["title"] = title
        if icon:
            meta["icon"] = icon
        if class_name:
            meta["class"] = class_name

        return cls._create_placeholder(
            "div",
            "sc-wa-callout",
            meta,
            body_html=body_html,
            extra_class=class_name,
        )
