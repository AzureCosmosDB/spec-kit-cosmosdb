'use strict';
const fs = require('fs');
const path = require('path');
const { ensureDir } = require('../lib/transform');

exports.install = async function (cwd, prompts, flags) {
  const rulesDir = path.join(cwd, '.cursor', 'rules');
  ensureDir(rulesDir);

  for (const p of prompts) {
    const fm = `---\ndescription: ${JSON.stringify(p.description)}\nglobs: \n---\n`;
    fs.writeFileSync(path.join(rulesDir, `${p.name}.mdc`), fm + '\n' + p.content);
  }

  // Agent Kit installation
  if (flags && flags.withAgentKit) {
    const rulesContent = fs.readFileSync(path.join(__dirname, '..', 'agent-kit-rules.md'), 'utf8');
    const fm = `---\ndescription: "Cosmos DB best practices - Agent Kit"\nglobs: "**/*"\n---\n\n`;
    fs.writeFileSync(path.join(rulesDir, 'cosmos-agent-kit.mdc'), fm + rulesContent);
  }
};
