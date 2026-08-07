'use strict';
const fs = require('fs');
const path = require('path');
const { withArguments, ensureDir } = require('../lib/transform');

exports.install = async function (cwd, prompts, flags) {
  const cmdDir = path.join(cwd, '.claude', 'commands');
  ensureDir(cmdDir);

  for (const p of prompts) {
    const name = p.name.replace(/^cosmos\./, 'cosmos-');
    fs.writeFileSync(path.join(cmdDir, `${name}.md`), withArguments(p.content));
  }

  // Append to CLAUDE.md
  const claudeFile = path.join(cwd, 'CLAUDE.md');
  const section = '\n\n## Cosmos Intent Commands\n\nThe following `/cosmos-*` slash commands are available:\n' +
    prompts.map(p => `- \`/${p.name.replace(/^cosmos\./, 'cosmos-')}\` — ${p.description}`).join('\n') + '\n';

  if (fs.existsSync(claudeFile)) {
    const existing = fs.readFileSync(claudeFile, 'utf8');
    if (!existing.includes('Cosmos Intent Commands')) {
      fs.appendFileSync(claudeFile, section);
    }
  } else {
    fs.writeFileSync(claudeFile, '# CLAUDE.md\n' + section);
  }

  // Agent Kit installation
  if (flags && flags.withAgentKit) {
    const rulesContent = fs.readFileSync(path.join(__dirname, '..', 'agent-kit-rules.md'), 'utf8');
    const header = '\n\n## Cosmos DB Agent Kit\n\n';
    if (fs.existsSync(claudeFile)) {
      const existing = fs.readFileSync(claudeFile, 'utf8');
      if (!existing.includes('Cosmos DB Agent Kit')) {
        fs.appendFileSync(claudeFile, header + rulesContent);
      }
    } else {
      fs.writeFileSync(claudeFile, '# CLAUDE.md\n' + header.trimStart() + rulesContent);
    }
  }
};
