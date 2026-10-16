/**
 * tests/myst/test-plugin-output.mjs
 * Unit tests for MyST Web Awesome plugin directive and role output.
 */

import test from 'node:test';
import assert from 'node:assert/strict';
import plugin from '../../assets/plugins/myst-webawesome.mjs';

const mockCtx = {
  parseMyst(text) {
    return {
      type: 'root',
      children: [
        {
          type: 'paragraph',
          children: [{ type: 'text', value: text }],
        },
      ],
    };
  },
};

test('Plugin exports directives and roles correctly', () => {
  assert.equal(plugin.name, 'SoftCloud Web Awesome Plugin');
  assert.equal(Array.isArray(plugin.directives), true);
  assert.equal(Array.isArray(plugin.roles), true);

  const directiveNames = plugin.directives.map((d) => d.name);
  assert.ok(directiveNames.includes('wa-card'));
  assert.ok(directiveNames.includes('wa-callout'));
  assert.ok(directiveNames.includes('wa-button'));

  const roleNames = plugin.roles.map((r) => r.name);
  assert.ok(roleNames.includes('icon'));
  assert.ok(roleNames.includes('fa'));
});

test('wa-card produces valid wrapper, metadata span, and body', () => {
  const cardDir = plugin.directives.find((d) => d.name === 'wa-card');
  const nodes = cardDir.run(
    {
      arg: 'My Card Header',
      options: { appearance: 'elevated', image: '/images/card.png', image_alt: 'Preview' },
      body: 'Body text inside card with [link](https://example.com).',
    },
    {},
    mockCtx
  );

  assert.equal(nodes.length, 1);
  const host = nodes[0];
  assert.equal(host.type, 'div');
  assert.ok(host.class.includes('sc-wa-host'));
  assert.ok(host.class.includes('sc-wa-card'));

  const metaSpan = host.children.find((c) => c.type === 'span' && c.class === 'sc-wa-meta');
  assert.ok(metaSpan, 'Expected exactly one sc-wa-meta child');
  const meta = JSON.parse(metaSpan.children[0].value);
  assert.equal(meta.component, 'wa-card');
  assert.equal(meta.schema_version, '1.0.0');
  assert.equal(meta.header, 'My Card Header');
  assert.equal(meta.appearance, 'elevated');
  assert.equal(meta.image, '/images/card.png');

  // Verify body is preserved
  assert.ok(host.children.length >= 2);
});

test('wa-callout produces valid wrapper and metadata', () => {
  const calloutDir = plugin.directives.find((d) => d.name === 'wa-callout');
  const nodes = calloutDir.run(
    {
      arg: 'Warning Note',
      options: { variant: 'warning', appearance: 'soft', icon: 'triangle-exclamation' },
      body: 'Careful with this configuration.',
    },
    {},
    mockCtx
  );

  assert.equal(nodes.length, 1);
  const host = nodes[0];
  assert.equal(host.type, 'div');
  assert.ok(host.class.includes('sc-wa-host'));
  assert.ok(host.class.includes('sc-wa-callout'));

  const metaSpan = host.children.find((c) => c.class === 'sc-wa-meta');
  const meta = JSON.parse(metaSpan.children[0].value);
  assert.equal(meta.component, 'wa-callout');
  assert.equal(meta.variant, 'warning');
  assert.equal(meta.title, 'Warning Note');
});

test('wa-button produces valid wrapper and link metadata', () => {
  const btnDir = plugin.directives.find((d) => d.name === 'wa-button');
  const nodes = btnDir.run(
    {
      arg: 'https://my.softcloud.dev/docs',
      options: { variant: 'primary', appearance: 'filled', size: 'large' },
      body: 'Launch Portal',
    },
    {},
    mockCtx
  );

  assert.equal(nodes.length, 1);
  const host = nodes[0];
  assert.equal(host.type, 'div');
  assert.ok(host.class.includes('sc-wa-host'));
  assert.ok(host.class.includes('sc-wa-button'));

  const metaSpan = host.children.find((c) => c.class === 'sc-wa-meta');
  const meta = JSON.parse(metaSpan.children[0].value);
  assert.equal(meta.component, 'wa-button');
  assert.equal(meta.variant, 'primary');
  assert.equal(meta.href, 'https://my.softcloud.dev/docs');
});

test('icon role produces inline span with metadata', () => {
  const iconRole = plugin.roles.find((r) => r.name === 'icon');
  const nodes = iconRole.run({ body: 'classic solid rocket' });

  assert.equal(nodes.length, 1);
  const host = nodes[0];
  assert.equal(host.type, 'span');
  assert.ok(host.class.includes('sc-wa-host'));
  assert.ok(host.class.includes('sc-wa-icon'));

  const metaSpan = host.children[0];
  const meta = JSON.parse(metaSpan.children[0].value);
  assert.equal(meta.component, 'wa-icon');
  assert.equal(meta.name, 'rocket');
  assert.equal(meta.family, 'classic');
  assert.equal(meta.style, 'solid');
});

test('fa role produces inline span with Font Awesome metadata', () => {
  const faRole = plugin.roles.find((r) => r.name === 'fa');
  const nodes = faRole.run({ body: 'brands github' });

  assert.equal(nodes.length, 1);
  const host = nodes[0];
  assert.equal(host.type, 'span');
  assert.ok(host.class.includes('sc-wa-host'));
  assert.ok(host.class.includes('sc-wa-icon'));

  const metaSpan = host.children[0];
  const meta = JSON.parse(metaSpan.children[0].value);
  assert.equal(meta.component, 'wa-icon');
  assert.equal(meta.library, 'fa');
  assert.equal(meta.name, 'github');
  assert.equal(meta.style, 'brands');
});

test('Plugin rejects invalid options or unsafe URLs', () => {
  const btnDir = plugin.directives.find((d) => d.name === 'wa-button');
  assert.throws(
    () => {
      btnDir.run({ options: { href: 'javascript:alert(1)' }, body: 'Click' }, {}, mockCtx);
    },
    /violates URL policy/
  );

  const cardDir = plugin.directives.find((d) => d.name === 'wa-card');
  assert.throws(
    () => {
      cardDir.run({ options: { appearance: 'nonexistent-look' } }, {}, mockCtx);
    },
    /Invalid value 'nonexistent-look'/
  );
});
