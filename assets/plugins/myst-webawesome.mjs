/**
 * assets/plugins/myst-webawesome.mjs
 * Authoritative MyST plugin for Web Awesome SSR components in SoftCloud.
 */

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const schemaPath = path.resolve(__dirname, '../shared/component-schema.json');
const SCHEMA = JSON.parse(fs.readFileSync(schemaPath, 'utf8'));

// Import validators
import { validateUrl } from '../../scripts/lib/url-policy.mjs';
import { validateComponentMetadata, normalizeComponentMetadata } from '../../scripts/lib/schema.mjs';

function createMetaNode(meta) {
  return {
    type: 'span',
    class: 'sc-wa-meta',
    children: [
      {
        type: 'text',
        value: JSON.stringify(meta),
      },
    ],
  };
}

function parseMarkdownBody(body, ctx) {
  if (!body || !body.trim()) return [];
  if (ctx && typeof ctx.parseMyst === 'function') {
    const parsed = ctx.parseMyst(body);
    return parsed.children || [parsed];
  }
  return [
    {
      type: 'paragraph',
      children: [{ type: 'text', value: body }],
    },
  ];
}

const waCardDirective = {
  name: 'wa-card',
  doc: 'Web Awesome Card container',
  arg: {
    type: String,
    doc: 'Optional card header',
    required: false,
  },
  options: {
    header: { type: String, doc: 'Card header text' },
    footer: { type: String, doc: 'Card footer text' },
    image: { type: String, doc: 'Card media URL' },
    image_alt: { type: String, doc: 'Card media alt text' },
    appearance: { type: String, doc: 'Appearance: accent, filled, outlined, filled-outlined, plain (or legacy elevated, default, flat)' },
    class: { type: String, doc: 'Custom CSS classes' },
  },
  body: {
    type: String,
    doc: 'Card content in MyST Markdown',
  },
  run(data, vfile, ctx) {
    const opts = { ...data.options };
    if (!opts.header && data.arg) {
      opts.header = data.arg.trim();
    }

    let meta = {
      schema_version: '2.0.0',
      component: 'wa-card',
      ...opts,
    };

    meta = normalizeComponentMetadata(meta, { context: 'wa-card' });
    const validation = validateComponentMetadata(meta);
    if (!validation.valid) {
      throw new Error(`[wa-card error] ${validation.errors.join('; ')}`);
    }

    const hostClasses = ['sc-wa-host', 'sc-wa-card'];
    if (meta.class) {
      hostClasses.push(meta.class);
    }

    const bodyChildren = parseMarkdownBody(data.body, ctx);
    const metaNode = createMetaNode(meta);

    return [
      {
        type: 'div',
        class: hostClasses.join(' '),
        children: [metaNode, ...bodyChildren],
      },
    ];
  },
};

const waCalloutDirective = {
  name: 'wa-callout',
  doc: 'Web Awesome Callout container',
  arg: {
    type: String,
    doc: 'Optional callout title',
    required: false,
  },
  options: {
    variant: { type: String, doc: 'Variant: neutral, brand, success, warning, danger' },
    appearance: { type: String, doc: 'Appearance: accent, filled, outlined, filled-outlined, plain (or legacy soft, solid, outline, default)' },
    icon: { type: String, doc: 'Icon name' },
    title: { type: String, doc: 'Callout title' },
    class: { type: String, doc: 'Custom CSS classes' },
  },
  body: {
    type: String,
    doc: 'Callout content in MyST Markdown',
  },
  run(data, vfile, ctx) {
    const opts = { ...data.options };
    if (!opts.title && data.arg) {
      opts.title = data.arg.trim();
    }

    let meta = {
      schema_version: '2.0.0',
      component: 'wa-callout',
      ...opts,
    };

    meta = normalizeComponentMetadata(meta, { context: 'wa-callout' });
    const validation = validateComponentMetadata(meta);
    if (!validation.valid) {
      throw new Error(`[wa-callout error] ${validation.errors.join('; ')}`);
    }

    const hostClasses = ['sc-wa-host', 'sc-wa-callout'];
    if (meta.class) {
      hostClasses.push(meta.class);
    }

    const bodyChildren = parseMarkdownBody(data.body, ctx);
    const metaNode = createMetaNode(meta);

    return [
      {
        type: 'div',
        class: hostClasses.join(' '),
        children: [metaNode, ...bodyChildren],
      },
    ];
  },
};

const waButtonDirective = {
  name: 'wa-button',
  doc: 'Web Awesome Button container',
  arg: {
    type: String,
    doc: 'Optional button label or href',
    required: false,
  },
  options: {
    variant: { type: String, doc: 'Variant: brand, neutral, success, warning, danger' },
    appearance: { type: String, doc: 'Appearance: accent, filled, outlined, filled-outlined, plain' },
    size: { type: String, doc: 'Size: xs, s, m, l, xl' },
    href: { type: String, doc: 'Link URL' },
    target: { type: String, doc: 'Link target' },
    rel: { type: String, doc: 'Link rel' },
    disabled: { type: Boolean, doc: 'Disabled boolean' },
    caret: { type: Boolean, doc: 'Show caret (legacy)' },
    'with-caret': { type: Boolean, doc: 'Show caret' },
    loading: { type: Boolean, doc: 'Loading state' },
    outline: { type: Boolean, doc: 'Outline style (legacy)' },
    pill: { type: Boolean, doc: 'Pill shape' },
    circle: { type: Boolean, doc: 'Circle shape' },
    label: { type: String, doc: 'Accessible label' },
    class: { type: String, doc: 'Custom CSS classes' },
  },
  body: {
    type: String,
    doc: 'Button label or content in MyST Markdown',
  },
  run(data, vfile, ctx) {
    const opts = { ...data.options };
    if (!opts.href && data.arg && (data.arg.startsWith('http') || data.arg.startsWith('/') || data.arg.startsWith('#'))) {
      opts.href = data.arg.trim();
    } else if (!opts.label && data.arg && !data.body) {
      opts.label = data.arg.trim();
    }

    let meta = {
      schema_version: '2.0.0',
      component: 'wa-button',
      ...opts,
    };

    meta = normalizeComponentMetadata(meta, { context: 'wa-button' });
    const validation = validateComponentMetadata(meta);
    if (!validation.valid) {
      throw new Error(`[wa-button error] ${validation.errors.join('; ')}`);
    }

    const hostClasses = ['sc-wa-host', 'sc-wa-button'];
    if (meta.class) {
      hostClasses.push(meta.class);
    }

    let bodyChildren = parseMarkdownBody(data.body, ctx);
    if (bodyChildren.length === 0 && data.arg && opts.href) {
      const buttonText = meta.label || opts.href;
      bodyChildren = [{ type: 'text', value: buttonText }];
    } else if (bodyChildren.length === 0 && meta.label) {
      bodyChildren = [{ type: 'text', value: meta.label }];
    }

    const metaNode = createMetaNode(meta);

    return [
      {
        type: 'div',
        class: hostClasses.join(' '),
        children: [metaNode, ...bodyChildren],
      },
    ];
  },
};

function parseIconRoleContent(content) {
  const parts = content.trim().split(/\s+/);
  const rawMeta = {
    schema_version: '2.0.0',
    component: 'wa-icon',
  };

  const allowedFamilies = new Set(['classic', 'sharp', 'duotone', 'brands']);
  const allowedVariants = new Set(['solid', 'regular', 'light', 'thin']);

  for (const part of parts) {
    if (part.includes('=')) {
      const [k, v] = part.split('=', 2);
      rawMeta[k] = v.replace(/^["']|["']$/g, '');
    } else if (allowedFamilies.has(part)) {
      rawMeta.family = part;
    } else if (allowedVariants.has(part)) {
      rawMeta.variant = part;
    } else if (part === 'brands') {
      rawMeta.family = 'brands';
    } else {
      rawMeta.name = part;
    }
  }

  return normalizeComponentMetadata(rawMeta, { context: 'icon' });
}

const iconRole = {
  name: 'icon',
  doc: 'Web Awesome Icon role',
  body: {
    type: String,
    doc: 'Icon specifications',
    required: true,
  },
  run(data) {
    const raw = data.body || data.arg || '';
    const meta = parseIconRoleContent(raw);

    const validation = validateComponentMetadata(meta);
    if (!validation.valid) {
      throw new Error(`[icon error] ${validation.errors.join('; ')}`);
    }

    const metaNode = createMetaNode(meta);
    return [
      {
        type: 'span',
        class: 'sc-wa-host sc-wa-icon',
        children: [metaNode],
      },
    ];
  },
};

const faRole = {
  name: 'fa',
  doc: 'Font Awesome Icon role',
  body: {
    type: String,
    doc: 'Font Awesome icon specifications',
    required: true,
  },
  run(data) {
    const raw = data.body || data.arg || '';
    const parts = raw.trim().split(/\s+/);
    let family = 'classic';
    let variant = 'solid';
    let name = '';

    if (parts.length === 1) {
      name = parts[0];
      // Check if known brand icon
      if (['github', 'linux', 'python', 'docker', 'rust', 'freebsd', 'git-alt', 'markdown', 'twitter', 'facebook', 'google'].includes(name)) {
        family = 'brands';
        variant = undefined;
      }
    } else if (parts.length >= 2) {
      const prefix = parts[0];
      name = parts[1];
      if (prefix === 'brands' || prefix === 'fab') {
        family = 'brands';
        variant = undefined;
      } else if (prefix === 'regular' || prefix === 'far') {
        family = 'classic';
        variant = 'regular';
      } else {
        family = 'classic';
        variant = 'solid';
      }
    }

    const rawMeta = {
      schema_version: '2.0.0',
      component: 'wa-icon',
      name,
      family,
    };
    if (variant) {
      rawMeta.variant = variant;
    }

    const meta = normalizeComponentMetadata(rawMeta, { context: 'fa' });
    const validation = validateComponentMetadata(meta);
    if (!validation.valid) {
      throw new Error(`[fa error] ${validation.errors.join('; ')}`);
    }

    const metaNode = createMetaNode(meta);
    return [
      {
        type: 'span',
        class: 'sc-wa-host sc-wa-icon',
        children: [metaNode],
      },
    ];
  },
};

const plugin = {
  name: 'SoftCloud Web Awesome Plugin',
  doc: 'MyST plugin generating validated Web Awesome component placeholders',
  directives: [waCardDirective, waCalloutDirective, waButtonDirective],
  roles: [iconRole, faRole],
};

export default plugin;
