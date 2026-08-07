'use strict';

const fs = require('fs');
const path = require('path');

const PROMPTS_DIR = path.resolve(__dirname, '../../prompts');

function loadPrompts() {
  const prompts = [];
  const categories = ['micro', 'component', 'scaffold', 'meta'];
  for (const cat of categories) {
    const dir = path.join(PROMPTS_DIR, cat);
    if (!fs.existsSync(dir)) continue;
    for (const file of fs.readdirSync(dir).filter(f => f.endsWith('.md'))) {
      const content = fs.readFileSync(path.join(dir, file), 'utf8');
      const name = file.replace(/\.md$/, '');
      const { title, description } = extractMeta(content);
      prompts.push({ name, title, description, content, category: cat, file });
    }
  }
  return prompts;
}

function extractMeta(content) {
  const lines = content.split('\n');
  let title = '', description = '';
  for (const line of lines) {
    if (!title && line.startsWith('# ')) {
      title = line.replace(/^#\s*/, '').replace(/^\//, '');
      continue;
    }
    if (!description && line.startsWith('>')) {
      description = line.replace(/^>\s*/, '');
      break;
    }
  }
  return { title: title || 'Cosmos Intent', description: description || title || '' };
}

function toFrontmatter(obj) {
  let fm = '---\n';
  for (const [k, v] of Object.entries(obj)) {
    fm += `${k}: ${typeof v === 'string' ? JSON.stringify(v) : v}\n`;
  }
  fm += '---\n';
  return fm;
}

function withArguments(content) {
  // Add $ARGUMENTS placeholder at end if not present
  if (!content.includes('$ARGUMENTS')) {
    return content + '\n\n## User Input\n\n$ARGUMENTS\n';
  }
  return content;
}

function ensureDir(dir) {
  fs.mkdirSync(dir, { recursive: true });
}

module.exports = { loadPrompts, extractMeta, toFrontmatter, withArguments, ensureDir };
