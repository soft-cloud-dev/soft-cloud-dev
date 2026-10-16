#!/usr/bin/env node
/**
 * scripts/lit-ssr-transform.mjs
 * CLI and library that transforms Web Awesome placeholders and attaches authentic Lit SSR DSD.
 */

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { parse, serialize } from 'parse5';

import { transformPlaceholders } from './lib/placeholder-transform.mjs';
import { renderComponentDSD } from './lib/lit-renderer.mjs';
import { validateHostDSD, validateDocumentDSD } from './lib/dsd-validator.mjs';
import { walkPostOrder, setAttr } from './lib/parse5-tree.mjs';
import { injectRuntimeAssets } from './lib/asset-injection.mjs';

const SUPPORTED_COMPONENTS = new Set(['wa-card', 'wa-callout', 'wa-button', 'wa-icon']);

/**
 * Transforms an HTML document: expands placeholders and attaches Lit SSR DSD.
 * @param {string} html - Raw HTML document.
 * @param {string} [baseUrl=''] - Optional base URL prefix for asset injection.
 * @returns {{ html: string, transformedCount: number, ssrCount: number }}
 */
export function transformAndRenderSSR(html, baseUrl = '') {
  // Step 1: Transform placeholders to custom element hosts
  const { html: placeholderHtml, transformedCount } = transformPlaceholders(html);

  // Step 2: Parse transformed HTML
  const ast = parse(placeholderHtml);

  // Collect custom element hosts in depth-first post-order (bottom-up / inside-out)
  const hosts = [];
  walkPostOrder(ast, (node) => {
    if (node.tagName && SUPPORTED_COMPONENTS.has(node.tagName)) {
      hosts.push(node);
    }
  });

  let ssrCount = 0;

  for (const host of hosts) {
    const tagName = host.tagName;
    const attrs = host.attrs || [];
    const hasDidSSR = attrs.some((a) => a.name === 'did-ssr');

    if (hasDidSSR) {
      // Rule 13: Treat an existing did-ssr without valid DSD as an error
      const validation = validateHostDSD(host);
      if (!validation.valid) {
        throw new Error(
          `Invalid state: existing 'did-ssr' on <${tagName}> failed DSD validation: ${validation.errors.join('; ')}`
        );
      }
      // Already validly SSR'd: idempotent skip
      continue;
    }

    // Step 3: Render through Lit SSR to extract DSD template
    const { dsdTemplateNode, hostAttrs } = renderComponentDSD(tagName, attrs);

    // Step 4: Prepend DSD template to host childNodes (before light DOM)
    host.childNodes = host.childNodes || [];
    host.childNodes.unshift(dsdTemplateNode);
    dsdTemplateNode.parentNode = host;

    // Step 5: Add did-ssr attribute
    setAttr(host, 'did-ssr', '');

    // Add default attributes emitted by component if not explicitly overridden
    for (const defAttr of hostAttrs) {
      if (!attrs.some((a) => a.name === defAttr.name)) {
        setAttr(host, defAttr.name, defAttr.value);
      }
    }

    // Step 6: Validate attached DSD
    const validation = validateHostDSD(host);
    if (!validation.valid) {
      throw new Error(`DSD validation failed for <${tagName}>: ${validation.errors.join('; ')}`);
    }

    ssrCount++;
  }

  // Validate entire document
  const docValidation = validateDocumentDSD(ast);
  if (!docValidation.valid) {
    throw new Error(`Document DSD validation failed: ${docValidation.errors.join('; ')}`);
  }

  // Step 7: Inject runtime assets if components are present
  if (hosts.length > 0 || docValidation.totalHosts > 0) {
    injectRuntimeAssets(ast, baseUrl);
  }

  const finalHtml = serialize(ast);
  return { html: finalHtml, transformedCount, ssrCount };
}

/**
 * Process a directory or file.
 */
export async function processPath(targetPath, baseUrl = '') {
  const stat = fs.statSync(targetPath);
  let files = [];

  if (stat.isDirectory()) {
    function findHtmlFiles(dir) {
      for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
        const full = path.join(dir, entry.name);
        if (entry.isDirectory()) {
          findHtmlFiles(full);
        } else if (entry.isFile() && entry.name.endsWith('.html')) {
          files.push(full);
        }
      }
    }
    findHtmlFiles(targetPath);
  } else if (stat.isFile() && targetPath.endsWith('.html')) {
    files.push(targetPath);
  }

  let totalTransformed = 0;
  let totalSSR = 0;

  for (const filePath of files) {
    const rawHtml = fs.readFileSync(filePath, 'utf8');
    const { html, transformedCount, ssrCount } = transformAndRenderSSR(rawHtml, baseUrl);
    fs.writeFileSync(filePath, html, 'utf8');
    totalTransformed += transformedCount;
    totalSSR += ssrCount;
  }

  return { filesCount: files.length, totalTransformed, totalSSR };
}

// CLI entry point
if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const target = process.argv[2];
  const baseUrl = process.argv[3] !== undefined ? process.argv[3] : (process.env.BASE_URL || '');
  if (!target) {
    console.error('Usage: node scripts/lit-ssr-transform.mjs <target-path> [base-url]');
    process.exit(1);
  }

  const absPath = path.resolve(process.cwd(), target);
  if (!fs.existsSync(absPath)) {
    console.error(`Error: target path does not exist: ${absPath}`);
    process.exit(1);
  }

  try {
    const { filesCount, totalTransformed, totalSSR } = await processPath(absPath, baseUrl);
    console.log(
      `[OK] Lit SSR Transform complete: ${filesCount} file(s) processed, ${totalTransformed} placeholder(s) transformed, ${totalSSR} DSD template(s) attached.`
    );
  } catch (err) {
    console.error(`[FAIL] Lit SSR Transform error:`, err);
    process.exit(1);
  }
}
