/**
 * tests/security/test-url-policy.mjs
 * Validates JS URL policy against the canonical url-corpus.json and tests schema rejection.
 */

import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

import { validateUrl } from '../../scripts/lib/url-policy.mjs';
import { validateComponentMetadata } from '../../scripts/lib/schema.mjs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const corpusPath = path.resolve(__dirname, 'url-corpus.json');
const corpus = JSON.parse(fs.readFileSync(corpusPath, 'utf8'));

test('URL policy validates entire corpus as expected', () => {
  for (const item of corpus) {
    const res = validateUrl(item.url, { context: item.context });
    assert.equal(
      res.valid,
      item.valid,
      `Failed on ${item.context} URL: '${item.url}'. Expected valid=${item.valid}, got=${res.valid} (${res.reason || 'ok'})`
    );
  }
});

test('Schema validator rejects unknown components', () => {
  const res = validateComponentMetadata({
    component: 'wa-unknown',
    schema_version: '1.0.0',
  });
  assert.equal(res.valid, false);
  assert.match(res.errors[0], /Unknown or unsupported component/);
});

test('Schema validator rejects unsupported schema versions', () => {
  const res = validateComponentMetadata({
    component: 'wa-button',
    schema_version: '2.0.0',
  });
  assert.equal(res.valid, false);
  assert.match(res.errors[0], /Unsupported schema version/);
});

test('Schema validator rejects unknown options / additional properties', () => {
  const res = validateComponentMetadata({
    component: 'wa-button',
    schema_version: '1.0.0',
    malicious_prop: '<script>alert(1)</script>',
  });
  assert.equal(res.valid, false);
  assert.match(res.errors[0], /Unknown field 'malicious_prop'/);
});

test('Schema validator rejects event handlers', () => {
  const res = validateComponentMetadata({
    component: 'wa-button',
    schema_version: '1.0.0',
    onclick: 'alert(1)',
  });
  assert.equal(res.valid, false);
});

test('Schema validator rejects invalid button variants', () => {
  const res = validateComponentMetadata({
    component: 'wa-button',
    schema_version: '1.0.0',
    variant: 'danger-zone',
  });
  assert.equal(res.valid, false);
  assert.match(res.errors[0], /Invalid value 'danger-zone'/);
});

test('Schema validator rejects button with unsafe javascript href', () => {
  const res = validateComponentMetadata({
    component: 'wa-button',
    schema_version: '1.0.0',
    href: 'javascript:alert(1)',
  });
  assert.equal(res.valid, false);
  assert.match(res.errors[0], /violates URL policy/);
});

test('Schema validator rejects card with mailto media image', () => {
  const res = validateComponentMetadata({
    component: 'wa-card',
    schema_version: '1.0.0',
    image: 'mailto:attacker@evil.com',
  });
  assert.equal(res.valid, false);
  assert.match(res.errors[0], /violates URL policy/);
});

test('Schema validator accepts valid button, card, callout, icon', () => {
  assert.equal(
    validateComponentMetadata({
      component: 'wa-button',
      schema_version: '1.0.0',
      variant: 'primary',
      appearance: 'filled',
      size: 'medium',
      href: 'https://my.softcloud.dev/docs',
      target: '_blank',
    }).valid,
    true
  );

  assert.equal(
    validateComponentMetadata({
      component: 'wa-card',
      schema_version: '1.0.0',
      header: 'Card Title',
      image: '/images/pic.png',
      image_alt: 'A description',
      appearance: 'elevated',
    }).valid,
    true
  );

  assert.equal(
    validateComponentMetadata({
      component: 'wa-callout',
      schema_version: '1.0.0',
      variant: 'brand',
      appearance: 'soft',
      icon: 'info',
    }).valid,
    true
  );

  assert.equal(
    validateComponentMetadata({
      component: 'wa-icon',
      schema_version: '1.0.0',
      name: 'rocket',
      style: 'solid',
      family: 'classic',
    }).valid,
    true
  );
});
