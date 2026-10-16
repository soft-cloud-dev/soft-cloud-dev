/**
 * scripts/lib/parse5-tree.mjs
 * Utilities for manipulating parse5 AST nodes cleanly without string interpolation.
 */

import { defaultTreeAdapter } from 'parse5';

export const treeAdapter = defaultTreeAdapter;

export function createElement(tagName, attrs = [], children = []) {
  const node = treeAdapter.createElement(tagName, 'http://www.w3.org/1999/xhtml', attrs);
  for (const child of children) {
    treeAdapter.appendChild(node, child);
  }
  return node;
}

export function createTextNode(text) {
  return treeAdapter.createTextNode(String(text));
}

export function createCommentNode(data) {
  return treeAdapter.createCommentNode(String(data));
}

export function getAttr(node, name) {
  if (!node.attrs) return null;
  const attr = node.attrs.find((a) => a.name === name);
  return attr ? attr.value : null;
}

export function setAttr(node, name, value) {
  if (!node.attrs) node.attrs = [];
  const existing = node.attrs.find((a) => a.name === name);
  if (existing) {
    existing.value = String(value);
  } else {
    node.attrs.push({ name, value: String(value) });
  }
}

export function removeAttr(node, name) {
  if (!node.attrs) return;
  node.attrs = node.attrs.filter((a) => a.name !== name);
}

export function getClassList(node) {
  const classVal = getAttr(node, 'class');
  if (!classVal) return [];
  return classVal.trim().split(/\s+/).filter(Boolean);
}

export function hasClass(node, className) {
  return getClassList(node).includes(className);
}

export function removeClass(node, className) {
  const classes = getClassList(node).filter((c) => c !== className);
  if (classes.length === 0) {
    removeAttr(node, 'class');
  } else {
    setAttr(node, 'class', classes.join(' '));
  }
}

export function getTextContent(node) {
  if (treeAdapter.isTextNode(node)) {
    return node.value;
  }
  if (!node.childNodes) return '';
  return node.childNodes.map(getTextContent).join('');
}

export function walkPostOrder(node, callback) {
  if (!node) return;
  const children = node.childNodes ? [...node.childNodes] : [];
  for (const child of children) {
    walkPostOrder(child, callback);
  }
  callback(node);
}

export function replaceChild(parent, oldChild, newChild) {
  const idx = parent.childNodes.indexOf(oldChild);
  if (idx !== -1) {
    parent.childNodes.splice(idx, 1, newChild);
    newChild.parentNode = parent;
    oldChild.parentNode = null;
  }
}

export function removeChild(parent, child) {
  const idx = parent.childNodes.indexOf(child);
  if (idx !== -1) {
    parent.childNodes.splice(idx, 1);
    child.parentNode = null;
  }
}
