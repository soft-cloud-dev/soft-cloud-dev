/**
 * scripts/lib/icon-validator.mjs
 * Validates that authored Font Awesome icons resolve to real local SVG assets.
 */

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

function findRepoRoot(startDir) {
  if (process.env.REPO_ROOT && fs.existsSync(path.join(process.env.REPO_ROOT, 'node_modules/@fortawesome/fontawesome-free/svgs'))) {
    return process.env.REPO_ROOT;
  }
  let cur = startDir;
  while (cur && cur !== path.dirname(cur)) {
    if (fs.existsSync(path.join(cur, 'node_modules/@fortawesome/fontawesome-free/svgs'))) {
      return cur;
    }
    cur = path.dirname(cur);
  }
  cur = process.cwd();
  while (cur && cur !== path.dirname(cur)) {
    if (fs.existsSync(path.join(cur, 'node_modules/@fortawesome/fontawesome-free/svgs'))) {
      return cur;
    }
    cur = path.dirname(cur);
  }
  return path.resolve(startDir, '../..');
}

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const rootDir = findRepoRoot(__dirname);

const SRC_SVGS_DIR = path.join(rootDir, 'node_modules/@fortawesome/fontawesome-free/svgs');
const STAGED_SVGS_DIR = path.join(rootDir, '_build/html/vendor/fontawesome/svgs');
const METADATA_PATH = path.join(rootDir, 'node_modules/@fortawesome/fontawesome-free/metadata/icon-families.json');

let aliasMap = null;
export function getIconAliasMap() {
  if (aliasMap) return aliasMap;
  aliasMap = new Map();
  try {
    if (fs.existsSync(METADATA_PATH)) {
      const data = JSON.parse(fs.readFileSync(METADATA_PATH, 'utf8'));
      for (const [canonical, info] of Object.entries(data)) {
        if (info.aliases?.names) {
          for (const alias of info.aliases.names) {
            aliasMap.set(alias, canonical);
          }
        }
      }
    }
  } catch {
    // Non-fatal fallback
  }
  return aliasMap;
}

/**
 * Resolves the folder name for a given family and variant.
 * @param {string} family - 'classic' | 'brands'
 * @param {string} variant - 'solid' | 'regular'
 * @returns {'solid' | 'regular' | 'brands'}
 */
export function getIconFolder(family = 'classic', variant = 'solid') {
  if (family === 'brands' || variant === 'brands') {
    return 'brands';
  }
  if (variant === 'regular') {
    return 'regular';
  }
  return 'solid';
}

/**
 * Validates that an icon exists in local Font Awesome Free SVG assets.
 * @param {string} name - Icon name
 * @param {{ family?: string, variant?: string, targetDir?: string }} options
 * @returns {{ valid: boolean, canonicalName: string, folder: string, filePath?: string, reason?: string }}
 */
export function validateIcon(name, options = {}) {
  if (!name || typeof name !== 'string') {
    return { valid: false, canonicalName: '', folder: '', reason: 'Icon name must be a non-empty string' };
  }

  const cleanName = name.trim().toLowerCase();
  const folder = getIconFolder(options.family, options.variant);

  const aliases = getIconAliasMap();
  const canonicalName = aliases.get(cleanName) || cleanName;

  // Search priority: targetDir (staged) -> SRC_SVGS_DIR
  const searchDirs = [];
  if (options.targetDir) {
    searchDirs.push(path.join(options.targetDir, 'vendor/fontawesome/svgs', folder));
    searchDirs.push(path.join(options.targetDir, folder));
  }
  if (fs.existsSync(STAGED_SVGS_DIR)) {
    searchDirs.push(path.join(STAGED_SVGS_DIR, folder));
  }
  if (fs.existsSync(SRC_SVGS_DIR)) {
    searchDirs.push(path.join(SRC_SVGS_DIR, folder));
  }

  // Check both requested name and canonical name
  const candidateNames = cleanName === canonicalName ? [cleanName] : [cleanName, canonicalName];

  for (const dir of searchDirs) {
    for (const cand of candidateNames) {
      const p = path.join(dir, `${cand}.svg`);
      if (fs.existsSync(p)) {
        return {
          valid: true,
          canonicalName,
          folder,
          filePath: p,
        };
      }
    }
  }

  return {
    valid: false,
    canonicalName,
    folder,
    reason: `Icon '${cleanName}' not found in local Font Awesome ${folder} library`,
  };
}
