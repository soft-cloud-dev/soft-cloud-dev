/**
 * scripts/lib/schema.mjs
 * Validates component metadata against canonical schema and security rules.
 */

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { validateUrl } from './url-policy.mjs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const schemaPath = path.resolve(__dirname, '../../assets/shared/component-schema.json');
export const SCHEMA = JSON.parse(fs.readFileSync(schemaPath, 'utf8'));

/**
 * Validates component metadata against schema and security policies.
 * @param {object} meta - Metadata object.
 * @returns {{ valid: boolean, errors: string[] }}
 */
export function validateComponentMetadata(meta) {
  const errors = [];

  if (!meta || typeof meta !== 'object' || Array.isArray(meta)) {
    return { valid: false, errors: ['Metadata must be a non-null object'] };
  }

  const { component, schema_version } = meta;

  if (!component || !SCHEMA.allowedComponents.includes(component)) {
    return { valid: false, errors: [`Unknown or unsupported component: '${component}'`] };
  }

  if (schema_version !== '1.0.0') {
    return { valid: false, errors: [`Unsupported schema version: '${schema_version}' (expected '1.0.0')`] };
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

  return {
    valid: errors.length === 0,
    errors,
  };
}
