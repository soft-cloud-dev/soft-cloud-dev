/**
 * scripts/lib/lit-renderer.mjs
 * Renders Web Awesome components via Lit SSR to generate authentic Declarative Shadow DOM.
 */

import { render } from '@lit-labs/ssr';
import { html, nothing } from 'lit';
import { parseFragment } from 'parse5';

// Import Web Awesome component definitions
import '@awesome.me/webawesome/dist/components/button/button.js';
import '@awesome.me/webawesome/dist/components/callout/callout.js';
import '@awesome.me/webawesome/dist/components/card/card.js';
import '@awesome.me/webawesome/dist/components/icon/icon.js';

/**
 * Builds a Lit template for a given Web Awesome component and its attributes.
 * @param {string} tagName - Component tag name ('wa-button', 'wa-card', etc.).
 * @param {Record<string, string>} attrMap - Attribute key-value mapping.
 * @returns {import('lit').TemplateResult}
 */
export function buildLitTemplate(tagName, attrMap) {
  switch (tagName) {
    case 'wa-button': {
      const {
        variant,
        appearance,
        size,
        href,
        target,
        rel,
        disabled,
        caret,
        'with-caret': withCaret,
        loading,
        outline,
        pill,
        circle,
      } = attrMap;

      const sizeMap = { small: 's', medium: 'm', large: 'l' };
      const normalizedSize = (size && sizeMap[String(size).toLowerCase()]) || size;

      return html`<wa-button
        ?disabled=${disabled !== undefined}
        ?with-caret=${withCaret !== undefined || caret !== undefined}
        ?loading=${loading !== undefined}
        ?outline=${outline !== undefined}
        ?pill=${pill !== undefined}
        ?circle=${circle !== undefined}
        variant=${variant || nothing}
        appearance=${appearance || nothing}
        size=${normalizedSize || nothing}
        href=${href || nothing}
        target=${target || nothing}
        rel=${rel || nothing}
      ></wa-button>`;
    }

    case 'wa-card': {
      const { appearance } = attrMap;
      return html`<wa-card appearance=${appearance || nothing}></wa-card>`;
    }

    case 'wa-callout': {
      const { variant, appearance } = attrMap;
      return html`<wa-callout
        variant=${variant || nothing}
        appearance=${appearance || nothing}
       ></wa-callout>`;
    }

    case 'wa-icon': {
      const { name, family, variant, style, label, library } = attrMap;
      return html`<wa-icon
        name=${name || nothing}
        family=${family || nothing}
        variant=${variant || nothing}
        style=${style || nothing}
        label=${label || nothing}
        library=${library || nothing}
      ></wa-icon>`;
    }

    default:
      throw new Error(`Unsupported component for Lit SSR: <${tagName}>`);
  }
}

/**
 * Renders a Web Awesome component and extracts its direct open DSD template node.
 * @param {string} tagName - Custom element tag name.
 * @param {Array<{ name: string, value: string }>} attrs - Node attributes.
 * @returns {{ dsdTemplateNode: object, hostAttrs: Array<{ name: string, value: string }> }}
 */
export function renderComponentDSD(tagName, attrs = []) {
  const attrMap = {};
  for (const a of attrs) {
    attrMap[a.name] = a.value;
  }

  const template = buildLitTemplate(tagName, attrMap);
  const chunks = [];
  for (const chunk of render(template)) {
    chunks.push(chunk);
  }
  const renderedHtml = chunks.join('');

  // Parse rendered HTML fragment to locate the host element and its DSD template
  const ast = parseFragment(renderedHtml);
  let renderedHost = null;

  for (const node of ast.childNodes || []) {
    if (node.tagName === tagName) {
      renderedHost = node;
      break;
    }
  }

  if (!renderedHost) {
    throw new Error(`Failed to locate rendered <${tagName}> in Lit SSR output`);
  }

  // Locate the direct template[shadowrootmode="open"] child
  const dsdTemplates = (renderedHost.childNodes || []).filter(
    (c) =>
      c.tagName === 'template' &&
      c.attrs &&
      c.attrs.some(
        (a) =>
          (a.name === 'shadowrootmode' || a.name === 'shadowroot') &&
          a.value === 'open'
      )
  );

  if (dsdTemplates.length === 0) {
    throw new Error(`No Declarative Shadow DOM template generated for <${tagName}>`);
  }
  if (dsdTemplates.length > 1) {
    throw new Error(`Multiple DSD templates generated for <${tagName}>`);
  }

  const dsdTemplateNode = dsdTemplates[0];

  return {
    dsdTemplateNode,
    hostAttrs: renderedHost.attrs || [],
  };
}
