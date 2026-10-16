/**
 * scripts/lib/placeholder-transform.mjs
 * Converts validated HTML placeholders into Web Awesome host elements.
 */

import { parse, parseFragment, serialize } from 'parse5';
import {
  hasClass,
  getClassList,
  getTextContent,
  replaceChild,
  walkPostOrder,
} from './parse5-tree.mjs';
import { validateComponentMetadata } from './schema.mjs';
import { buildCustomElementNode } from './component-render-model.mjs';

const MARKER_TO_COMPONENT = {
  'sc-wa-card': 'wa-card',
  'sc-wa-callout': 'wa-callout',
  'sc-wa-button': 'wa-button',
  'sc-wa-icon': 'wa-icon',
};

/**
 * Transforms all Web Awesome placeholders in an HTML string into custom elements.
 * @param {string} html - Input HTML string.
 * @param {{ isFragment?: boolean }} options - Options.
 * @returns {{ html: string, transformedCount: number }}
 */
export function transformPlaceholders(html, options = {}) {
  if (typeof html !== 'string') {
    throw new TypeError('Input HTML must be a string');
  }

  const isFragment = Boolean(options.isFragment);
  const ast = isFragment ? parseFragment(html) : parse(html);

  // Collect candidate placeholder nodes in post-order (bottom-up)
  const placeholderNodes = [];
  walkPostOrder(ast, (node) => {
    if (node.tagName && hasClass(node, 'sc-wa-host')) {
      placeholderNodes.push(node);
    }
  });

  let transformedCount = 0;

  for (const node of placeholderNodes) {
    const parentNode = node.parentNode;
    if (!parentNode) continue;

    const classList = getClassList(node);

    // Identify component type from marker class
    let componentType = null;
    for (const [marker, comp] of Object.entries(MARKER_TO_COMPONENT)) {
      if (classList.includes(marker)) {
        componentType = comp;
        break;
      }
    }

    if (!componentType) {
      throw new Error(
        `Malformed placeholder: host element has 'sc-wa-host' but missing component marker class (found: ${classList.join(' ')})`
      );
    }

    // Direct metadata child validation
    const directChildren = node.childNodes || [];
    const metaChildren = directChildren.filter(
      (c) => c.tagName === 'span' && hasClass(c, 'sc-wa-meta')
    );

    if (metaChildren.length === 0) {
      throw new Error(`Malformed placeholder: missing metadata span in '${componentType}'`);
    }
    if (metaChildren.length > 1) {
      throw new Error(`Malformed placeholder: duplicate metadata spans in '${componentType}'`);
    }

    const metaSpan = metaChildren[0];
    const rawMetaText = getTextContent(metaSpan).trim();

    let meta;
    try {
      meta = JSON.parse(rawMetaText);
    } catch (e) {
      throw new Error(`Malformed placeholder: invalid JSON in metadata span: ${e.message}`);
    }

    if (meta.component !== componentType) {
      throw new Error(
        `Component mismatch: marker class is '${componentType}' but metadata specifies '${meta.component}'`
      );
    }

    // Validate metadata against schema and security rules
    const validation = validateComponentMetadata(meta);
    if (!validation.valid) {
      throw new Error(`Metadata validation failed for '${componentType}': ${validation.errors.join('; ')}`);
    }

    // Retain user classes that aren't synthetic markers
    const userClasses = classList.filter(
      (c) => c !== 'sc-wa-host' && !MARKER_TO_COMPONENT[c]
    );
    if (userClasses.length > 0) {
      meta.class = meta.class
        ? `${meta.class} ${userClasses.join(' ')}`.trim()
        : userClasses.join(' ');
    }

    // Move light-DOM children (excluding the metadata span)
    const lightDomChildren = directChildren.filter((c) => c !== metaSpan);

    // Build the new custom element node
    const customElementNode = buildCustomElementNode(meta, lightDomChildren);

    // Replace the placeholder in the parent
    replaceChild(parentNode, node, customElementNode);
    transformedCount++;
  }

  const resultHtml = serialize(ast);
  return { html: resultHtml, transformedCount };
}
