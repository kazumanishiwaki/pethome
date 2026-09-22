/* Run the existing self-check handler in a no-network DOM harness.
 * The review therefore uses the SAME result copy/conditions as the public UI.
 * This is a content-export test, not a substitute for browser layout tests.
 */
'use strict';
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const definitions = JSON.parse(fs.readFileSync(0, 'utf8'));
class Element {
  constructor() { this.textContent = ''; this.children = []; this.handlers = {}; this.hidden = true; this.href = ''; }
  addEventListener(name, callback) { this.handlers[name] = callback; }
  append(...nodes) { this.children.push(...nodes); }
  replaceChildren(...nodes) { this.children = nodes; }
  setAttribute() {} focus() {} scrollIntoView() {} click() {} remove() {}
  reportValidity() { return true; }
}
const form = new Element();
const nodes = new Map(['#self-check', '#check-result', '#result-title', '#result-body', '#result-checks', '#result-link', '#save-brief'].map(id => [id, new Element()]));
nodes.set('#self-check', form);
let memo = '';
const document = {
  querySelector: id => nodes.get(id) || null,
  querySelectorAll: () => [],
  createElement: () => new Element(),
  createDocumentFragment: () => new Element(),
  body: new Element()
};
const context = {
  document,
  FormData: class { constructor(f) { this.values = f.values; } get(key) { return this.values[key]; } },
  matchMedia: () => ({matches:true}),
  Blob: class { constructor(parts) { this.parts = parts; } },
  URL: {createObjectURL(blob) { memo = blob.parts.join('').replace(/^\uFEFF/,''); return 'blob:review'; }, revokeObjectURL() {}},
  setTimeout: fn => fn()
};
vm.runInNewContext(fs.readFileSync(path.join(root, 'assets/js/site.js'), 'utf8'), context, {timeout:2000, filename:'site.js'});
if (typeof form.handlers.submit !== 'function') throw new Error('Self-check submit handler missing');
const rows = [];
for (const pet of definitions.pet) for (const home of definitions.home) for (const goal of definitions.goal) {
  form.values = {pet:pet.value, home:home.value, goal:goal.value};
  nodes.get('#result-title').textContent = '';
  form.handlers.submit({preventDefault(){}});
  const title = nodes.get('#result-title').textContent;
  if (!title) throw new Error('Missing result for ' + JSON.stringify(form.values));
  nodes.get('#save-brief').handlers.click();
  rows.push({input:{...form.values}, labels:{pet:pet.label,home:home.label,goal:goal.label}, title, body:nodes.get('#result-body').textContent,
    checks:nodes.get('#result-checks').children.map(n=>n.textContent), link:nodes.get('#result-link').href, memo});
}
process.stdout.write(JSON.stringify(rows));
