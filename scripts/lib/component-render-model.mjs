/**
 * scripts/lib/component-render-model.mjs
 * Constructs typed Web Awesome custom element nodes from validated metadata.
 */

import { createElement, createTextNode, setAttr } from './parse5-tree.mjs';

/**
 * Builds a typed custom element AST node from component metadata and moved children.
 * @param {object} meta - Validated metadata object.
 * @param {Array} lightDomChildren - Moved light-DOM child nodes.
 * @returns {object} parse5 element node for the custom element.
 */
export function buildCustomElementNode(meta, lightDomChildren = []) {
  const { component } = meta;

  switch (component) {
    case 'wa-card': {
      const host = createElement('wa-card');
      if (meta.appearance && meta.appearance !== 'default') {
        setAttr(host, 'appearance', meta.appearance);
      }
      if (meta.class) {
        setAttr(host, 'class', meta.class);
      }

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

      return host;
    }

    case 'wa-callout': {
      const host = createElement('wa-callout');
      if (meta.variant && meta.variant !== 'neutral') {
        setAttr(host, 'variant', meta.variant);
      }
      if (meta.appearance && meta.appearance !== 'default') {
        setAttr(host, 'appearance', meta.appearance);
      }
      if (meta.icon) {
        setAttr(host, 'icon', meta.icon);
      }
      if (meta.class) {
        setAttr(host, 'class', meta.class);
      }

      // 1. Title slot
      if (meta.title) {
        const titleSpan = createElement('span', [{ name: 'slot', value: 'title' }]);
        const textNode = createTextNode(meta.title);
        titleSpan.childNodes.push(textNode);
        textNode.parentNode = titleSpan;
        host.childNodes.push(titleSpan);
        titleSpan.parentNode = host;
      }

      // 2. Body light-DOM children
      for (const child of lightDomChildren) {
        host.childNodes.push(child);
        child.parentNode = host;
      }

      return host;
    }

    case 'wa-button': {
      const host = createElement('wa-button');
      if (meta.variant && meta.variant !== 'default') {
        setAttr(host, 'variant', meta.variant);
      }
      if (meta.appearance) {
        setAttr(host, 'appearance', meta.appearance);
      }
      if (meta.size) {
        const sizeMap = { small: 's', medium: 'm', large: 'l' };
        const normalizedSize = sizeMap[String(meta.size).toLowerCase()] || meta.size;
        setAttr(host, 'size', normalizedSize);
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
      if (meta.caret) {
        setAttr(host, 'caret', '');
      }
      if (meta.loading) {
        setAttr(host, 'loading', '');
      }
      if (meta.outline) {
        setAttr(host, 'outline', '');
      }
      if (meta.pill) {
        setAttr(host, 'pill', '');
      }
      if (meta.circle) {
        setAttr(host, 'circle', '');
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
      if (meta.style) {
        setAttr(host, 'style', meta.style);
      }
      if (meta.label) {
        setAttr(host, 'label', meta.label);
      }
      if (meta.library && meta.library !== 'default') {
        setAttr(host, 'library', meta.library);
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
