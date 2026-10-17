/**
 * assets/static/softcloud-webawesome.mjs
 * Web Awesome 3.14.0 + Font Awesome Free 6.5.2 Runtime Bootstrap.
 * Configures self-hosted SVG icon resolution before Web Awesome SSR-aware loader runs.
 */

import { setBasePath, setIconPath } from '../vendor/webawesome/webawesome.js';

const basePath = new URL('../vendor/webawesome/', import.meta.url);
setBasePath(basePath.pathname.replace(/\/$/, ''));

const iconPath = new URL('../vendor/fontawesome/svgs/', import.meta.url);
setIconPath(iconPath.pathname.replace(/\/$/, ''));

await import('../vendor/webawesome/webawesome.ssr-loader.js');
