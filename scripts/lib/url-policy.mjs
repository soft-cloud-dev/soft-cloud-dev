/**
 * scripts/lib/url-policy.mjs
 * URL policy enforcement for SoftCloud Web Awesome SSR components.
 */

const CONTROL_CHARS_REGEX = /[\x00-\x1F\x7F]/;
const HTML_CHARS_REGEX = /[<>"']/;
const BACKSLASH_REGEX = /\\/;

const ALLOWED_SCHEMES_LINK = new Set(['http:', 'https:', 'mailto:']);
const ALLOWED_SCHEMES_MEDIA = new Set(['http:', 'https:']);

/**
 * Validates a URL against SoftCloud security policy.
 * @param {string} url - URL string to validate.
 * @param {{ context?: 'link' | 'media' }} options - Context: 'link' (default) or 'media'.
 * @returns {{ valid: boolean, reason?: string, sanitizedUrl?: string }}
 */
export function validateUrl(url, options = {}) {
  const context = options.context || 'link';

  if (typeof url !== 'string' || url.trim().length === 0) {
    return { valid: false, reason: 'URL must be a non-empty string' };
  }

  const trimmed = url.trim();

  // 1. Control character check
  if (CONTROL_CHARS_REGEX.test(trimmed)) {
    return { valid: false, reason: 'URL contains forbidden control characters' };
  }

  // 2. Backslash check
  if (BACKSLASH_REGEX.test(trimmed)) {
    return { valid: false, reason: 'URL contains forbidden backslashes' };
  }

  // 3. HTML / attribute injection characters
  if (HTML_CHARS_REGEX.test(trimmed)) {
    return { valid: false, reason: 'URL contains forbidden HTML characters' };
  }

  // 4. Protocol-relative check
  if (trimmed.startsWith('//')) {
    return { valid: false, reason: 'Protocol-relative URLs are forbidden' };
  }

  // 5. Scheme extraction
  // Match potential scheme (e.g. "javascript:", "https:", "mailto:")
  const schemeMatch = trimmed.match(/^([a-zA-Z][a-zA-Z0-9+.-]*):/);

  if (schemeMatch) {
    const scheme = schemeMatch[1].toLowerCase() + ':';

    if (context === 'media') {
      if (!ALLOWED_SCHEMES_MEDIA.has(scheme)) {
        return { valid: false, reason: `Scheme '${scheme}' is not permitted for media` };
      }
    } else {
      if (!ALLOWED_SCHEMES_LINK.has(scheme)) {
        return { valid: false, reason: `Scheme '${scheme}' is not permitted for links` };
      }
    }

    if (scheme === 'mailto:') {
      // Validate mailto format: mailto:user@domain.com
      const emailPart = trimmed.slice(7);
      if (!emailPart || emailPart.startsWith('?') || emailPart.startsWith('#')) {
        return { valid: false, reason: 'Malformed mailto URL' };
      }
      return { valid: true, sanitizedUrl: trimmed };
    }

    // For http: and https:, parse with URL to inspect host and userinfo
    try {
      const parsed = new URL(trimmed);
      if (parsed.protocol !== scheme) {
        return { valid: false, reason: 'Parsed protocol mismatch' };
      }
      if (!parsed.hostname || parsed.hostname.length === 0) {
        return { valid: false, reason: 'Missing hostname in absolute URL' };
      }
      if (parsed.username || parsed.password) {
        return { valid: false, reason: 'Credentials in URL are forbidden' };
      }
      return { valid: true, sanitizedUrl: trimmed };
    } catch {
      return { valid: false, reason: 'Malformed absolute URL' };
    }
  }

  // Relative URLs (path, query, fragment)
  // Check for colon in first segment that isn't a scheme
  const firstSlash = trimmed.indexOf('/');
  const colonIndex = trimmed.indexOf(':');
  if (colonIndex !== -1 && (firstSlash === -1 || colonIndex < firstSlash)) {
    return { valid: false, reason: 'Unknown or unsupported URL scheme' };
  }

  return { valid: true, sanitizedUrl: trimmed };
}
