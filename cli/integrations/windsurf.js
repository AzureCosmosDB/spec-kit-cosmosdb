'use strict';
const fs = require('fs');
const path = require('path');
const { ensureDir } = require('../lib/transform');

exports.install = async function (cwd, prompts, flags) {
  const rulesDir = path.join(cwd, '.windsurf', 'rules');
  ensureDir(rulesDir);

  for (const p of prompts) {
    const name = p.name.replace(/^cosmos\./, 'cosmos-');
    fs.writeFileSync(path.join(rulesDir, `${name}.md`), p.content);
  }

  // Agent Kit installation
  if (flags && flags.withAgentKit) {
    const rulesContent = fs.readFileSync(path.join(__dirname, '..', 'agent-kit-rules.md'), 'utf8');
    fs.writeFileSync(path.join(rulesDir, 'cosmos-agent-kit.md'), rulesContent);
  }
};
