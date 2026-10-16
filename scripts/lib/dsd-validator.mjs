/**
 * scripts/lib/dsd-validator.mjs
 * Validates Declarative Shadow DOM structure and did-ssr consistency.
 */

import { walkPostOrder } from './parse5-tree.mjs';

const SUPPORTED_COMPONENTS = new Set(['wa-card', 'wa-callout', 'wa-button', 'wa-icon']);

/**
 * Validates the DSD template attachment on a single custom element host.
 * @param {object} hostNode - parse5 element node.
 * @returns {{ valid: boolean, errors: string[] }}
 */
export function validateHostDSD(hostNode) {
  const errors = [];
  const tagName = hostNode.tagName;

  if (!SUPPORTED_COMPONENTS.has(tagName)) {
    return { valid: true, errors: [] };
  }

  const attrs = hostNode.attrs || [];
  const hasDidSSR = attrs.some((a) => a.name === 'did-ssr');

  const children = hostNode.childNodes || [];
  const dsdTemplates = children.filter(
    (c) =>
      c.tagName === 'template' &&
      c.attrs &&
      c.attrs.some(
        (a) =>
          (a.name === 'shadowrootmode' || a.name === 'shadowroot') &&
          a.value === 'open'
      )
  );

  if (hasDidSSR && dsdTemplates.length === 0) {
    errors.push(`Host <${tagName}> has 'did-ssr' attribute but is missing a valid DSD template`);
  }

  if (!hasDidSSR && dsdTemplates.length > 0) {
    errors.push(`Host <${tagName}> contains a DSD template but is missing the 'did-ssr' attribute`);
  }

  if (dsdTemplates.length > 1) {
    errors.push(`Host <${tagName}> contains multiple direct DSD templates (found ${dsdTemplates.length})`);
  }

  if (dsdTemplates.length === 1) {
    const tpl = dsdTemplates[0];
    const templateIdx = children.indexOf(tpl);
    if (templateIdx !== 0) {
      // DSD template should be the very first child of the host
      // Notice: sometimes leading whitespace text nodes exist; template must precede light-DOM elements
      const precedingNonWhitespace = children
        .slice(0, templateIdx)
        .some((c) => c.tagName || (c.nodeName === '#text' && c.value.trim().length > 0));
      if (precedingNonWhitespace) {
        errors.push(`Host <${tagName}> has light-DOM content preceding the DSD template`);
      }
    }

    // Template should contain shadow root content (e.g. style or elements)
    const tplContent = tpl.content || tpl;
    const tplChildren = tplContent.childNodes || [];
    if (tplChildren.length === 0) {
      errors.push(`Host <${tagName}> DSD template is empty`);
    }
  }

  return {
    valid: errors.length === 0,
    errors,
  };
}

/**
 * Validates DSD across an entire parsed document AST.
 * @param {object} ast - parse5 document AST.
 * @returns {{ valid: boolean, totalHosts: number, dsdCount: number, errors: string[] }}
 */
export function validateDocumentDSD(ast) {
  let totalHosts = 0;
  let dsdCount = 0;
  const allErrors = [];

  walkPostOrder(ast, (node) => {
    if (node.tagName && SUPPORTED_COMPONENTS.has(node.tagName)) {
      totalHosts++;
      const res = validateHostDSD(node);
      if (!res.valid) {
        allErrors.push(...res.errors);
      }
      const attrs = node.attrs || [];
      if (attrs.some((a) => a.name === 'did-ssr')) {
        dsdCount++;
      }
    }
  });

  return {
    valid: allErrors.length === 0,
    totalHosts,
    dsdCount,
    errors: allErrors,
  };
}
