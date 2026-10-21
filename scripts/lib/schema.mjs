/**
 * scripts/lib/schema.mjs
 * Validates component metadata against canonical schema 2.0.0 and security rules,
 * providing explicit migration normalization for 1.0.0 legacy metadata.
 */

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { validateUrl } from './url-policy.mjs';
import { validateIcon } from './icon-validator.mjs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const schemaPath = path.resolve(__dirname, '../../assets/shared/component-schema.json');
export const SCHEMA = JSON.parse(fs.readFileSync(schemaPath, 'utf8'));
export const SUPPORTED_COMPONENTS = new Set(SCHEMA.allowedComponents);
export const NORMALIZATION = SCHEMA.normalization || {};

/**
 * Explicit migration and normalization of component metadata from schema 1.0.0 to 2.0.0.
 * Rejects conflicting legacy and canonical parameters.
 * @param {object} rawMeta - Component metadata.
 * @param {{ context?: string }} options - Context diagnostics.
 * @returns {object} Normalized 2.0.0 metadata.
 */
export function normalizeComponentMetadata(rawMeta, options = {}) {
  if (!rawMeta || typeof rawMeta !== 'object' || Array.isArray(rawMeta)) {
    throw new TypeError('Metadata must be a non-null object');
  }

  const meta = { ...rawMeta };
  const ctx = options.context ? ` [${options.context}]` : '';

  // 1. Verify component
  const component = meta.component;
  if (!component || !SCHEMA.allowedComponents.includes(component)) {
    throw new Error(`Unknown or unsupported component: '${component}'${ctx}`);
  }

  // 2. Reject conflicting legacy and canonical parameters
  if (component === 'wa-button') {
    if (meta.variant === 'primary' && meta.variant === 'brand') {
      throw new Error(`Conflicting legacy and canonical variant parameters for '${component}'${ctx}`);
    }
    if (meta.outline && meta.appearance && meta.appearance !== 'outlined') {
      throw new Error(
        `Conflicting button outline=true with appearance='${meta.appearance}' in '${component}'${ctx}`
      );
    }
    if (meta.caret !== undefined && meta['with-caret'] !== undefined && meta.caret !== meta['with-caret']) {
      throw new Error(`Conflicting caret and with-caret boolean parameters in '${component}'${ctx}`);
    }
  }

  if (component === 'wa-icon') {
    if (meta.style === 'brands' && meta.family && meta.family !== 'brands') {
      throw new Error(
        `Conflicting legacy style='brands' with family='${meta.family}' in '${component}'${ctx}`
      );
    }
    if (meta.style === 'solid' && meta.variant && meta.variant !== 'solid') {
      throw new Error(
        `Conflicting legacy style='solid' with variant='${meta.variant}' in '${component}'${ctx}`
      );
    }
    if (meta.style === 'regular' && meta.variant && meta.variant !== 'regular') {
      throw new Error(
        `Conflicting legacy style='regular' with variant='${meta.variant}' in '${component}'${ctx}`
      );
    }
  }

  // 3. Apply explicit component normalization
  switch (component) {
    case 'wa-card': {
      if (meta.appearance === 'default') {
        delete meta.appearance;
      } else if (meta.appearance === 'elevated') {
        meta.appearance = NORMALIZATION.cardAppearances?.elevated || 'filled-outlined';
        meta.class = meta.class ? `${meta.class} sc-elevation`.trim() : 'sc-elevation';
      } else if (meta.appearance && NORMALIZATION.cardAppearances?.[meta.appearance]) {
        meta.appearance = NORMALIZATION.cardAppearances[meta.appearance];
      }
      break;
    }

    case 'wa-callout': {
      if (meta.appearance === 'default') {
        delete meta.appearance;
      } else if (meta.appearance && NORMALIZATION.calloutAppearances?.[meta.appearance]) {
        meta.appearance = NORMALIZATION.calloutAppearances[meta.appearance];
      }

      if (meta.icon && NORMALIZATION.iconNames?.[meta.icon]) {
        meta.icon = NORMALIZATION.iconNames[meta.icon];
      }
      break;
    }

    case 'wa-button': {
      if (meta.variant === 'default') {
        delete meta.variant;
      } else if (meta.variant && NORMALIZATION.buttonVariants?.[meta.variant]) {
        meta.variant = NORMALIZATION.buttonVariants[meta.variant];
      }

      if (meta.appearance && NORMALIZATION.buttonAppearances?.[meta.appearance]) {
        meta.appearance = NORMALIZATION.buttonAppearances[meta.appearance];
      }

      if (meta.outline) {
        meta.appearance = 'outlined';
        delete meta.outline;
      }

      if (meta.caret) {
        meta['with-caret'] = true;
        delete meta.caret;
      }

      if (meta.circle) {
        meta.class = meta.class ? `${meta.class} sc-button-circle`.trim() : 'sc-button-circle';
        delete meta.circle;
      }

      if (meta.size) {
        const sizeMap = NORMALIZATION.buttonSizes || { small: 's', medium: 'm', large: 'l' };
        meta.size = sizeMap[String(meta.size).toLowerCase()] || meta.size;
      }
      break;
    }

    case 'wa-icon': {
      if (meta.name && NORMALIZATION.iconNames?.[meta.name]) {
        meta.name = NORMALIZATION.iconNames[meta.name];
      }
      if (meta.style === 'solid') {
        meta.variant = 'solid';
        meta.family = meta.family || 'classic';
      } else if (meta.style === 'regular') {
        meta.variant = 'regular';
        meta.family = meta.family || 'classic';
      } else if (meta.style === 'brands') {
        meta.family = 'brands';
        delete meta.variant;
      }
      delete meta.style;

      if (meta.library === 'fa' || meta.library === 'default') {
        delete meta.library;
      }

      if (meta.family !== 'brands') {
        meta.family = meta.family || 'classic';
        meta.variant = meta.variant || 'solid';
      }
      break;
    }
  }

  meta.schema_version = '2.0.0';
  return meta;
}

/**
 * Validates component metadata against canonical schema 2.0.0 and security policies.
 * @param {object} meta - Metadata object.
 * @param {{ allowMigration?: boolean, context?: string }} options
 * @returns {{ valid: boolean, errors: string[] }}
 */
export function validateComponentMetadata(meta, options = {}) {
  const errors = [];

  if (!meta || typeof meta !== 'object' || Array.isArray(meta)) {
    return { valid: false, errors: ['Metadata must be a non-null object'] };
  }

  const { component, schema_version } = meta;

  if (!component || !SCHEMA.allowedComponents.includes(component)) {
    return { valid: false, errors: [`Unknown or unsupported component: '${component}'`] };
  }

  if (schema_version !== '2.0.0') {
    if (schema_version === '1.0.0' && options.allowMigration) {
      // Allowed during migration
    } else {
      return {
        valid: false,
        errors: [`Unsupported schema version: '${schema_version}' (expected '2.0.0')`],
      };
    }
  }

  const def = SCHEMA.definitions[component];
  if (!def) {
    return { valid: false, errors: [`No schema definition for '${component}'`] };
  }

  // Check required properties
  if (def.required) {
    for (const req of def.required) {
      if (meta[req] === undefined || meta[req] === null || meta[req] === '') {
        errors.push(`Missing required field '${req}' for '${component}'`);
      }
    }
  }

  // Check additionalProperties: false (no unknown fields allowed)
  for (const key of Object.keys(meta)) {
    if (!def.properties[key]) {
      errors.push(`Unknown field '${key}' in '${component}' metadata`);
      continue;
    }

    const propDef = def.properties[key];
    const val = meta[key];

    // Check type
    if (propDef.type === 'string') {
      if (typeof val !== 'string') {
        errors.push(`Field '${key}' must be a string in '${component}'`);
        continue;
      }
      if (propDef.enum && !propDef.enum.includes(val)) {
        errors.push(`Invalid value '${val}' for '${key}'. Allowed: ${propDef.enum.join(', ')}`);
      }
      if (propDef.pattern) {
        const regex = new RegExp(propDef.pattern);
        if (!regex.test(val)) {
          errors.push(`Field '${key}' value '${val}' does not match pattern ${propDef.pattern}`);
        }
      }
    } else if (propDef.type === 'boolean') {
      if (typeof val !== 'boolean') {
        errors.push(`Field '${key}' must be a boolean in '${component}'`);
      }
    }

    // Check for event handler attributes
    if (key.toLowerCase().startsWith('on')) {
      errors.push(`Forbidden event-handler attribute '${key}' in '${component}'`);
    }
  }

  // URL security validation
  if (component === 'wa-button' && meta.href) {
    const urlCheck = validateUrl(meta.href, { context: 'link' });
    if (!urlCheck.valid) {
      errors.push(`Button href violates URL policy: ${urlCheck.reason}`);
    }
  }

  if (component === 'wa-card' && meta.image) {
    const urlCheck = validateUrl(meta.image, { context: 'media' });
    if (!urlCheck.valid) {
      errors.push(`Card image violates URL policy: ${urlCheck.reason}`);
    }
  }

  // Icon asset validation (WA-ICON-004)
  if (component === 'wa-icon' && meta.name) {
    const iconCheck = validateIcon(meta.name, { family: meta.family, variant: meta.variant });
    if (!iconCheck.valid) {
      errors.push(iconCheck.reason);
    }
  }

  return {
    valid: errors.length === 0,
    errors,
  };
}
