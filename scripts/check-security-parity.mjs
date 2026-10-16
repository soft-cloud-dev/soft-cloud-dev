#!/usr/bin/env node
/**
 * scripts/check-security-parity.mjs
 * Validates that JS and Python URL security policies produce identical results on the test corpus.
 */

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { execFileSync } from 'node:child_process';

import { validateUrl } from './lib/url-policy.mjs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const rootDir = path.resolve(__dirname, '..');
const corpusPath = path.join(rootDir, 'tests/security/url-corpus.json');
const corpus = JSON.parse(fs.readFileSync(corpusPath, 'utf8'));

// Run Python script to evaluate the same corpus
const pythonScript = `
import json, sys
from pathlib import Path

root = Path("${rootDir}")
sys.path.insert(0, str(root / "assets" / "python"))
from softcloud_security import validate_url

corpus = json.loads(Path("${corpusPath}").read_text(encoding="utf-8"))
results = []
for item in corpus:
    valid, reason = validate_url(item["url"], context=item["context"])
    results.append({"valid": valid, "reason": reason})

print(json.dumps(results))
`;

const pythonBin = fs.existsSync(path.join(rootDir, '.venv/bin/python'))
  ? path.join(rootDir, '.venv/bin/python')
  : 'python3';

let pyResults;
try {
  const stdout = execFileSync(pythonBin, ['-c', pythonScript], { encoding: 'utf8' });
  pyResults = JSON.parse(stdout);
} catch (err) {
  console.error('[FAIL] Could not run Python validation script:', err);
  process.exit(1);
}

let mismatches = 0;
for (let i = 0; i < corpus.length; i++) {
  const item = corpus[i];
  const jsRes = validateUrl(item.url, { context: item.context });
  const pyRes = pyResults[i];

  if (jsRes.valid !== pyRes.valid) {
    console.error(`[MISMATCH] Case ${i}: "${item.url}" (${item.context})`);
    console.error(`  JS:     valid=${jsRes.valid} (${jsRes.reason || ''})`);
    console.error(`  Python: valid=${pyRes.valid} (${pyRes.reason || ''})`);
    mismatches++;
  } else if (jsRes.valid !== item.valid) {
    console.error(`[ERROR] Case ${i}: "${item.url}" (${item.context}) expected ${item.valid}, both got ${jsRes.valid}`);
    mismatches++;
  }
}

if (mismatches > 0) {
  console.error(`[FAIL] Security parity check failed with ${mismatches} mismatch(es)`);
  process.exit(1);
}

console.log(`[OK] Security parity verified: 100% agreement across all ${corpus.length} corpus cases in JS and Python`);
