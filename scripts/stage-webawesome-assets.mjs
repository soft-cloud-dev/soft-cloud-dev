#!/usr/bin/env node
/**
 * scripts/stage-webawesome-assets.mjs
 * Stages all Web Awesome, Font Awesome (including self-hosted SVGs),
 * and SoftCloud runtime static assets into the publication build directory.
 */

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const rootDir = path.resolve(__dirname, '..');

export function stageAssets(targetDir) {
  const destRoot = path.resolve(process.cwd(), targetDir);
  if (!fs.existsSync(destRoot)) {
    fs.mkdirSync(destRoot, { recursive: true });
  }

  // 1. Copy Web Awesome dist-cdn tree and merge redundant chunks
  const waSrc = path.join(rootDir, 'node_modules/@awesome.me/webawesome/dist-cdn');
  const waDst = path.join(destRoot, 'vendor/webawesome');
  fs.rmSync(waDst, { recursive: true, force: true });
  fs.mkdirSync(waDst, { recursive: true });
  fs.cpSync(waSrc, waDst, { recursive: true });
  const chunkStats = mergeWebAwesomeChunks(waDst);

  // 2. Copy Font Awesome CSS and webfonts
  const faCssSrc = path.join(rootDir, 'node_modules/@fortawesome/fontawesome-free/css/all.min.css');
  const faWebfontsSrc = path.join(rootDir, 'node_modules/@fortawesome/fontawesome-free/webfonts');
  const faCssDst = path.join(destRoot, 'vendor/fontawesome/css/all.min.css');
  const faWebfontsDst = path.join(destRoot, 'vendor/fontawesome/webfonts');

  fs.mkdirSync(path.dirname(faCssDst), { recursive: true });
  fs.copyFileSync(faCssSrc, faCssDst);

  fs.mkdirSync(faWebfontsDst, { recursive: true });
  fs.cpSync(faWebfontsSrc, faWebfontsDst, { recursive: true });

  // 3. Copy Font Awesome SVGs (solid, regular, brands) for Web Awesome setIconPath() (WA-ICON-001)
  const faSvgsSrc = path.join(rootDir, 'node_modules/@fortawesome/fontawesome-free/svgs');
  const faSvgsDst = path.join(destRoot, 'vendor/fontawesome/svgs');
  fs.mkdirSync(faSvgsDst, { recursive: true });
  fs.cpSync(faSvgsSrc, faSvgsDst, { recursive: true });

  // Stage aliases for legacy icon names (e.g. info-circle -> circle-info)
  stageIconAliases(faSvgsDst);

  // 4. Copy SoftCloud static assets
  const staticSrc = path.join(rootDir, 'assets/static');
  const staticDst = path.join(destRoot, 'static');
  fs.mkdirSync(staticDst, { recursive: true });
  fs.cpSync(staticSrc, staticDst, { recursive: true });

  // Verification of key assets
  const expectedFiles = [
    path.join(destRoot, 'vendor/webawesome/webawesome.js'),
    path.join(destRoot, 'vendor/webawesome/webawesome.ssr-loader.js'),
    path.join(destRoot, 'vendor/webawesome/styles/webawesome.css'),
    path.join(destRoot, 'vendor/fontawesome/css/all.min.css'),
    path.join(destRoot, 'vendor/fontawesome/svgs/solid/server.svg'),
    path.join(destRoot, 'vendor/fontawesome/svgs/brands/github.svg'),
    path.join(destRoot, 'static/softcloud.css'),
    path.join(destRoot, 'static/softcloud-theme.js'),
    path.join(destRoot, 'static/softcloud-theme-init.js'),
    path.join(destRoot, 'static/softcloud-webawesome.mjs'),
  ];

  for (const f of expectedFiles) {
    if (!fs.existsSync(f)) {
      throw new Error(`Asset staging failed: missing expected file ${f}`);
    }
  }

  return { destRoot, stagedCount: expectedFiles.length, chunkStats };
}

function collectJsFiles(dir, list = []) {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      collectJsFiles(full, list);
    } else if (entry.isFile() && entry.name.endsWith('.js')) {
      list.push(full);
    }
  }
  return list;
}

function parseEsmChunk(content) {
  const imports = [];
  const exportsMap = new Map();
  let body = content.replace(/^\/\*![\s\S]*?\*\/\s*/, '');

  body = body.replace(/^import\s+(?:\{([\s\S]*?)\}\s+from\s+)?"([^"]+)";\s*/gm, (_m, spec, from) => {
    const names = spec
      ? spec.split(',').map((s) => s.replace(/\s+/g, ' ').trim()).filter(Boolean)
      : [];
    imports.push({ names, from });
    return '';
  });

  body = body.replace(/^export\s+\{([\s\S]*?)\};\s*/gm, (_m, spec) => {
    const items = spec.split(',').map((s) => s.replace(/\s+/g, ' ').trim()).filter(Boolean);
    for (const item of items) {
      const parts = item.split(/\s+as\s+/);
      const exportedName = parts.length > 1 ? parts[1].trim() : parts[0].trim();
      exportsMap.set(exportedName, item);
    }
    return '';
  });

  return { imports, exportsMap, body: body.trim() };
}

/**
 * Merges and prunes Web Awesome dist-cdn chunks in the staged directory:
 * 1. Removes the 4 empty license-only chunks.
 * 2. Prunes the unused `react/` wrapper directory and 74 React-only chunks.
 * 3. Merges the 12 core `webawesome.js` bootstrap chunks into `chunk.JHZRD2LV.js`.
 * 4. Merges all 44 `src/events/*.ts` chunks into `chunk.26QE47KB.js`.
 * 5. Merges all 22 `src/internal/*` and `src/styles/component/*` chunks into `chunk.LBLI4KS5.js`.
 * 6. Merges all 70 per-component `.styles.ts` chunks and 6 component-internal helper chunks
 *    directly into their owning component chunks.
 * 7. Merges the core SSR component chunks (`icon`, `spinner`, `callout`, `card`, `button`)
 *    into `chunk.QVJVDGCX.js`.
 */
export function mergeWebAwesomeChunks(waDst) {
  const chunkDir = path.join(waDst, 'chunks');
  if (!fs.existsSync(chunkDir)) {
    return { initialCount: 0, finalCount: 0 };
  }

  const initialChunks = fs.readdirSync(chunkDir).filter((f) => f.endsWith('.js')).sort();
  const emptyChunks = new Set(
    initialChunks.filter((f) => {
      const c = fs.readFileSync(path.join(chunkDir, f), 'utf8');
      return !c.replace(/\/\*[\s\S]*?\*\//g, '').trim();
    })
  );

  // Prune unused React wrapper directory and unreachable React-only chunks
  fs.rmSync(path.join(waDst, 'react'), { recursive: true, force: true });
  const nonReactEntries = collectJsFiles(waDst).filter(
    (p) => !path.relative(waDst, p).startsWith('chunks/')
  );
  const reachable = new Set();
  const queue = [];

  for (const entry of nonReactEntries) {
    const c = fs.readFileSync(entry, 'utf8');
    for (const m of c.matchAll(/chunk\.[A-Z0-9]+\.js/g)) {
      if (!reachable.has(m[0])) {
        reachable.add(m[0]);
        queue.push(m[0]);
      }
    }
  }
  while (queue.length > 0) {
    const ch = queue.shift();
    const p = path.join(chunkDir, ch);
    if (!fs.existsSync(p)) continue;
    const c = fs.readFileSync(p, 'utf8');
    for (const m of c.matchAll(/chunk\.[A-Z0-9]+\.js/g)) {
      if (!reachable.has(m[0])) {
        reachable.add(m[0]);
        queue.push(m[0]);
      }
    }
  }

  for (const f of initialChunks) {
    if (!reachable.has(f) || emptyChunks.has(f)) {
      fs.rmSync(path.join(chunkDir, f), { force: true });
    }
  }

  // Alias `i` -> `__wa_css` in `.styles.ts` chunks to prevent identifier collision with component chunks
  const remainingAfterPrune = fs.readdirSync(chunkDir).filter((f) => f.endsWith('.js')).sort();
  for (const f of remainingAfterPrune) {
    const p = path.join(chunkDir, f);
    let c = fs.readFileSync(p, 'utf8');
    const srcs = [...c.matchAll(/\/\/ (src\/[^\n]+)/g)].map((m) => m[1]);
    if (srcs.length === 1 && srcs[0].includes('.styles.') && c.includes('chunk.TLFIX76K.js')) {
      c = c.replace(
        /import\s+\{\s*i\s*\}\s+from\s+"\.\/chunk\.TLFIX76K\.js";/,
        'import {\n  i as __wa_css\n} from "./chunk.TLFIX76K.js";'
      );
      c = c.replace(/=\s*i`/g, '= __wa_css`');
      fs.writeFileSync(p, c, 'utf8');
    }
  }

  // Alias `e` in icon.ts and card.ts so they do not collide with `@state()` `e` in button.ts
  const iconChunkPath = path.join(chunkDir, 'chunk.SLTXS4GR.js');
  if (fs.existsSync(iconChunkPath)) {
    let ic = fs.readFileSync(iconChunkPath, 'utf8');
    ic = ic.replace(
      /import\s+\{\s*e\s*\}\s+from\s+"\.\/chunk\.EFUXUR2V\.js";/,
      'import {\n  e as __wa_is_template\n} from "./chunk.EFUXUR2V.js";'
    );
    ic = ic.replace(/\bif\s*\(e\(svg\)\)/g, 'if (__wa_is_template(svg))');
    fs.writeFileSync(iconChunkPath, ic, 'utf8');
  }

  const cardChunkPath = path.join(chunkDir, 'chunk.2E2VZMOR.js');
  if (fs.existsSync(cardChunkPath)) {
    let cc = fs.readFileSync(cardChunkPath, 'utf8');
    cc = cc.replace(
      /import\s+\{\s*e\s*\}\s+from\s+"\.\/chunk\.KWDPKKFO\.js";/,
      'import {\n  e as e2\n} from "./chunk.KWDPKKFO.js";'
    );
    cc = cc.replace(/class=\$\{e\(\{/g, 'class=${e2({');
    fs.writeFileSync(cardChunkPath, cc, 'utf8');
  }

  const redirectMap = new Map();
  function resolveRedirect(chunkName) {
    let cur = chunkName;
    while (redirectMap.has(cur)) cur = redirectMap.get(cur);
    return cur;
  }

  function mergeChunkGroup(groupOrder, targetChunk) {
    const existingGroup = groupOrder.filter((ch) => fs.existsSync(path.join(chunkDir, ch)));
    if (existingGroup.length <= 1) return;

    const groupSet = new Set(existingGroup);
    const extNamedImports = new Map();
    const extSideEffects = new Set();
    const mergedExports = new Map();
    const bodies = [];

    for (const ch of existingGroup) {
      const raw = fs.readFileSync(path.join(chunkDir, ch), 'utf8');
      const { imports, exportsMap, body } = parseEsmChunk(raw);

      for (const imp of imports) {
        const baseFrom = path.basename(imp.from);
        if (emptyChunks.has(baseFrom)) continue;
        const resolvedBase = resolveRedirect(baseFrom);
        if (groupSet.has(baseFrom) || groupSet.has(resolvedBase)) continue;
        const resolvedFrom = imp.from.replace(baseFrom, resolvedBase);
        if (imp.names.length === 0) {
          extSideEffects.add(resolvedFrom);
        } else {
          if (!extNamedImports.has(resolvedFrom)) extNamedImports.set(resolvedFrom, new Set());
          for (const n of imp.names) extNamedImports.get(resolvedFrom).add(n);
        }
      }

      for (const [expName, fullSpec] of exportsMap) {
        mergedExports.set(expName, fullSpec);
      }
      if (body) bodies.push(body);
    }

    const lines = ['/*! Copyright 2026 Fonticons, Inc. - https://webawesome.com/license */'];
    for (const [fromPath, specSet] of extNamedImports) {
      lines.push(`import {\n  ${[...specSet].join(',\n  ')}\n} from "${fromPath}";`);
    }
    for (const fromPath of extSideEffects) {
      if (!extNamedImports.has(fromPath)) {
        lines.push(`import "${fromPath}";`);
      }
    }
    lines.push('');
    lines.push(bodies.join('\n\n'));
    if (mergedExports.size > 0) {
      lines.push('');
      lines.push(`export {\n  ${[...mergedExports.values()].join(',\n  ')}\n};`);
    }
    lines.push('');

    fs.writeFileSync(path.join(chunkDir, targetChunk), lines.join('\n'), 'utf8');
    for (const ch of existingGroup) {
      if (ch !== targetChunk) {
        redirectMap.set(ch, targetChunk);
        fs.rmSync(path.join(chunkDir, ch), { force: true });
      }
    }
  }

  // Group 1: Bootstrap core (webawesome.js / webawesome.ssr-loader.js shared runtime) -> chunk.JHZRD2LV.js
  mergeChunkGroup(
    [
      'chunk.JHZRD2LV.js',
      'chunk.HGBRCPUS.js',
      'chunk.YPRC5XZF.js',
      'chunk.KKI7M5DP.js',
      'chunk.UDRJMWVZ.js',
      'chunk.HOKYDFUG.js',
      'chunk.D5HA4OFX.js',
      'chunk.DL7HG4WM.js',
      'chunk.LN7M2NWC.js',
      'chunk.ZFSRFTCP.js',
      'chunk.LRYJ2M5H.js',
      'chunk.X55YNZ3B.js',
    ],
    'chunk.JHZRD2LV.js'
  );

  // Group 2: All 44 custom event chunks (src/events/*.ts) -> chunk.26QE47KB.js
  const chunksBeforeEvents = fs.readdirSync(chunkDir).filter((f) => f.endsWith('.js')).sort();
  const eventGroup = chunksBeforeEvents.filter((f) => {
    const c = fs.readFileSync(path.join(chunkDir, f), 'utf8');
    const srcs = [...c.matchAll(/\/\/ (src\/[^\n]+)/g)].map((m) => m[1]);
    return srcs.length > 0 && srcs.every((s) => s.startsWith('src/events/'));
  });
  mergeChunkGroup(eventGroup, 'chunk.26QE47KB.js');

  // Group 3: All 22 internal & shared component style chunks (src/internal/* + src/styles/component/*) -> chunk.LBLI4KS5.js
  const chunksBeforeInternal = fs.readdirSync(chunkDir).filter((f) => f.endsWith('.js')).sort();
  const internalGroupRest = chunksBeforeInternal.filter((f) => {
    if (f === 'chunk.LBLI4KS5.js' || f === 'chunk.5VKLVAP2.js') return false;
    const c = fs.readFileSync(path.join(chunkDir, f), 'utf8');
    const srcs = [...c.matchAll(/\/\/ (src\/[^\n]+)/g)].map((m) => m[1]);
    return srcs.length > 0 && srcs.every((s) => s.startsWith('src/internal/') || s.startsWith('src/styles/'));
  });
  mergeChunkGroup(['chunk.LBLI4KS5.js', 'chunk.5VKLVAP2.js', ...internalGroupRest], 'chunk.LBLI4KS5.js');

  // Group 4: Per-component .styles.ts and 1-to-1 internal component helper chunks into owning component chunk
  const chunksBeforeCompPairs = fs.readdirSync(chunkDir).filter((f) => f.endsWith('.js')).sort();
  const chunkImporters = new Map(chunksBeforeCompPairs.map((f) => [f, []]));
  for (const f of chunksBeforeCompPairs) {
    const c = fs.readFileSync(path.join(chunkDir, f), 'utf8');
    const deps = [...new Set([...c.matchAll(/chunk\.[A-Z0-9]+\.js/g)].map((m) => resolveRedirect(m[0])))];
    for (const d of deps) {
      if (d !== f && chunkImporters.has(d)) chunkImporters.get(d).push(f);
    }
  }

  const subChunksByTarget = new Map();
  for (const f of chunksBeforeCompPairs) {
    const c = fs.readFileSync(path.join(chunkDir, f), 'utf8');
    const srcs = [...c.matchAll(/\/\/ (src\/components\/[^\n]+)/g)].map((m) => m[1]);
    if (
      srcs.length === 1 &&
      (srcs[0].includes('.styles.') ||
        srcs[0].includes('/internal/') ||
        srcs[0].endsWith('/request.ts') ||
        srcs[0].endsWith('/autoplay-controller.ts'))
    ) {
      const imps = chunkImporters.get(f);
      if (imps && imps.length === 1) {
        const target = imps[0];
        if (!subChunksByTarget.has(target)) subChunksByTarget.set(target, []);
        subChunksByTarget.get(target).push(f);
      }
    }
  }
  for (const [target, subs] of subChunksByTarget) {
    mergeChunkGroup([...subs, target], target);
  }

  // Group 5: Core SSR components (icon, spinner, callout, card, button) -> chunk.QVJVDGCX.js
  mergeChunkGroup(
    [
      'chunk.SLTXS4GR.js',
      'chunk.L2PH6XPF.js',
      'chunk.BGEID5TE.js',
      'chunk.2E2VZMOR.js',
      'chunk.QVJVDGCX.js',
    ],
    'chunk.QVJVDGCX.js'
  );

  // Rewrite and deduplicate imports across all remaining JS files in waDst
  for (const filePath of collectJsFiles(waDst)) {
    const fileName = path.basename(filePath);
    const isChunk = path.basename(path.dirname(filePath)) === 'chunks';
    let content = fs.readFileSync(filePath, 'utf8');

    const namedImports = new Map();
    const sideEffects = [];
    const importOrder = [];

    let headerComment = '';
    const hcMatch = content.match(/^\/\*![\s\S]*?\*\/\s*/);
    if (hcMatch) {
      headerComment = hcMatch[0].trim();
      content = content.slice(hcMatch[0].length);
    }

    const stripped = content.replace(
      /^import\s+(?:\{([\s\S]*?)\}\s+from\s+)?"([^"]+)";\s*/gm,
      (_m, spec, from) => {
        const baseFrom = path.basename(from);
        if (emptyChunks.has(baseFrom)) return '';
        const resolvedBase = resolveRedirect(baseFrom);
        if (isChunk && resolvedBase === fileName) return '';
        const resolvedFrom = from.replace(baseFrom, resolvedBase);
        const names = spec
          ? spec.split(',').map((s) => s.replace(/\s+/g, ' ').trim()).filter(Boolean)
          : [];
        if (names.length > 0) {
          if (!namedImports.has(resolvedFrom)) {
            namedImports.set(resolvedFrom, new Set());
            importOrder.push({ path: resolvedFrom });
          }
          for (const n of names) namedImports.get(resolvedFrom).add(n);
        } else if (!sideEffects.includes(resolvedFrom)) {
          sideEffects.push(resolvedFrom);
          importOrder.push({ path: resolvedFrom });
        }
        return '';
      }
    );

    const outLines = [];
    if (headerComment) outLines.push(headerComment);
    const emittedPaths = new Set();
    for (const item of importOrder) {
      if (emittedPaths.has(item.path)) continue;
      emittedPaths.add(item.path);
      if (namedImports.has(item.path)) {
        const specs = [...namedImports.get(item.path)];
        outLines.push(`import {\n  ${specs.join(',\n  ')}\n} from "${item.path}";`);
      } else {
        outLines.push(`import "${item.path}";`);
      }
    }
    const rest = stripped.trim();
    if (rest) outLines.push(rest);
    fs.writeFileSync(filePath, outLines.join('\n') + '\n', 'utf8');
  }

  const finalChunks = fs.readdirSync(chunkDir).filter((f) => f.endsWith('.js'));
  return {
    initialCount: initialChunks.length,
    finalCount: finalChunks.length,
    eliminatedCount: initialChunks.length - finalChunks.length,
  };
}

function stageIconAliases(svgsDest) {
  const metaPath = path.join(rootDir, 'node_modules/@fortawesome/fontawesome-free/metadata/icon-families.json');
  if (!fs.existsSync(metaPath)) return;

  try {
    const data = JSON.parse(fs.readFileSync(metaPath, 'utf8'));
    const folders = ['solid', 'regular', 'brands'];

    for (const [canonical, info] of Object.entries(data)) {
      if (!info.aliases?.names) continue;

      for (const folder of folders) {
        const folderPath = path.join(svgsDest, folder);
        if (!fs.existsSync(folderPath)) continue;

        const canonicalFile = path.join(folderPath, `${canonical}.svg`);
        if (!fs.existsSync(canonicalFile)) continue;

        for (const alias of info.aliases.names) {
          const aliasFile = path.join(folderPath, `${alias}.svg`);
          if (!fs.existsSync(aliasFile)) {
            try {
              fs.copyFileSync(canonicalFile, aliasFile);
            } catch {
              // Ignore copy collision
            }
          }
        }
      }
    }
  } catch (err) {
    console.warn('[WARN] Staging icon aliases encountered warning:', err.message);
  }
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const target = process.argv[2] || '_build/html';
  try {
    const { destRoot } = stageAssets(target);
    console.log(`[OK] Runtime assets staged successfully to ${destRoot}`);
  } catch (err) {
    console.error(`[FAIL] Asset staging error:`, err);
    process.exit(1);
  }
}
