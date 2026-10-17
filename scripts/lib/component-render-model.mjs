/**
 * scripts/lib/component-render-model.mjs
 * Constructs typed Web Awesome custom element nodes from validated/normalized metadata
 * conforming strictly to Web Awesome 3.14.0.
 */

import { createElement, createTextNode, setAttr, getAttr } from './parse5-tree.mjs';
import { normalizeComponentMetadata } from './schema.mjs';

/**
 * Builds a typed custom element AST node from component metadata and moved children.
 * @param {object} rawMeta - Metadata object (1.0.0 or 2.0.0).
 * @param {Array} lightDomChildren - Moved light-DOM child nodes.
 * @returns {object} parse5 element node for the custom element.
 */
export function buildCustomElementNode(rawMeta, lightDomChildren = []) {
  const meta = normalizeComponentMetadata(rawMeta);
  const { component } = meta;

  switch (component) {
    case 'wa-card': {
      const host = createElement('wa-card');
      if (meta.appearance) {
        setAttr(host, 'appearance', meta.appearance);
      }
      if (meta.class) {
        setAttr(host, 'class', meta.class);
      }

      let hasHeader = Boolean(meta.header);
      let hasFooter = Boolean(meta.footer);
      let hasMedia = Boolean(meta.image);
      let hasHeaderActions = false;
      let hasFooterActions = false;

      // 1. Media slot (image)
      if (meta.image) {
        const img = createElement('img');
        setAttr(img, 'slot', 'media');
        setAttr(img, 'src', meta.image);
        if (meta.image_alt) {
          setAttr(img, 'alt', meta.image_alt);
        }
        host.childNodes.push(img);
        img.parentNode = host;
      }

      // 2. Header slot
      if (meta.header) {
        const headerDiv = createElement('div', [{ name: 'slot', value: 'header' }]);
        const textNode = createTextNode(meta.header);
        headerDiv.childNodes.push(textNode);
        textNode.parentNode = headerDiv;
        host.childNodes.push(headerDiv);
        headerDiv.parentNode = host;
      }

      // 3. Body light-DOM children
      for (const child of lightDomChildren) {
        const slotAttr = getAttr(child, 'slot');
        if (slotAttr === 'header') hasHeader = true;
        else if (slotAttr === 'footer') hasFooter = true;
        else if (slotAttr === 'media') hasMedia = true;
        else if (slotAttr === 'header-actions') hasHeaderActions = true;
        else if (slotAttr === 'footer-actions') hasFooterActions = true;

        host.childNodes.push(child);
        child.parentNode = host;
      }

      // 4. Footer slot
      if (meta.footer) {
        const footerDiv = createElement('div', [{ name: 'slot', value: 'footer' }]);
        const textNode = createTextNode(meta.footer);
        footerDiv.childNodes.push(textNode);
        textNode.parentNode = footerDiv;
        host.childNodes.push(footerDiv);
        footerDiv.parentNode = host;
      }

      // 5. SSR presence attributes for Web Awesome 3.14.0 (WA-004)
      if (hasHeader) setAttr(host, 'with-header', '');
      if (hasFooter) setAttr(host, 'with-footer', '');
      if (hasMedia) setAttr(host, 'with-media', '');
      if (hasHeaderActions) setAttr(host, 'with-header-actions', '');
      if (hasFooterActions) setAttr(host, 'with-footer-actions', '');

      return host;
    }

    case 'wa-callout': {
      const host = createElement('wa-callout');
      if (meta.variant) {
        setAttr(host, 'variant', meta.variant);
      }
      if (meta.appearance) {
        setAttr(host, 'appearance', meta.appearance);
      }
      if (meta.class) {
        setAttr(host, 'class', meta.class);
      }

      // 1. Icon slot (WA-001, WA-002) - slotted into slot="icon"
      if (meta.icon) {
        const iconEl = createElement('wa-icon');
        setAttr(iconEl, 'slot', 'icon');
        setAttr(iconEl, 'name', meta.icon);
        setAttr(iconEl, 'family', 'classic');
        setAttr(iconEl, 'variant', 'solid');
        setAttr(iconEl, 'aria-hidden', 'true');
        host.childNodes.push(iconEl);
        iconEl.parentNode = host;
      }

      // 2. Default slot content: wrap title and body in .sc-wa-callout-content (WA-002)
      const contentDiv = createElement('div', [{ name: 'class', value: 'sc-wa-callout-content' }]);

      if (meta.title) {
        const titleEl = createElement('strong', [{ name: 'class', value: 'sc-wa-callout-title' }]);
        const textNode = createTextNode(meta.title);
        titleEl.childNodes.push(textNode);
        textNode.parentNode = titleEl;
        contentDiv.childNodes.push(titleEl);
        titleEl.parentNode = contentDiv;
      }

      for (const child of lightDomChildren) {
        contentDiv.childNodes.push(child);
        child.parentNode = contentDiv;
      }

      host.childNodes.push(contentDiv);
      contentDiv.parentNode = host;

      return host;
    }

    case 'wa-button': {
      const host = createElement('wa-button');
      if (meta.variant) {
        setAttr(host, 'variant', meta.variant);
      }
      if (meta.appearance) {
        setAttr(host, 'appearance', meta.appearance);
      }
      if (meta.size) {
        setAttr(host, 'size', meta.size);
      }
      if (meta.href) {
        setAttr(host, 'href', meta.href);
      }
      if (meta.target) {
        setAttr(host, 'target', meta.target);
      }
      if (meta.rel) {
        setAttr(host, 'rel', meta.rel);
      }
      if (meta.disabled) {
        setAttr(host, 'disabled', '');
      }
      if (meta['with-caret']) {
        setAttr(host, 'with-caret', '');
      }
      if (meta.loading) {
        setAttr(host, 'loading', '');
      }
      if (meta.pill) {
        setAttr(host, 'pill', '');
      }
      if (meta.label) {
        setAttr(host, 'aria-label', meta.label);
      }
      if (meta.class) {
        setAttr(host, 'class', meta.class);
      }

      for (const child of lightDomChildren) {
        host.childNodes.push(child);
        child.parentNode = host;
      }

      return host;
    }

    case 'wa-icon': {
      const host = createElement('wa-icon');
      setAttr(host, 'name', meta.name);
      if (meta.family) {
        setAttr(host, 'family', meta.family);
      }
      if (meta.variant) {
        setAttr(host, 'variant', meta.variant);
      }
      if (meta.label) {
        setAttr(host, 'label', meta.label);
      } else {
        setAttr(host, 'aria-hidden', 'true');
      }
      if (meta.class) {
        setAttr(host, 'class', meta.class);
      }
      return host;
    }

    default:
      throw new Error(`Unsupported component type: ${component}`);
  }
}
